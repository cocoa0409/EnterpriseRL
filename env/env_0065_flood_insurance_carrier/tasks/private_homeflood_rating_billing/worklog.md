# worklog private_homeflood_rating_billing (env_0065) M=2
draw (draw_counts.py --tasks 2): T0 prerequisite_problems=3 factor_counts=[6,6,4,6]; T1 prerequisite_problems=1 factor_counts=[5,5]
scratch: /tmp/private_homeflood_rating_billing_0065 (generators p1..p4.py, gen_ext.py)

## T0 (renewal held pending certificate review)
Problems: homeflood_ext_certificate_rerate (6, agent) -> homeflood_ext_rerate_credit (4, agent) -> homeflood_ext_renewal_booking (6, agent) -> ROOT homeflood_ext_installment_payment (6, user)
Edges: rerate_credit<-certificate_rerate (value_input new_premium); renewal_booking<-certificate_rerate (value_input cert_prem); renewal_booking<-rerate_credit (state_gate);
       installment_payment<-renewal_booking (value_input term_item); installment_payment<-rerate_credit (value_input closed_credit)
Tools: apply_certificate_review_8d563756, book_rerate_credit_70dc8da2, book_renewal_term_27983a73, pay_installment_4d782e9d (owner=user)
- extended policies T0 written (frag/10..40) 
## T1 (sale) planned: homeflood_ext_sale_cancellation (5) -> ROOT homeflood_ext_final_payment (5, user)
- task_tools.py T0 (4 tools) -> TASK TOOL CONTRACT OK (fixed: not_found receipts had to describe homeflood_policy_id)
- tasks/0.json written (scratch build0*.py). Gate fixes: D prereq sentence carried code token TERM_PREMIUM -> "term premium item"; replay MISMATCH (4 unread excess_billing rows) -> rows dropped;
  compute: certificate_rerate history not load-bearing when zeroed (NFIP 2017 paid claim kept loss tier fixed) -> NFIP paid claim moved to 2012-06-25 (outside 120 months);
  rerate_credit cross reads had no seeded dwelling_changes rows and were not load-bearing -> rerate_credit reworked to read only HomeFlood certificate entries (cross_category []).
- T0 per-task gates: extended OK, task_tools OK, replay OK, solvability OK, compute OK, grounding OK, cross_fire OK; traceability: only the 4 unlock tool-name misses (docs unpublished).
- T0 values: 1373.62 / 113.35 / 1256.86 / 111.43; baselines 2138.12 / 102.54 / 1928.81 / 257.37. Probe table in tasks/0.json design_rationale §8.
## T1 (sale) — homeflood_ext_sale_cancellation (5, agent process_cancellation_request_bf9010ee) -> ROOT homeflood_ext_closing_payment (5, user pay_closing_balance_b53536cf)
- policies frag/50,60 written; tools appended; TASK TOOL CONTRACT OK (6 tools). closing payment tool marks the closed account settled (balance 0) because late charge/courtesies are not booked as items.
- sim: E 289.23 (baseline 469.82; factors 262.06/297.95/560.97/271.73/254.23); F 290.84 (baseline 327.90; 278.62/296.84/294.12/315.84/305.84); skip E -> F 583.35
- tasks/1.json written; T1 per-task gates all OK (extended, task_tools, replay, solvability, compute, grounding, cross_fire). Probe table in tasks/1.json design_rationale §8.

## Final gate block (difficulty-wide, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (0.json 17 acts det nonvac match; 1.json 12 acts match) | SOLVABILITY OK (gates 11 / 7, seed rows 21 / 15)
COMPUTE OK (suite means branches=66.00 steps=14.50; history_rows_max=29; branches_max=104) | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO (optional)
check_traceability: NOT OK only for the 6 unlock tool-name misses (KB not yet published): apply_certificate_review_8d563756, book_rerate_credit_70dc8da2,
  book_renewal_term_27983a73, pay_installment_4d782e9d (0.json); process_cancellation_request_bf9010ee, pay_closing_balance_b53536cf (1.json). No other id/value miss.
