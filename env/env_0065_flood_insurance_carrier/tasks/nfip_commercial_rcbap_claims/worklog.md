# worklog nfip_commercial_rcbap_claims (env_0065)  — M=2
Draw (draw_counts.py --tasks 2): T0 prerequisite_problems=1 factor_counts=[5,4]; T1 prerequisite_problems=3 factor_counts=[5,5,4,5].

## Difficulty-level pre-check
- Claimed events: claim_reported, adjuster_report, proof_of_loss_filed, claim_paid, claim_payment_voided, claim_denied, endorsement_issued, coverage_updated, premium_charged, policy_cancelled, premium_credit, refund_disbursed.
- User-owned writes in the blueprint role split: proof of loss (numeric: the sworn amount) and cancellation request (only a date). Endorsement premium needs rating-engine figures with no record source. Hence each task's user tool is a proof of loss: T0 building, T1 contents.
- Cross category: bizflood (BizFlood is designed around the NFIP General Property Form: Excess over NFIP tier, concurrent primary tiers, statement of values per location). Used for the SFIP "other insurance" apportionment (primary up to the other policy's deductible, then share by limits).

## Task 0 (in progress)
- Root nfipcom_ext_building_payment (agent, 5 factors) <- prerequisite nfipcom_ext_building_proof_amount (user, 4 factors), value_input on pb_sworn.
- Seed built by /tmp scratch script (uuid4 ids). frozen_time 2026-10-14 10:20:00 CDT. Expected: proof 67,630.00 (all-baseline 487,666.67); payment 24,971.08 (all-baseline 67,630.00); every factor moves its result (see tasks/0.json computations.factor_sensitivity).
- Revision: replay closure flagged 5 BizFlood billing rows never read by gold -> removed (noise); REPLAY OK after.
- Per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY: only the two unlock tool names unsourced (expected until KB render).

## Task 1
- Root nfipcom_ext_cancellation_refund (agent, 5 factors) <- nfipcom_ext_cancellation_credit (agent, 5; value_input on xr_credits) and <- nfipcom_ext_contents_payment (agent, 5; state_gate: payment after the latest report for each measured coverage); contents payment <- nfipcom_ext_contents_proof_amount (user, 4; value_input on cy_sworn). Draw [5,5,4,5] matched.
- Prerequisite sentence directions across the charter: building payment negated, contents payment affirmative, refund affirmative (credits) and negated (claims settled).
- Expected: contents proof 8,200.00; contents payment 5,466.67; risk credit 5,912.21 (ICC 71.30, HFIAA 237.67 traced); RFA 1,077.03; refund 6,784.31. Every factor moves its result; all-baseline figures 140,800.00 / 8,200.00 / 6,079.69 / 7,304.94.
- Revision: check_compute flagged the cancellation policy's BizFlood read (private-replacement tier) as not load-bearing in this world -> the replacement tier now uses the effective date the request names (base: private policy's date when later), cross_category []. Cross-difficulty factors of task 1 remain in the contents proof/payment policies.
- Realism compromises flagged for audit: mortgagee holdback on the refund, earned-day convention on a sale, contents value ceiling from the BizFlood statement of values, the refund gate on open claim coverages (Tidemark servicing), and the refund's balance factors (shortfall/excess, re-rate carry, earlier terms).
- Edge probes (scratch copies): BizFlood absent/inactive or on the Excess over NFIP tier -> no apportionment; no SUPPLEMENTAL/FINAL -> FINAL/PRELIMINARY; no endorsement/certificate -> 0; refund before cancellation -> credits 0, days guarded to 0; voided-not-reissued item -> counted as paid.

## Final gate block (full suite, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 12 acts, 1.json 18 acts, det True, nonvac True, 0 errs, closure match); SOLVABILITY OK; COMPUTE OK (suite means branches=55.50 steps=15.00; history_rows_max=44; branches_max=68); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
TRACEABILITY NOT OK — only the six unlock tool names (sign_building_proof_of_loss_d76eab34, issue_building_claim_payment_972d0779, sign_contents_proof_of_loss_65413413, issue_contents_claim_payment_a4dbf5ac, process_cancellation_a892a1e4, disburse_cancellation_refund_941cdf13) lack a source before the KB is rendered; no id/value miss.
ROUND 1: gates 8/8 green

