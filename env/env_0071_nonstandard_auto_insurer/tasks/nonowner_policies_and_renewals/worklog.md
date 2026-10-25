# worklog — nonowner_policies_and_renewals (env_0071), round 1

## Step 0 — difficulty pre-check
- draws: task0 prerequisite_problems=1 factor_counts=[5,4]; task1 prerequisite_problems=3 factor_counts=[6,6,4,5]
- base charter: no premium rating table; numeric nonowner writes = full_term_premium (renewal_issued create,
  limits_changed update), premium rows (written / additional / return / policy fee / reinstatement fee / fee waived).
  Transition-only events (renewal_accepted, cancelled_*, reinstated, rescinded, expired, not_taken) carry no number,
  so they can be a problem only when the tool also books the row the event triggers (cancellations -> return premium).
- numeric user acts available: (U1) nonowner_cancelled_insured_request (lifecycle in_force->cancelled by user) with its
  triggered nonowner_return_premium; (U2) nonowner_limits_changed elected by the insured, only computable when the target
  package is fixed by records (an out-of-state certificate rejected for limits -> lowest package meeting the filing state).
  Statement signings carry no numeric field and stay seeded.
- FR-44-cure-by-rejection is not producible by the fr charter (fr_filing_eligibility requires package >= minimum
  backing package); the out-of-state SR-22 rejection IS producible (Minimum Limits = residence-state minimum, filing
  state's limits govern) -> used for U2.

## Scope plan (claimed task by task)
- task 0 (TX): root U1 nonowner_ext_insured_cancel_return (user) <- nonowner_ext_late_renewal_written (agent, value_input)
- task 1 (FL, reserved headroom): root renewal-offer premium (agent) <- U2 package change (user) <- additional premium for the
  increase (agent) <- reinstatement re-written premium (agent). Disjoint from task 0 (different events/tools).

## Events written by tools, with base triggers (XF14)
- nonowner_premium_written: triggers [] (task 0 agent tool)
- nonowner_cancelled_insured_request: triggers nonowner:nonowner_return_premium (written in the same call); return_premium triggers []
- (task 1) nonowner_limits_changed triggers []; nonowner_additional_premium triggers []; nonowner_renewal_issued triggers []
- none lands in another category.

## Task 0 design notes
(see tasks/0.json design_rationale for the dossier; numbers below are the verification run)
- policies: nonowner_ext_late_renewal_written (state_due, agent, 5 factors) -> book_renewal_written_premium_ed68a083;
  nonowner_ext_insured_cancel_return (on_request, user, 4 factors) -> cancel_nonowner_term_6aabad38. Edge root<-late renewal: value_input,
  state form "The requested-cancellation return is fixed only after the term's premium ledger carries a premium-written entry for the term."
- verification (scratch harness = check_compute.build_env + real tool bodies on a dict copy): written 1258.59 (whole baseline 1089.74;
  per-factor 1187.35 / 1233.91 / 1221.93 / 1233.91 / 1237.84); return 1044.66 (whole baseline 1089.16; per-factor 969.05 / 1069.87 /
  1036.26 / 1128.50); return with the premium booking skipped = 0.00.
- revisions: (1) gate: factor bindings must read fr themselves -> certificate_form_load and lapse_exposure_days got their own CFIELD reads
  (shared plain binding removed in that policy); (2) gate: own-history LATEST on the Statement of No Loss made history "decorative" ->
  exposure tier 2 re-keyed on the latest billing payment channel (agent office / agent phone binds at payment, posting day charged);
  (3) replay: empty-string FKs -> None; 12 unread rows -> reads by customer_id on premium ledger / documents, plus fr fee ledger and
  invoices reads (each states the decision it feeds); (4) DOB stated as 1991-03-22 verbatim.
- per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 0 — later revisions (propagated by regenerating 0.json from the scratch generator)
- renewal-term full-term premium re-derived with the renewal offer rule (task 1 policy) on the 2026-09-10 world: 880.00 x TX 1.08 x points
  class 1.28 x late 1.03 x returned 1.04 x SR-22 1.04 = 1355.25; term-1 binding premium 1214.85 (spring table); billing rows re-priced
  (down 20% + fees, equal installments with final absorbing). New gold: written premium 1539.44 (182 days from 2026-10-10), return
  1277.78 (162 unearned days, retention 6.75%).
- XF5(f): third overwrite on nonowner_unearned_premium_return (transaction-by-transaction sentence) because the run-off method changes the
  unearned days; replaced_by restates nonpayment/underwriting/conversion/void returns as unchanged.
- XF8: late-renewal rule now prices out-of-scope (no lapse recorded) as the base figure (full-term premium); same-day tie rule stated for
  LATEST/XLATEST reads.
- XF10: exposure tier 2 re-keyed from "in-force days + 1" (constant shift = fail) to days from the latest payment's posting date (data input).

## Task 1 (FL) — claimed: reinstatement re-write, package re-rate (user), increase premium, renewal offer (root)
- tools: book_reinstatement_rewritten_premium_bf43cbc7, change_nonowner_package_67dc97ad (owner=user), book_package_increase_premium_8b98e0ec,
  issue_nonowner_renewal_offer_23563ff0. Draw [6,6,4,5]: renewal offer 6, re-rate 6, increase 4, re-write 5.
- tree: offer <- re-rate (value_input, state), offer <- increase (state_gate, ACTION form: nothing records that/when a package was raised),
  increase <- re-rate (value_input, state), increase <- re-write (value_input, state). Topological order re-write, re-rate, increase, offer;
  re-write and re-rate commute (harness ran both orders: identical values and terminal world).
- gold: re-write 163.89 (38 days from 2026-10-10), re-rate 1249.12 on Non-Owner 50/100/50, increase 84.87 (30 days from 2026-10-18),
  renewal offer 1365.48 (2026-11-17..2027-05-17, 181 days). Skips: no re-rate -> offer 932.56 (Minimum Limits) and increase 0.00;
  no re-write -> increase 108.71 on the standard basis; no increase -> missing limits-increase entry (state gate).
- revisions: points moved from a factor into the standard rating (a field is not a factor tier); late-payment relativity added; rate
  table tiers decided by DAYS() spans; on_request -> state_due for the re-rate (the cure is owed by the state rejection, not asked by
  the caller); renewal-offer intent cited from initial_state; removed nonowner_nonrenewal (does not govern renewal_issued); history depth
  raised to 10 rows by a real July late payment + rescinded notice under the Six-Pay plan before the 2026-07-31 switch to Monthly EFT.
- realism notes (honest): the company rating plan (tables, relativities, state factors) and the certificate-liability day rules are
  company schedules stated in the charter, not statute; the out-of-state SR-22 rejection is producible by the fr charter (minimum backing
  package = Minimum Limits; filing state's limits govern); the package-change owner=user is justified as the insured's own coverage
  election (the blueprint lists signing statements and confirming cancellations as user acts; package election is not listed).

## Pairwise method-tier table (XF10) — distinguishing input per pair
| policy / method factor | tier A | tier B | fall-through | A-B | A-C | B-C |
|---|---|---|---|---|---|---|
| late renewal / lapse_exposure_days | DAYS(term effective, exp) | DAYS(latest payment posted, exp) | DAYS(last lapse day, exp)-1 | renewal effective date vs billing posting date | different date input | billing posting date input |
| cancel return / certificate_runoff | std - (CPARAM sr26 + CPARAM runoff) | DAYS(MX(cancel, certificate end), exp) | std | tariff params vs end-date input + max | tariff params | end-date input + max |
| re-write / certificate_lapse_rewrite | DAYS(cancellation eff, exp) | DAYS(cancel, exp) - MX(0, DAYS(cert end, reinst)) | DAYS(reinst eff, exp) | cert-end input + max | cancellation-date input | cert-end input + max |
| increase / increase_unearned_basis | ledger: rerated share - written share + returns share - re-written share | rerated share - written share over its own days | (rerated - written) x d / term days | return/re-write inputs | return/re-write inputs | written-days input |
| re-rate, offer / *_rate_table | spring tariff | winter tariff | standard tariff | different tariff parameter | tariff parameter | tariff parameter |

## Probe table (XF8) — scratch copies, rule outcome observed
 | Q8 base world | (1539.44, {'late_renewal_charged_days': 182}) |
 | Q8 no certificate on file (filed->withdrawn), latest payment online | (1484.38, {'late_renewal_charged_days': 179, 'certificate_form_load': 1.0}) |
 | Q8 no certificate, latest payment at agent office | (1492.67, {'late_renewal_charged_days': 180}) |
 | Q8 absent lapse (no lapse recorded) | (1355.25, {}) |
 | Q8 lapse 6 days | (1597.53, {'lapse_length_load': 1.1}) |
 | U1 base world (after booking) | (1277.78, {'unearned_days': 162, 'retention_pct': 6.75}) |
 | U1 absent filing record | (1280.4, {'unearned_days': 175, 'requirement_relief': 1.0}) |
 | U1 SR-26 sent, certificate end 2026-10-27 (decoy: later than cancel date) | (1207.23, {'unearned_days': 165}) |
 | U1 request backdated (requested before received) | (1186.3, {'cancellation_date': '2026-10-14', 'advance_notice_credit': 1.0}) |
 | U1 no premium entry (prerequisite skipped) | (0.0, {'written_entry_days': None}) |
 | U1 replaced_with_other_insurance, no certificate | (1330.36, {'requirement_relief': 0.75}) |
 | b base world | (163.89, {'reinstatement_rewritten_days': 38}) |
 | b no certificate on file | (142.36, {'reinstatement_rewritten_days': 34}) |
 | b SR-26 sent, end 2026-10-12 | (150.74, {'reinstatement_rewritten_days': 36}) |
 | b reinstatement without lapse (base figure) | (122.99, {}) |
 | b absent nonpayment return | (0.0, {}) |
 | B after b,U (gold handling world) | (84.87, {'increase_before_loads': 74.2733409610984}) |
 | B with no re-written entry (standard basis) | (108.71, {'increase_before_loads': 95.13913043478259}) |
 | B late-renewal style written entry 170 days, no re-write | (98.5, {'increase_before_loads': 86.20204603580562}) |
 | B Paid-in-Full plan, Texas rejection | (80.79, {'increase_plan_credit': 0.96, 'increase_certification_load': 1.03}) |
 | B negative difference floored | (0.0, {}) |
 | U2 rating date 2026-05-31 | (1249.12, {'rerate_rate_table_rate': 730.0}) |
 | U2 rating date 2026-06-01 | (1300.45, {'rerate_rate_table_rate': 760.0}) |
 | U2 rating date 2026-10-31 | (1300.45, {'rerate_rate_table_rate': 760.0}) |
 | U2 rating date 2026-11-01 | (1365.48, {'rerate_rate_table_rate': 798.0}) |
 | C gold handling world | (1365.48, {'offer_rate_table_rate': 798.0, 'expiring_package': 'Cardinal Point Non-Owner 50/100/50'}) |
 | C no filed certificate, no lapse | (1238.64, {'offer_certificate_relativity': 1.0, 'offer_lapse_relativity': 1.0}) |

## Final gate block (difficulty-level, no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
(check_traceability deferred until the KB is rendered; check_cache_diff informational)
INSTANTIATE round 1: gates 7/7 green

# ROUND 2 (rework) — audit audits/policy_task/nonowner_policies_and_renewals/ (CG-1..CG-9, T0-F1/F2, T1-F1..F5, O-1..O-12) + XF 17-19
## Plan (written before edits)
- CG-1: task 1 moves to Virginia; the rejected certificate becomes an FR-44 Operator certificate (VA minimum backing package =
  Cardinal Point Non-Owner 100/200/50 in the fr base); the package re-rate moves the term to exactly that package, as the fr cure says.
- CG-2/CG-3 (class: every method factor): rate-table swaps and start-date swaps removed. Methods now: late-renewal written premium
  flat full-term vs per-day vs fully-earned-minimum floor; re-write flat vs per-day vs minimum re-write floor; filer class applied
  per day (requirement ends inside the term) vs flat (runs through) vs none, in the re-rate and the renewal offer; increase basis
  (ledger vs written-days vs difference) kept; run-off method kept.
- CG-4 + XF17 (class: every ladder key): state-of-rejection ladder removed; late-fee and notice counts removed everywhere. Keys kept/used:
  package (base rate), state factor, violation-points class, filer class (certificate form x points), lapse length, cancellation for
  nonpayment recency, returned-payment (NSF) history (the billing charter's own certified-funds key), paperless (e-signature),
  billing plan credit / installment service charge, days-based methods.
- CG-5/XF18 (class: every certificate read): no factor keys on the term's financial_responsibility_filing stamp; in both worlds the
  stamp is stale ('none': the certificate was added after binding without an endorsement) and every rule says the stamp is not read.
- CG-6: P2's replaced_by restates the full transaction-by-transaction formula for the other cancellations.
- CG-7: the agent-office "bound at payment" tier is deleted.
- CG-8 (class): every certificate read filters to Operator forms explicitly and states that an FR-44 counts over an SR-22 when both are on
  file; SR-26-sent reads are Operator-only too.
- CG-9: P6 tier 2 requires the premium-written entry to record more than zero days, in words and compute.
- XF19: edge sentences re-checked for strength and deadlock after the rewrite.

## Round 2 — what was done (scored values live only in the task files)
- Charter regenerated from scratch scripts (base copy byte-identical; 6 extended policies, same ids, tools and computes).
- Shared company rating plan (one table set, each policy names its own copy): package six-month base rate, residence-state factor,
  violation-points class (standard rating), filer class by certificate form x points (Operator SR-22/FR-44 requirement read from fr
  records only: requested/filed/rejected; FR-44 counts over SR-22; withdrawn/terminated/cancellation_filed and Owner certificates
  excluded; the term's financial_responsibility_filing stamp never read), lapse length, cancellation-for-nonpayment recency,
  returned-payment (NSF) history, paperless (e-signed statement and mailed documents), billing plan credit.
- P1 late-renewal written premium: re-rated as of the renewal effective date on that plan; factors lapse / NSF / paperless / plan +
  method charging basis (flat full-term when an Operator certificate on file ran through the lapse, per-day, or per-day floored at a
  fully earned half for twelve-month terms). Agent-office "bound at payment" tier deleted (CG-7).
- P2 requested-cancellation return: replaced_by restates the full transaction-by-transaction formula (CG-6); Operator filters and
  FR-44 precedence on every certificate read (CG-8); factors unchanged.
- P3 package re-rate: the cure package is the fr minimum backing package of the rejected FR-44 Operator certificate (VA ->
  Non-Owner 100/200/50, FL -> Non-Owner 100/300/50), exactly the fr base cure (CG-1); factors lapse / nonpayment / NSF / paperless /
  plan + method filer basis (class applied by share of months run / in full / none). Rate-table swap deleted (CG-2).
- P4 renewal offer: same plan on the expiring package; method filer basis by renewal months (CG-2); edge sentence to P3 now names
  "the minimum backing package of every Operator certificate the named insured has requested, filed or had rejected".
- P5 reinstatement re-write: factors lapse / nonpayment / NSF + methods filer basis (per day / full / none) and exposure basis (flat
  whole return / re-write days floored at 45 or the return's days when under 60 days remain / per-day) — no start-date swap (CG-3).
- P6 increase charge: state-of-rejection load deleted (CG-4); plan credit replaced by installment service charge (five / one-or-three
  installments / paid in full) and a filer handling load by certificate form; tier 2 requires more than zero recorded days (CG-9).
- Worlds: task 0 stamps set to none (SR-22 taken over in May without endorsement), renewal plan Paid-in-Full, Statement of No Loss
  mailed, billing re-priced (filing fee on installment 2's invoice); term premiums re-derived with the plan (binding and the
  2026-09-10 renewal offer). Task 1 moved to Virginia: Minimum Limits with UM term, FR-44 Operator carrier-transfer request rejected
  for limits plus a withdrawn duplicate, VA 15-day notices, billing re-priced and balanced.
- Honest residual: the seeded FR-44 request was transmitted although fr_filing_eligibility asks for the backing package to be at or
  above the minimum backing package at request; the state's limits rejection is exactly the case the fr cure clause handles, and
  the move P3 makes is that cure.

## Pairwise method-tier table, round 2 (XF10)
| policy / method | tier A | tier B | fall-through | A-B | A-C | B-C |
|---|---|---|---|---|---|---|
| P1 late_charging_basis | flat share 1 (no day input) | MX(days share, one half) | days in force / term days | max op vs none | drops day inputs | adds max op |
| P2 certificate_runoff | std - CPARAM sr26 - CPARAM runoff | DAYS(MX(cancel, cert end), exp) | std days | tariff vs end-date+max | tariff params | end-date input + max |
| P3/P4/P5 *_filer_basis | 1 + (class-1) x share (months or days run) | class(form, points) | 1 | share inputs | form/points/date inputs | form/points inputs |
| P5 rewrite_exposure_basis | whole return (no day ratio) | return x MX(d, MN(45, rd)) / rd | return x d / rd | max/min ops vs none | drops day inputs | adds max/min ops |
| P6 increase_unearned_basis | ledger shares of every entry | rerated share - written over its own (>0) days | difference x d / term days | return/re-write inputs | return/re-write inputs | written-days input |

## Probe table, round 2 (XF8; scratch copies, decoys / absent records / boundaries / zero division)
| Q8 gold world | 1266.29 | {'late_charge_share': 1.0, 'late_filer_factor': 1.025} |
| Q8 filed SR-22 made withdrawn (absent certificate) -> per-day | 1215.04 | {'late_charge_share': 0.9835164835164835, 'late_filer_factor': 1.0} |
| Q8 decoy Owner SR-22 certificate filed (not Operator) | 1215.04 | {'late_charge_share': 0.9835164835164835, 'late_filer_factor': 1.0} |
| Q8 decoy terminated FR-44 Operator | 1266.29 | {'late_filer_factor': 1.025} |
| Q8 second certificate: FR-44 Operator requested too (FR-44 counts) | 1667.8 | {'late_filer_factor': 1.35} |
| Q8 certificate required-through before first lapse day -> per-day | 1215.04 | {'late_charge_share': 0.9835164835164835, 'late_filer_factor': 1.0} |
| Q8 twelve-month term, no certificate -> half floor | 2430.08 | {'late_charge_share': 0.9835164835164835} |
| Q8 no lapse recorded -> base figure | 1231.96 | {} |
| Q8 lapse 5 vs 6 days | 1337.97 | {'late_lapse_relativity': 1.12} |
| U1 gold world | 1051.06 | {'unearned_days': 162, 'retention_pct': 6.75} |
| U1 Owner certificate filed only (not Operator) | 1053.21 | {'unearned_days': 175, 'requirement_relief': 1.0} |
| U1 Owner certificate cancellation_filed (ignored) | 1053.21 | {'unearned_days': 175} |
| U1 Operator SR-26 sent, end 2026-10-27 | 993.03 | {'unearned_days': 165} |
| U1 0-day premium entry (zero division guard) | 1051.06 | {'written_entry_days': 0} |
| b gold world | 231.45 | {'rewrite_amount_basis': 144.0, 'rewrite_filer_factor': 1.35} |
| b certificate filed before the lapse -> flat | 231.45 | {'rewrite_amount_basis': 144.0} |
| b >= 60 days left -> per-day (move reinstatement earlier) | 578.63 | {'rewrite_amount_basis': 360.0, 'days_from_reinstatement': 95} |
| b required-through inside the re-write period -> per-day share | 204.98 | {'rewrite_filer_factor': 1.1955882352941176} |
| b required-through before reinstatement -> none | 171.45 | {'rewrite_filer_factor': 1.0} |
| b no requirement (only withdrawn) | 171.45 | {'rewrite_filer_factor': 1.0} |
| b absent nonpayment return -> 0 | 0.0 | {} |
| b without-lapse reinstatement -> base figure | 128.84 | {} |
| U2 gold world | 1617.76 | {'rerate_base_rate': 880.0, 'rerate_filer_factor': 1.35} |
| U2 no FR-44 limits rejection -> base figure | 697.25 | {} |
| U2 SR-22 Operator rejected for limits (not FR-44) -> base figure | 697.25 | {} |
| U2 nonpay 90 vs 91 days (cancellation 2026-07-20) | 1617.76 | {'rerate_nonpay_days': 90, 'rerate_nonpay_relativity': 1.08} |
| U2 required-through ending in month 6 of the term | 1617.76 | {'rerate_filer_factor': 1.35} |
| U2 required-through on expiration day -> full | 1617.76 | {'rerate_filer_factor': 1.35} |
| B gold handling world | 96.41 | {'increase_before_loads': 81.0436784897025} |
| B no re-write, 0-day written entry -> standard (CG-9) | 178.55 | {'increase_before_loads': 150.08315217391305} |
| B written entry 170 days -> written-days basis | 167.41 | {'increase_before_loads': 140.72109974424552} |
| B Paid-in-Full / Four-Pay plans | 95.01 | {'increase_service_charge': 1.015} |
| C gold handling world | 1477.96 | {'offer_filer_factor': 1.2333333333333334, 'offer_requirement_share': 0.6666666666666666} |
| C requirement through 2027-05-17 (renewal end) -> full | 1617.76 | {'offer_filer_factor': 1.35} |
| C requirement through 2027-05-16 -> six of six months | 1617.76 | {'offer_filer_factor': 1.35, 'offer_requirement_share': 1.0} |
| C requirement through 2026-11-16 (before renewal) -> none | 1198.34 | {'offer_filer_factor': 1.0} |
REWORK round 2: gates 7/7 green

# ROUND 3 (rework) — audit revision_2 items R2-A..R2-H + XF 20-22
## Plan (before edits)
- R2-A: paperless credit struck from P1/P3/P4 (whole factor, not just the middle tier).
- R2-B: P2 advance-notice cut struck -> replaced by a real dimension already in the records: term origin (new-business term vs renewal
  accepted after a lapse vs on-time renewal) scaling the short-rate retention. P6 installment service charge and filer handling load
  struck; P6 now rates the moved package itself for the increase days (each rating dimension once in the charge) less the ledger's
  unearned premium.
- R2-C (class): lapse ladders in lapse-scoped policies (P1, P5) become 6+ / 3-5 / 1-2 days; P5's universal nonpayment ladder struck.
- R2-D: every period the rules use is defined with included/excluded ends in words.
- R2-E: "or none" removed (P1 charging basis, P5 exposure basis).
- R2-F: task 1 re-seeded as a producible history: Virginia insured on Non-Owner 250/500/100 (DUI not accepted), a new FR-44 Operator
  requirement filed on that term (fr eligibility met: package above the FR-44 minimum backing package, VA in its FR-44 states), which
  makes the package unacceptable under nonowner_eligibility; P3 realigns the term to the highest package that accepts a DUI-related
  requirement and backs an FR-44 in the residence state (Non-Owner 100/300/50). The FR-44 cure story is dropped.
- R2-G: filer per-share method dropped; filer class is a parameter everywhere. Methods: P1 charging basis, P2 run-off, P3 change basis
  (flat re-rate in the underwriting period / per-day blend of old and new package / premium kept in the last 15 days), P4 lapse window
  (per-month share / floored share / flat), P5 exposure basis, P6 unearned basis.
- R2-H: one generic combination sentence per policy.
- XF20: P6 states that a change not raising the premium for the remaining days owes nothing; P4's action-form edge waits only on an
  increase charge that is owed.

## Round 3 — what was done (scored values live only in the task files)
- R2-A: paperless credit removed as a whole factor from P1, P3 and P4. No add-on replaces it.
- R2-B: struck the P2 advance-notice cut, the P6 installment service charge and the P6 filer handling load.
  - P2's fourth factor is term origin, a real dimension already on the ledger: the reason on the latest premium-written entry, which scales the short-rate retention.
  - P6 rates the moved package once and deducts the ledger's unearned premium entry by entry. Each rating dimension is charged once.
- R2-C: every tier is reachable inside its own policy's scope.
  - P1 and P5 use scoped lapse ladders (6+, 3–5, 1–2 days).
  - P5's universal nonpayment ladder is gone.
  - The P1 floor tier was dead in P1's scope (the late window is 5 days at most). It is replaced by a certified-days tier (see XF23).
- R2-D: every period is defined, with both ends stated in words:
  - P1: days in force, and charged days.
  - P3: days run, and days remaining.
  - P4: renewal term, and lapse window.
  - P5: re-write days, and charged days.
  - P6: increase days.
- R2-E: "or none" is gone. P1 and P5 now read "required-through date ... or is not recorded". A missing certificate is its own words ("including no such certificate"), so there is exactly one booking date per tier.
- R2-F: task 1 is re-seeded as a producible Virginia DUI realignment.
  - The insured holds 250/500/100, which does not accept a DUI.
  - The FR-44 Operator certificate was requested on 2026-10-01 and filed on 2026-10-02. That term is fr-eligible: VA is among its FR-44 states and it is above the minimum backing package.
  - The fee is on installment 4's invoice, as the fr fee_billing_rule requires.
  - There is no SR-26: the term was reinstated on day 3 of the 3-day window, before one was sent, so the certificate continued (fr_sr26_notice).
  - P3 realigns the term to 100/300/50.
- R2-G: method shapes are listed in the pairwise table below. No method pair substitutes only a multiplier.
- R2-H: one generic combination sentence per policy. It names no factor quantity.
- XF20 (zero-amount edges):
  - P6 books nothing for a nil or non-positive charge, and P4's action edge waits only on an increase charge that is owed.
  - P5's nil case (no nonpayment return) is unreachable, because base always books that return mid-term.
- XF21 (look-backs):
  - Returned payments are counted over 12 whole months. Task 1's plan runs from 2026-05-26, and every billing row from inception is seeded.
  - The nonpayment relativity reads the term's own ledger return. The lapse relativity reads the term's own Statement of No Loss.
  - Task 0's twelve-month window covers its seeded term-1 history.
- XF22 (removing beats adding): nothing was added in place of a struck factor.
  - The P1 and P5 method tiers changed shape, not dimension.
  - The new own-history reads re-key existing dimensions (lapse, prior nonpayment cancellation) onto the records that evidence them. They are not new add-ons.
- XF23 (coordinator realism bar), checked factor by factor:
  - Every factor is keyed on a rate-filing dimension and applied to a premium-derived amount:
    - filer class (SR-22/FR-44 × points);
    - prior insurance lapse;
    - prior cancellation for nonpayment;
    - returned-payment history (a billing-history relativity, stated as the company's filed relativity);
    - payment plan (EFT/autopay, PIF);
    - package (rate table), state and points class.
  - Numbers are stated as the company's own relativities. No statute is cited.
  - Retention or charge for no-exposure days:
    - Struck: P5's fully earned minimum floor, which booked more days than remain and so charged lapse days with no exposure (audit observation O2-1).
    - Struck: P1's half-term floor.
    - Both are replaced by a certified-days tier: lapse days are charged only while the company stayed certified on a filed Operator certificate, which is real exposure to the state under fr_sr26_notice. The flat tiers charge the whole lapse only when the certificate ran through its last day.
    - The P2 short-rate retention is base's insured-request retention (short rate is a real days-based method). Its scales are elapsed-term share, requirement relief and term origin. Run-off days are certificate exposure.
  - Residual risk, disclosed: the returned-payment relativity is not in the coordinator's example list. It is kept as a billing-history rating dimension because striking it would leave P1, P3, P4, P5 and P6 below their drawn counts with no real dimension left in the records to replace it.
- History depth (gate):
  - The paperless reads used to touch the documents table and have been removed.
  - The lapse relativity now counts from the latest Statement of No Loss's attested lapse start, and the nonpayment relativity from the term's ledger nonpayment return. Both are guarded by a COUNT, which makes the history load-bearing.
  - history_rows_max is 9.
- Events written (XF14) are unchanged; see the round-1 list. No new tool and no tool body change in round 3, apart from the P6 docstring wording ("package change").

## Pairwise method-tier table, round 3 (XF10) — distinguishing input or operation per pair
| policy / method | T1 | T2 | T3 (= baseline) | T1 vs T2 | T2 vs T3 | T1 vs T3 |
|---|---|---|---|---|---|---|
| P1 late_charging_basis | flat share one (no day ratio) | (term days − lapse days after required-through) / term days | days in force / term days | adds required-through date and lapse end | adds required-through date; drops in-force date | drops the day ratio |
| P2 certificate_runoff | standard unearned days less SR-26 transmission days plus run-off days (certificate on file) | days from the later of cancellation date and the certificate end date (SR-26 already sent) | standard unearned days | tariff days vs data-selected window start | adds certificate end date and a max (later-of) | adds two tariff-day inputs |
| P3 rerate_change_basis | MX(current base, new base) for the whole term (<15 days left) | per-day blend current/new by days run/remaining (>60 run, ≥15 left) | flat new base | max operation vs day-weighted sum | adds days run and current base | adds current base and max |
| P4 offer_lapse_window | relativity by remaining-window months / term months (3–5 days, window ends inside) | that share floored at one half (6+ days) | standard flat relativity | adds floor operation | adds window-month input | adds window-month input |
| P5 rewrite_exposure_basis | whole return (no day ratio) | return × (return days − lapse days after required-through) / return days | return × re-write days / return days | adds required-through and lapse end | adds required-through; drops reinstatement date | drops the day ratio |
| P6 increase_deduction_basis | ledger entry by entry (each entry over its own days) | written premium over its own (>0) days | written × increase days / term days | adds re-write and return entries | adds the entry's own days | adds entries |

## Probe table, round 3 (XF8; scratch copies; decoys / absent records / boundaries / zero division) — "gold" = seeded outcome
| probe | outcome |
|---|---|
| P5 seeded (FR-44 filed before lapse, through 2029) | gold, flat tier |
| P5 FR-44 filed after first lapse day | per-day tier (= exposure baseline) |
| P5 required-through inside lapse | certified-days tier (two lapse days after through not re-written) |
| P5 required-through = first lapse day | certified-days tier (three lapse days not re-written) |
| P5 required-through = last lapse day | flat tier (boundary inclusive) |
| P5 required-through before lapse | per-day tier |
| P5 required-through not recorded | flat tier |
| P5 only a withdrawn decoy / FR-44 cancellation_filed | per-day tier (status filed only) |
| P5 no Statement of No Loss | lapse counts no days -> no lapse relativity |
| P5 older SNL decoy (earlier lapse) / same-date SNL recorded later | latest kept / first recorded kept; gold unchanged |
| P5 no nonpayment return | 0, nothing booked (unreachable: base always books it) |
| P5 return days 0 | flat tier unaffected; per-day and certified-days guarded to 0 (unreachable: base return carries its days) |
| P3 no nonpayment return / insured-request return decoy | nonpayment relativity none |
| P3 no SNL / older SNL decoy | lapse none / gold unchanged |
| P4 no nonpayment return | nonpayment relativity none |
| P1 seeded (SR-22 filed 05-06, through 10-16) | gold, flat tier |
| P1 required-through inside lapse (10-11) | certified-days share (one lapse day uncharged) |
| P1 required-through = last lapse day | flat (boundary inclusive) |
| P1 required-through before lapse / filed after first lapse day / withdrawn decoy only | per-day share |
| P1 no SNL | lapse none |
| Task 1 order swap (re-write vs realignment) | identical values and terminal world |
| Task 1 skips | re-write skipped -> increase on written basis; realignment skipped -> increase and offer on 250/500/100; increase skipped -> offer unchanged (action gate) |

## Final gate block, round 3 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 43/43 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK (history_rows_max=9, branches_max=199) · GROUNDING OK · SCOPE OK

REWORK round 3: gates 7/7 green

# ROUND 4 (rework) — audit revision_3 (task0=PASS; task 1 RED on R3-A, R3-B) + observations O3-1..O3-7
## Plan (before edits)
- Edits are minimal. Task 0's world and everything revision_3 passed stay untouched, and every combination sentence keeps its order.
- R3-A: P6's generic combination sentence will state the non-commuting order the compute already uses: the combined relativity multiplies the increase rated premium once, before the increase deduction is subtracted.
- R3-B: P6's scoped overwrite will name the limits-decrease case.

## Round 4 — what was done (scored values live only in the task files)
- R3-A: one clause of P6's combination sentence changed. The order is unchanged: replacements first, then the combined relativity, rounding last. The sentence now says the combined relativity "multiplies the increase rated premium once, before the increase deduction is subtracted". It names no factor quantity. The compute was already in that order, so no scored value moved, and the one compute_basis quote of the sentence is updated verbatim.
- R3-B: P6's overwrite of nonowner_premium_charging now has a scoped replaced_by, and the same sentence opens P6's rule. It states:
  - every package-change charge is booked as one additional-premium entry, its reason naming the direction (limits_increase for a move to a higher six-month base rate, limits_decrease for a lower one);
  - a move to a lower base rate whose charge is above zero (the DUI realignment) is charged as additional premium, not returned, and only such a move;
  - every other move to a lower base rate still returns unearned premium as a return-premium entry for the limits decrease, as the base event meaning says;
  - a reinstatement still re-writes premium under the reinstatement rule.
- R3-B tool change: the increase tool takes a direction argument with its own two values (higher_base_rate, lower_base_rate) and records reason limits_increase or limits_decrease from it. It no longer stamps limits_increase unconditionally. Task 1's gold call passes lower_base_rate (1180.00 -> 950.00), so the entry carries limits_decrease. The P4 prerequisite condition and task 1's closure edge read "reason limits_increase or limits_decrease".
- XF20: P4's wait stays non-zero, because task 1's increase charge is above zero, which is what makes it additional premium. No value changed.
- O3-6 (factual): task 1's final bill now splits its total the way the field meanings require: past_due_amount is the invoiced-and-unpaid amount (installment 3, NSF fee, late fee); premium_amount is the unbilled premium net of the return credit; fee_amount is the FR-44 filing fee not yet invoiced. The minimum_due total is unchanged and no rule reads these fields. Task 0 was not touched.
- O3-7 (factual): the wording in rework_r3_claims.md is corrected. Task 0's round-3 values differ from revision_2; they did not move when the P1 method tiers changed afterwards.
- O3-3 (P3's stored re-rated premium is unused by any charge): not a factual error. The tool stores the re-rated full-term premium the rule defines, and P6 rates the remaining days independently. Left as is.
- O3-1, O3-2, O3-4, O3-5: not factual errors; carried. O3-2 is the returned-payment residual risk already disclosed.
- Sweeps:
  - Every compute_basis quote, replaced_by, policy_source and baseline is verbatim in its rule (0 misses).
  - Base copy lines 1-1889 are identical to the blueprint.
  - Only P6 (overwrite, rule, one basis quote) and P4 (one prerequisite condition) changed in the charter.
  - Every rule quote in the task-file traces was re-checked.
  - task_tools.py contains no forbidden substrings.

## Final gate block, round 4 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 43/43 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK (history_rows_max=9, branches_max=199) · GROUNDING OK · SCOPE OK

REWORK round 4: gates 7/7 green

# ROUND 5 (rework) — renderer pre-render scan audits/render_source/nonowner_policies_and_renewals/render_r1.md (F1, F2, F3)
## Plan (before edits)
- Minimal source-side edits.
- revision_4 passed everything, so no task world changes.
- Every combination sentence keeps its order.
- Each class is closed across all six policies.

## Round 5 — what was done (scored values live only in the task files)
- **F1 (scope sentence names another policy and a factor):**
  - Deleted the clause ", as when the package re-rate rule's DUI realignment brings a filer class and other relativities onto the remaining days," from P6's rule and from its overwrite replaced_by. The operative test "whose increase charge by this rule is above zero" stays.
  - Class sweep over every rule: no other scope or overwrite sentence names another extended policy's action or a factor quantity. P6's "a reinstatement still re-writes premium under the reinstatement rule" restates the retired base clause on nonowner_reinstatement.
- **F2 (P2 unearned days can go to zero or below):**
  - unearned_days is now MX(0, ...) in compute. The rule adds "in every case the unearned days are never fewer than zero" to the run-off sentence.
  - The booking sentence now reads "when the unearned days come to zero nothing is returned and the cancellation books no return entry; otherwise the return is booked as one return entry ...". This is a record test, not a 0.00 row.
  - The user cancellation tool still cancels the term, but creates the return-premium entry only for an amount above zero. Its docstring states the zero case, so no 0.00 line is ever posted.
  - Class sweep of every other day count and amount:
    - P1 days in force: positive, because the late window is at most 5 days.
    - P5 per-day, certified-days and flat amounts: at least 0; a missing return books nothing (unreachable).
    - P3 days run and remaining: at least 0.
    - P4 window share: floored at 0.
    - P6: MX(0) with a 15-day minimum; nil books nothing.
- **F3 (binding placement, XF1):**
  - The `*_fr44_through` and `*_sr22_through` bindings of P1, P3, P4 and P6 are removed. Their required-through reads are now inlined, as an and/or chain in the same status order (requested, then filed, then rejected), in the `*_fr44_active` and `*_sr22_active` bindings of the filer-class factor that alone uses them. Semantics are identical, which the probes confirm. No rule text changed.
  - `request_reason` is moved into P2's requirement_relief factor bindings.
  - `offer_window_left` is taken out of P4's offer_lapse_window factor. It is now a plain binding that the standard figure defines, and its compute_basis quotes that standard sentence. offer_window_share reads the window span itself.
  - Class sweep: every remaining plain binding read by a single factor is that factor's baseline quantity (late_standard_share, standard_unearned_days, offer_lapse_value, offer_window_left, written_on_term). No factor baseline reads another factor's binding.
- **Sweeps:**
  - Every compute_basis quote, replaced_by, policy_source and baseline is verbatim in its rule (0 misses), and every binding has a basis and is defined before use.
  - Base lines 1-1889 are identical to the blueprint.
  - Task worlds and all scored values are unchanged: replay reordered db_closure keys only.
  - Proof-text quotes in both tasks were re-checked against the rules.
  - task_tools.py contains no forbidden substrings.

## Probe table, round 5 (scratch, compute harness of check_compute + real tool bodies)
| probe | outcome |
|---|---|
| P2 task 0 gold | gold unchanged |
| P2 SR-22 on file, 9 days left | unearned days floored at 0 -> return 0, nothing booked |
| P2 SR-22 on file, 13 days left (= SR-26 3 + run-off 10) | 0 (boundary) |
| P2 SR-22 on file, 14 days left | positive return (1 unearned day) |
| P2 SR-26 sent, certificate end after expiration | 0 |
| cancel tool with zero amount | term cancelled; no return entry created; net written unchanged |
| P3 task 1 gold | gold unchanged |
| P3 FR-44 required-through before today | filer class none |
| P3 FR-44 required-through not recorded | FR-44 class (gold) |
| P3 requested FR-44 expired + filed FR-44 live | requested read first -> none (same as before the inlining) |
| P3 FR-44 only withdrawn | realignment not due -> term premium kept |
| P4 task 1 gold (window share read from the span) | gold unchanged |

## Final gate block, round 5 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 43/43 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK (history_rows_max=9, branches_max=212) · GROUNDING OK · SCOPE OK

REWORK round 5: gates 7/7 green

# ROUND 6 (rework) — audit revision_5 item R5-A (XF26) — task 1 PASS untouched
## Plan (before edits)
- Rebuild P1 on the renewal term's recorded full-term premium (the renewal offer) as its standard figure.
- Every factor must carry a change since the offer's issue date, or the transaction's own method.
- P1 stays at 5 factors, all point-23 keys.
- Change task 0's world only where a factor needs an event after the offer date.
- Task 1 and every combination sentence keep their order and content.

## Round 6 — what was done (scored values live only in the task files)
- **P1 standard figure:** the late-renewal rated premium is now the recorded full-term premium "the premium its renewal offer was issued at and rated on the records of the offer's issue date, the renewal term's opened date". The rate table, state factor and points class are removed from P1 (rule, compute and params), and the baseline is the recorded premium times the standard per-day share.
- **P1 factors (5).** Point-23 keys only, each acting on what the recorded premium does not embed:
  - **late_filer_change:** an Operator requirement now counted that was requested after the issue date adds its class (same selection sentence as before). A certificate of the offer's that had its SR-26 sent after the issue date removes its class. The change is the added class over the removed class; a requirement requested on or before the issue date is already in the recorded premium.
  - **late_lapse_relativity:** the renewal term's own lapse, which is new at the late acceptance. Unchanged.
  - **late_return_change:** applies when the latest returned payment posted after the issue date. The recorded premium is taken to carry the relativity of one fewer return: one gives 1.04, two give 1.08/1.04, three or more give none.
  - **late_plan_change:** the renewal plan's credit divided by the credit of the expiring term's plan, which is the plan the offer was rated with.
  - **late_charging_basis:** the transaction's own exposure method. Unchanged.
- The combination sentence is kept word for word and in order.
- **Multi-source:** the filer-change bindings test FR-44/SR-22 status together with policy dates and points on every branch (no single-source IfExp), so task 0 keeps a multi-source factor.
- **Task 0 world (only what the factors need):**
  - **SR-22 transfer:** the carrier transfer is now requested on 2026-09-15, after the 2026-09-10 offer, and filed 2026-09-16. Story: she came off her mother's car policy, whose carrier sends its own SR-26. The withdrawn duplicate and the fees move to the same day.
  - **Returned payment:** the 2026-09-10 bank payment for installment 5 was returned on 2026-09-14 (NSF fee 25.00). She repaid on 2026-09-15 by debit card, together with the SR-22 filing fee. This second return in 12 months restricted every open plan to certified funds that day, which fits the renewal payment by debit card on 2026-10-12.
  - **Invoice 2:** goes back to its 9.00 fee, and its payments are re-tied to that.
  - **Recorded offer premium:** re-derived on the 2026-09-10 records (the June return; no requirement then; Six-Pay credit none). The renewal bill, renewal payment and plan 2 follow it.
  - **Ledger check:** plan 1 still balances to zero.
  - **Persona:** mentions the September transfer, and the payment history only when asked.
- **XF26 check on task 0:** reading the recorded premium and applying lapse and plan alone no longer gives gold (the rationale states the figure); every P1 factor moves gold.
- **Class pass over the other policies:**
  - P2 reads no recorded premium figure that embeds its retention factors.
  - P3 acts on a binding-time premium that carried none of its factors.
  - P5 acts on the return derived from that premium.
  - P4 and P6 read a package and premium the same task writes; auditor observation O5-2 notes these are not a usable embedded figure.
  - No other member.
- **Sweeps:**
  - Every compute_basis quote, replaced_by, policy_source and baseline is verbatim in its rule, and every binding has a basis and is defined before use.
  - Base lines 1-1889 are identical.
  - Task 1 is byte-equivalent except db_closure order.
  - Task 0's proof text, tier labels and quotes were re-checked; P2's two paraphrased tier labels are corrected to the exact ladder text.
- **Disclosed:** the SR-22 filing fee requested on 2026-09-15 is charged to the backing term's plan and paid with the same-day repayment, because that plan issues no later invoice.

## Probe table, round 6 (P1 on task 0's world; compute harness of check_compute + real tool bodies)
| probe | outcome |
|---|---|
| gold | filer change 1.15, return change 1.08/1.04, plan change 0.94, lapse 1.06, share 1 |
| SR-22 requested 2026-09-01 or on the issue date | filer change none (already in the recorded premium) |
| May SR-22 released, SR-26 after the issue date | filer change 1/1.15; charging basis falls to per-day (no filed certificate) |
| May SR-22 released + new SR-22 requested after issue | filer change 1.0 (class over class) |
| released certificate whose through date fell before the renewal start | filer change none (the offer never carried it) |
| only the withdrawn duplicate | filer change none |
| latest return before the issue date | return change none |
| three returns, latest after issue | return change none (1.08 both counts) |
| one return, after issue | return change 1.04 |
| renewal plan the same as the expiring plan | plan change none |
| expiring Paid-in-Full -> renewal Six-Pay | plan change 1/0.94 |
| no prior term id | offer credit 1.00 (no plan read) |

## Final gate block, round 6 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 46/46 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK

REWORK round 6: gates 7/7 green

# ROUND 7 (rework) — audit revision_6 item R6-A (charter: P1 returned-payment change not exact)
## Finding and route
- R6-A: P1's returned-payment change assumed the recorded offer premium carried one fewer return than today's twelve-month window holds. That is wrong when an old return ages out (double charge) and when two returns post after the offer (under-charge).
- An exact now ÷ offer needs the number of returns in the offer's own window (the twelve whole months before the issue date). The compute DSL cannot count that:
  - XCOUNT/XSUM windows are anchored at the processing date;
  - their filters are exact values only;
  - XLATEST yields only the single latest row.
- No equivalent exact record test exists in the records:
  - the renewal plan opens at the issue date, and a returned renewal down payment voids the term;
  - the expiring plan mixes returns from before and after the offer;
  - certified-funds flags carry no date.
- Route taken: removing beats adding (XF22). The returned-payment change is struck from P1, so P1 now has rule words and compute that are identical and exact.
- The draw lets the author assign the counts, so task 0's factor_counts [5,4] now go return 5, late-renewal 4. The return gains one point-23 dimension applied to a short-rate return (XF23 names exactly this pairing): the plan multiplier of the retention, read from the term's billing plan, with the company's relativities Paid-in-Full 0.80, Monthly EFT/Card Autopay 0.90, other none.
- Every combination sentence keeps its wording and order. P2's sentence ("every retention multiplier is multiplied into the package's retention percentage before the reduction is taken") already covers the new multiplier.

## Round 7 — what was done (scored values live only in the task files)
- **P1:** removed the returned-payment change from the rule, compute, compute_basis and factors. The billing-transaction history declaration and the NSF params are gone. The billing cross-category entry now reads the plans only.
- **P1 factors (4):**
  - filer change;
  - the renewal term's lapse;
  - plan change;
  - charging basis.
  Each acts only on what the recorded offer premium does not embed (XF26 holds).
- **P2:** the plan-multiplier sentence is inserted before the run-off sentence. Compute adds cancel_billing_plan (a factor binding) and plan_retention_scale into retention_pct. billing is declared in cross_category and inputs.
- **P2 factors (5):**
  - requirement relief;
  - elapsed term;
  - term origin;
  - plan multiplier;
  - run-off method.
- **Task 0:**
  - The world is unchanged. The September return stays as seeded history: it explains the certified-funds restriction, and no rule re-rates payment history after the offer.
  - Scored values moved because the fix requires it: the written premium loses the returned-payment change, and the return gains the plan multiplier.
  - Traces, computations, gold effects, closure texts, read necessities and the rationale are rebuilt from the harness.
- **Task 1:** untouched (db_closure order only).
- **Sweeps:**
  - Every compute_basis quote, replaced_by, policy_source and baseline is verbatim in its rule.
  - Every K() is declared in params, and every binding has a basis and is defined before use.
  - There are no XF1 cross-reads.
  - Base lines 1-1889 are identical.
  - There is no stale returned-payment-change text or old figure in task 0.
- **Class pass:** no other policy prices a change against a count it assumes the embedded figure carries. P3, P4, P5 and P6 count today's window against premiums that carry no returned-payment relativity (binding-time or freshly rated).

## Probe table, round 7 (compute harness of check_compute + real tool bodies, task 0 world)
| probe | outcome |
|---|---|
| P1 gold | unchanged by any returned payment |
| P1 aged-out world (June return moved to 2025-09-20) | same as gold: no double charge |
| P1 two-post-offer world (second return 2026-10-01) | same as gold: no count assumption left |
| P1 no returns at all | same as gold |
| P2 gold (Paid-in-Full) | plan multiplier 0.80 |
| P2 renewal plan Monthly EFT | multiplier 0.90 |
| P2 renewal plan Six-Pay | none |
| P2 decoy: expiring term's plan Paid-in-Full, renewal Six-Pay | none (reads the term's own plan) |
| P2 no billing plan on the term | none |

## Final gate block, round 7 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 46/46 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK

REWORK round 7: gates 7/7 green

# ROUND 8 (rework) — renderer second scan audits/render_source/nonowner_policies_and_renewals/render_r2.md (F4, F5)
## Round 8 — what was done (no scored value moves)
- **F4 (unused params):**
  - Deleted from nonowner_ext_late_renewal_written: lapse_window_months, nonpay_recent_months, nonpay_window_months, rel_nonpay_recent, rel_nonpay_later.
  - Deleted from nonowner_ext_reinstatement_rewritten: lapse_window_months.
  - Class sweep over all six policies: every K()/P() in compute, ladders and factor baselines checked against params; no other unused param.
  - Every binding is read by another binding, by result, or by a ladder or factor baseline; no unused binding.
  - P2's baseline names the package variant parameter insured_cancel_short_rate_retention_pct, read by P() (not a policy param).
- **F5 (filer reading order):** the four filer readings now state the order exactly as the compute does: late_filer_change (P1), rerate_filer_class (P3), offer_filer_class (P4) and increase_filer_class (P6). Each now reads "for each form the filing read is its requested filing, otherwise its filed one, otherwise its rejected one, the one recorded first within a status, and that filing counts when its required-through date is on or after <date> or is not recorded, no other filing of the form being read when it does not; when both forms count the FR-44 one counts".
- **F5, late_released_form (P1):** the certificate-release clause now states:
  - the FR-44 form is tested before the SR-22 form;
  - per form, the first-recorded cancellation_filed filing is read, then the first-recorded terminated filing when the first does not qualify;
  - a read certificate qualifies when all three conditions hold: requested on or before the issue date, required-through on or after the renewal term's effective date (or not recorded), and SR-26 date after the issue date.
- **Compute and tasks:** no compute line changed, and both task files are identical in content (replay reorders db_closure only). compute_basis quotes of the changed sentences are updated verbatim.
- **Sweeps:**
  - Every basis quote, replaced_by, policy_source and baseline is verbatim in its rule.
  - Every K() is declared.
  - Base lines 1-1889 are identical.
  - No task text quotes the old wording.

## Final gate block, round 8 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 46/46 match; 1.json 19 acts 40/40 match) · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK

REWORK round 8: gates 7/7 green

# ROUND 9 (rework) — cross-product KB re-judge revision_2: S1–S4 (policy_kb + runtime_context)
## Route
- **S1 (task 1, scored).** The seeded FR-44 was still filed with no SR-26, although its backing term was cancelled and reinstated with a lapse. The published fr rules (doc_fr_lapse_sr26_transmission_f48c5bcb; doc_fr_sr26_notice_terms_5a921652) make a lapse SR-26 owed for that case.
- **Seed-only route tried first.** The SR-26 is sent inside its window and a reinstatement refiling is filed on the reinstated term. This makes every filer reading take the refiling, so P3, P4 and P6 keep their figures. But P5's exposure method read only certificates "on file (status filed)". After a realistic lapse SR-26 no such certificate predates the lapse, so P5's method would fall to the per-day baseline and stop bearing weight on the drawn 4-factor re-write. The seed-only route therefore cannot keep the design.
- **Fallback taken (coordinator's d3 class, scoped to the certificate reads it concerns).**
  - The two exposure methods now read the certificate's standing during the lapse: P5 rewrite_exposure_basis, and P1 late_charging_basis for the same class.
  - The FR-44 form is read before the SR-22 form.
  - For each form, the filings tried are, in order, the first-recorded filed, cancellation_filed and terminated filing; the first whose filing date is on or before the first lapse day is read.
  - Its certified-through date is the earlier of its required-through and certificate end dates. The same flat / certified-days / per-day tiers apply on that date.
  - With this, the realistic re-seed keeps every scored value.
  - The filer-class readings (status requested, filed or rejected) are unchanged; the refiling is the requirement they count.
- **Hashes:** nonowner.extended.yaml changed (63b0174b -> 53a9ceec); the nonowner docs must be re-rendered for the two method sentences and ladders. task_tools.py is unchanged (66fd633c).

## Task 1 re-seed (fr and billing rows re-priced with their owning docs)
- **First FR-44 (fr):**
  - Requested 2026-09-21 and filed 2026-09-22 while the term was in force; the notice came on 2026-09-25 (S2).
  - Effective 2026-09-21, required through 2029-09-21. Fee 35.00, billed on installment 4's draft notice.
- **Lapse SR-26 (fr):**
  - Transmitted 2026-10-12, inside its window (lapse start + 3), reason policy_cancelled.
  - Lapse run-off 13: a 4-day lapse is counted from the lapse start (10 - 2 = 8), plus Operator on a non-owner term 1, Virginia 4, same state 0, term form none 0.
  - Certificate end 2026-10-25; status cancellation_filed.
- **Reinstatement refiling (fr):**
  - Ordered by the insured 2026-10-14 and filed 2026-10-15. It carries over form, state, case number and required-through, and names the first filing as replaced.
  - Fee 26.00: the replaced certificate was still certified on the refiling date, so half the flat fee rounded up gives 13; plus restoration 5.00, Operator/non-owner 2.00, Virginia 6.00, other charges 0. Charged to the plan.
- **Withdrawn duplicate:** moved to 2026-09-21.
- **Billing calendar (S3):**
  - Installment 1 due 2026-07-02 (one month after the effective date), invoiced 20 days before, paid late 2026-07-09 (late fee 07-08, notice 07-07 rescinded).
  - On 2026-07-10 the plan switched to Monthly EFT (authorization that day) and the due day moved 2 -> 12. That is one change, 10 days of shift, requested 23 days ahead, with the plan current.
  - Draft notices are issued 10 days before each due date. Installment 3 was drafted 2026-09-14 (the due date fell on a Saturday) and returned 2026-09-16 with the NSF fee; late fee 2026-09-18.
  - The notice of 2026-09-25 shows minimum 266.16.
  - Installment 4's notice of 2026-10-02 bills premium, fee, the FR-44 fee and the past-due amount; it fell due inside the lapse and is carried to the next invoice.
  - The final bill covers the balance after the return credit. The reinstatement payment of 266.16 reactivates the plan.
- **Scored values:** recomputed with the harness, all identical (re-write, re-rate, increase, offer, every baseline and every sensitivity).
- **GT note fixed:** the claim "no SR-26 because the term was reinstated before one was due" is gone. Proof, objective, seed, closure and rationale text are swept; the filer evidence paths now name the refiling.
- **Task 0 (S4):** the Paid-in-Full plan's status is now paid_in_full (credit balance, nothing left to bill). No rule reads it, and no value changed. Task 0's charging-basis tier label and trace now use the certified-through wording.

## Probe table, round 9 (P5 on task 1's world, harness)
| probe | outcome |
|---|---|
| gold: first FR-44 cancellation_filed, certificate end 2026-10-25 | flat |
| certificate end inside the lapse (2026-10-11) | certified-days (two lapse days not re-written) |
| certificate end = last lapse day | flat |
| certificate end before the lapse | per-day |
| first FR-44 terminated (end 2026-10-25) | flat |
| first FR-44 absent (only the post-lapse refiling) | per-day |
| first FR-44 filed after the first lapse day | per-day |
| first FR-44 still filed, no SR-26 | flat (unchanged behaviour) |
| FR-44s fail the date test, SR-22 filed earlier through 2026-10-12 | certified-days on the SR-22 |

## Final gate block, round 9 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK

REWORK round 9: gates 7/7 green

# ROUND 10 (rework, seed-only) — KB re-judge revision_3 notes N1, N2 (task 1)
- **N1 (SR-26 kind and end date):** first FR-44 c236… had its SR-26 sent on 2026-10-12. On that date the term was cancelled (2026-10-10) and not yet reinstated, so it is a cancellation SR-26 (fr cancellation_sr26_transmission: reason policy_cancelled, window closed date + 3 days).
  - The cancellation run-off is now priced by the cancellation schedule:
    - Nonpayment: 2 days from the closed date to the SR-26 date, within the 250/500/100 package's 30-day reinstatement window, so the larger of 10 and 30 - 2 gives 28.
    - Add Operator on a non-owner term 1, Virginia 4 and filing state = residence 0, for 33 days in total.
  - The certificate end date becomes 2026-11-14 (was 2026-10-25, priced with the lapse schedule).
  - The reinstatement with lapse came after that SR-26, so the certificate was not revived and no further SR-26 is owed.
  - The refiling fee is unchanged at 26.00: the replaced certificate is still certified on the refiling date, so the half-fee basis holds.
  - The re-write stays flat: certified-through 2026-11-14 is after the last lapse day.
- **N2 (final bill):** final bill 1d27… is split by field meaning:
  - past_due_amount 266.16: installment 3, its NSF fee and late fee, the only amount past due on 2026-10-11;
  - premium_amount 43.15: installment 4's premium plus the unbilled last installment, less the 411.19 return credit;
  - fee_amount 39.00: installment 4's already-charged installment fee plus the FR-44 filing fee it billed; no new installment fee.
  The minimum due is unchanged at 348.31. The 266.16 reinstatement payment pays every past-due amount, as the nonowner reinstatement rule requires.
- **Gold:** unchanged. Every computation expected value, baseline and sensitivity is equal, and so is every gold argument; the gates' compute match confirms it.
- **Text sweep:** the rationale, objective and trace wording (lapse SR-26 -> cancellation SR-26, end date, final-bill split) is updated, and no stale "lapse SR-26" or "2026-10-25" remains.
- **Hashes:** nonowner.extended.yaml 53a9ceec84691dd3 and task_tools.py 66fd633c4fb7a3df are byte-identical (unchanged).

## Final gate block, round 10 (difficulty-level, no --task)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK (0.json 15 acts 46/46 match; 1.json 19 acts 43/43 match) · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK

REWORK round 10: gates 7/7 green
