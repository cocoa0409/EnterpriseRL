# orthodontic_benefits — instantiate worklog

## Step 0 (difficulty pre-check)
- Base ortho charter read: 8 claimed events; base benefit calc / installments / transfer / reversal / lifetime max; user acts per lifecycle: rider change requests (withdraw / voluntary termination).
- Draws (draw_counts.py --tasks 2): task 0 prereq=1 factors [4,5]; task 1 prereq=1 factors [6,5].
- DSL limits found: history primitives scoped to the rider; equality filters only; CFIELD adds customer_id (provider agreements of practices unreadable); replay closure requires every seeded row to be returned by a gold read (practice customers cannot be in closure, so practice agreements are not seeded; empty foreign keys seeded as null).
- Case facts exist only after establishment, so no establishment computation is possible in-call; case benefit kept as a plain base binding in every policy.

## Task 0 (closed)
- Tree: root ortho_ext_carried_first_payment (agent, 5 factors) <- ortho_ext_transfer_recognised_fee (user, 4 factors), value_input via the latest transfer entry (tr_fee / tr_network / tr_left), state-form prerequisite sentence.
- Gold: allowed_case_fee 1020.17; carried payment 98.53 (installment 12, 2026-09, member). Skip-prerequisite 54.43. All-baseline 1695.83 / 42.51.
- Decoy probes: denied D0330, D0330 on another enrollment, D0150 out of window, other-case establishment/transfer/payment/reversal, closure row -> stable; records absent -> moves (absent branch).
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Resume after account cut: applied coordinator XF points 14-17 to task 0 (trigger list: transfers/installments carry no base triggers; method-shape all-pairs tables in rationale section 15; assembly folded into result so no plain binding reads a factor-owned binding; every factor sentence names its result; ledgers reproduce). Task-0 gates re-run: all OK, gold unchanged (1020.17 / 98.53).

## Task 1 (closed)
- Tree: root ortho_ext_member_overpayment_return (user, 5 factors) <- ortho_ext_waiting_takeover_fee (agent, 6 factors), value_input via the latest establishment entry (est_fee / est_remaining / origin), state-form prerequisite sentence in the negated direction.
- Gold: takeover re-establishment allowed_case_fee 2405.74 (months_remaining 20); member repayment 166.47 against the initial payment. Skip-prerequisite 187.50. All-baseline 4000.00 / 375.00.
- XF 14-17 applied: no cross-category triggers (takeover entries trigger nothing; reversals none); method-shape all-pairs tables in the task rationale; assembly folded into result; every factor sentence names its result; premium ledger 2026-09..11 seeded and read.
- Decoy probes: denied D0330 on banding date, D0330 a day later, earlier case with another number, reversal on another case -> stable; records absent and another case's payment move the result as the rule states.
- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 32, branches_max 51), GROUNDING OK, SCOPE OK.
INSTANTIATE round 1: gates 7/7 green

## Rework round 2

- Charter redesign: P1 assembly sentence made generic (no factor quantities), single-month / no-schedule / no-establishment edges stated and guarded. P2 rebuilt (case_benefit_basis m, unused_deductible p, retention_reserve p, payment_spread m, begun_periods m); base lower-fee clause of ortho_evt_case_transfer applied plainly; one scoped overwrite (transfer s1) restating later payments, payees and untouched installments; interest pair and allowance cut removed. P3 rebuilt (waiting_months p, dental_tenure p, start_work_share p, banding_visit_records p x-dental, covered_month_count m, covered_fee_basis m); month-for-month credit plain; overwrites of eligibility s2/s5 restate the waiting and genuine-takeover rules. P4 rebuilt (takeover_benefit_basis m, takeover_deductible p, takeover_retention_reserve p, takeover_installment_count m, first_period_share p); repayment = MN(initial, MX(0, paid - payable)); overwrites of reversal s1 (grounds restated in full) and benefit_calculation s2 (proration kept for every takeover that does not supersede a new-start entry).
- Edge pass after first gate run: covered_month_count now reads the new-start entry itself (history); guards + sentences for a rider with no establishment entry (P2, P3, P4), no attached enrollment (P3 tenure), payable takeover installments capped at the spread count (P4). Gold unchanged.
- Worlds rebuilt: T0 Family 1500, OON Tacoma practices, in-network Spokane orthodontist with seeded PPO agreement (read by find_provider_agreements; practice row in closure via find_provider_requests). T1 Family 1500 adult patient, Premier 2000 since 2022-07, OON practice. Every seeded payment / transfer fee reproduces from base + charter rules (seed_consistency rows).

### (a) Decoy / absent-record probes (scratch copies; policy | probe | read | gold | probed | expected | verdict)
- transfer_recognised_fee | reversed initial payment | COUNT installments net of reversals | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | closure-type case row (voided) | LATEST establishment | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | prior case, earlier establishment | LATEST establishment | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | same-date second establishment entered later | LATEST tie rule | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | transfer entry of another case | COUNT transfers by case | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | records lines 4 months back (outside window) | XSUM dental window | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | denied records lines in window | XSUM paid only | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | records lines on the subscriber's own enrollment | XSUM patient enrollment | 1600.09 | 1600.09 | same | PASS
- transfer_recognised_fee | absent records lines | XSUM dental (absent) | 1600.09 | 1796.09 | 1796.09 | PASS
- transfer_recognised_fee | absent transfer entry | COUNT transfers (absent) | 1600.09 | 1799.65 | 1799.65 | PASS
- carried_first_payment | reversal on another case | SUM case paid by case | 285.16 | 285.16 | same | PASS
- carried_first_payment | closure-type case row (voided) | LATEST transfer / establishment | 285.16 | 285.16 | same | PASS
- carried_first_payment | older transfer entry (prior record) | LATEST transfer | 285.16 | 285.16 | same | PASS
- carried_first_payment | same-date transfer entered after the move | LATEST tie rule | 285.16 | 285.16 | same | PASS
- carried_first_payment | later installment on another case | LATEST payment service period | 285.16 | 285.16 | same | PASS
- carried_first_payment | second case, allowed 30.00 (< deductible) | COUNT/SUM establishments | 285.16 | 288.02 | 288.02 | PASS
- carried_first_payment | second case, allowed 2000.00 | COUNT/SUM establishments | 285.16 | 288.02 | 288.02 | PASS
- carried_first_payment | absent new transfer (stale Fenwick entry) | LATEST transfer | 237.62 | 237.62 | 237.62 | PASS
- waiting_takeover_fee | takeover entry with other months (not new start) | MAX new-start fields | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | prior case, earlier establishment | LATEST case number | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | daughter's banding-day lines | XSUM patient enrollment | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | records lines the day after banding | XSUM banding date | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | denied records lines on the banding date | XSUM paid only | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | prior-benefit-year records lines | XSUM banding date | 3396.17 | 3396.17 | same | PASS
- waiting_takeover_fee | absent records lines | XSUM (absent) | 3396.17 | 3592.17 | 3592.17 | PASS
- waiting_takeover_fee | transfer entry of another case | COUNT transfers by case | 3396.17 | 3396.17 | same | PASS
- member_overpayment_return | reversal of an initial payment on another case | SUM case paid / initial by case | 337.98 | 337.98 | same | PASS
- member_overpayment_return | closure-type case row (voided) | LATEST establishment | 337.98 | 337.98 | same | PASS
- member_overpayment_return | prior case, earlier establishment (allowed 30.00) | LATEST establishment | 337.98 | 333.88 | 333.88 | PASS
- member_overpayment_return | same-date establishment entered after the takeover | LATEST tie rule | 337.98 | 337.98 | same | PASS
- member_overpayment_return | reversed 2026-12 installment on the case | SUM case paid net of reversals | 337.98 | 197.35 | 197.35 | PASS
- member_overpayment_return | absent takeover entry | LATEST establishment (absent takeover) | 290.64 | 290.64 | 290.64 | PASS
- Edge worlds (no raise): P1 no establishment entry: ok result=0;P1 one-month plan: ok result=0;P1 zero-month plan: ok result=0;P2 no establishment entry: ok result=0;P2 no payments: ok result=563.48;P3 no attached enrollment: ok result=4190.87;P3 zero planned months: ok result=0;P3 no establishment entry: ok result=0;P3 29-Feb DOB: ok result=3994.87;P4 far future (all periods begun): ok result=0.0 begun=21 count=7;P4 no payments: ok result=0.0 begun=3 count=7;P4 no establishment entry: ok result=0 begun=0 count=1;

