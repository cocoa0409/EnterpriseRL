# excess_flood_layering — difficulty worklog (env_0065)

Scratch / authoring scripts: /tmp/excess_flood_layering_0065/ (plan.md = running plan; scripts/ = builders + harness).

## Draws
- task 0: prerequisite_problems=1, factor_counts [6,6]; task 1: prerequisite_problems=1, factor_counts [6,5].

## Task 0 (closed, per-task gates green)
- Tree: excess_ext_limit_increase_premium (root, user tool sign_excess_limit_increase_cddf0413) <- excess_ext_renewal_term_premium (agent tool book_excess_renewal_30706efc), value_input, state-form sentence.
- Gold: renewal term premium 1530.31 (baseline 1795.00 = renewal offer decoy); to-value increase 1,450,000 flat as of 2026-10-01, additional premium 179.60 (baseline 186.36), revised 1709.91.
- Per-task gates: extended / task_tools / replay / solvability / compute / grounding / cross_fire OK; traceability misses only the two unlock tool names (docs not yet rendered).
- Revisions: increase scoped to to-value requests (compute cannot read a stated limit); Feb-2026 history increase is a stated-limit increase under the base endorsement rule; flat window bounded below by the term start; intent_source kinds fixed (initial_state / user_scenario).

## Task 1 (closed, per-task gates green)
- Tree: excess_ext_sale_cancellation_return (root, user tool sign_excess_sale_cancellation_a26754a5) <- excess_ext_loss_of_use_payment (agent tool pay_excess_loss_of_use_f5cb8480), value_input, state-form sentence in the negated direction ("is not fixed until ... carries a loss-of-use payment issued after that report").
- Gold: loss-of-use payment 14,398.50 on XC-4310887 (baseline 70,530.00); sale cancellation effective 2026-09-15 with returned premium 1,225.90 (1,307.31 without the payment; baseline 1,391.70); tool adds 73.55 tax and refunds 1,299.45.
- Revisions: HomeFlood old-home term moved to 2026-06-25 so the 25% minimum binds in the waiver baseline; earning-period split and cancellation-date anchor factors dropped (identical result / straw-man baseline); minimum-waiver tiers set to three-or-more / one-two renewals so the renewal count bears weight when history is zeroed.

## Difficulty-level closure
- 4 extended policies, 4 task tools, scopes disjoint (task 0: renewal + increase; task 1: loss-of-use payment + sale cancellation); every task calls one owner=user tool; one value_input edge per task.
- Charter carries prerequisite sentences in both directions (affirmative "only once" in the increase rule, negated "not ... until" in the cancellation rule).
- Overwrites (all scoped in their replaced_by): excess_premium_rating (renewal premium), excess_waiting_period + excess_endorsements (to-value increases), excess_claim_settlement (loss of use), excess_cancellation_refund x3 (gate sentence, PROPERTY_SOLD effective date, pro rata with minimum).
- Identifier band respected: phones 8435541274 / 8435547719, SSN last4 4318 / 4682, policy/claim/loan/payment refs first digit 4, surnames Rutledge / Sutherland, lenders Seaboard Coastal Bank / Southern Tidewater Bank, street numbers 418 / 447 / 456.

## Final gate block (run from repo root, no --task)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 14 acts det nonvac 0 errs; 1.json 12 acts det nonvac 0 errs)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches=46.50 steps=13.00; history_rows_max=18; branches_max=51)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (optional)
- check_cross_fire: SCOPE OK
- check_traceability (pre-render): only misses are the four unlock tool names (book_excess_renewal_30706efc, sign_excess_limit_increase_cddf0413, pay_excess_loss_of_use_f5cb8480, sign_excess_sale_cancellation_a26754a5) — expected before the KB is published; no id/value miss.

ROUND 1: gates 8/8 green

