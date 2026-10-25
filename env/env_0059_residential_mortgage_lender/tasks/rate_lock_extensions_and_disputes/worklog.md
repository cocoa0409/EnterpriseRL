# rate_lock_extensions_and_disputes — instantiation worklog (M=2)

Per-task dossiers (running worklog, revision logs for rounds 1 to 3, manual value gates): `tasks/0.json` and `tasks/1.json`, field `design_rationale`. The round-2 item-by-item closure list (audit ids CG-1..CG-15, T0-1..T0-3, T1-1..T1-5) is in `tasks/1.json` → `design_rationale` → "Difficulty-level closing — round-2 item list". The round-3 closure list (render_source render_lock_r1 items 1–6, two minor points, class sweep) follows it as "Difficulty-level closing — round-3 item list".

Draws (`draw_counts.py --tasks 2`): task 0 = 2 prerequisite problems, factors [5,5,6]; task 1 = 3 prerequisite problems, factors [6,4,4,4].

| task | root (user write) | prerequisites | tools |
|---|---|---|---|
| 0 | lock_ext_extension_charge (6) | lock_ext_extension_dispute_relief (5, value_input), lock_ext_extension_request_length (5, borrower's own request, state_gate) | decide_extension_charge_dispute_a9bc145e, submit_lock_extension_request_8348adff (user), book_lock_extension_178d685b |
| 1 | lock_ext_float_down_fee (6, borrower exercises) | lock_ext_relock_price (4, state_gate), lock_ext_relock_fee (4, value_input), lock_ext_appraisal_delay_waiver (4, value_input into the relock fee) | waive_extension_charge_02e9996e, relock_expired_rate_20a82baa, book_relock_fee_339fcee1, exercise_float_down_fc7d974d (user) |

Gold (rounds 2 and 3, unchanged in round 3): task 0 — dispute waived 0.160 pts / 1,459.84; request 10 days; extension 3 = 10 days, 6 borne, 0.100 pts / 912.40, new expiration 2026-11-16. Task 1 — waiver 0.390 pts / 1,736.96; relock 6.750 @ 0.875 to 2026-11-18; relock fee 0.050 pts / 222.69; float-down to 6.375, 0.575 pts / 2,560.90.

Round-2 gates (difficulty-wide): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 21 acts closure 29=29; 1.json 23 acts closure 21=21), SOLVABILITY OK, COMPUTE OK (branches mean 76.5, steps mean 22.0, history max 8, branches max 84), GROUNDING OK, SCOPE OK, CACHE-DIFF info only; TRACEABILITY not OK pre-KB only for the 7 unlock tool names.

Round-3 gates (difficulty-wide): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 21 acts closure 29=29; 1.json 23 acts closure 21=21), SOLVABILITY OK, COMPUTE OK (branches mean 76.5, steps mean 22.0, history max 8, branches max 84), GROUNDING OK, TRACEABILITY OK (0.json 27 copied / 0 missing; 1.json 28 / 0), CACHE-DIFF info only, SCOPE OK.