### (b) All-pairs method-shape tables
- P1 progress_measure: monthly-ledger vs quarterly-coverage = operation (count ratio vs months-not-covered ratio, 3 x issued); monthly-ledger vs calendar = operation (payment ledger vs date span); quarterly-coverage vs calendar = operation (payment ledger vs date span).
- P2 case_benefit_basis: takeover-prorated vs OON-lesser-of = operation (proration factor vs MN with treatment fee) + tariff (coins by entry network vs coins_oon); takeover vs standard = operation (proration added); OON-lesser-of vs standard = operation (MN added) + tariff (coins_oon vs coins_in).
- P2 payment_spread: lump vs quarterly = operation (constant 1 vs ceil(tr_left/3)); lump vs monthly = operation (1 vs tr_left); lump vs original = operation (1 vs schedule remainder); quarterly vs monthly = operation (/3 rounded up added); quarterly vs original = operation (transfer months vs original schedule ledger); monthly vs original = operation (transfer months vs original schedule ledger).
- P2 begun_periods: monthly vs quarterly = operation (whole months vs months // 3); monthly vs one = operation (date span vs constant); quarterly vs one = operation (date span // 3 vs constant).
- P3 covered_month_count: quarterly-whole-quarters vs lump-none = operation (floor to multiple of 3 vs zero); quarterly vs every-month = operation (floor to quarters added); lump-none vs every-month = operation (zero vs months still to come).
- P3 covered_fee_basis: transferred vs OON-lesser-of = operation (transfer fee x covered/tr_left, capped vs MN(allowed, treatment fee)); transferred vs allowed = operation (different record and ratio); OON-lesser-of vs allowed = operation (MN added).
- P4 takeover_benefit_basis: superseding vs lone-OON = operation (no proration vs MN(prorated fee, treatment fee)) + tariff (entry network vs coins_oon); superseding vs standard = operation (proration removed); lone-OON vs standard = operation (MN added) + tariff.
- P4 takeover_installment_count: single vs quarterly = operation (1 vs ceil(MN(left, cap)/3)); single vs original = operation (1 vs schedule count); quarterly vs original = operation (takeover months vs planned months after banding).

### (c) Mechanical transitive factor-independence check (closure over the compute graph)
- ortho_ext_transfer_recognised_fee: factors=4 factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=21 non_verbatim=none factor_id_in_tool_file=none trigger=on_request
- ortho_ext_carried_first_payment: factors=5 factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=20 non_verbatim=none factor_id_in_tool_file=none trigger=on_request
- ortho_ext_waiting_takeover_fee: factors=6 factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=19 non_verbatim=none factor_id_in_tool_file=none trigger=state_due
- ortho_ext_member_overpayment_return: factors=5 factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=22 non_verbatim=none factor_id_in_tool_file=none trigger=on_request
- No multiplicative pair in which one factor's baseline zeroes another: every factor's baseline is a neutral value of its own term (0 amount, 100/1 share, standard measure/method), and each per-factor baseline differs from gold (computations.factor_sensitivity).

### (d) Verbatim compute_basis / quote sweep
- compute_basis quotes: P1 21, P2 20, P3 19, P4 22; non-verbatim none (indep.py, after whitespace normalisation). replaced_by text verbatim in each rule (assemble.py).
- task quotes: task 0: quotes=9 not_verbatim=0
- task quotes: task 1: quotes=4 not_verbatim=0

### (e) Trigger-rule list
- move_ortho_case_49ae8ecf -> ortho_case_transferred: base triggers [] (no fee/bill write).
- issue_ortho_carried_payment_56eb10f4 -> ortho_installment_payment: base triggers [].
- record_ortho_takeover_case_574129ed -> ortho_case_established (case_origin takeover): base trigger ortho_initial_payment fires only when case_origin == new_start, so none fires.
- repay_ortho_overpayment_ce1ed3cf -> ortho_payment_reversal: base triggers [].
- Charter triggers: P1 on_request, P2 on_request, P3 state_due, P4 on_request.

### Item closures
- T0-1 / C2: base lower-fee clause applied as stated (plain carried-benefit binding); only s1 retired, by a scoped overwrite.
- T0-2 / C5-a: interest pair removed; independence check above clean.
- T0-3 / C6-b / C8-a / C8-e / C11 (P2): ladders now rider practice (coinsurance by network and fee basis, deductible, retention, quarterly spread in quarters, begun periods); five factors.
- T0-4: Engstrom PPO agreement seeded and read; case/transfer rows carry no agreement and out_of_network for the non-participating Tacoma practices; proofs recomputed.
- T1-1 / C3: takeover proration retired only by a declared overwrite scoped to superseding takeovers; restated for every other takeover.
- T1-2 / C5-b / C5-c: waiting/credit/tenure no longer gated (baseline child months, credit plain); repayment_measure removed.
- T1-3 / C6-a / C6-c / C6-d: waiting ladder now adult 24 vs group 0 vs child 12 on a world taking the adult tier; schedule-start tier removed.
- T1-4 / C7: P3 has two real method factors (covered_month_count, covered_fee_basis); prior_coverage_credit dropped as a factor.
- T1-5 / C8-b / C8-c / C8-d / C8-f: allowance cut, gap share and aged recovery removed; baseline waiting is the rider's child months.
- C1 (a-e): every overwrite's replaced_by restates the in-force content for out-of-scope cases.
- C4: single-rider scope sentence (P2, P4); deductible ladder by establishment entries' case numbers; payee/offset sentence; excess-over-maximum stays a restated base ground.
- C9: assembly sentences generic (no factor quantities) in P1-P4.
- C10: edges stated and guarded (single-month / zero-month plan, absent establishment entry, absent enrollment, same-date ties, month-end convention, payable cap); probes above.

- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 14, branches_max 87), GROUNDING OK, SCOPE OK; probes 32/32 PASS; edge worlds raise none.
REWORK round 2 claims: T0-1,T0-2,T0-3,T0-4,T1-1,T1-2,T1-3,T1-4,T1-5,C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11
REWORK round 2: gates 7/7 green