Coverage: 6 extended policies, T0 {certificate_rerate, rerate_credit, renewal_booking, installment_payment}, T1 {sale_cancellation, closing_payment}; disjoint.
Known risks for audit: several factor ladders are Tidemark-own schedules declared through overwrite (aging foot, vent split, layer split, occupancy, NFIP transfer, review delay,
  first-certificate, renewal booking adjustments, installment pay-ahead/booking-delay/Excess paid-up, claim share, exit fee, closing courtesies); first-match CFIELD reads assume
  one NFIP record and one Excess policy per address.
ROUND 1: gates 8/8 green

## REWORK round 2 claims
- F1 (= T1-P1): cancellation rule now scopes the paid-claim share to the premium return (term-premium and loss-of-use parts) and fixes the assembly order in one generic sentence (shares/percents first on the part they name, then amounts added/taken off, one rounding, floor zero); compute unchanged and now matches the only reading. Class A3 swept: the other five assembly sentences are order-explicit or purely additive.
- F2 (= T0-T1): undefined date anchors defined in every rule: re-rating date (certificate rule: day the review is completed and recorded, explicitly not the receipt date or term start), booking date (renewal), payment date (installment, closing payment), processing date (cancellation); compute_basis of every window/tenure binding quotes the definition (class B11).
- F3 (= T0-C2): installment rule defines the installment's term as the term of the latest installment-1 payment; all installment bindings read that term (new plain binding); declared condition/effect rewritten to the same object; condition false at the opening and term_item 0.00 -> booked figure; booking-delay guard for an unbooked term added and stated.
- F4 (= T0-C1): both RERATE-credit prerequisite sentences now quantify over certificate entries received during the expiring / an earlier term, save one kept on file with a re-rated premium recorded; conditions rewritten; unmet at the opening for the 2026-07-20 entry (class C13).
- T0-T2 (a) pro rata proof text corrected; (b) 'no NFIP record' probe text corrected (claims-free tier); (c) seed claim payment re-derived with the base settlement rule (ACV, deductible in force on the date of loss) and seed_consistency text rewritten (class E15).
- T1-T1: seed claim payment re-derived with the base settlement rule (ACV less deductible), proof of loss aligned, seed_consistency rewritten.
- O1: new-home courtesy reads only NFIP policies in force; other first-match reads (one NFIP record / one Excess per address) documented with decoy probes in the rationales.
- O2: early-renewal credit reads the coming term's installment-1 payment, stated in the rule.
- O3: earlier-term credit stated as the earlier terms taken together (matches compute).
- O4: overdue-installment wording matches compute (latest installment fee booked, when unpaid).
- O5: flood-vent credit requires a certificate accepted for rating (compute and ladder); probe recorded.
- O6, O7: not changed (observations; declared tails cover the replaced chains; realism doubts kept as company schedules).
- Proof sweep (class F17): closure edges re-copied from policy fields, why_false/flips/edge_load_bearing recomputed (installment skip-renewal effect now 0.00), traces, tracing, read-node text, seed checks and rationale updated; all scored values and factor_sensitivity figures recomputed unchanged.
Probe table (decoys): older decoy certificate entry -> latest used; no certificate / no NFIP / no Excess / Excess closed after or effective after term start / aged and over-age certificate / no BFE (task 0 rationale); WITHDRAWN decoy request, sale without statement, no claim, flat cancellation, new policy, no new-home NFIP, installment paid (task 1 rationale).
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: only the 6 unlock tool-name misses.
REWORK round 2: gates 8/8 green

