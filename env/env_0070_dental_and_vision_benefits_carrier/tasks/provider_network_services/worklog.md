# provider_network_services — instantiate worklog
- draws: task0 prereq=2 factors[6,5,6]; task1 prereq=3 factors[6,6,6,6]
- task0 (Takahashi Family Dentistry, DHMO PCD ending 2026-12-31): repayment interest 1.26 + capitation continuing withholding 12,608.40 -> exit settlement 12,785.36 (user)
- task1 (Vaughn Dental Arts, PPO weekly runs): run continuation 701.48 -> post-decision 129.22 -> plan down payment 967.48 (user) -> first plan installment 53.66
- known compromises: practice-owned staff group billing account under a provider_practice profile (billing entry gate names employer_group); refunds by the practice are owner=user; task1 notices' source claim lines left empty (replay closure admits no unread rows); refund_window_passed treated as retired difficulty-wide by the gate script because of the plan installment's scoped overwrite (evidence kept in base_preconditions)
INSTANTIATE round 1: gates 7/7 green

## Rework round 2
- Items: S1 billing account removed, cross reads moved to the practice's own applied Cascade group contract + census (cap_small_practice, pl_small_practice); exit/down factors re-based on provider records. S2 notices backed by overpaid remittances on the ledger (task0 supplemental capitation/duplicate runs; task1 re-issued runs), unsupported 2025 notices removed. C1 scope sentence points to the scoped replacement. C2 unverifiable clause dropped. C3a/b computed scope (claim-paid; first post-decision; day after decision). C3c/C10 plan balance tiers redesigned. C4+C5 shared scoped replacement of offset-order/practice-level sentences in four policies + scoped overwrite of the refund-window start sentence. C6 per-overpayment caps. C7 dependency wording removed from installment scope and both docstrings. C8a/b/c and run aging fall-throughs made reachable. C9 generic combination sentences. P1 equations generated from the ledger and asserted.

### (a) decoy / absent-record probes (scratch copies)
| task | probe | values | outcome |
|---|---|---|---|
| 0 | cancelled earlier group contract listed first | [1.26, 0.0, 11234.43] | same |
| 0 | older census reporting 25 employees | [1.26, 0.0, 11234.43] | same |
| 0 | newer member-added event (not a census) | [1.26, 0.0, 11234.43] | same |
| 0 | absent: no group contract or census | [1.26, 1801.2, 11234.43] | MOVED |
| 0 | older dispute decision | [1.26, 0.0, 11234.43] | same |
| 0 | newer pending dispute filing (no decision) | [1.26, 0.0, 11234.43] | same |
| 0 | newer withdrawn panel-open request | [1.26, 0.0, 11234.43] | same |
| 0 | capitation payment of another agreement dated today | [1.26, 0.0, 11234.43] | same |
| 0 | second capitation entry dated today listed after (tie) | [1.26, 0.0, 11105.82] | MOVED |
| 0 | absent: no capitation payments | [1.26, 0, 0] | MOVED |
| 0 | absent: no dispute decisions | [0, 0.0, 11234.43] | MOVED |
| 1 | terminated earlier group contract listed first | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | older census reporting 22 employees | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | newer member-terminated event (not a census) | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | absent: no group contract or census | [664.56, 793.78, 1065.74, 128.21] | MOVED |
| 1 | older dispute decision | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | second same-day decision (withdrawn) listed after (tie) | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | claim run of another agreement dated today | [664.56, 793.78, 1065.74, 98.62] | same |
| 1 | decided overpayment already withheld once (listed first) | [719.94, 0, 1058.64, 98.62] | MOVED |
| 1 | absent: no claim payment runs | [0, 0, 1125.78, 0] | MOVED |
| 1 | absent: no dispute records | [590.72, 0, 915.63, 142.46] | MOVED |
Moves are only absent-record tiers, stated tie/first-withholding rules, or genuine ledger entries entering a stated aggregate.

