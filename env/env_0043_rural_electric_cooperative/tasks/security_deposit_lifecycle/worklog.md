# worklog security_deposit_lifecycle (M=2)
- step0: draw_counts --tasks 2 -> task0 prereq=2 factors [4,6,6]; task1 prereq=2 factors [4,6,4]
- step0: constraints found: deposit tools may not write apply_balance/apply_prepay (always trigger other categories), bill_credit refunds/payouts (trigger service); computations can only read their target deposit record + its ledger + other categories, so value_input edges must run inside one deposit record; every target must be an initial_state deposit row (P() reads the target's tier).
- step0 scope plan: task0 = repeat reconnection on a Schedule R home (pay the open reestablishment deposit's accelerated remainder [user,4f] -> repeat reestablishment deposit [6f]) + reinstatement of a shop waiver that rested on the home's history [6f]; task1 = good-payment refund (2025 year-end accrual [4f] -> part-year accrual [6f] -> refund by check [user,4f]). Disjoint families: task0 = assessment+payment, task1 = interest+refund.
- step0 revision (after exhausting alternatives): payments of an overdue deposit are accelerated to the whole remainder (no factors), so a rich member payment must be a first installment not yet due; a computation reads only its own target record, so the reconnection deposit (Credit Reestablishment tier) targets the reinstated Standard deposit and carries the Credit Reestablishment figures in its own params. Final task0 = Schedule R home disconnected 2026-09-24: (B) member pays the first installment of the waiver-reinstatement deposit the system assessed at disconnection [user, 4f] -> (R) reconnection deposit, credited only with cash actually held on the account's deposits [6f]; (A) reinstatement of the member's shop deposit waiver that rested on the home's payment record [6f], state gate on R. task1 = refund chain.
pay_reinstated_deposit_installment_114bda0d
assess_reconnection_deposit_9009d8a2
assess_reinstated_deposit_c3ac4854
post_year_end_deposit_interest_3b717487
post_refund_date_deposit_interest_50449ec1
refund_deposit_by_check_ead765c2
- task0 compute run: A0 450.00 (baseline 560), B 83.60 (baseline 220.00), R 365.00 (baseline 410.00); all factor substitutions move result (see computations).
- task0 closed: all per-task gates OK (traceability skipped: KB unpublished)
- task1 tools added; task1 design: recalculation refund by check [user,6f] <- refund-date accrual [4f] <- 2025 year-end accrual [4f]
- task1 closed: all per-task gates OK; values C 14.54, D 9.85, E 399.39
- final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means branches=96.50 steps=16.00; history_rows_max=17; branches_max=103), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability skipped (KB not published)

## round 2 (audit rework)
- read audits/policy_task/security_deposit_lifecycle/{_difficulty,0,1}.md; items F1-F4 RED, O1-O12, T0-O1, T0-O2, T1-O1, T1-O2
- F4: rebuilt deposit_ext_reinstated_first_installment: removed number-selector remote_meter_allowance; new method factor relief_points_combination (sum / larger+half smaller / larger only, by returned payments); O10: remainder sentence restated without pointing at the superseded clause
- F1/F2: overwrite entries on deposit_evt_interest day-count sentence in both accrual policies; F3: installment relief keyed to days from the reinstated deposit's assessment to its first installment (prompt/on-time/late, all reachable); O1: overwrite of deposit_agg_service_total netting in reinstatement and reconnection + scope sentence; O2: condition text; O4: window keys on most recent connect fee being another account's; O5: certificate 'accepted or not'; O6: 'rounded to the nearest cent' everywhere; O7: deposit_evt_interest payout clause overridden in recalc refund; O9: new-meter supplement replaced by kept-arrangement supplement
- round 2: task0 reseeded reinstated deposit 480.00 (T0-O1), new gold B 108.00, R 325.00; task1 values unchanged (14.54/9.85/399.39); full gate block re-run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability skipped