## REWORK round 2 claims
- F-1: renewal loss-history ladder made realistic and multi-source (layer payment or two primary payments / no layer payment and exactly one primary payment / none); primary payments counted only on the NFIP or HomeFlood policy of the home; task 1's seeded renewal history re-derived under it; task 0 now carries a surviving multi-source factor.
- F-2: relocation allowance removed; replaced by a severity-based moving and storage allowance (FINAL whole dwelling loss as a share of RCV) inside the loss-of-use payable, netted against payments already issued; task 1 history re-derived.
- F-3: minimum-earned waiver re-keyed to renewal count AND layer claim payments in the last 12 months (no conjunct universal to the policy's scope); renamed tenure_minimum_waiver.
- F-4: base due-date sentence of excess_claim_intake_pol declared as overwritten for loss-of-use payments under the policy (scoped replaced_by; building/contents payments stay under base); base ref added.
- F-5: paid-claim bar now reads the paid claim with the latest date of loss net of voided payments; the base bar sentence declared as overwritten with a scoped replaced_by.
- F-6: (a)(b)(c) all NFIP reads confined to the NFIP policy of the home (address + in force) via a plain shared binding; (d) HomeFlood offset filtered to the underlying claim number recorded at first notice; (e) every claim read confined to the claim carrying the latest adjuster report; (f)(g) HomeFlood term end and tier limit read by the underlying policy number; (h) removed with the relocation factor. Probe table in each task's design_rationale.
- T0-1: closed by F-1 (multi-source loss-history factor).
- T1-1: closed by F-4. T1-2: closed by F-2. T1-3: closed by F-3.
- O-2/O-3: prerequisite conditions aligned with their sentences. O-4: sentence states the term end as excluded. O-5: replaced_by names the underlying offset. O-6: flat window requires no claim with a date of loss on or after the term start. O-9: cross-category reads list every filtered field. O-10: offset no longer lets the layer drop down. O-12: one name for the elevation multiplier. O-T0-1: persona authorisation line neutral. O-T0-2: half-cent tie removed (renewal payment date moved). O-T1-1: contents attachment set per base. O-T1-2: FINAL report and building proof of loss inside the 60-day window. O-1, O-7, O-8, O-11: left as observations.
- Proof text swept: design_rationale, prerequisite_closure, necessity/objective text, argument tracing, factor traces and seed consistency regenerated from the harness run.
- Gates: check_extended OK, check_task_tools OK, replay_tasks OK, check_solvability OK, check_compute OK, check_grounding OK, check_cache_diff info, check_cross_fire OK; check_traceability misses only the four unlock tool names (pre-render).
REWORK round 2: gates 8/8 green

## REWORK round 3 claims
- N-1: underlying-offset ladder rebuilt with three methods distinct on every charter-producible world (Tidemark HomeFlood underlying -> that tier's loss-of-use limit read by the underlying policy number; another carrier's private primary -> a share of the underlying dwelling limit on record; NFIP underlying -> first dollar); the paid-versus-limit split that HomeFlood's own settlement rule made identical is gone. Class swept: every other ladder (P1 account/occupancy/loss history, P2 rate derivation/signing window, P3 unexpired cutoff/waiver/retention/charge, P4 period end/interest anchor/share/allowance/rate) checked for tiers coinciding on the domain the other charters can produce; none found.
- T1-4: closed by N-1; the HomeFlood claim-file read no longer feeds any decision, so it was dropped from gold reads and its rows from the seed (write steps now 8 and 10); traces, solvability steps and prior-step references updated.
- Stale proof text (design_rationale pairwise tier table and factor card, probe list, business-object card): rewritten for the new ladder.
- Gates: check_extended OK, check_task_tools OK, replay_tasks OK, check_solvability OK, check_compute OK, check_grounding OK, check_cache_diff info, check_cross_fire OK; check_traceability misses only the four unlock tool names (pre-render).
REWORK round 3: gates 8/8 green

## REWORK round 4 claims
- F1: late-payment interest given a standard method in the loss-of-use computation (a default yearly rate and the base due date); the due-date anchor and the claim-age rate now each replace one baseline quantity and each change the result on its own. Class swept: no other pair of factor quantities is combined so that one zeroes the other (all other factor quantities enter as summed percentages, multipliers with a non-zero baseline, or added amounts).
- F2: displacement cut restated in whole displacement months exceeding the tier maximum, matching the whole-month count; the sale tier also requires the closing on or after the date of loss (negative gap given a stated tier).
- F3: certificate age stated in whole months (twelve per year) before receipt, matching the compute; class swept for every other month/year comparison (loss window, recency, claim age, repeat window, payment window are all stated as whole months).
- F4: absent underlying declarations fall back to the policy record's underlying dwelling limit, and an absent booked term premium item to the policy record's term premium, both stated in the rule; absent-record tiers re-checked charter-wide.
- F5: the unreachable term-end deferral tier replaced by a reachable short-term tier (waiting period kept, minimum 60-day share charged); waiting overwrite text aligned.
- F6: scheduled dwelling and personal property charges defined in the increase rule; undefined-term sweep run on all four rules.
- F7: every replaced_by tail now restates the base content it keeps for out-of-scope cases (renewal rating, increase waiting and endorsement, four cancellation clauses, loss-of-use due date; the loss-of-use settlement tail states it covers every such payment); no overwrite retires nothing.
- N1: single-factor bindings moved into their factors (renewal HomeFlood-of-home id; increase rates/minimum/zone factor and NFIP-of-home id; loss-of-use sale closing, maximum months, claim-payment days) — no scored value moved; the sale-tier factor is now labelled cross-difficulty.
- N2: loss-history counts net voided payments off on both the primary and the layer.
- Tie-breaks: each rule states the same-day rule the compute applies (entry first on file is read).
- XF 8-14 re-applied charter-wide: basis quotations verbatim (scripted sweep), rounding once at the end, scopes and decoys, prerequisite conditions equal their sentences, overwrite tails restated.
- Proof text: computations, factor sensitivities, prerequisite closure and design_rationale of both tasks updated for the changed sensitivities.
- Gates: check_extended OK, check_task_tools OK, replay_tasks OK, check_solvability OK, check_compute OK, check_grounding OK, check_cache_diff info, check_cross_fire OK; check_traceability misses only the four unlock tool names.
REWORK round 4: gates 8/8 green

## REWORK round 5 claims
- R4-1: loss-history rule now states the netting exactly as the compute performs it (each void posted in the same window takes one payment off the count), for primary and layer payments alike; no field pairs a void with its payment in the readable records.
- R4-2: the undefined "documented on a later report" qualifier removed; the due-date tiers read the latest adjuster report's kind and the loss-of-use proof directly, as the compute does.
- R4-3: the short-term tier now covers only 30 to 59 days left (waiting period still ending inside the recorded term); with fewer days the standard share is stated as nothing, the increase belonging to the next term, which agrees with the prerequisite sentence; task 0's prerequisite closure and design_rationale contrast restored accordingly.
- R4-4: report kind and displacement months moved into their factors; scripted sweep over every plain binding of all four policies found and moved one further member (increase loss-of-use charge into its rate-method factor); no other plain binding is read by a single factor.
- Self-probe sweep: every read probed on scratch copies with cancelled, expired, prior-term, second-record, voided and absent decoys (cancelled NFIP and HomeFlood at the address, prior-term unpaid claim, absent declarations, decrease and term-premium credit decoys, earlier second excess claim, void on another claim, expired HomeFlood entered first, fully voided current-term claim); rule words and compute agree on every probe; the first-match class is now stated in every rule's tie-break sentence (two policy records answering the same description: the one entered first is read).
- Proof text: task 0 prerequisite closure and rationale updated; task 1 rationale updated; scored values unchanged.
- Gates: check_extended OK, check_task_tools OK, replay_tasks OK, check_solvability OK, check_compute OK, check_grounding OK, check_cache_diff info, check_cross_fire OK; check_traceability misses only the four unlock tool names.
REWORK round 5: gates 8/8 green

## REWORK round 6 claims
- R5-1 (increase short-term tier vs prerequisite term-end exclusion): tier now reads "more than 30 but fewer than 60 days of the term remain" in rule, ladder and compute (days_left > standard waiting days and < 60); at exactly 30 days left the waiting period ends on the term end, the share is nothing and the increase belongs to the next term, agreeing with the prerequisite sentence ("up to, but not including, its end"). Probed on the task 0 world at 28/29/30/31/32/59/60/61 days left: 28-30 nothing (effective on/after term end), 31-59 the 60-day minimum share (effective inside the term), 60+ the standard share; task 0 proof text swept (days-into-term span corrected).
- Same-kind class (every read where a second record of the same kind could change which record the rule means), handled by route (a) exact identifying filter unless noted:
  - P1 renewal: NFIP policy of the home (home_nfip_id), HomeFlood policy of the home (home_homeflood_id), account EXISTS reads (homeflood active / dwelling in force), occupancy designation - all keyed by policy_number = underlying policy number on the policy record (+ status); NFIP certificate reads and NFIP/HomeFlood claim counts keyed by that policy's id; renewal payment keyed by term_start = current term end; renewal term premium count and layer claim counts are policy-wide by rule ("on the policy"), single holding.
  - P2 increase: NFIP policy for recency (home_nfip_id) and flood zone keyed by underlying policy number + in force; underlying declarations keyed by underlying_policy_number (latest of those); booked term premium keyed by term_start = current term start, rule now says "latest term premium item booked for the current term"; latest loss date and repeat-increase count are policy-wide by rule.
  - P3 sale cancellation: sale closing date keyed by HomeFlood policy_number = underlying policy number + cancellation_reason PROPERTY_SOLD (rule scope sentence restated to that policy); underlying declarations keyed by underlying_policy_number; HomeFlood term end keyed by policy number; paid-claim bar keyed by the latest-loss-date paid claim's claim_number (net of its voids); loss-of-use payment and renewal counts policy-wide by rule.
  - P4 loss of use: claim in hand = claim of the latest adjuster report; date of loss, incurred, report date/kind, prior payments and voids, latest FINAL report, latest loss-of-use proof, latest proof, latest settlement record all keyed by that claim_number (rule now says "latest" for FINAL report, loss-of-use proof and settlement record); sale closing keyed as P3; HomeFlood loss-of-use limit keyed by underlying policy number.
  - cross_category reads/notes updated (policy_number read; property_address no longer read by P3/P4). Decoy probes (task 0: second in-force NFIP policy on the same address with another number, VE zone, non-primary, recent building payment, later declarations for another number; task 1: second HomeFlood policy on the same address cancelled for a sale on another date with another LOU limit, later declarations for another number) leave all four results unchanged.
- No scored value moved: T0 renewal 1503.36 / increase 175.93; T1 loss of use 11898.50 / returned premium 1588.38; baselines and sensitivities recomputed equal (check_compute).
- Gates: extended, task_tools, replay, solvability, compute, grounding, cache_diff (info), cross_fire all OK; check_traceability: only the four unlock tool-name misses.
REWORK round 6: gates 8/8 green

## REWORK round 7 claims
- R6-1 (signing_window ladder face vs rule/compute): the short-term tier's ladder text now reads "the increase is signed when more than 30 but fewer than 60 days of the term remain", the same tier set as the rule and the compute (exactly 30 days left falls to the otherwise tier, nothing charged); this corrects the round-6 claim that the ladder had already been changed. Class sweep by script over every ladder tier of all four policies (each comparison phrase with a number or number word in when/method/value must appear in its policy's rule; each tier value's figure must match its parameter): no other divergent tier; two residual hits are wording-equivalent and left untouched - sale backdating "more than 90 days" (rule: "31 to 90 days ... received later", compute > 90) and tenure "otherwise (fewer than two)" (rule tiers five or more / two to four / otherwise). Nothing else touched; task proof text carries no stale tier wording.
- Gates: extended, task_tools, replay, solvability, compute, grounding, cache_diff (info), cross_fire all OK; check_traceability: only the four unlock tool-name misses.
REWORK round 7: gates 8/8 green

## REWORK round 8 claims
- R7-1 (signing_window short-term "minimum" undercut by the next tier): the 60-day minimum is now a real floor across every tier it applies to - an increase not made flat whose standard waiting period ends before the term end is charged the share from the end of that period to the term end, never less than a minimum share of 60 days over the days of the term; where the waiting period ends on or after the term end nothing is charged and the increase belongs to the next term. Rule sentence, compute_basis, signing_window ladder (flat / waiting-period share floored at 60 days / nothing) and compute (MX of 60 days and the post-waiting days, only where days left exceed the waiting period) are identical; the factor's baseline (plain post-waiting share) is unchanged. Probed on the task 0 world at 29/30/31/59/60/61/89/90/91/120 days left: nothing at 29-30, 60 days charged from 31 through 90, 61 at 91, 90 at 120 - the charge never falls as the remaining term grows. Class check: the charter's other minimums (renewal minimum premium, sale-cancellation minimum earned share) already bind on every tier; no other tier undercuts a stated minimum. Task 0 pairwise-tier proof text and round note updated; nothing else touched.
- Gates: extended, task_tools, replay, solvability, compute, grounding, cache_diff (info), cross_fire all OK; check_traceability: only the four unlock tool-name misses.
REWORK round 8: gates 8/8 green

## REWORK round 9 claims
- SRC-2 (renewal rule "only their claim files and certificates are read" contradicting its own account and occupancy reads): the sentence now states exactly what the renewal reads of the NFIP and HomeFlood policies of the home - their status, the NFIP policy's primary-residence designation, their claim payments and voided payments, and the NFIP policy's applied Elevation Certificates - matching the account (status), occupancy (designation), loss-history (payments net of voids) and certificate-source reads in compute; class check: no other rule sentence in the four policies limits what is read; every compute_basis quote still verbatim; no compute, ladder or scored value changed; task proof text never quoted the sentence. The published KB docs that carry the old sentence (account relationship, loss history) need the coordinator's re-render.
- SRC-1: not touched (base parameter meanings in the frozen blueprint; logged BLUEPRINT-KNOWN by the coordinator).
- Gates: extended, task_tools, replay, solvability, compute, grounding, cache_diff (info), cross_fire all OK; check_traceability OK (docs published).
REWORK round 9: gates 8/8 green

## REWORK round 10 claims
- SRC-3.1 (task 1 HomeFlood cancellation without its request and ledger): seeded the named insured's signed property-sold cancellation request (settlement statement, effective on the closing date) and the full HomeFlood ledger of the old home - every term's term premium item and policy fee with its payment from new business, the cancellation credit worked out under the published HomeFlood cancellation credit rule referenced to the request, and its refund to the insured - plus the renewal offers and the application certificate; the old home's term premium and application date were brought onto the published rate manual and waiting period, and the new home's first term (premium on the rate manual, policy fee, escrow payment) was seeded with it.
- SRC-3.2 (task 1 HomeFlood claim file empty, 995,000 not producible): seeded claim HFC-4402173 with first notice, preliminary/final/supplemental adjuster reports, proofs of loss and payments settled under the published HomeFlood settlement rule (actual cash value dwelling less the deductible capped at the limit, personal property at replacement cost, loss of use up to the tier limit within the tier period); the excess file's underlying settlement record now carries the dwelling amount that settlement pays (not read by any computation).
- SRC-3.3 (task 0 NFIP certificate applied with no ledger): seeded the NFIP premium ledger for every term from new business (components as the published component rule builds them, renewals within the statutory cap, escrow payments), the re-rate credits the applied certificate produces from its receipt date with their refund to the escrow payor of record, the re-rated figures on both certificate entries (applied one lower, unapplied one higher), and the yearly renewal bills.
- Gold reads added so the closure covers the new rows (task 0 NFIP billing; task 1 HomeFlood requests, claims, billing, servicing documents); write steps and every step reference shifted; proof text (rationale, standard solution, row counts, stale "not seeded" sentences) swept; no computation reads the new rows and no scored value moved; excess.extended.yaml and task_tools.py byte-identical to the coordinator's freeze (sha256 checked).
- Gates: extended, task_tools, replay (closure matches), solvability, compute, grounding, cache_diff (info), cross_fire all OK; check_traceability OK.
REWORK round 10: gates 8/8 green
