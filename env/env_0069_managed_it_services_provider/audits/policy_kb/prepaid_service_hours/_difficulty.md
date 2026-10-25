# KB-doc policy audit — prepaid_service_hours (product timebank, TimeBank Prepaid Service Hours)

## revision_1

Auditor: erl-kb-doc-policy-audit agent, 2026-10-18 (independent of the renderer, the instantiators and the policy-side auditor).

### Entry conditions (Step 0)
- Policy-side verdict (tail line of audits/policy_task/prepaid_service_hours/_difficulty.md, read before the freeze, nothing else under audits/): `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot supplied with the brief (coordinator, 2026-10-18T16:59:03): check_docs DOCS OK; check_traceability TRACEABILITY OK (non-OK lines 0); check_extended / check_task_tools / replay_tasks --check / check_solvability / check_compute / check_grounding / check_cross_fire rc=0; timebank.extended.yaml sha256 4bf1e7bb...0a0; task_tools.py sha256 f7013dc5...39c; docs/timebank 63 files, tree sha256 6368ac29...a45.
- Runtime view and DB access path supplied: 0.runtime.json a97f79cd...0fd, 1.runtime.json ef38fb4d...65e (hashes re-verified); db_query.py tool-shaped queries. Blind audits are blind on the DB side.

### Per-task verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form | Files |
|---|---|---|---|---|
| 0 (repeat order, 20-Hour) | PASS — blind answer equals GT on every write (2.82 / 1.55 / 2938.80), every factor tier, the tree (3 state-derived hops) | PASS | PASS | runtime_context/prepaid_service_hours/0.md, policy_kb/prepaid_service_hours/0.md |
| 1 (extension, 160-Hour) | PASS — blind answer equals GT on every write (2.36 / 6.47 / 4.81 / 325.87, 2027-06-08), every factor tier, the tree (3 state-derived hops) | PASS | PASS | runtime_context/prepaid_service_hours/1.md, policy_kb/prepaid_service_hours/1.md |

### Source-side items (src) — report only, no fix arranged
- **SEED-MGB-0** (task 0, managed seed rows): monthly fee rows for service months 2026-05, 06, 07 (INV-581190..581192) carry 4194.92 = 34 x 123.38, the per-seat rate of the term that began 2026-07-15; under the published ClearPath renewal and "term in force" documents the pre-renewal months bill the lower expiring rate (123.38 = 120.96 x 1.02 -> 4112.64). No TimeBank figure reads these rows; no scored value moves.
- **SEED-MGB-1** (task 1, managed seed rows): all eleven monthly fee rows 2025-12..2026-10 carry 8542.74, which is neither 58 x 148.26 = 8599.08 (the agreement's own rate and seats) nor a pre-renewal figure (58 x 145.35 = 8430.30); the pre- and post-renewal (2026-02-24) months are equal although the published renewal rules raise the rate. No scored value moves (the hardware managed-spend relief reads rate x seats from the agreement record, 2.0 points either way).
- **SEED-SCOPE-HOWTO** (plausible; tasks 0 and 1, managed ticket seed rows): how-to remote business-hours tickets SB-2275518 (Standard) and SB-2297262 (Professional) are recorded billable_out_of_scope and drawn from the TimeBank block, while both tiers include "Covered remote help desk work during coverage hours" and the scope guide covers help desk work on such tiers (labor would be included, L3). The managed docs give no category-to-scope mapping, so this rests on reading a how-to question as help desk work. Records stand as the authority on the scored path; no scored value moves.

### Notes (not findings)
- Generic assembly sentence in repeat_order_price_calculation ("The percentages that apply to the order are added into one total ...") is the source's own assembly, names no factor; not a KB-EXPLICIT item.
- travel_trip_hours_calculation's unconditional "A block whose size carries onsite trip hours of zero draws no travel" entails the source's "whatever the schedules below select".
- New-expiry month arithmetic is unstated in the source and the KB alike (policy-side openness); both readings coincide for task 1.
- A hypothetical figure in remote_session_callout_and_weekend_minutes (142.5 weighted minutes, 2.375 h) equals an intermediate of task 0's service visit in another draw kind and size; no scored value appears in any example.

### Closing checklist (Step 5)
- Audit files one-to-one with tasks 0 and 1; revision_1 only; every comparison section carries PASS.
- Every normative atom of the timebank charter (variants, 9 base policies, 7 extended policies with their overwrites, 3+3 prerequisites and 34 factor ladders) is entailed by docs/timebank; each prerequisite sentence verbatim, state form, only in the blocked policy's hub; each tool name only in its own hub; no route or aggregated chain.
- check_docs re-run on the final (unchanged) corpus by this auditor: `[PASS] mechanical gates ...` / `DOCS OK`. check_traceability not run by this auditor per the brief; the coordinator's line `TRACEABILITY OK (non-OK lines: 0)` stands for the same corpus (docs tree sha256 6368ac29...a45 re-computed unchanged).
- Scratch /tmp/kbaudit_timebank_0069/ removed at the end.

KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SEED-MGB-0,SEED-MGB-1,SEED-SCOPE-HOWTO

## revision_2

Re-audit round 2 (2026-10-18), seed-only rework.

### Gate and snapshot
- Policy-side tail line: `VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN` (matches the required line).
- `/tmp/erl0069_coord/kb_snapshot.sh prepaid_service_hours timebank` (executed, 2026-10-18T17:59:08): check_docs DOCS OK; check_traceability TRACEABILITY OK (non-OK lines: 0); check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0; 0.runtime.json a97f79cd...0fd and 1.runtime.json ef38fb4d...65e (unchanged); timebank.extended.yaml 4bf1e7bb716bcf4f...0a0, task_tools.py f7013dc51432fa1b...39c, docs/timebank 63 files tree 6368ac29...a45, all unchanged from revision_1 (re-computed independently). Only tasks/0.json and tasks/1.json changed (17:45:09). No re-render, so the revision_1 KB scans stand.

### The three revision_1 items
- **SEED-MGB-0: closed, and the revision_1 item was an auditor error.** In revision_1 I said the renewed rate must be strictly above the expiring rate. That left out the published service-intensity adjustment of the renewal rate (ticket_volume_at_renewal: fewer tickets opened in the 12-month window than seats, 0.5 percent off). Re-derived for the 2026-07-15 renewal (7th renewal; cap 5 less 1 = 4; live >= 60 months, rule b): the lowest of 123.38 x 1.04 = 128.32, list 124.00 and 123.38 x 1.02 = 125.85 is 124.00. The adjustments are: 6 tickets opened in the window against 34 seats, so 0.5 off; seat growth 34 against 32 contracted, so nothing; no late fee and no service credit. That gives 124.00 x 0.995 = 123.38, the same as the expiring rate, so the rate is in steady state. With no earlier history in the seed, the prior renewals give 123.38 the same way. The monthly fee is 34 x 123.38 = 4194.92 for May to October (34 billed seats is under the 40-seat volume break, no seat change inside any of those months, and no F3, server, Continuum, CSP or Sentinel inputs exist). The rows match the published managed rules.
- **SEED-MGB-1: closed, and the revision_1 item was an auditor error.** In revision_1 I missed volume_price_break_on_monthly_fees. Under the current-month scope each fee was the current service month on its posting day, with no seat change in the month. Billed seats are max(58, floor 53) = 58; seats 40 to 58 are 19 seats x 2.0 = 38, divided by 58, which is 0.655 percent off. So 8599.08 less 0.655 percent is 8542.74 for every month. The renewal on 2026-02-24 (4th renewal; cap 4; live 72 months, rule b): the lowest of 154.19, 149.00 and 151.23 is 149.00. Then 3 tickets in the window against 58 seats gives 0.5 off, and seat growth (58 against 55 contracted, threshold 61) gives nothing, so 149.00 x 0.995 = 148.255, which rounds to 148.26, the same as the expiring rate (the 2025-02-24 renewal under rule c, 59 months, also gives 148.26). The pre- and post-renewal fees are therefore equal. Payments (ACH on the 22nd, net 30) and the open October balance are consistent.
- **SEED-SCOPE-HOWTO: closed.** SB-2275518 (task 0, now P4 service_request, email) and SB-2297262 (task 1, now P3 service_request, chat) are re-seeded out of the how-to category. They are now recorded billable out of scope and routed to TimeBank like the clients' other remote service requests. Their existing draws still reproduce under the published TimeBank rules: 45 minutes, floor at the size's remote minimum, 0.75 h, technician, business hours. No how-to ticket remains on either covered tier.

### No new defect, nothing regressed
- Re-queried every other cross-product row via db_query.py. They are unchanged and still consistent: tickets, seat ledger, agreement fields, TimeBank blocks/ledgers/billing/orders; for task 1, hardware HQ-604418 (1444.80 / 18652.60 / deposit 3357.47 / final 15295.13) and project SOW-337412 (10.5, deposit 7160.00, work logs).
- One observation, not a seed defect: the round-14 worklog computes the hardware managed-spend relief as 8542.74 / 18652.60. The published document defines it as seat rate x seat count = 8599.08, which is 0.461 of the quote. Both fall in the 2.0-point band, so the seeded deposit 3357.47 stands.
- Scored values have not moved. The gold writes in the re-seeded task JSONs are identical to revision_1: task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 4.81 / 325.87, expiry 2027-06-08. Every input the blind derivation used (block balances 9.39 and 80.86, ledgers, billing, ClearPath tier/seats/go-live/renewals, tickets SB-2306631 / SB-2311409 / SB-2310275, hardware order, project logs) re-queries unchanged. So each value is still uniquely reachable from the visible surface by the frozen revision_1 derivations, and the gt_comparison PASS verdicts stand.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none