### (b) method-shape all-pairs
| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
|---|---|---|---|
| cap_aging_adj floor(d/5) / 5 / 0 | pass (floor) | pass | pass (5 != 0) |
| rep_clock_start DAYS(due,rep) / DAYS(refund,rep) / DAYS(resolved,rep) | pass (refund ledger anchor) | pass (distinct decision fields) | pass |
| exit_projection 2L-A / A / L | pass | pass | pass (SUM/COUNT added) |
| run_aging_adj floor(d/3) / 4 / 0 | pass | pass | pass |
| dec_catch_up 4*floor(d/7) / 4 / 0 | pass | pass | pass |
| dp_shape min(250,R) / 500+0.1(R-2000) / 0.2R | pass | pass (min pick) | pass (tariff addend) |
| pl_balance_measure R-open(dec) / R-min(open(rec), room) / R | pass (run amount + min pick added) | pass | pass |

### (c) transitive factor independence, (d) verbatim compute_basis sweep
| policy | factors | factor reads factor | plain reads factor | quotes | factor id in tool name |
|---|---|---|---|---|---|
| provider_ext_capitation_continuation | 6 | none | none | 20 quotes, misses none | none |
| provider_ext_repayment_interest | 5 | none | none | 13 quotes, misses none | none |
| provider_ext_exit_settlement | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_run_continuation | 6 | none | none | 19 quotes, misses none | none |
| provider_ext_decision_resumption | 6 | none | none | 20 quotes, misses none | none |
| provider_ext_plan_down_payment | 6 | none | none | 16 quotes, misses none | none |
| provider_ext_plan_installment | 6 | none | none | 19 quotes, misses none | none |

### (e) trigger rule
| tool | event written | base triggers |
|---|---|---|
| book_capitation_withholding_57430a7a / book_run_withholding_d2ce9ec8 / book_decision_withholding_431b56e1 / book_plan_installment_e88126b0 | provider_overpayment_recouped | [] |
| pay_exit_settlement_0b962b39 / pay_plan_down_payment_331c146f | provider_overpayment_refund_received | [] |
| pay_repayment_interest_bafa5446 | provider_remittance_issued (prompt_pay_interest) | [] |
No write lands in another category.

REWORK round 2: gates 7/7 green