## REWORK round 3 claims
- M1: paid-claim share no-return tier now requires net payments above zero and measures the threshold against the dwelling and personal property limits together (rule, compute, ladder); probe: a Renters policy with no claim gets the whole premium return.
- M2: every overwrite tail charter-wide (13 replaced_by: certificate re-rate x6, re-rate credit, renewal booking, installment, cancellation x3, closing payment) now restates the still-in-force base content for out-of-scope cases instead of deferring to "the base rule"; the cancellation fee-earned and paid-claim-bar replacements carry their own "only for a cancellation credit worked out under this rule" scope; sibling fee-earned overwrites (cancellation, closing payment) each name the other's exception (sold or replaced home; policy-fee return). No overwrite retires nothing.
- M3: household credit reworked to existence tiers (in-force NFIP on a non-primary residence, plus active Excess at the HomeFlood address), no first-match pick; new-home courtesy reads the unique in-force primary-residence NFIP policy, then tests the address; decoy probe (in-force NFIP at the sold address listed first) leaves the courtesy unchanged.
- M4: overdue-fee waiver states the negative-gap case (installment due after the effective date: full fee back, any reason) and requires an on-or-before due date for the sale/replacement tiers; an installment's due date is defined as its installment-fee posting date; probe recorded.
- M5: review completion defined as the day the re-rate credit is booked (rule and basis).
- M6: pay-ahead month count stated exactly as computed (whole months from the term start less the previous due-month offset); absent first payment tier stated.
- Lower (wording): deposit difference rephrased as payment less the sum of policy_fee and the down share.
- Lower (ties): same-day tie-break (first recorded counts) stated in every rule and quoted by every LATEST binding; "another, earlier" certificate entry reworded to "another" entry.
- Lower (placement): single-factor definitions moved into their factors (loss history: NFIP id and re-rating date; credit start: survey date; pay-ahead: previous-due offset; earning basis: request reason and document; loyalty: NFIP-record definition); shared ones stay plain.
- XF 8-14 sweep: rounding mode stated (nearest cent, halves to even) in every rule and probed (no scored value at a tie; half-up agrees); compute_basis quotes re-checked verbatim by scratch script (0 misses); months/days wording re-checked against MONTHS()/DAYS() use; absent-record guards added (renewal first payment, installment first payment).
- Proof sweep: task rationales, factor traces, tier_taken texts, tracing and read-node necessity updated; all scored values and factor_sensitivity figures recomputed unchanged.
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: only the 6 unlock tool-name misses.
REWORK round 3: gates 8/8 green

## REWORK round 4 claims
- R3-1: the cancellation rule's fee-earned exception now enumerates, in the closing payment rule's own tier words, every case of the closing payment's overdue-fee give-back (full fee: installment due after the effective date for any reason, or sale with a settlement statement within the window; half: replacement with the replacing declarations within the window); the closing payment's tail still names the cancellation's policy-fee return; the two sibling texts agree on the same cases.
- R3-3: every first-record-by-address read given an exact scope — certificate re-rate NFIP record (loss history, occupancy, transfer) and renewal loyalty NFIP record read by the replaced NFIP policy number (rule defines the record as the NFIP policy this HomeFlood policy replaced; none when it replaced none); certificate re-rate layer credit and installment Excess paid-up credit read the Excess Flood policy in status active at the address, unique under the Excess charter's one-live-policy rule (rule says so); transfer factor no longer re-tests the number; layer sentence's closed-after-term-start branch removed with its tail still restating the base package rule.
- T1-R3-1: task-1 claim-share tier_taken, near-miss line and policy read-node objective/necessity now name the dwelling and personal property limits together.
- Class sweep (C12 reads): request on file stated as the latest signed request (withdrawn/unsigned never count) in cancellation and closing payment; installment deposit stated as the payments received as installment 1; early-renewal credit stated as the latest installment-1 payment of the coming term.
- Adversarial probe sweep over every read at every handling time (cancelled earlier Excess listed first, second in-force NFIP at the HomeFlood address listed first, cancelled primary NFIP elsewhere, same-day second certificate recorded after, paid-then-voided payment on a new claim, older renewal offer, withdrawn newer request): rule words and compute give the same single answer in every case; recorded in both rationales.
- render_r1 re-verification: M1-M6 and the lower-severity items remain closed (rules, compute and ladders unchanged apart from the scoped reads above); compute_basis/replaced_by/policy_source/baseline verbatim sweep 0 misses.
- Proof sweep: task-0 probe text for a closed Excess updated; both rationales carry a round-4 note; all scored values and factor_sensitivity figures recomputed unchanged.
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: only the 6 unlock tool-name misses.
REWORK round 4: gates 8/8 green