## Rework round 3

- Charter: every factor now varies something the base leaves open; base-fixed quantities (coinsurance by network, unused deductible, waiting months by market and age, prior-coverage credit, takeover proration) are plain standard-measure bindings stated as the base states them.
  - P1 transfer fee (5): start_share p, progress_measure m, carry_percent p, dental_records p (x-dental, 6-month window), retention_share p (retention part kept whole, new).
  - P2 first carried payment (4): practice_network_ratio p (unpaid benefit follows the network of the practice now treating the patient, new), retention_reserve p, payment_spread m, begun_periods m. case_benefit_basis and unused_deductible removed (base rule now plain). Overwrites: transfer re-spread (single-rider scope plus restatement for persons with an earlier rider), installment issue (restated plus the hold of installments once a claim shows the patient at another orthodontist), takeover proration (restated for every takeover; a superseding takeover is not prorated).
  - P3 takeover fee (6): dental_tenure p, start_work_share p, banding_visit_records p (x-dental), retention_part p, appliance_removal_part p, covered_fee_basis m (moved case: practice rate; planned months beyond the cap: cap share; else allowed fee). waiting_months and covered_month_count removed; waiting months plain base; whole-month convention stated; the takeover entry takes the network status and agreement in force on its date (tool now takes both).
  - P4 repayment (5): case_network_terms p (a case begun outside the network keeps out-of-network terms; continuity of care when the practice leaves), progress_records_offset p (x-dental), takeover_retention_reserve p, takeover_installment_count m (months within the cap window), first_period_share p. takeover_benefit_basis and takeover_deductible removed. Overwrites: reversal grounds (restated for every person; the member return scoped to single-rider persons), takeover proration (same sentence as P2), case benefit sentence (restated with the network terms of a superseding takeover).
- Worlds: T0 frozen 2027-03-09; complete premium ledger 2024-01..2027-03; installments 2026-06 and 2026-09 seeded; 2026-12 and 2027-03 held under the hold sentence (Engstrom claim adjudicated 2026-10-13); Engstrom remittance seeded. T1 frozen 2027-01-12; allowed 5000.00 below the 5400.00 fee; complete ledger 2022-07..2027-01; Gallagher agreement effective 2026-09-01 with its remittance; no annual-maximum postings for Premier 2000 preventive lines; partial June quarter counted once (fee counts every covered month, the repayment applies the 2/3 first-period share).

### (a) Decoy / absent-record probes (scratch copies; policy | probe | read | gold | probed | expected | verdict)
- transfer_recognised_fee | reversed initial payment | COUNT installments net of reversals | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | closure-type case row (voided) | LATEST establishment / appliance | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | prior case, earlier establishment | LATEST establishment | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | same-date second establishment entered later | LATEST tie rule | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | transfer entry of another case | COUNT transfers by case | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | records lines 7 months back (outside window) | XSUM dental window | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | denied records lines in window | XSUM paid only | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | records lines on the subscriber's own enrollment | XSUM patient enrollment | 1135.22 | 1135.22 | same | PASS
- transfer_recognised_fee | absent records lines | XSUM dental (absent) | 1135.22 | 1331.22 | 1331.22 | PASS
- transfer_recognised_fee | absent transfer entry | COUNT transfers (absent) | 1135.22 | 1283.13 | 1283.13 | PASS
- carried_first_payment | reversal on another case (small) | SUM case paid by case | 340.56 | 340.56 | same | PASS
- carried_first_payment | closure-type case row (voided) | LATEST transfer / establishment network | 340.56 | 340.56 | same | PASS
- carried_first_payment | older in-network transfer entry (prior record) | LATEST transfer | 340.56 | 340.56 | same | PASS
- carried_first_payment | same-date out-of-network transfer entered after the move | LATEST tie rule | 340.56 | 340.56 | same | PASS
- carried_first_payment | later installment on another case (small) | LATEST payment service period | 340.56 | 340.56 | same | PASS
- carried_first_payment | reversed later installment on the case | COUNT issued net of reversals | 340.56 | 340.56 | 340.56 | PASS
- carried_first_payment | absent new transfer (stale Fenwick entry) | LATEST transfer | 230.64 | 230.64 | 230.64 | PASS
- waiting_takeover_fee | takeover entry with other months (not new start) | MAX new-start fields | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | prior case, earlier establishment | LATEST case number / appliance | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | daughter's banding-day pano | XSUM patient enrollment | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | records lines the day after banding | XSUM banding date | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | denied records lines on the banding date | XSUM paid only | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | prior-benefit-year records lines | XSUM banding date | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | absent records lines | XSUM (absent) | 3490.77 | 3686.77 | 3686.77 | PASS
- waiting_takeover_fee | transfer entry of another case | COUNT transfers by case (basis tier) | 3490.77 | 3490.77 | same | PASS
- waiting_takeover_fee | closed dental enrollment row of another person | CFIELD attached enrollment | 3490.77 | 3490.77 | same | PASS
- member_overpayment_return | reversal of an initial payment on another case | SUM case paid / initial by case | 356.54 | 356.54 | same | PASS
- member_overpayment_return | closure-type case row (voided) | LATEST establishment / network | 356.54 | 356.54 | same | PASS
- member_overpayment_return | same-date establishment entered after the takeover | LATEST tie rule | 356.54 | 356.54 | same | PASS
- member_overpayment_return | daughter's later pano and eval | XLATEST patient enrollment | 356.54 | 356.54 | same | PASS
- member_overpayment_return | denied later pano | XLATEST paid only | 356.54 | 356.54 | same | PASS
- member_overpayment_return | pano dated before coverage (prior record) | XLATEST coverage month | 356.54 | 325.02 | 325.02 | PASS
- member_overpayment_return | absent progress pano | XLATEST (absent) | 356.54 | 325.02 | 325.02 | PASS
- member_overpayment_return | reversed 2026-12 installment on the case | SUM case paid net of reversals | 356.54 | 215.91 | 215.91 | PASS
- member_overpayment_return | absent takeover entry | LATEST establishment (absent takeover) | 321.69 | 321.69 | 321.69 | PASS
- Edge worlds (no raise): P1 no establishment entry: result 0;P1 one-month plan: result 128.0;P1 zero-month plan: result 128.0;P2 no establishment entry: result 0;P2 no payments: result 718.45;P2 takeover entry from the start: result 0.0;P3 no attached enrollment: result 4080.0;P3 zero planned months: result 0;P3 one planned month: result 504.0;P3 no establishment entry: result 0;P3 29-Feb date of birth: result 3884.0;P3 transfer with zero months remaining: result 3490.77;P4 far future: result 0.0;P4 no payments: result 0.0;P4 no establishment entry: result 0;P4 no dental lines: result 325.02;