## Rework round 3
- N2: small-practice ladders (cap_small_practice, pl_small_practice) measure practice size from two sources (census of the practice's own applied/active staff group contract, otherwise 3-month payments / size_volume_per_employee); no tier turns on buying coverage. N4: exit_base_share now counts dispute decisions of the last 24 whole months; exit <- capitation effect restated and verified exact. N5: one continuing capitation withholding per payment, one continuing run withholding per run as its first entry, first plan installment as the run's last entry (in-force sentences + compute guards). O8 resolved with N4 (monotone ladder). N1/N3: coordinator ruling, unchanged.

### (a) decoy / absent-record probes (scratch copies)
| task | probe | values | outcome |
|---|---|---|---|
| 0 | ended group contract (cancelled) listed first | (1.26, 9906.6, 23976.18) | same |
| 0 | older census reporting 25 employees | (1.26, 9906.6, 23976.18) | same |
| 0 | newer member-added event (not a census) | (1.26, 9906.6, 23976.18) | same |
| 0 | absent group contract and census (payments fallback) | (1.26, 10807.2, 23976.18) | MOVED |
| 0 | remittance of another agreement dated today | (1.26, 9906.6, 23976.18) | same |
| 0 | older dispute decision (30 months ago) | (1.26, 9906.6, 23976.18) | same |
| 0 | newer pending dispute filing (no decision) | (1.26, 9906.6, 23976.18) | same |
| 0 | absent dispute records | (0, 9906.6, 22558.61) | MOVED |
| 0 | absent capitation payments | (1.26, 0, 0) | MOVED |
| 1 | ended group contract (cancelled) listed first | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | older census reporting 25 employees | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | newer member-added event (not a census) | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | absent group contract and census (payments fallback) | (664.56, 793.78, 1065.74, 111.48) | MOVED |
| 1 | remittance of another agreement dated today | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | older dispute decision (30 months ago) | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | newer pending dispute filing (no decision) | (664.56, 793.78, 1065.74, 98.62) | same |
| 1 | absent dispute records | (590.72, 0, 915.63, 142.46) | MOVED |
| 1 | absent claim payment runs | (0, 0, 1125.78, 0) | MOVED |

### (b) method-shape all-pairs (unchanged method factors)
| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
|---|---|---|---|
| cap_aging_adj floor(d/5) / 5 / 0 | pass | pass | pass |
| rep_clock_start DAYS(due,rep) / DAYS(refund,rep) / DAYS(resolved,rep) | pass | pass | pass |
| exit_projection 2L-A / A / L | pass | pass | pass |
| run_aging_adj floor(d/3) / 4 / 0 | pass | pass | pass |
| dec_catch_up 4*floor(d/7) / 4 / 0 | pass | pass | pass |
| dp_shape min(250,R) / 500+0.1(R-2000) / 0.2R | pass | pass | pass |
| pl_balance_measure R-open(dec) / R-min(open(rec), room) / R | pass | pass | pass |

### (c) transitive factor independence, (d) verbatim compute_basis sweep
| policy | factors | factor reads factor | plain reads factor | quotes | factor id in tool name |
|---|---|---|---|---|---|
| provider_ext_capitation_continuation | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_repayment_interest | 5 | none | none | 13 quotes, misses none | none |
| provider_ext_exit_settlement | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_run_continuation | 6 | none | none | 19 quotes, misses none | none |
| provider_ext_decision_resumption | 6 | none | none | 20 quotes, misses none | none |
| provider_ext_plan_down_payment | 6 | none | none | 16 quotes, misses none | none |
| provider_ext_plan_installment | 6 | none | none | 21 quotes, misses none | none |

### (e) trigger rule
| event written | tools | base triggers |
|---|---|---|
| provider_overpayment_recouped | book_capitation_withholding_57430a7a, book_run_withholding_d2ce9ec8, book_decision_withholding_431b56e1, book_plan_installment_e88126b0 | [] |
| provider_overpayment_refund_received | pay_exit_settlement_0b962b39, pay_plan_down_payment_331c146f | [] |
| provider_remittance_issued (prompt_pay_interest) | pay_repayment_interest_bafa5446 | [] |

REWORK round 3 claims: N2, N4, N5, O8
REWORK round 3: gates 7/7 green

## Rework round 4
- R3-N2: payments proxy removed (small_volume binding and size_volume_per_employee param gone). cap_small_practice and pl_small_practice read only the documented employee headcount: the latest census of the practice's own not-ended (applied/active) Cascade staff group contract, now scoped by that contract's id. The rule says this census is the only headcount documentation Cascade holds. The absent-census / ended-contract / larger-headcount branch is a stated tier: standard terms, nothing. The same-size claim is gone.
- R3-N6: book_plan_installment_e88126b0 writes remittance_component "claim_payment". No withholding tool writes that value (they write not_applicable). The PLAN in-force sentence and its compute guard both test that component, on the run, for the plan overpayment.
- O10: closed with the proxy. CAP sums no payments, and CAP is the same with and without the prior interest write (checked).
- The task JSON texts (factor_trace, tracing, necessity, tier_taken, rationale) were swept of the proxy text. A round-4 revision log and round-4 probes were added.

### (a) decoy / absent-record probes (scratch copies, gold handling-time worlds)
| task | probe | values | outcome |
|---|---|---|---|
| 0 | decoy ended contract carrying a newer census of 25 | (1.26, 9906.6, 14069.58) | same |
| 0 | older census of 25 on the live contract | (1.26, 9906.6, 14069.58) | same |
| 0 | newer member-added event (not a census) | (1.26, 9906.6, 14069.58) | same |
| 0 | no census on file | (1.26, 11707.8, 14069.58) | MOVED (standard terms) |
| 0 | live contract ended (cancelled) | (1.26, 11707.8, 14069.58) | MOVED (standard terms) |
| 0 | latest census documents 7 | (1.26, 10807.2, 14069.58) | MOVED (second tier) |
| 0 | latest census documents 25 | (1.26, 11707.8, 14069.58) | MOVED (standard terms) |
| 0 | CAP without the prior interest write (O10) | 9906.6 | same |
| 1 | decoy ended contract carrying a newer census of 25 | (664.56, 129.22, 953.02, 36.4) | same |
| 1 | older census of 25 on the live contract | (664.56, 129.22, 953.02, 36.4) | same |
| 1 | newer member-added event (not a census) | (664.56, 129.22, 953.02, 36.4) | same |
| 1 | no census on file | (664.56, 129.22, 953.02, 47.33) | MOVED (standard terms) |
| 1 | live contract ended (cancelled) | (664.56, 129.22, 953.02, 47.33) | MOVED (standard terms) |
| 1 | latest census documents 7 | (664.56, 129.22, 953.02, 41.15) | MOVED (second tier) |
| 1 | latest census documents 25 | (664.56, 129.22, 953.02, 47.33) | MOVED (standard terms) |
| 1 | pre-installment world + withholding entry (not_applicable) 10.00 on the installment run for the plan overpayment | 36.02 | balance only, not blocked |
| 1 | pre-installment world + installment entry (claim_payment) on that run | 0 | MOVED (blocked) |
| 1 | re-evaluate run withholding after down payment / after installment; installment after installment | 0 / 0 / 0 | as stated |

### (b) method-shape all-pairs (method factors unchanged; small-practice factors are parameter type)
| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
|---|---|---|---|
| cap_aging_adj floor(d/5) / 5 / 0 | pass | pass | pass |
| rep_clock_start DAYS(due,rep) / DAYS(refund,rep) / DAYS(resolved,rep) | pass | pass | pass |
| exit_projection 2L-A / A / L | pass | pass | pass |
| run_aging_adj floor(d/3) / 4 / 0 | pass | pass | pass |
| dec_catch_up 4*floor(d/7) / 4 / 0 | pass | pass | pass |
| dp_shape min(250,R) / 500+0.1(R-2000) / 0.2R | pass | pass | pass |
| pl_balance_measure R-open(dec) / R-min(open(rec), room) / R | pass | pass | pass |

### (c) transitive factor independence, (d) verbatim compute_basis sweep
| policy | factors | factor reads factor | plain reads factor | quotes | factor id in tool name |
|---|---|---|---|---|---|
| provider_ext_capitation_continuation | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_repayment_interest | 5 | none | none | 13 quotes, misses none | none |
| provider_ext_exit_settlement | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_run_continuation | 6 | none | none | 19 quotes, misses none | none |
| provider_ext_decision_resumption | 6 | none | none | 20 quotes, misses none | none |
| provider_ext_plan_down_payment | 6 | none | none | 16 quotes, misses none | none |
| provider_ext_plan_installment | 6 | none | none | 21 quotes, misses none | none |

### (e) trigger rule
| event written | tools | base triggers |
|---|---|---|
| provider_overpayment_recouped (component not_applicable) | book_capitation_withholding_57430a7a, book_run_withholding_d2ce9ec8, book_decision_withholding_431b56e1 | [] |
| provider_overpayment_recouped (component claim_payment) | book_plan_installment_e88126b0 | [] |
| provider_overpayment_refund_received | pay_exit_settlement_0b962b39, pay_plan_down_payment_331c146f | [] |
| provider_remittance_issued (prompt_pay_interest) | pay_repayment_interest_bafa5446 | [] |

Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; cache-diff info only. A traceability pre-run lists only the unpublished discoverable tool names (publication-dependent).

REWORK round 4 claims: R3-N2, R3-N6, O10
REWORK round 4: gates 7/7 green

## Rework round 5
- R4-N7: the claim_payment marker is removed. book_plan_installment_e88126b0 writes remittance_component "not_applicable", as db_schema requires for overpayment entries; its docstring and receipt no longer mention a component. The PLAN once-per-run guard is back to the round-3 form: COUNT(recouped, remittance_number=run_no, original_payment_event_id=plan_case) == 0. The rule sentence now states the base grain: "A remittance carries at most one withholding entry per overpayment, so when the run already carries any withholding entry for the overpayment the plan down payment was recorded against, nothing more is withheld from it under this policy."
- Class: every recouped writer respects one row per (overpayment, remittance). CAP blocks on (case, payment). OFF blocks on any entry on the run. RSM blocks on any entry of the decided case. PLAN blocks on (plan case, run).
- Text sweep: task 0 needed one sentence of its round-4 log edited (no write or figure moved). In task 1, the round-4 R3-N6 log sentence was replaced by a round-5 log, and the marker probe was replaced by the round-5 probes.

### (a) probes (scratch copies; PLAN on the gold pre-installment world unless stated)
| task | probe | value | outcome |
|---|---|---|---|
| 1 | gold (the installment run's two earlier entries are on other overpayments) | 36.4 | gold |
| 1 | + withholding entry 100.00 on the installment run for the plan overpayment (continuing, post-decision or earlier installment alike) | 0 | MOVED (blocked, base grain) |
| 1 | + withholding entry 100.00 on the installment run for another overpayment | 29.22 | not blocked (run room falls) |
| 1 | + withholding entry 100.00 for the plan overpayment on the previous run | 32.56 | not blocked (open balance falls) |
| 1 | after all gold writes: PLAN / OFF / RSM | 0 / 0 / 0 | as stated |
| 1 | OFF after the down payment | 0 | as stated |
| 0, 1 | all scored figures on gold handling-time worlds | equal to gold | unchanged |
| 0, 1 | census probes of round 4 (decoy ended contract, older census, non-census event, no census, ended contract, 7, 25) | unchanged (no census read touched) | as round 4 |

### (b) method-shape all-pairs: unchanged from round 4 (no method factor touched); all pairs pass.

### (c) transitive factor independence, (d) verbatim compute_basis sweep
| policy | factors | factor reads factor | plain reads factor | quotes | factor id in tool name |
|---|---|---|---|---|---|
| provider_ext_capitation_continuation | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_repayment_interest | 5 | none | none | 13 quotes, misses none | none |
| provider_ext_exit_settlement | 6 | none | none | 21 quotes, misses none | none |
| provider_ext_run_continuation | 6 | none | none | 19 quotes, misses none | none |
| provider_ext_decision_resumption | 6 | none | none | 20 quotes, misses none | none |
| provider_ext_plan_down_payment | 6 | none | none | 16 quotes, misses none | none |
| provider_ext_plan_installment | 6 | none | none | 21 quotes, misses none | none |

### (e) trigger rule
| event written | tools | base triggers |
|---|---|---|
| provider_overpayment_recouped (component not_applicable) | book_capitation_withholding_57430a7a, book_run_withholding_d2ce9ec8, book_decision_withholding_431b56e1, book_plan_installment_e88126b0 | [] |
| provider_overpayment_refund_received | pay_exit_settlement_0b962b39, pay_plan_down_payment_331c146f | [] |
| provider_remittance_issued (prompt_pay_interest) | pay_repayment_interest_bafa5446 | [] |

Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; cache-diff info only.

REWORK round 5 claims: R4-N7
REWORK round 5: gates 7/7 green

## Rework round 6 (text-only)
- S1: the find_group_contracts necessity texts in tasks 0 and 1 no longer say the factor falls back to the agreement's payments. They now say the factor reads the documented headcount (the census of the practice's own not-ended staff group contract) and that with no such contract or census the practice is on the standard terms (no adjustment). That matches cap_small_practice / pl_small_practice.
- Sweep: every string in both task JSONs (rationale, necessity, objective, tracing, factor_trace, tier text, prerequisite_closure, solvability_contract) and the round-5 worklog section were checked for proxy remnants (fallback, proxy, payments measure, size_volume, 6,000, same size, middle tier, two sources). The only other hits are the round-3/4 revision-log sentences, which state that the proxy was removed and are accurate.
- Untouched: provider.extended.yaml (0721673c4508e267…) and task_tools.py (398bc89af826a284…) are byte-identical. No scored value, gold argument or world row changed.
- (a)-(e) are unchanged from round 5: no compute, read, factor, tool or event changed.

Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; cache-diff info only.

REWORK round 6 claims: S1
REWORK round 6: gates 7/7 green