## REWORK round 5 claims
- S1: certificate re-rate now declares the overwrite of the base rating clause on the credit-percent reduction (replaced by the re-rate's own credit assembly, whose tail restates both base steps for every other rating); the baseline states that the credit percent recorded on the policy for the term is not carried into the re-rating (one reading of credits_applied_pct; K1 co-cause).
- S2: "Excess Flood charter" replaced by "Excess Flood program" in the certificate re-rate and installment rules; no authoring vocabulary left in any rule (scripted check).
- S3: re-rate acceptance rests on recorded fields (survey and receipt dates); the FEMA form, seal and no-alteration conditions are stated as the condition for recording an entry at all, with the base acceptance restated for every other use.
- S4: renewal autopay and installment autopay-fee ladders now say "one to three payments, every one by ACH" (zero payments fall through), matching the compute.
- S5: the cancellation rule's fee sentence states only its own case (installment fees fully earned in the cancellation credit; base content for every other cancellation credit) and no longer embeds the closing payment's give-back ladder; the closing payment rule keeps its ladder and its tail.
- Coordinator principle (no incidental counts, rule = compute on every record set): the re-rate credit's count-keyed tiers were replaced by keys on the certificate under review (credit start: received before or within 30 days after the term start -> term start; mitigation-survey addition: openings certified, survey age at receipt); the fall source's first tier is the latest endorsement within the term (every entry carries the in-force premium); the credit is capped at the net premium booked for the term (stated; not binding here). Probes (older prior-term endorsement, mortgagee change after receipt, same-day second certificate) give the same single answer by rule and compute.
- K1-K7: render-side, left to the renderer (docs/ not edited); source co-causes of K1 (S1 + baseline sentence) and K6 (S5) closed.
- Proof sweep: task-0 traces, factor_sensitivity id/tier texts (vent_survey_addition), tracing, rationale and seed-check wording updated; task-1 rationale note; all scored values and factor_sensitivity figures recomputed unchanged.
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: TRACEABILITY OK (0 misses).
REWORK round 5: gates 8/8 green

## REWORK round 6 claims
- R5-1: re-rate credit fall source — "within the term" now bounded on both sides in rule, ladder and compute (on or after term_start and before term_end); probe: an endorsement recorded after term end falls to the renewal offer by rule and compute alike.
- T0-R5-1: task-0 fall_measure_source tier_taken corrected to the round-5/6 ladder wording; rationale note added; nothing else touched.
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: TRACEABILITY OK.
REWORK round 6: gates 8/8 green

## REWORK round 7 claims
- S6: task-0 Excess XF-3409126 re-seeded to the published Excess rules — term premium at the tier minimum the rate manual yields for this layer, zone and no certificate; effective date on the standalone 30-day wait from its application, renewal term dates moved with it; still effective before the HomeFlood term start, active, zero balance (no read moves).
- S7: task-0 NFIP condominium 3118840265 re-seeded — application date on the 30-day standard wait before its original effective date; ICC premium removed (ICC does not attach on the Residential Condominium Unit tier); only status and primary-residence flag are read.
- Observation (cross-category ledger history): not added — the replay closure rejects rows no read covers; the field-level states read remain reachable under the owning rules (recorded in the task-0 rationale).
- Proof sweep: task-0 read-node, trace, tracing and rationale text updated to the new Excess effective date; round-7 rationale note added; task 1 untouched.
- Seed-only constraint: homeflood.extended.yaml and task_tools.py sha256 equal to the coordinator freeze before and after.
Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO; check_traceability: TRACEABILITY OK.
REWORK round 7: gates 8/8 green