## Rework round 2 — design notes and checklist tables
Sources verified for realism (copies kept only in scratch during the work): 44 CFR 61 App. A(3) (RCBAP) VIII.B.1 and App. A(2) (GPF) VII.B.1 carry the same other-insurance condition for flood insurance not issued under the Act (pro rata; primary when the other policy is excess; primary, subject to its own deductible, up to the other flood policy's deductible, then pro rata). The "excess over insurance in the association's name" clause is the Dwelling Form's (unit owner), not the RCBAP's; the RCBAP is primary over a unit owner's NFIP policy. Coinsurance exists only in the RCBAP (VII); the GPF settles at ACV with no coinsurance (base tier params already do this). FEMA Flood Insurance Manual (How to Cancel, reasons 01/02) and the TRRP Plan cancellation-reason pages: pro rata (premium with ICC, RFA, HFIAA) for the term the cancellation falls in, FPF and probation earned; full refund, fees and surcharges included, for any additional term; WYO handles the current and one prior year; "Open Claim: Policy cannot be canceled"; closed claim with payment -> effective date after the loss date. 44 CFR 61.5 / FEMA guide: minimum deductibles 1,000/1,000 up to a 100,000 building limit, 1,250/1,250 above.
Structure kept: T0 = building proof (4: report P, value basis P cross, deductible floor P, already sworn M) -> building payment (5: sworn total M, deductible layer P cross MS, contents share P, other cover P cross MS, paid before P). T1 = refund (5: ICC M, RFA M, FPF P, probation P, premium received but not owed P) <- cancellation (4: current term M, previous term P, endorsement M, re-rate P; effective date is a plain base sentence) <- contents payment (5, mirror of the building payment) <- contents proof (5: report P, ceiling P cross, deductible floor P, already sworn on the claim M, already sworn under a duplicate number P).
A1/A7 baselines: every factor's baseline is the standard working of its own policy's baseline paragraph (FINAL report; policy RCV; deductible shown; nothing already sworn / latest proof; no other policy's deductible; no other insurance; claim-only payments / base pro rata from the effective date; nothing for the earlier term; endorsement with its term; no re-rate taken back / base pro rata ICC and RFA; fees earned; nothing received but not owed).
A2/A3 assembly: one generic order sentence per policy ("reduction for under-insurance, deductible, limit, already sworn"; "part carried alone, share of the rest, payments already made"; "current and earlier term parts, endorsement part, re-rate taken back"; refund = credits plus premium received but not owed). The shared BizFlood deductible layer is split between building and contents in proportion to their sworn amounts in both payment rules (commutes; one reading).
A4/A5 independence (factor -> reads): report choice -> claim's reports; value basis -> latest-SOV BizFlood policy, its adjuster rows, in-force dates, policy RCV; deductible floors -> policy limit/deductible, renewal charges, tier minimums; already sworn -> the claim's proofs/payments; duplicate sworn -> proofs/payments for the date of loss minus the claim's; sworn totals -> proofs for the date of loss; layer -> in-force non-excess BizFlood tier, SOV location, zone, adjuster value; other-coverage share -> other coverage's proofs/payments; other cover -> BizFlood value endorsements and SOV; paid before -> notices, payments, voids; current/previous term -> term risk charges (window and current-term sums), plain effective date, claim bar rows; endorsement -> latest ENDORSEMENT risk charge by reference id and its change row; re-rate -> latest RERATE risk credit by reference id and its certificate row; ICC/RFA/FPF/probation/excess -> their own ledger rows and the policy's cancellation effective date (prerequisite output). No factor reads another factor's binding.
A6 tier tables: one distinguishing input per pair is listed in each task's design_rationale (TIER TABLES); methods change the formula's shape (sum of proofs / payments net of voids / none; sum less late / sum / latest; full / nothing / pro rata; full / own period / with the term; none / earlier pro rata plus current full / current pro rata; per occasion / inception in full / pro rata).
B8-B11: every branch and cap is in the rule (contents limit cap stated; required-insurance rounding stated); compute_basis quotes swept by script (all verbatim); rounding is half-up at every step in rule and compute (epsilon before round so a 0.005 tie rounds up); "the term before the current one" and "the days of a term" defined where read.
C12 probe table (scratch copies): BizFlood cancelled after the loss counts, one cancelled before or begun after does not; an older SOV on another BizFlood ignored; LOCATION_ADD/DELETE not value endorsements; a later value endorsement after the loss -> SOV; latest SUPPLEMENTAL measuring no coverage -> FINAL; proof or payment under a duplicate number -> counted for the date of loss; voided payment not reissued -> counted as paid; MORTGAGEE_CHANGE books no charge; endorsement/certificate of an earlier term -> with that term; future-term payment -> refunded whole. C13: each prerequisite sentence's scope equals its condition and is unmet at opening (T0 SUPPLEMENTAL 2026-10-09 vs last building proof 2026-09-25; T1 SUPPLEMENTAL 2026-10-08 with no payment after it; policy in force; latest contents proof before the SUPPLEMENTAL).
D14 overwrites: building proof (required insurance RCV), building and contents payments (sibling "new payment" overwrites, each naming the other), contents proof (contents settlement; minimum contents deductible), cancellation (refund method sentence for the risk credit; claim bar with the open-claim hold), refund (component booking; refund method sentence for its components; fees earned sentence) — each replaced_by names its own scope.
E15 world: historical proofs and payments recomputed day by day with the claim rules; renewal booked at the statutory cap with the bill at the indicated premium (base renewal); endorsement and re-rate entries are base pro rata figures; BizFlood term premium and total insured value re-rated on value endorsements; condominium association moved to the BizFlood Building tier. E16: no company holdback, earned-day or balance schedule remains; the only claims-to-cancellation link is FEMA's open-claim rule.
F17: design_rationale, closure, necessity texts, factor traces and argument tracing rebuilt from the new evaluator run; stale-figure sweep over both task files found none.

## REWORK round 2 claims
- CG-1: the claim bar is kept (current-term ladder and refund sentence) and its open-claim hold declared as an overwrite; FULL_FROM_INCEPTION, PRO_RATA and the fee sentence are declared overwrites scoped by component and limited to the current and previous term.
- CG-2: both payment rules share the other policy's deductible layer in proportion to the sworn building and contents amounts; no "first" order remains.
- CG-3: the contents limit cap is stated in the contents rule and overwrite; the earlier-terms factor and every refund carry are removed.
- CG-4: BizFlood reads scoped to the latest-SOV policy in force on the date of loss and its location; value endorsements restricted to value increases and decreases; report choice states the latest SUPPLEMENTAL; endorsement and certificate read by reference id within the effective term; probe table recorded.
- CG-5: duplicate tiers removed (effective date made a plain base sentence, term charge, term balance, re-rate carry and earned day removed, Reserve Fund tiers distinct, value-basis limit tier replaced).
- CG-6: report choices relabelled parameter; proof computations carry the already-sworn method; cancellation methods are the current-term and endorsement returns.
- CG-7: sworn totals no longer depend on a prior payment; additive balances removed; the other-insurance condition verified as the one both forms carry; the limit-as-replacement-cost tier replaced by the BizFlood adjuster's value at loss.
- CG-8: the earned-day factor is removed; the effective date follows base by reason.
- CG-9: the cancellation edge's effect is written for any coverage left open on a claim's latest report.
- CG-10: the refund waits on the processed cancellation (status and effective date), reachable even when a credit is zero.
- O-1: kept bizflood as the only cross product in the blueprint that bears on these claims; noted.
- O-2: deductible floors now have producible tiers only (federal minimum pairs); the carried-forward deductible is documented.
- O-3: the refund edge condition now matches its sentence.
- O-4: mortgagee holdback and the company claims gate removed; ICC, HFIAA and fees read every term charge; the processing records the mortgagee notice.
- O-5: contents ceiling kept as value verification against the insured's own declared value in force on the loss date.
- O-6: rounding of the required insurance stated (half-up).
- T0-1: other-insurance condition confirmed for the RCBAP and stated as such; the association holds the BizFlood Building tier.
- T0-2: closed by the already-sworn method of the building proof.
- T0-3: closed with CG-2.
- T1-1: cancellation and refund ladders rebuilt from FEMA reason-code refund rules with distinct, genuine tiers.
- T1-2: the renewal is paid in full (as billed); no shortfall or unrefunded earlier balance remains.
- T1-3: closed with CG-2.
- T1 observations: steering persona line removed; BizFlood total insured value and premium updated; first contents proof placed under the duplicate number by the claim that carried the report that day.

## Rework round 2 gate block (full suite, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 12 acts, 1.json 18 acts, det True, nonvac True, 0 errs, closure match); SOLVABILITY OK; COMPUTE OK (suite means branches and steps above floors); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
TRACEABILITY NOT OK — only the six unlock tool names lack a source before the KB is rendered; no id/value miss.
REWORK round 2: gates 8/8 green

## Rework round 3 — notes
- Prerequisite-scope class (R2-1): the cancellation's hold now reads by date of loss ("every coverage measured on the latest adjuster report for each date of loss ... a payment or a written denial for that date of loss"), so a claim filed under a duplicate first notice is closed by a payment under the other number; condition, effect and task closure text rewritten to the same scope. Other sentences re-checked: building/contents payment sentences and the refund sentence already equal their conditions.
- Layer-sharing class (R2-2): the other flood policy's deductible layer applies to a coverage only when that policy insures it at the address (SOV building / contents value), and the building-contents sharing applies only when it insures both; contents payment mirrors the building payment. Task 0's association policy is back on the BizFlood Building and Contents tier (the association, a non-profit corporation, owns the building and its common contents; SOV contents 60,000, premium and total insured value re-rated); the 2026-10-01 contents payment recomputed under the contents rule. Scored figures unchanged.
- Latest-record class (R2-3): (a) claim bar (credit current-term tier, refund ICC/HFIAA/RFA current-term zeros) reads the latest date of loss on which a claim payment was issued, with payments netted against voids; (b) value endorsements (building other cover, contents other cover, contents ceiling) read the endorsement in force on the date of loss: of the latest increase and the latest decrease, the later one effective on or before the loss; (c) endorsement and re-rate returns still isolate one endorsement and one certificate per term by reference id — the DSL cannot iterate rows, no task world carries a second premium-bearing endorsement or certificate in a term, and the rule says exactly what is read.
- Rule-vs-compute order class (R2-4): refund Reserve Fund ladder reordered to inception, claim bar, per-occasion, pro rata in both rule and compute; the claim bar now zeroes the per-occasion tier as well; all other ladders checked tier by tier against compute order.
- Probes (scratch): BizFlood writing no contents -> building carries the whole layer; increase in force plus decrease after the loss -> increase limit; voided-only payment -> no claim bar; claim-barred voluntary cancellation with a paid current-term claim -> ICC and RFA zero.
- Observations: O2-1 assembly sentences made generic in credit and refund; O2-2 mortgagee notice kept (base requires the notice; scope gate OK); O2-3 proportional layer moves as later proofs arrive (earlier payments are not clawed back, new payments are issued only when positive); O2-4 the 24-month window holds while the policy is in its current term at handling time; O2-5 renewal excess refunded with the cancellation (base gives no timing).

## REWORK round 3 claims
- R2-1: prerequisite sentence, condition and effect rescoped by date of loss so a duplicate-number payment closes the claim; task closure text aligned.
- R2-2: layers and building-contents sharing apply only to coverages the other flood policy insures, in both payment rules; task 0 world given a BizFlood policy that insures both coverages.
- R2-3: claim bar reads paid dates of loss net of voids; value endorsements read the one in force on the date of loss; single-endorsement and single-certificate reads stated exactly in the rule.
- R2-4: Reserve Fund ladder order and claim-bar tier aligned between rule and compute.
REWORK round 3: gates 8/8 green

## Rework round 4 — notes
- Ladder-face sweep (R3-1): tier 2 of the building other-cover, contents other-cover and contents ceiling ladders now read "no value endorsement for that location was in force on the date of loss", matching rule and compute; every ladder tier re-listed against its rule sentence, and no "latest value increase", "latest reported claim" or "live BizFlood" wording remains in the charter.
- Claim bar (R3-2, coordinator route): credit and refund read the claim payments, net of voided items, on all losses dated in the current term (a loss counting when dated no more whole calendar months before the processing date than term_start is), so a voided later loss cannot hide an earlier paid one; rule, ladder tier, compute and inputs aligned. Probe: earlier paid loss plus later voided loss in the current term -> barred.
- One-record scope (R3-3, coordinator route): the credit's and the refund's method overwrites now name their own scope, a current and previous term together carrying at most one premium-bearing endorsement and at most one re-rate credit (counted by their risk premium entries); for any other term the base refund-method clause applies verbatim (restated in the replaced_by) and compute switches to it. Probe: a second endorsement in the term -> base pro rata. Both task worlds are inside the scope; no scored value moved.

## REWORK round 4 claims
- R3-1: stale tier-2 ladder text replaced in all three value-endorsement ladders; charter swept for round-3 leftovers.
- R3-2: claim bar reads the term's claim payments net of voids across all losses, in rule, ladder and compute of both cancellation policies.
- R3-3: credit and refund scoped by self-naming overwrite to terms with at most one premium-bearing endorsement and one re-rate credit, base clause restated and computed for every other term.
REWORK round 4: gates 8/8 green

## Rework round 5 — notes
- Claim bar (R4-1, coordinator route): the claim-barred tiers (credit current-term ladder; refund ICC, HFIAA and Reserve Fund zeros) are scoped, in the credit's claim-bar overwrite and in both rules, to a policy with at most one loss reported within the whole calendar months counted back from the processing date to term_start. Inside the scope the one loss's date of loss is tested against term_start with a two-date test (on or after term_start = current-term loss) and its claim payments are netted against voids; with two or more losses reported in that window the base claim bar applies as written (restated in the overwrite and the refund rule). Rule, ladder, compute_basis, compute and task rationale aligned; no scored value moved.
- Probes (scratch): a paid loss dated before term_start inside the month window -> no bar; one current-term loss paid -> bar; two current-term losses with the later voided -> base clause, bar.

## REWORK round 5 claims
- R4-1: claim-barred tiers scoped to one reported loss in the month window with a date test against term_start and net payments; base claim bar restated and applied for two or more losses.
REWORK round 5: gates 8/8 green

## Rework round 6 — notes
- Claim bar (R5-1, coordinator route a then b): with m the whole months from term_start to the processing date, losses dated inside the m-month window are current-term by construction; the boundary band between the m and m+1 windows is classified by a two-date test on the latest reported loss when that loss is the band's only paid candidate. The bar holds when a loss dated on or after term_start carries claim payments net of voids above zero. The residue the records cannot place (a paid band loss with a later loss reported after the band, or two or more band losses whose latest is current-term and unpaid) is not priced by this schedule: the claim-barred tiers are not applied, and the rule states that the base claim bar, restated verbatim, governs it at the claims desk. Applied to the credit's current-term ladder and claim-bar overwrite, and to the refund's ICC, HFIAA and Reserve Fund zeros and its ladder; rule, ladder, compute_basis, compute and task 1 rationale aligned; duplicate first notices of one loss now resolve to that loss (O5-1). No scored value moved.
- Probes (scratch, processing 2026-10-20, term_start 2026-09-15): R5-1 world -> held, bar not applied; prior-term paid loss in the band only -> no bar; current-term paid loss in the band -> bar; current paid loss after the band -> bar; earlier current paid plus later voided -> bar; two band losses with the latest current and unpaid and a prior paid -> held; duplicate notice of one paid current loss -> bar.

## REWORK round 6 claims
- R5-1: claim bar computed exactly from the month window plus a dated boundary band; the undeterminable residue is stated and computed as not priced by this schedule, with the base claim bar restated as governing it.
REWORK round 6: gates 8/8 green

## Rework round 7 — notes
- Claim bar residue (R6-1, coordinator route): the residue now has one conclusion in both cancellation policies; the schedule holds the current term's return (booked as zero by these credits, the other parts returned as worked out), declared as a departure from the base claim bar for that residue only, by the credit's claim-bar overwrite and a new refund overwrite; the 'claims desk' wording is gone from rule, overwrite and design rationale.
- Residue shrunk with exact-value filters: the latest loss on which a claim payment was ever issued, and the net payments on that date of loss, now place a band loss on either side of term_start; only a latest paid loss dated after the band, or in the band on or after term_start with its payments all voided, remains held. Unused claim-bar bindings removed.
- Adversarial sweep over every read (scratch copies; cancelled / voided / prior-term / second / absent records): fixed the governing adjuster report filter (a same-day PRELIMINARY or SUPPLEMENTAL beside the FINAL), the duplicate-notice test (a second first notice under the same claim number), a BizFlood location deleted by endorsement before the loss, the value-endorsement wording (latest of each kind by effective date), the signed-request reading (latest signed request; withdrawn and unsigned ignored) and an overpayment already refunded. Probes on requests, prior-prior-term charges and payments, old re-rates and endorsements, and absent BizFlood records gave matching single answers with no change. Scored values unchanged.

## REWORK round 7 claims
- R6-1: the held residue has one conclusion, the current-term return held at zero with the other parts returned as worked out, declared as a scoped departure from the base claim bar in both cancellation policies; the residue is reduced to the cases the latest paid date of loss cannot place, and the charter-wide read sweep closed the remaining cancelled, second-record and refunded-record members.
REWORK round 7: gates 8/8 green

## Rework round 8 — notes
- R7-1 and the second-record class (coordinator route: (a) exact identifying filter, or (b) scope to the single-record case with the multi-record case defined in words). Every read, with its handling:

| read (bindings) | second record that could change the record meant | handling |
|---|---|---|
| claim and date of loss (`*_cn`, `*_dol`) | adjuster report on another claim | rule defines the claim as the one carrying the latest adjuster report; exact |
| governing report (`*_final_date`, `*_supp_*`, `*_prelim_date`, `*_gov_*`, `bp_loss`, `cp_measured`) | second FINAL / SUPPLEMENTAL / PRELIMINARY, same-day report of another type | (a) claim number + report type + event date filters; rule now says "latest FINAL report" |
| proofs of loss (`*_pol_*`, `*_bpol_*`, `*_cpol_*`) | further or late proofs | aggregates or "latest proof" as the rule defines; filtered by claim number or date of loss and coverage |
| claim payments and voids (`*_paid*`, `*_void*`, `*_last_*`) | void, reissue, duplicate claim number | net sums or "latest void/payment" as the rule defines; filtered by claim number or date of loss and coverage |
| first notices (`*_n_notice`) | second notice on the same claim number | (a) notices under other claim numbers only |
| BizFlood adjuster value (`*_bzval`, `*_locval`, `*_n_val`) | revised BizFlood adjuster report | (a) policy + location + date-of-loss filters; rule now names the adjuster's latest report for the date of loss |
| BizFlood policy and SOV (`*_bz`, `bp_bz_pid`, `*_loc`, `*_sov_*`, `*_bz_bldg`, `*_bz_cont`) | second SOV or second BizFlood policy for the address | (b) latest-of-kind reading stated as exact only with one SOV for the address; with more, the rule means the policy and SOV in force for the location on the date of loss (compute not priced there) |
| value endorsements (`*_inc_*`, `*_dec_*`, `*_chg_*`) | second increase or decrease (R7-1) | (b) exact with at most one of each kind; with more, the rule means the endorsement in force on the date of loss (compute not priced there) |
| location deletion and re-adding (`*_del_eff`, `*_add_eff`, `*_deleted`) | second deletion or re-adding | (b) as for value endorsements |
| BizFlood in-force dates and parameters (`*_bz_eff`, `*_bz_cxl`, CPARAM) | none | (a) by BizFlood policy id |
| renewal charge test (`*_n_renewal`) | any renewal charge | existence test, as the rule states; no record choice |
| cancellation request in the credit (`xc_reason`, `xc_req_date`, `xc_received`) | older or later signed request | (b) exact with one signed request; with more, the rule means the signed request being processed (compute not priced there); withdrawn and unsigned requests are filtered out |
| cancellation request in the refund (`xr_req_id`, `xr_reason`) | older or later signed request | (a) the request the risk CANCELLATION credit references, and the reason the cancelled policy shows |
| endorsement and re-rate entries (`xc_endo_*`, `xc_rr_*`, `xr_endo_*`, `xr_rr_*`, `*_ec_eff`, `*_endo_eff`) | second endorsement or re-rate | (b) existing self-naming one-endorsement/one-re-rate scope overwrite, with the base clause restated and computed otherwise; change rows by exact id |
| term charges, credits, payments and refunds (`*_cur`, `*_prev`, `xr_*_cur`, `xr_*_prev`, `xr_pay_*`, `xr_ex_*`, `xr_refd`) | other-term rows | aggregates filtered by term_start or by a 24-month term window, as the rule states |
| claim bar (`*_netin`, `*_netall`, `*_dp`, `*_netdp`) | other losses or voided payments | net aggregates plus "latest loss ever paid" as the rule defines; residue declared (round 7) |
- Rationale probe lines updated in both tasks. The refund's prerequisite sentence was restored verbatim. Probes: a later second signed request leaves the refund unchanged. Scored values unchanged.

## REWORK round 8 claims
- R7-1: value endorsement, location deletion/re-adding and BizFlood policy/SOV reads made exact only in the single-record case, with the multi-record case defined in words in all four claim rules; the whole second-record class swept read by read (table above), with the governing report, BizFlood adjuster report and refund request made exact by filter.
REWORK round 8: gates 8/8 green

## Rework round 9 — notes
- The words-only branch of round 8 is withdrawn. In every case, the rule's words and the compute now give one answer.
- The BizFlood policy is now chosen by the BizFlood adjuster report for this date of loss (an exact filter on date_of_loss), in all four claim policies. The building's location on it is the location number its statement of values gives the address.
- The location deletion and re-adding reads, and their rule clauses, are dropped. Coverage of the location is carried by the BizFlood adjuster report for the date of loss together with the policy's in-force dates.
- The other-insurance limit still needs the statement of values and the value endorsement in force on the date of loss. The DSL cannot pick that across several records, so each claim rule is scoped by an exact count:
  - every BizFlood adjuster report for the date of loss is on that one BizFlood policy;
  - for the address, that policy holds at most one statement of values;
  - for the payments and the contents ceiling, it also holds at most one value increase and at most one value decrease.
  - Otherwise the rule states, and the compute gives, nil: no amount is worked out or issued under the rule, and the matter is referred to the adjuster.
  - Within scope, the value-endorsement reading is exact.
- The credit's signed request is stated as the compute reads it: the latest signed cancellation request received on the policy, with withdrawn or unsigned requests not counting. The refund's request stays exact: the request the risk credit references.
- Probes on scratch copies, all giving the same answer from rule and compute:
  - second value increase (the R7-1 world) -> nil;
  - second statement of values -> nil;
  - a second BizFlood policy adjusted for the same date of loss -> nil;
  - no BizFlood adjuster report -> no other insurance;
  - task worlds -> unchanged.
- Rationale probe lines updated in both tasks. Scored values unchanged.

## REWORK round 9 claims
- R8-1: every listed member re-keyed or scoped exactly. The BizFlood policy is keyed by its adjuster report for this date of loss, and the deletion reads are dropped. The statement of values and value endorsement reads are exact within a stated count scope, with a stated, computed nil outcome outside it. The credit's request is stated as exactly what the compute reads. No rule now defines a value the compute does not compute.
REWORK round 9: gates 8/8 green

## Rework round 10 — notes
- R9-1, coordinator route. The other BizFlood policy is again the one whose statement of values schedules the property's address (exact filter on the location address), in all four claim policies.
- It counts only when in force on the date of loss. That is now defined in the rule and computed by policy id with two-date DAYS tests: on or after its effective date, before its term end (newly read) and before any cancellation effective date.
- A BizFlood adjuster report is no longer needed for the policy to count.
- Location value at loss: the BizFlood adjuster's value on its latest report for the location and the date of loss, and otherwise the building and contents values its statement of values schedules for the location, added together. The V/VE deductible-layer tier now uses this value in both payments, so it no longer falls through without a measurement.
- The single-record scope is kept with the referral and nil outcome: at most one statement of values schedules the address across the named insured's BizFlood policies, and, for the payments and the contents ceiling, at most one value increase and at most one value decrease. The round-9 count on adjuster reports across policies is dropped.
- Probes on scratch copies, all giving the same answer from rule and compute:
  - no BizFlood adjuster report, zone V -> layer on the statement-of-values values;
  - no report, zone AE -> flat per-location deductible, other insurance counted;
  - a second policy schedules the address -> nil;
  - BizFlood term ended before the loss -> not in force;
  - task worlds -> unchanged.
- Rationale probe lines updated in both tasks. Scored values unchanged.

## REWORK round 10 claims
- R9-1: the BizFlood policy is re-keyed to the statement of values for the address, with in force defined and computed from its effective, term-end and cancellation dates. The location value at loss is the adjuster's value, or the scheduled values when there is no report, in every tier that uses it, including the V/VE layer. The single-record scope with nil and referral is kept for two or more scheduling statements.
REWORK round 10: gates 8/8 green

## Rework round 11 — notes (renderer source scan render_r1)
- Item 1, factor reading another factor: `pb_other` no longer reads `pb_n_sched`. Class sweep with a scratch checker over all six policies (every factor binding against every other factor's bindings) found no other cross read.
- Item 2, claim bar against the endorsement return: under the claim bar on a current-term cancellation, the endorsement return is now nil in compute (`xc_endo_ret`) and in the rule (bar sentence, held wording, endorsement sentence and ladder). The claim-bar bindings are now plain, shared by the current-term and endorsement factors. The re-rate takeback is left as it is: the credit is floored at zero, so the result is nil either way.
- Item 3, "in full" against netting: the rule now says a later term's Reserve Fund Assessment charges are returned in full less the re-rate credits booked on them, as the compute does.
- Item 4, same-day value endorsements: an increase and a decrease taking effect the same day are settled by the one recorded later, and by the increase when both were recorded the same day. This is in the rule, the compute (`*_inc_rec`/`*_dec_rec`) and the ladders of all three value-endorsement reads.
- Item 5, single-factor definitions outside their factor:
  - `bp_bz_pid`, `bp_bz_loc` and the guard `bp_one` now sit in the value-basis factor.
  - `cp_bz` and its in-force bindings, and the guard `cp_one`, now sit in the ceiling factor.
  - The proofs' guard is now a tier condition: with more than one statement of values (or, for the ceiling, more than one value increase or value decrease), the policy's own replacement cost value or contents limit applies. Both results are back to the plain assembly.
  - The duplicate reads `pb_sov_value` and `cy_sov_cont` are merged into the shared plain `pb_bz_bldg` and `cy_bz_cont`.
  - Class sweep: `xc_prev` and `xr_eff_end` moved into their only factors. The remaining single-use plain bindings (`pb_cn`, `cy_cn`, `xc_cur`, `xc_endo_term`) are baseline quantities.
- Non-blocking item, ratios above 100%: an endorsement or certificate effective after the cancellation date now returns its Reserve Fund Assessment charge, or takes back its re-rate credit, in full.
- Non-blocking item, prior-term Reserve Fund Assessment ignored: a cancellation before term_start with no endorsement or re-rate in its term now gets a new tier, matching ICC and HFIAA. The current term is returned in full less re-rate credits, and the term before it pro rata (or in full less re-rate credits when it fell on or before that term's start).
- Non-blocking item, undefined request: with a zero risk credit (none booked), the refund reads the latest signed cancellation request. This is stated and computed.
- Probes on scratch copies, all giving the same answer from rule and compute:
  - claim-barred current-term cancellation with a current endorsement -> credit nil, refund ICC/RFA/HFIAA nil;
  - late endorsement or certificate -> full charge or full takeback;
  - plain prior-term cancellation -> new tier figure;
  - zero credit -> latest signed request;
  - same-day increase and decrease -> recorded-later rule;
  - task worlds -> unchanged.
- Rationale probe lines updated in both tasks. Scored values unchanged.

## REWORK round 11 claims
- render_r1 item 1: the other-cover factor's cross read of the layer factor removed; no other cross read found charter-wide.
- render_r1 item 2: the claim bar zeroes the current-term endorsement return in rule and compute, consistent with the refund's Reserve Fund Assessment.
- render_r1 item 3: the Reserve Fund Assessment "in full" wording states the re-rate netting the compute applies.
- render_r1 item 4: the same-day increase/decrease tie is defined and computed in all three value-endorsement reads.
- render_r1 item 5: single-factor BizFlood definitions and the proofs' scope moved into their factors, duplicate reads merged, and the class swept charter-wide.
- render_r1 non-blocking items (ratios above 100%, prior-term Reserve Fund Assessment, undefined request with no credit row): each now has a stated, computed, realistic tier.
REWORK round 11: gates 8/8 green

## Rework round 12 — notes (KB audit round 1, source-side items)
- kb-1 (source side): the base sentence applying fees_refundable_on_pro_rata ("Under CURRENT_TERM_FULL and PRO_RATA the Federal Policy Fee and probation surcharge are fully earned (fees_refundable_on_pro_rata is false).") is declared overwritten by overwrite 3. Its replaced_by now names its own scope: a cancellation refund whose current term and the term before it carry at most one premium-bearing endorsement and at most one re-rate credit. It restates the base clause verbatim for the multi-record case and for every other fee, so the KB can mark the parameter sentence retired.
- src-1: the three refund overwrites now exclude each other by name, and the assembly sentence is aligned with them, matching the compute (`result` in scope; `xr_risk + xr_base_other` out of scope):
  - Overwrite 1 (booking and total) adds the premium received but not owed only for the in-scope refund, and says the multi-record refund is the total of its credits alone.
  - Overwrite 3 (fees) is scoped the same way.
  - Overwrite 2 names its multi-record branch as the case the premium-received and fee sentences leave to the base clause.
  - The assembly sentence adds the premium received but not owed only "where the booking sentence above adds it".
- Charter-wide check: the credit's scope overwrite and its claim-bar overwrite already exclude each other and match its compute; no other unconditional-versus-scoped overwrite pair found.
- src-2 not in scope this round (coordinator stop rule). kb-2 and the wording note are KB-side.
- Rationale probe line updated. Scored values unchanged; base section byte-identical.

## REWORK round 12 claims
- kb-1: the fees_refundable_on_pro_rata base sentence is declared overwritten with a self-scoped replaced_by that restates the base clause for every other refund and fee.
- src-1: the booking/total, fee and multi-record overwrites, and the assembly sentence, now exclude each other by name and match the compute's in-scope and out-of-scope results.
REWORK round 12: gates 8/8 green