### (b) All-pairs method-shape tables
- P1 progress_measure: monthly-ledger vs quarterly-ledger = operation (count ratio vs months-not-covered ratio with 3 x issued); monthly-ledger vs calendar = operation (payment ledger vs date span); quarterly-ledger vs calendar = operation (payment ledger vs date span).
- P2 payment_spread: lump vs quarterly = operation (constant 1 vs ceil(remaining/3)); lump vs monthly = operation (1 vs remaining); lump vs original = operation (1 vs schedule remainder); quarterly vs monthly = operation (division by three rounded up added); quarterly vs original = operation (transfer months vs original-schedule ledger); monthly vs original = operation (transfer months vs ledger).
- P2 begun_periods: monthly vs quarterly = operation (whole months vs months // 3); monthly vs one = operation (date span vs constant); quarterly vs one = operation (date span // 3 vs constant).
- P3 covered_fee_basis: moved vs cap-share = operation (MN of allowed fee and transfer-entry rate x planned months vs allowed fee x cap / months after banding); moved vs allowed = operation (MN with a transfer-entry input added); cap-share vs allowed = operation (tariff cap and division added).
- P4 takeover_installment_count: single vs window = operation (1 vs ceil(MN(remaining, cap - months before coverage)/3)); single vs original = operation (1 vs schedule count); window vs original = operation (takeover months and cap window vs planned months after banding).

### (c) Mechanical transitive factor-independence check (closure over the compute graph)
- ortho_ext_transfer_recognised_fee: factors=5 {'parameter': 4, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=20 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=0
- ortho_ext_carried_first_payment: factors=4 {'parameter': 2, 'method': 2} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=23 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=3
- ortho_ext_waiting_takeover_fee: factors=6 {'parameter': 5, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=17 non_verbatim=none factor_id_in_tool_file=none trigger=state_due overwrites=2
- ortho_ext_member_overpayment_return: factors=5 {'parameter': 4, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=23 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=3
- No factor's baseline zeroes another: every baseline is a neutral value of its own term (0 amount or part, ratio 1, 100% carry, standard measure or method, the base coinsurance), and each per-factor baseline differs from gold (computations.factor_sensitivity).

### (d) Verbatim compute_basis / quote sweep
- compute_basis quotes verbatim in each rule (indep.py: non_verbatim none for P1-P4); replaced_by and prerequisite sentences verbatim (assemble.py).
- task 0: quoted spans=10 not verbatim=0 persona evidence not verbatim=0
- task 1: quoted spans=6 not verbatim=0 persona evidence not verbatim=0

### (e) Trigger-rule list
- move_ortho_case_49ae8ecf -> ortho_case_transferred: base triggers [].
- issue_ortho_carried_payment_56eb10f4 -> ortho_installment_payment: base triggers [].
- record_ortho_takeover_case_574129ed -> ortho_case_established with case_origin takeover: the base trigger ortho_initial_payment fires only for case_origin new_start, so none fires.
- repay_ortho_overpayment_ce1ed3cf -> ortho_payment_reversal: base triggers [].
- Charter triggers: P1 on_request, P2 on_request, P3 state_due, P4 on_request. No write lands in another category.

### Item closures (round 3)
- R2-C1: transfer overwrite restates the base re-spread for persons who held an earlier rider; reversal overwrite restates the grounds for every person and scopes only the member return; the takeover proration overwrite is general (every takeover, actual installments included).
- R2-C2 / T0-R2-1 / T1-R2-1 (deductible part): coinsurance by network and the unused deductible are plain base bindings in P2 and P4; the factors that rebuilt them are removed.
- R2-C3: P2 and P4 carry the same takeover sentence: a takeover entry superseding a new-start entry is not prorated, every other takeover is.
- R2-C6 / T1-R2-1: waiting_months (base-fixed, unreachable tier), takeover_benefit_basis (universal tier), the deductible factors and the min-with-charge tiers are gone; every remaining tier is reachable and not true of every in-scope customer.
- R2-C8 / T1-R2-2: no quarter rounding of the covered months; the partial first quarter is counted once (every covered month in the fee, the first-period share in the repayment).
- R2-C10: P3 states the whole-month convention matching MONTHS() and the 19th-birthday count.
- R2-C11 / T0-R2-2 / T1-R2-4: drawn counts met with real ladders: P1 5, P2 4, P3 6, P4 5, each with >= 2 parameters and >= 1 method.
- T0-R2-3: complete ledger (2026-06 and 2026-09 installments seeded; the held quarters rest on the stated hold rule, not on a missing row); premium ledger from the rider start; practice remittance seeded.
- T1-R2-3: allowed fee below the practice's fee; no Premier 2000 postings for preventive lines; premium ledger from the dental start.

- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 18, branches_max 78), GROUNDING OK, SCOPE OK; probes 35/35 PASS; edge worlds raise none.
REWORK round 3 claims: R2-C1,R2-C2,R2-C3,R2-C6,R2-C8,R2-C10,R2-C11,T0-R2-1,T0-R2-2,T0-R2-3,T1-R2-1,T1-R2-2,T1-R2-3,T1-R2-4
REWORK round 3: gates 7/7 green

## Rework round 4

- Task 0 (passed in revision_3): world, tree, tools, persona and every gold argument except the two scored values unchanged. The records factor moved from the transfer fee (which cannot know the new practice) to the carried payment, which reads only lines billed under the agreement named on the latest transfer entry (R3-C7). Transfer fee: 4 factors; carried payment: 5.
- Charter:
  - P2/P4 share the takeover-proration sentence and the case-benefit sentence, each followed by a sentence naming the other rule (R3-C1).
  - One network rule for a superseding takeover, stated alike in both: month-weighted coinsurance when the case moved once after coverage began and by the takeover date; the begun-under network when the case had not moved and its practice joined or left the network; otherwise the takeover entry's network. P2 applies it plainly and re-rates the unpaid benefit from that coinsurance at a move; P4 carries it as a method factor whose baseline is the base rule (R3-C3).
  - Network-ratio and network-terms tiers apply only on riders whose coinsurances differ (R3-C6).
  - Records factors read only lines under the treating orthodontist's agreement: the carried payment uses the latest transfer entry's agreement, the takeover fee uses its records visit under that agreement, the repayment uses the takeover entry's agreement after the latest move (R3-C7).
  - Takeover fee: appliance-removal part and the cap-share tier removed (R3-C8). New genuine methods: the tenure credit follows the rider's own credit rule (month for month on credit riders, fixed reductions otherwise), and the fee basis follows the practices that render the treatment (weighted for one move, latest practice rate for several, otherwise the allowed fee). Plus the carry percentage for a moved case. Six factors, 2 of them methods (R3-C11).
- Task 1 world rebuilt (frozen 2026-11-20): the banding practice was out of network and closed; on 2026-09-25 the member recorded the move to an in-network PPO orthodontist, with the fee computed by the transfer rule on that date. Installments for 2026-06 and 2026-09 were paid to the member. No period began between the adjudication of the new practice's claim and the transfer. The ledger is complete from 2022-07, the practice remittances are seeded, and Premier 2000 has no preventive postings.

### (a) Decoy / absent-record probes (scratch copies; policy | probe | read | gold | probed | expected | verdict)
- transfer_recognised_fee | reversed initial payment | COUNT issued net of reversals | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | closure-type case row (voided) | LATEST establishment / appliance | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | prior case, earlier establishment | LATEST establishment | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | same-date second establishment entered later | LATEST tie rule | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | transfer entry of another case | COUNT transfers by case | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | absent transfer entry | COUNT transfers (absent) | 1331.22 | 1479.13 | 1479.13 | PASS
- carried_first_payment | general dentist D0150/D0330 in window under another agreement | XSUM records by agreement | 237.92 | 237.92 | same | PASS
- carried_first_payment | out-of-network D0150/D0330 in window (no agreement) | XSUM records by agreement | 237.92 | 237.92 | same | PASS
- carried_first_payment | denied Engstrom lines in window | XSUM paid only | 237.92 | 237.92 | same | PASS
- carried_first_payment | Engstrom lines 7 months back | XSUM window | 237.92 | 355.52 | 355.52 | PASS
- carried_first_payment | Engstrom lines on the subscriber's enrollment | XSUM patient enrollment | 237.92 | 355.52 | 355.52 | PASS
- carried_first_payment | closure-type case row (voided) | LATEST transfer / network | 237.92 | 237.92 | same | PASS
- carried_first_payment | older in-network transfer entry (prior record) | LATEST transfer | 237.92 | 237.92 | same | PASS
- carried_first_payment | same-date transfer entered after the move | LATEST tie rule | 237.92 | 237.92 | same | PASS
- carried_first_payment | later small installment on another case | LATEST payment service period | 237.92 | 225.92 | 225.92 | PASS
- carried_first_payment | absent new transfer (stale Fenwick entry) | LATEST transfer | 230.64 | 230.64 | 230.64 | PASS
- waiting_takeover_fee | takeover row with other months (not new start) | MAX new-start fields | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | prior case, earlier establishment | LATEST case number | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | general dentist D0150 + D0330 later under another agreement | XLATEST/XSUM records visit by agreement | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | out-of-network D0150/D0330 later (no agreement) | XLATEST/XSUM records visit | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | daughter's Hennessey D0150 later | XLATEST patient enrollment | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | denied Hennessey D0150 later | XLATEST paid only | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | transfer entry of another case | COUNT/LATEST transfers by case | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | closed dental enrollment of another person | CFIELD attached enrollment | 2987.59 | 2987.59 | same | PASS
- waiting_takeover_fee | absent Hennessey D0150 | records visit (absent) | 2987.59 | 3065.59 | 3065.59 | PASS
- waiting_takeover_fee | absent transfer entry | fee basis / carry (absent) | 2987.59 | 3511.92 | 3511.92 | PASS
- member_overpayment_return | reversal of an initial payment on another case | SUM case paid / initial by case | 366.71 | 366.71 | same | PASS
- member_overpayment_return | closure-type case row (voided) | LATEST establishment / network | 366.71 | 366.71 | same | PASS
- member_overpayment_return | same-date establishment entered after the takeover | LATEST tie rule | 366.71 | 366.71 | same | PASS
- member_overpayment_return | general dentist later pano under another agreement | XLATEST progress by agreement | 366.71 | 366.71 | same | PASS
- member_overpayment_return | daughter's later pano | XLATEST patient enrollment | 366.71 | 366.71 | same | PASS
- member_overpayment_return | denied later pano | XLATEST paid only | 366.71 | 366.71 | same | PASS
- member_overpayment_return | pano before the move (prior record) | XLATEST after transfer | 366.71 | 346.99 | 346.99 | PASS
- member_overpayment_return | reversed 2026-09 installment on the case | SUM case paid net of reversals | 366.71 | 226.08 | 226.08 | PASS
- member_overpayment_return | absent takeover entry | LATEST establishment (absent takeover) | 318.76 | 318.76 | 318.76 | PASS
- Edge worlds (no raise): P1 no establishment entry: result 0;P1 zero-month plan: result 324.0;P2 no establishment entry: result 0;P2 no payments: result 718.45;P3 no attached enrollment: result 3413.08;P3 zero planned months: result 0;P3 no establishment entry: result 0;P3 transfer with zero months remaining: result 3082.73;P3 transfer without agreement: result 3065.59;P3 month-for-month credit rider: result 3335.08;P4 far future: result 0.0;P4 no payments: result 0.0;P4 no establishment entry: result 0;P4 takeover without agreement: result 346.99;P4 equal-coinsurance rider: result 375.0;

### (b) All-pairs method-shape tables
- P1 progress_measure: as round 3 (monthly ledger vs quarterly ledger = operation; each vs calendar = operation).
- P2 payment_spread and begun_periods: as round 3 (all pairs differ by an operation or a data-selected window).
- P3 dental_tenure: month-for-month vs long = operation (data input: months of dental coverage vs tariff); month-for-month vs short = operation; month-for-month vs none = operation; long vs short = tariff parameter; long vs none and short vs none = tariff vs zero (no tier is 0 over its whole domain except the fall-through).
- P3 covered_fee_basis: one-move weighting vs several-moves rate = operation (weighted sum with the transfer entry's months vs a single MN); one-move vs allowed = operation (rate input and weighting added); several-moves vs allowed = operation (MN with a rate input added).
- P4 covered_network_terms: month-weighted vs begun-under = operation (weighted by months vs a data-selected tariff); month-weighted vs takeover network = operation; begun-under vs takeover network = data-selected tariff on a different entry (differs exactly when the two entries' networks differ, which the tier requires).
- P4 takeover_installment_count: as round 3.

### (c) Mechanical transitive factor-independence check
- ortho_ext_transfer_recognised_fee: factors=4 {'parameter': 3, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=15 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=0
- ortho_ext_carried_first_payment: factors=5 {'parameter': 3, 'method': 2} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=25 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=4
- ortho_ext_waiting_takeover_fee: factors=6 {'method': 2, 'parameter': 4} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=13 non_verbatim=none factor_id_in_tool_file=none trigger=state_due overwrites=2
- ortho_ext_member_overpayment_return: factors=5 {'method': 2, 'parameter': 3} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=23 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=3
- No factor's baseline zeroes another; every per-factor baseline differs from gold (computations.factor_sensitivity).

### (d) Verbatim compute_basis / quote sweep
- compute_basis quotes verbatim (non_verbatim none for P1-P4); replaced_by, prerequisite sentences verbatim (assemble.py).
- task 0: quoted spans=10 not verbatim=0 persona evidence not verbatim=0
- task 1: quoted spans=6 not verbatim=0 persona evidence not verbatim=0

### (e) Trigger-rule list
- move_ortho_case_49ae8ecf -> ortho_case_transferred: base triggers [].
- issue_ortho_carried_payment_56eb10f4 -> ortho_installment_payment: base triggers [].
- record_ortho_takeover_case_574129ed -> ortho_case_established, case_origin takeover: the base ortho_initial_payment trigger fires only for new_start.
- repay_ortho_overpayment_ce1ed3cf -> ortho_payment_reversal: base triggers [].
- Charter triggers: P1 on_request, P2 on_request, P3 state_due, P4 on_request.

### Item closures (round 4)
- R3-C1: sibling overwrites of the proration and case-benefit sentences name each other in both rules.
- R3-C3: one network rule for a superseding takeover in both rules; the carried payment re-rates from the coinsurance the case benefit was set at.
- R3-C6: network tiers conditioned on riders whose coinsurances differ.
- R3-C7: every records read filtered by the treating orthodontist's agreement; the transfer fee no longer reads records.
- R3-C8 / T1-R3-1: appliance-removal part and the cap-share tier removed.
- R3-C11 / T1-R3-2: takeover fee has two genuine method factors (tenure credit by the rider's credit rule; fee basis by rendering practice).

- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 18, branches_max 100), GROUNDING OK, SCOPE OK; probes 35/35 PASS; edge worlds raise none.
REWORK round 4 claims: R3-C1,R3-C3,R3-C6,R3-C7,R3-C8,R3-C11,T1-R3-1,T1-R3-2
REWORK round 4: gates 7/7 green

## Rework round 5

- Task 0 (passed): world, tree, tools, gold arguments and scored values unchanged. P2's scope is now limited to cases whose latest establishment entry is a new-start entry, and takeover cases stay under the base re-spread, which is restated. As a result P2 no longer retires or restates the takeover-proration or case-benefit sentences, and its standard measure is the base benefit rule with the establishment entry's network. Only the stale overwrite wording in task 0's rationale was edited.
- P3 (takeover fee, 6 factors):
  - removed: carry percentage, and the month-for-month tier of dental tenure;
  - dental_tenure is now a parameter (long/short/none on any rider; dental coverage is never orthodontic coverage);
  - new method covered_payment_shape follows the payment shape the rider gives the case: a lump-sum case is paid in one payment at banding, so nothing after coverage is valued; for a moved case, covered months before the month of the latest move are valued at the allowed fee and the rest plus the retention part at the lesser of the allowed fee and the latest practice's rate, for any number of moves; otherwise everything at the allowed fee;
  - new parameter treating_practice_plan: when the new practice plans fewer months than the new-start plan still had, the covered months from the move are capped at its plan; when it plans more, they are valued at the shorter share, because longer treatment adds no benefit;
  - kept: start_work_share, retention_part, practice_records_visit.
- P4: the case-benefit clause restated by its overwrite now states the takeover entry's network, which is exactly the network factor's baseline. The network factor, applied for the member's repayment, values months before the month of the latest move at the new-start entry's network for any number of moves, and keeps the begun-under network when the practice joined or left the network without a move. No sibling overwrite remains.
- Task 1 world: the new-start entry has allowed 5200.00 against a fee of 5600.00. The 2026-09-25 transfer has a revised plan of 25 months, 19 remaining, fee 3100.00, and its recognised fee is recomputed by the transfer rule on that date. Everything else is as in round 4.

### (a) Decoy / absent-record probes (scratch copies; policy | probe | read | gold | probed | expected | verdict)
- transfer_recognised_fee | reversed initial payment | COUNT issued net of reversals | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | closure-type case row (voided) | LATEST establishment | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | prior case, earlier establishment | LATEST establishment | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | same-date second establishment entered later | LATEST tie rule | 1331.22 | 1331.22 | same | PASS
- transfer_recognised_fee | absent transfer entry | COUNT transfers (absent) | 1331.22 | 1479.13 | 1479.13 | PASS
- carried_first_payment | general dentist D0150/D0330 under another agreement | XSUM records by agreement | 237.92 | 237.92 | same | PASS
- carried_first_payment | denied Engstrom lines in window | XSUM paid only | 237.92 | 237.92 | same | PASS
- carried_first_payment | Engstrom lines 7 months back | XSUM window | 237.92 | 355.52 | 355.52 | PASS
- carried_first_payment | older transfer entry (prior record) | LATEST transfer | 237.92 | 237.92 | same | PASS
- carried_first_payment | same-date transfer entered after the move | LATEST tie rule | 237.92 | 237.92 | same | PASS
- carried_first_payment | absent new transfer | LATEST transfer | 230.64 | 230.64 | 230.64 | PASS
- waiting_takeover_fee | takeover row with other months (not new start) | MAX new-start fields | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | prior case, earlier establishment | LATEST case number | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | general dentist D0150 + D0330 later under another agreement | records visit by agreement | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | daughter's Hennessey D0150 later | records visit patient enrollment | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | denied Hennessey D0150 later | records visit paid only | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | transfer entry of another case | transfers by case (shape, plan) | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | older second transfer entry (earlier move) | LATEST transfer (any number of moves) | 2971.21 | 2971.21 | 2971.21 | PASS
- waiting_takeover_fee | closed dental enrollment of another person | CFIELD attached enrollment | 2971.21 | 2971.21 | same | PASS
- waiting_takeover_fee | absent transfer entry | shape / plan (absent) | 2971.21 | 3970.0 | 3970.0 | PASS
- member_overpayment_return | reversal on another case | SUM case paid by case | 368.43 | 368.43 | same | PASS
- member_overpayment_return | closure-type case row (voided) | LATEST establishment / network | 368.43 | 368.43 | same | PASS
- member_overpayment_return | same-date establishment entered after the takeover | LATEST tie rule | 368.43 | 368.43 | same | PASS
- member_overpayment_return | older second transfer entry (earlier move) | network rule, any number of moves | 368.43 | 368.43 | same | PASS
- member_overpayment_return | general dentist later pano under another agreement | XLATEST progress by agreement | 368.43 | 368.43 | same | PASS
- member_overpayment_return | denied later pano | XLATEST paid only | 368.43 | 368.43 | same | PASS
- member_overpayment_return | pano before the move (prior record) | XLATEST after transfer | 368.43 | 348.71 | 348.71 | PASS
- member_overpayment_return | absent takeover entry | LATEST establishment (absent takeover) | 318.76 | 318.76 | 318.76 | PASS
- Edge worlds (no raise): P3 no attached enrollment: result 3499.21;P3 zero planned months: result 0;P3 lump case (5 months): result 0;P3 no establishment entry: result 0;P3 transfer with zero months remaining: result 3892.0;P3 longer new plan: result 2172.42;P3 transfer without agreement: result 3049.21;P4 far future: result 0.0;P4 no payments: result 0.0;P4 no establishment entry: result 0;P4 equal-coinsurance rider: result 375.0;

### (b) All-pairs method-shape tables
- P1 progress_measure; P2 payment_spread and begun_periods; P4 takeover_installment_count: as round 3.
- P3 covered_payment_shape: lump vs moved = operation (constant zero vs a month split with a rate input); lump vs standard = operation (zero vs months proration; the standard is not zero on its domain); moved vs standard = operation (MN with the practice's rate and a split at the move month added).
- P4 covered_network_terms: month-weighted vs begun-under = operation (weighted by months vs a data-selected tariff); month-weighted vs takeover network = operation; begun-under vs takeover network = data-selected tariff on another entry (differs exactly when the two networks differ, which the tier requires).

### (c) Mechanical transitive factor-independence check, and (d) verbatim quote sweep
- ortho_ext_transfer_recognised_fee: factors=4 {'parameter': 3, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=15 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=0
- ortho_ext_carried_first_payment: factors=5 {'parameter': 3, 'method': 2} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=21 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=2
- ortho_ext_waiting_takeover_fee: factors=6 {'parameter': 5, 'method': 1} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=17 non_verbatim=none factor_id_in_tool_file=none trigger=state_due overwrites=2
- ortho_ext_member_overpayment_return: factors=5 {'method': 2, 'parameter': 3} factor->factor(transitive)=none plain->factor(transitive)=none basis_quotes=23 non_verbatim=none factor_id_in_tool_file=none trigger=on_request overwrites=3
- task 0: quoted spans=10 not verbatim=0
- task 1: quoted spans=6 not verbatim=0
- No factor's baseline zeroes another factor's effect. treating_practice_plan acts on the months from the move under every payment shape, and covered_payment_shape acts at the plan baseline. Every per-factor baseline differs from gold.

### (e) Trigger-rule list
- move_ortho_case_49ae8ecf -> ortho_case_transferred: base triggers [].
- issue_ortho_carried_payment_56eb10f4 -> ortho_installment_payment: base triggers [].
- record_ortho_takeover_case_574129ed -> ortho_case_established, case_origin takeover: the base ortho_initial_payment trigger fires only for new_start.
- repay_ortho_overpayment_ce1ed3cf -> ortho_payment_reversal: base triggers [].

### Item closures (round 5)
- T1-R4-1 / R4-C8a: takeover carry percentage removed.
- T1-R4-2 / R4-C7: dental tenure is a parameter with no month-for-month tier, and dental coverage is not counted as orthodontic coverage; the takeover fee's method is now covered_payment_shape.
- T1-R4-3 / R4-C2: the restated case-benefit clause states the takeover entry's network, so the network factor's baseline is exactly the in-force text; the carried-payment rule no longer carries the network sentence.
- R4-C8b: months before the latest move are valued at the allowed fee and the rest at the latest practice's rate, for any number of moves; no tier values earlier practices' months at a later practice's rate.

- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 18, branches_max 118), GROUNDING OK, SCOPE OK; probes 28/28 PASS; edge worlds raise none.
REWORK round 5 claims: T1-R4-1,T1-R4-2,T1-R4-3,R4-C2,R4-C7,R4-C8
REWORK round 5: gates 7/7 green

## Rework round 6

- R5-C3 (carried-payment rule vs the takeover proration in force): the standard case benefit of the carried-payment rule now states and computes the rider's benefit rule in full. A takeover entry's amount is prorated by its months remaining over its planned treatment months and rounded half up, unless the entry supersedes a new-start entry of the same case. The round-5 clause limiting the rule to new-start cases is removed from the scope sentence and its restated overwrite text. The assembly sentence and its order are unchanged. No world row, gold argument or scored value moves; all four computations and every factor baseline recomputed equal.
- Auditor's example probed on a scratch copy (Child 1500, no deductible): a takeover entry with no earlier entry, 12 of 24 months remaining, allowed 3000.00, 50% -> case benefit 750.00. The same entry superseding a new-start entry of the same case -> 1500.00 (no proration).
- Probes on the new reads (LATEST months remaining and origin, COUNT of establishment entries):
  - carried_first_payment | closure-type case row with takeover origin (voided) | 237.92 | 237.92 | same | PASS
  - carried_first_payment | takeover entry of another case, earlier | 237.92 | 237.92 | same | PASS
  - carried_first_payment | same-date takeover entry entered after the new-start entry | 237.92 | 237.92 | same | PASS
  - carried_first_payment | takeover entry of the same case, later (supersedes: no proration) | 237.92 | 237.92 | same | PASS
  - P2 basis quotes non-verbatim: none
  - P2 plain->factor: none | factor->factor: none
- Trigger list unchanged (transferred [], installment [], established -> initial payment only for new_start, reversal []). The stale scope wording in both rationales was swept.
- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 6 claims: R5-C3
REWORK round 6: gates 7/7 green

## Rework round 7 (render pre-scan render_r1.md, findings 1-6)

- 1 (takeover fee assembly): the combination sentence is now generic and states what the compute does: every share taken off the fee and every part kept whole is first set aside from the value of the covered months; the rest is divided by the planned treatment months; every part kept whole is then added back as its share of the fee of the practice now treating the patient; amounts are then subtracted; the result is rounded once and never below zero. Order unchanged.
- 2 (factor naming another factor's quantity): the fee of the practice now treating the patient is now a plain shared binding, stated once in its own sentence. The retention factor states its own valuation at that fee. covered_payment_shape no longer mentions the retention part in its sentence or ladder and owns only its mode code. Scored values are unchanged. Only task 1's covered_payment_shape baseline_result moved, because at the shape baseline the retention part stays at the treating practice's fee; its trace was updated.
- 3 (carried payment, no installment yet): the rule now says such a case counts whole calendar months from the banding date itself, not from the first day of the banding month, matching the compute. No value moves.
- 4 (repayment, coverage before the first service period): stated; the first takeover installment is then the one for the original schedule's first service period, which it covers in full. This matches the compute and the first-period-share fall-through.
- 5 (repayment, zero installment count): the quarterly tier is now 'rounded up but never fewer than one', both in the rule and in the compute (MX(1, ...)), so there is no division by zero.
- 6 ('passed over'): removed. A case whose latest transfer entry has no months remaining is treated as a case that has not moved for the treating practice's fee, the payment shape and the treating practice's plan.
- Whole class re-checked on all four policies: every assembly sentence is generic; no factor sentence describes another factor's quantity; month counts match MONTHS(); every division is guarded by a stated tier; no other 'passed over' wording remains. Independence and quote sweep:
  - ortho_ext_transfer_recognised_fee: factor->factor=none plain->factor=none non_verbatim=none factor ids in tool file=none
  - ortho_ext_carried_first_payment: factor->factor=none plain->factor=none non_verbatim=none factor ids in tool file=none
  - ortho_ext_waiting_takeover_fee: factor->factor=none plain->factor=none non_verbatim=none factor ids in tool file=none
  - ortho_ext_member_overpayment_return: factor->factor=none plain->factor=none non_verbatim=none factor ids in tool file=none
- Probes on scratch copies:
  - P2 no installment, monthly, banded 2027-01-15, today 2027-03-09: since_months 1 (whole months from the banding date), catch_periods 1
  - P3 transfer with 0 months remaining: shape_code 3, move_rate 5200.0, post_cap 999, result 3892.0
  - P3 retention part at move_rate 4242.11 under shape 2 and at baseline shape 3: results 2971.21 / 3496.21
  - P4 coverage index 2 before the first period (offset 3): start_index 3, first_share 1, result 358.84
  - P4 count with no months inside the cap window: installment_count 1, result 375.0
- Trigger list unchanged. All four scored values and every all-baseline result were recomputed equal.
- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 7 claims: R1-1,R1-2,R1-3,R1-4,R1-5,R1-6
REWORK round 7: gates 7/7 green

## Rework round 8 (seed-only; KB cross-product re-judge revision_2: S2, S3, S4, S5)

- ortho.extended.yaml (7fb0c4d97ce747af) and task_tools.py (ae8fd16b76be984b) are byte-identical; only the two worlds and their proof text changed.
- S2: the world is changed so the dental history legitimately allows Engstrom's 2026-10-06 panoramic. The earlier 2025-07-28 panoramic decoy line and its annual-maximum posting are removed, so no paid panoramic film lies inside Plus 1500's 60-month interval. Aksel's two 2026 oral evaluations stay within the count of 2.
- S3: Joanna's routine visit (D0120/D0274) is moved to 2025-11-04 (prior benefit year). Her earlier panoramic film is a general dentist's of 2023-08-15, outside Premier 2000's 36-month interval before 2026-11-10. Her 2026 evaluations are now the Gallagher banding-day D0150 and the Hennessey D0150 of 2026-09-15 (2 of 2), and the Hennessey D0330 of 2026-11-10 is payable.
- S4: every Direct Bill invoice is dated 20 calendar days before the first of its coverage month (16 rows in task 0, 22 in task 1). Task 1 gains the 2026-12 invoice dated 2026-11-11 (not yet due), and its balance_due is now 122.63, invoices less payments.
- S5: credentialing decision dates are set to the last recredentialing (Engstrom 2024-05-01, Hennessey 2024-04-01), 36 months before their due dates.
- Same pass, own find: task 1's second remittance was moved to the 2026-11-13 run, seven days times seven after the 2026-09-25 run, with the Hennessey D0330 adjudicated 2026-11-12.
- Exhaustive re-price of every other-product row in both worlds against docs/dental, docs/billing and docs/provider. Checks: evaluation counts, panoramic and bitewing intervals, lines inside coverage, plan payment, member share, annual-maximum postings (Plus 1500 posts preventive; Premier 2000 does not), premiums by month, invoice lead time, payment timing, missing invoices up to frozen_time, balance, paid-through, recredentialing cycle, and remittances per seven-day run. Result:
  - task 0: 4 lines, 4 postings, 78 billing rows, 1 agreements, 1 remittances; issues: none
  - task 1: 7 lines, 0 postings, 107 billing rows, 1 agreements, 2 remittances; issues: none
- Seed edits:
  - t0 removed D0330 2025-07-28 line 6e0ed449-fb02-469f-923b-12feb9a9d5ff and its posting 72fec732-a306-4b54-8f97-2ded0cf7beab
  - t0 agreement Dr. Lars Engstrom decision 2018-04-02 -> 2024-05-01 (due 2027-05-01)
  - t1 balance_due -> 122.63 (2026-12 invoice issued, due 2026-12-01)
  - t1 moved D0120 routine line 8c8b7cea-15a7-4c62-862d-0361e457a714 to 2025-11-04 (prior benefit year)
  - t1 moved D0274 routine line cd6f3961-c9a4-49df-bff0-2137a0aa5c62 to 2025-11-04 (prior benefit year)
  - t1 moved panoramic line 87c00e53-a966-4f7a-8545-6790c44decb5 to a general dentist visit of 2023-08-15 (outside the 36-month interval before 2026-11-10)
  - t1 agreement Dr. Ronan Hennessey decision 2015-03-18 -> 2024-04-01 (due 2027-04-01)
  - t1 Hennessey D0330 of 2026-11-10 adjudicated 2026-11-12 and remitted in the 2026-11-13 run (seven-day cycle from the 2026-09-25 run)
  - (and the invoice-date moves listed above)
- No scored value moved (task 0: transfer fee and carried payment; task 1: takeover fee and repayment). Every computation, all-baseline result and per-factor baseline recomputed equal. Stale proof text was swept in both tasks (world-row lists, lookup objectives, remittance dates).
- Final full gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 8 claims: S2,S3,S4,S5
REWORK round 8: gates 7/7 green
