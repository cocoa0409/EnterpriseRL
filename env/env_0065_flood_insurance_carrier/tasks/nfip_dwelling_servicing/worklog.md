# worklog — nfip_dwelling_servicing (env_0065_flood_insurance_carrier), M=2

## Round 1 (relaunch after account cut; prior attempt left only a scratch stub)
- Draw (draw_counts.py --tasks 2): task 0 prerequisite_problems=3, factor_counts=[6,6,6,6]; task 1 prerequisite_problems=2, factor_counts=[4,5,4].
- Feasibility findings (recorded in /tmp/nfip_dwelling_servicing_0065/plan.md): only payments (amount) and signed
  requests (date) are numeric user writes; grace-renewal booking would duplicate the renewal-cap logic of a payment, so
  the user root of task 0 is a pre-expiry renewal remittance (renewed term books at expiration, in the future); the
  user step of task 1 is the signed cancellation request whose date is computed by record selection (subject
  dwelling_premium_credit, no signed-request gate on the signing step itself).

## Task 0 — renewal remittance tree (Celeste Arceneaux, condo unit policy 1104582261, frozen 2026-10-14 10:20 CDT)
- Problems: dwelling_ext_certificate_rerate_credit (apply_elevation_certificate_36dc84dc) -> dwelling_ext_coverage_increase_charge
  (bill_coverage_increase_e35332a0) -> dwelling_ext_renewal_remittance (pay_renewal_premium_abaf74a5, owner=user, ROOT)
  <- dwelling_ext_residence_redesignation_credit (record_primary_residence_225abe6c). All edges value_input, state form.
- Gold: 40.36/7.26 credit (cert surveyed 2026-08-31), 12.84/2.31 charge (effective 2026-09-25), 54.86 surcharge credit,
  remittance 1681.91 by CREDIT_CARD. Baselines 30.96 / 3.54 / 11.10 / 1909.93. Edge skips: 12.84->0.00, 1681.91->1476.04, ->1961.77.
- Cross-difficulty: homeflood (former home sold 2026-08-14; refund paid). Near-miss: 2019-surveyed certificate received later.
- Per-task gates: extended, task_tools, replay, solvability, compute, grounding, cross_fire all green.

## Task 1 — replacement cancellation tree (Dominic Boudreaux, tenant contents policy 1152297408, frozen 2026-10-13 14:05 CDT)
- Problems: dwelling_ext_replacement_cancellation_date (sign_cancellation_request_cbba569e, owner=user) ->
  dwelling_ext_replacement_cancellation_credit (process_policy_cancellation_6794673f) -> dwelling_ext_replacement_refund_payout
  (disburse_premium_refund_739bd910, ROOT). Both edges value_input, state form.
- Gold: request dated 2026-08-20 (HomeFlood HF1260814 effective date), credits 406.88/73.24/23.01, payout 615.05 to INSURED
  (cancellation credits 503.13 + 60.00 card overpayment + 51.92 unrefunded re-rate credits).
- Revisions: debit-day factor compute read the latest payment method while the rule said "taken by ACH" -> rewrote to
  count ACH debits (risk credit 405.67 -> 406.88, payout 613.56 -> 615.05, propagated to task JSON); cancellation credit
  trigger on_request -> state_due (signed request obliges processing); signature-date policy history not load-bearing
  -> debit window now counts ACH/check/card payments.

## Known risks for audit (not gate-detected)
- Several factors are Tidemark servicing-schedule constructs (allowance/relief days, windows, carry rules) rather than
  FEMA rules: the NFIP Dwelling domain offers few real three-tier ladders per computation at the drawn 4-6 count.
- Some rule sentences name several factor quantities in one assembly sentence (e.g. "plus the backdating allowance, the
  relocation allowance and the review allowance") — candidate for the assembly-sentence class.
- Overwrite replaced_by tails of the certificate and coverage-increase policies do not say that every other case keeps
  the base rule.

## Final gate block (round 1)
EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK (suite branches 53.00, steps 15.00,
history_rows_max 46, branches_max 68) · GROUNDING OK · SCOPE OK · CACHE-DIFF INFO (optional).
check_traceability: only the 7 unlock tool names lack a source (expected before the KB is rendered); no other miss.
ROUND 1: gates 7/7 green

## REWORK round 2 (audit audits/policy_task/nfip_dwelling_servicing/, coordinator decision on F1)
Structure: task 1 folds the refund into the cancellation write (process_policy_cancellation books the credits and pays the
refund to the payor of record); the payout policy and disburse tool are removed; a new insured coverage-increase policy
(dwelling_ext_insured_increase_charge, tool bill_insured_increase_9da169e7) is the second prerequisite of the cancellation.
Task 0 keeps certificate -> increase (now a state_gate) and increase/designation -> renewal (value_input). Draw unchanged
(task 0 [6,6,6,6]; task 1 [4,5,4] as date 5, increase 4, refund 4).

### Class tables (XF_recipe)
A1-A5 factor structure: every factor's bindings read only raw fields and plain selections; assembly happens only in plain
bindings (windows_met / evidence_met / start_date / charged_days / result) stated once in generic words ("only when every
... window of this policy is met"); no factor reads another factor's binding (checked transitively: anchors read raw dates,
windows read their own evidence, set-off reads the ledger).
| policy | factors -> fields read |
| certificate | engine_figure_choice -> certificate survey/receipt/figure; rerate_anchor_rule -> governing survey date, term start, original effective date; diagram/elevation/age/floor-height windows -> certificate diagram, lowest floor vs BFE, policy zone, first floor height |
| loan increase | loan_anchor_rule -> request, closing, premium date; loan_waiting_rule -> closing, map revision; escrow_premium_window_rule -> payment method; closing_window_rule -> lender on request vs mortgagee; quote_window_rule -> closing date, engine figure; loan_rise_basis_rule -> re-rate credit date, booked charge |
| designation | occupancy_rule -> latest HomeFlood sale date; sale/refund/closure windows -> HomeFlood refund, plan, mortgage flag; report/proof windows -> latest adjuster report, proof of loss |
| renewal | outside_rise_rule -> increase/decrease records; cap_percentage_rule -> designation, term payments; term_surcharge_rule -> designation, tier eligibility, probation; setoff_rule -> ledger; bill_window_rule -> renewal bill; term_end_window_rule -> term payments by method |
| date | anchor_rule -> replacing HomeFlood effective date vs term; backdate_window_rule -> reported losses; lead_window_rule -> replacing basis; paid_up_window_rule -> replacing plan; breadth_rule -> mortgage flag, replacing variant |
| insured increase | anchor_rule_increase, waiting_days_rule, premium_window_rule, rise_basis_rule (as loan increase, no loan tier reached) |
| refund | returned_days_rule -> reason, claims; endorsement_fraction_rule -> increase effective date; rerate_fraction_rule -> rating-change date; lines_rule -> reason, booked lines |
A6 tiers: every ladder has pairwise-distinct outcomes on distinct inputs; former coinciding tiers removed (limit base tier 2, credit base, re-rate rule); multipliers are labelled parameter (fractions, windows, cap percentage).
A7 baselines: each baseline.rule states one standard figure that the compute baseline reproduces (certificate: governing receipt date with the latest-received figure; increase: request date plus the standard wait; designation: from the recording date; renewal: premium alone at 25 percent and the expiring surcharge; date: signing date; refund: every current-term component in full).
B8-B11: compute_basis, policy_source, baseline sentences and replaced_by texts swept verbatim by script (0 misses); every rounding is half-up via a 0.000001 nudge before round (tie probe below); floors stated (never below zero, no credit when the figure does not lower the premium, nothing after term end).
C12 probes (harness): decoy cancelled HomeFlood naming the policy -> date unchanged; no HomeFlood -> signing date; open current-term claim -> no backdating and the refund bar returns nothing; older second sale record -> designation unchanged (latest sale); no sale -> standard credit; renewal bill for another term -> remittance unchanged; decoy certificate removed -> credit unchanged; tie at 2.675 -> 2.68 under the rule (Python round gives 2.67).
C13: each prerequisite condition is literally unmet at the opening (certificate awaiting review, increase without effective date, no designation, no signed request, increase request without effective date).
D14: overwrites restate the in-force base text for out-of-scope cases and name their scope; the two increase policies each exclude the other's case by name; refund and renewal set-off overwrites name the payor scope.
E15: HomeFlood rows recomputed with the HomeFlood charter (rating formula, 14-day standard wait, annual plan, pro rata cancellation from the sale date); dwelling renewal bills now equal the booked figures where below the cap.
E16 (F1) residual, stated plainly: FEMA rules carry the anchors, waiting basis and exceptions, cap percentages, surcharges, refund method by reason and claim bar, payee by payor, pro rata unwinding and like-for-like rise; the draw's 6-factor floor in task 0 (and 2-parameter floor everywhere) exceeds the FEMA rules available for these writes, so the remaining factors are Tidemark documentation windows on recorded evidence (certificate, sale, replacement, request) and payment-application windows on the set-off; none adds, removes or forgives days or amounts of federal premium as an allowance, share or forfeiture.
F17: design_rationale, prerequisite_closure, evaluation objectives, argument tracing, seed_consistency and factor traces regenerated from the round-2 harness.

## REWORK round 2 claims
- P1: closed — the increase charge rule has no relief terms; every compute_basis quote is verbatim (script sweep).
- P2: closed — both increase policies date the increase from the later of request and premium receipt, apply the loan exception only when the premium arrived by the closing, and declare the waiting-period overwrite with scope.
- P3: closed — all roundings use half-up with a nudge and the rule sentences say so at the same placement; the halving terms are gone.
- P4: closed — the refund is paid with the cancellation as the total credits plus any held credit balance to the payor of record; the renewal set-off is a declared overwrite of both refund sentences.
- P5: closed — the certificate overwrite states that the rating change takes effect on the date its credit runs from; the tool argument follows it.
- P6: closed — certificate, increase and renewal policies are scoped to tiers with no ICC coverage and restate the base text for ICC tiers; reserve fund follows the base percentage.
- P7: closed — claim tests read the latest claim's payments net of voids and reports with payment or denial, not payment-row counts.
- P8: closed — the refund applies the claim bar for the four bar reasons (no returned days, no lines).
- P9: closed — every condition and floor the compute takes is stated in its rule (no unstated maxima, first-term or positivity conditions).
- P11: closed — reads are scoped: active replacing HomeFlood by replaced number, latest sale by date, renewal bill by the coming term start, increase by empty effective date, current-term ledger by term start; decoy probes recorded.
- F1: partly closed — all allowances, reliefs, shares, forfeitures and payment-channel conditions removed; FEMA rules carry the core; residual company windows listed in E16 above.
- F2: closed — no ladder has coinciding tiers; former limit-base, credit-base and re-rate tiers rebuilt.
- F3: closed — fractions, windows and percentages are labelled parameter; methods change formula shape.
- F4: closed — each baseline is one coherent standard reproduced by the compute baseline; the payout baseline issue is removed with the payout.
- F5: closed — HomeFlood term anniversaries, waiting days, premium and cancellation refund follow the HomeFlood charter.
- F6: closed — no rule sentence assembles factor quantities by name; combinations are stated generically.
- F7: closed — the sender field is no longer used; the closing window reads the lender named on the request against the mortgagee of record.
- O1: closed — the residence edge condition now matches its sentence.
- O2: closed — the certificate prerequisite names the governing certificate.
- O3: closed — scopes name a real condition (tier without ICC, loan transaction, insured request).
- O4: kept — base_policy_refs must list every base policy governing the subject events (gate requirement).
- O5: closed — the set-off is a declared payment-application rule on the same policy and payor.
- O6: closed — the refund returns the ICC line with the HFIAA line for pro rata reasons.
- O7: kept, declared — the renewal fee is the rated Federal Policy Fee on the policy because the renewal bill records no fee.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2: P2, P6, P11, F1, F2, F4, F6, F8)
Changes: both increase policies regenerated (dating = anchor/waiting with the base "earlier effective date is recorded"
rule applied when several datings qualify; 13-month map window counted by calendar months with the last day
qualifying; company request windows gate only the exception dating, the standard dating otherwise); certificate,
designation and renewal policies regenerated with fall-through tiers equal to their baselines; struck keys removed
(certificate diagram/elevation/height/age windows, lender-identity closing window, sold-home plan/mortgage windows,
adjuster-report and proof-of-loss windows, renewal no-payment cap tier); cancellation tool gains an ICC credit line;
claim bar reads every current-term paid claim net of voids; certificate tie tier reads the lower-figure certificate.
Worlds: task 1 records a 2025-09-15 map revision (the increase takes effect the day after its premium, the charge and
refund recomputed); task 0 request recorded 2026-09-23 with its premium on 2026-09-24, before the closing.
Probes (harness): map revision exactly 13 months before receipt qualifies, one day earlier does not; loan and map
datings both qualifying record the earlier; an earlier current-term claim paid with the latest one voided bars the
refund. Residual edge: the claim-bar window counts losses in the calendar month before the term start's month day.
Residual F1, stated plainly: the certificate and designation computations have two FEMA-grounded factors each; the
draw's six factors per task-0 computation are filled with Tidemark servicing windows keyed to the renewal bill, the
term's payment status, current-term claim status, later coverage requests and later certificates; renewal and the
increases keep the windows the audit listed as carrier-controlled. No FEMA ladder found in this base reaches six for
those two writes.
Residual F4: the refund's returned-days and lines factors keep the whole-term baseline because the task-1 reason is
the pro rata standard; every other factor's baseline is its fall-through tier.

## REWORK round 3 claims
- P2: closed — both increase policies record the earlier date when more than one dating qualifies and count the map window by calendar months with the last day qualifying, as the base states.
- P6: closed — process_policy_cancellation takes an ICC credit argument for the line the refund rule returns; certificate and increase policies stay scoped to tiers without ICC coverage.
- P11: closed — the claim bar sums every current-term paid claim net of voids (plus the latest-claim check); the certificate tie tier reads the lower-figure certificate's dates.
- F1: partly closed — every key the audit struck is removed; residual company windows on the certificate and designation computations listed above.
- F2: closed — unreachable tiers removed or re-scoped (insured loan tiers, quote no-closing tier, certificate diagram/zone tiers, lead STANDARD tier now 20 days, renewal cap tier); set-off tiers are distinct methods.
- F4: partly closed — fall-through equals baseline on every factor except the refund's returned-days and lines factors; straw-man baseline sentences replaced by the standard dating and standard rise, and the renewal baseline no longer cites 25 percent.
- F6: closed — dating, cap and premium sentences are stated generically.
- F8: closed — waiting tiers read raw request, premium, closing and map records, never the anchor binding.
- O8: closed — the certificate edge condition matches its sentence.
- O9: closed — the refund edge now moves the refund by more than a day's premium.
- O4: kept — base_policy_refs must list every base policy of the subject events (gate rule).
- O7: kept, declared.
REWORK round 3: gates 7/7 green

## ROUND 4 feasibility table (written before any round-4 edit)
| computation | ladder | rule source | tiers reachable on the world |
|---|---|---|---|
| EC re-rate credit | governing certificate; credit start | base dwelling_ec_rating / FIM EC section | 2 real ladders only -> dropped as a computation |
| residence credit | occupancy; sale evidence | HFIAA primary-residence definition | 2 real ladders only -> dropped as a computation |
| renewal remittance (task 0 root) | rise kept outside the cap (increases / decrease / none) | HFIAA: coverage changes are not rate increases | increases and a decrease in the expiring term |
| | term surcharges (HFIAA x probation, designation evidence read from the HomeFlood sale) | base dwelling_premium_components, HFIAA | primary evidence + probation (75) |
| | set-off (credit <= premium / balance owed / nothing) | WYO payment application across billed items | unrefunded re-rate credit balance |
| | bill window; term-end window; claim window | Tidemark servicing schedule (audit: carrier-controlled) | bill 27 d, term end 18 d, closed claim |
| loan coverage increase (building) | anchor (closing / coming term start / receipt) | base dwelling_waiting_period loan exception | loan closing, premium before closing |
| | waiting days (0 / 1 / 30) | base waiting period | loan exception -> 0 |
| | premium, transaction, quote windows | servicing schedule (audit: carrier-controlled) | all met |
| | rise basis (like for like / no figure / standard) | FIM endorsement rating basis | re-rate credit booked after the request |
| loan contents increase | same six ladders, contents-limit scope | same | same closing transaction |
| loan deductible decrease | same six ladders, deductible scope | same | same closing transaction |
| replacement cancellation date (task 1) | anchor (replacing effective date / original effective date / signing) ; backdating, lead, paid-up, breadth windows | base cancellation date rule, FIM reason 26 | replacement effective in the prior term |
| insured increase | waiting (map / renewal / 30), premium and quote windows, rise basis | base waiting period, map-revision exception | map revision 13-month window |
| cancellation refund | returned days (barred / cancellation before the current term start -> current term only / pro rata) | base PRO_RATA + current-term refund limit | replacement began before the current term |
| | lines (inception / term never ran -> lines and fees in full / barred / pro rata) | base refund methods, fees earned rule | same |
| | endorsement fraction; re-rate fraction | pro rata unwinding of term items | increase and re-rate after the cancellation date |
Decision: task 0 re-treed to renewal <- building increase, contents increase, deductible decrease (one loan
transaction); EC and residence computations removed; task 1 world moves the replacement into the prior term so the
honest pro-rata baseline is kept and every refund factor bites.
Post-edit note (round 4): the table rows above were written before editing; as built, the task-1 lines rule returns the
current term's HFIAA surcharge and ICC premium in full when the cancellation takes effect on or before the current term
start (fees earned, as under the base CURRENT_TERM_FULL method), the refund is the total of the cancellation credits as
the base rule states, the building increase's rise ladder has no earlier-request tier (it is the first request of the
closing), and the renewal's residence basis reads the HomeFlood sale record of the former home.

## REWORK round 4 claims
- F1: task 0 re-treed after the feasibility table: the certificate re-rate and residence computations and their tools are removed; the four drawn computations are the building-limit increase, contents-limit increase and deductible decrease of one loan closing (anchor, waiting, premium/transaction/quote windows, rise basis each) and the renewal remittance (outside-cap rise, HFIAA x probation surcharge with the residence basis, set-off, bill/term-end/claim windows); the certificate stays as seed only.
- F2: the payment-window and certificate-window members left with the removed policies; every tier of the new ladders is reachable on recorded fields (no duplicate values: set-off subtract / add / nothing; lines bar / inception / full / term share).
- F4: the credit baseline.rule is the base PRO_RATA method applied to the current term as booked; every credit factor's baseline equals its fall-through tier (returned days, endorsement and re-rate fractions at the term share, lines at the term share); task 1's world moves the replacement's effective date before the current term start so each factor bites honestly; the refund is the total of the cancellation credits, as the base rule states.
- F6: the endorsement dating sentence is generic ("the date the dating rules of this policy give"); the anchor sentence describes only its own quantity.
- P11: (a) closed with the removed certificate policy; (b) the claim bar reads the latest paid and latest reported claims against the term start and the rule states exactly that; (c) the renewal claim window names the most recent claim by date of loss; endorsement rise tiers test "billed" by the booked endorsement charge.
- P12: the set-off overwrites scope a credit balance larger than the renewal premium out in words and restate the base refund clause for it; the set-off ladder is subtract a credit no larger than the premium / add a balance owed / nothing.
- O10: the lines rule rounds the HFIAA and ICC lines separately, matching the two credit lines the tool posts.
- Probes (scratch, deleted): renewal with no credits and no endorsement payment adds the balance owed; a paid current-term claim bars the refund to zero; full gate block plus traceability (unlock tool-name misses only).
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- F1: the coming term is rated as a primary residence only on the policy's recorded primary-residence designation (the record the insured's residence certification produces; the frozen schema has no other residence-document record: dwelling_requests carries only CANCELLATION/ASSIGNMENT with no residence document type); task 0 seeds the designation, the HomeFlood sale is no longer residence evidence and only dates the move for the current-term residence credit (more-than-half-term test), declared by a scoped overwrite of the once-per-term booking clause; the persona's primary-residence line is removed; the coming-term HFIAA surcharge and cap follow the base designation rule (the earlier HFIAA overwrite is dropped).
- P11: the credit's claim bar now follows the base bar (any current-term claim paid or still open) and states exactly what is computed: losses fewer whole months back than the term start are current-term, the boundary month is placed by the latest paid / latest reported claim's date against the term start, an open claim is one without payments net of voids above zero or a denial, and the residue the reading cannot place holds the current-term return at zero with the hold stated, as a declared scoped overwrite of the base bar clause for that residue only.
- Probe sweep (every read; scratch, deleted): selection reads of the three loan-closing endorsements (a later non-loan pending increase is not billed under them and is the insured-increase policy's request, whose selection now requires no loan closing date), prior-request and billed-charge reads, payment and re-rate reads, renewal bill (most recently issued), deductible/increase recorded last, HomeFlood sale (non-sale cancellation ignored; absent record gives no credit), claim windows and the date policy's backdating window (a voided payment no longer counts as closing a claim), credit request (signed only), increase put into effect most recently, applied certificate, term-scoped ledger sums; claim-bar cases: band-before paid, band-in paid, inner paid, voided, open, prior-term open, two claims with one open, none — rule words and compute give the same single answer in each.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- P11: the open-claim test equals the base measure across the charter (a claim with neither a payment row nor a denial on record): the cancellation credit's open-claim bar and its clear-of-open test, the renewal claim window and the cancellation-date backdating window now read and say exactly that; the paid side keeps the base net-of-voids measure; probe (paid then voided claim in the current term) gives refund due by both the rule and the compute.
- P13: the residence credit is booked by the write that applies it: pay_renewal_premium now takes the residence credit and books it, in its own body, as a re-rate credit on the current term's HFIAA surcharge line before the payment; the renewal rule says the credit is booked with the remittance; task 0's gold payment carries the credit and the persona enters the figure given; after the gold writes the account holds exactly the coming term's premium paid in advance.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- render item 1 (map-revision dating): the three loan-closing endorsements compute one dating, the date the waiting period runs from plus the waiting days; the second map-revision dating and the earlier-of step are removed from the compute, and a declared scoped overwrite of the base "earlier effective date" clause states that the loan-transaction dating governs these requests.
- render item 2 (windows and gating): no factor is gated through another and no window is measured from a factor's result. Endorsement and insured-increase windows are limits measured between record dates (request to payment, request to closing, request to billing or to receipt); when a limit is not met the change may take effect no earlier than the standard dating, and the effective date is the latest of the dates the dating and limit rules give. Cancellation-date windows are limits measured from record dates (backdating from the replacing policy's effective date); each limit dates the request no earlier than the signing date, and the request is dated the latest of the dates the rules give, with breadth now a stated limit. Renewal windows are floors (the remittance before the credits booked with it may not be less than the renewal premium), assembled in a stated order: adjustments, then limits, then credits. The set-off reads only the account, with the larger-credit case handled in the assembly as the overwrite states. The cap rule and the baseline name no factor quantity; the outside-cap rise states its own effect on the cap. An independence check confirms no factor reads another factor's binding, directly or through plain bindings.
- render item 3 (claim bar used only by factors): the claim-bar reading now belongs to the baseline (the standard credit returns nothing when a claim bars the refund or the return is held) and is used by the result. The refund-method and lines factors no longer carry a bar tier; the refund-method factor replaces the returned-days factor (inception / current term in full / term share).
- lower items: the no-ICC scope is computed in all five scoped policies (a tier carrying ICC coverage is referred and nothing is charged or computed, as the rule states); the hold is now recordable: no cancellation credit and no refund are booked, with no unrecordable "stated" step.
- sweep: task 1's applied certificate now takes effect on its receipt date under the base certificate rule (its re-rate credits and refund recomputed), so the cancellation figures and all proof text were updated; traces and tier texts were refreshed for the limit wording; probes (a replacing deductible above the allowance, an ICC tier, a stale renewal bill) give the single answer the rule states.
REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- F1: the quote window of the building-limit, contents-limit and deductible-decrease loan-closing policies is now measured from the request date to the premium receipt date (customer/lender-side record dates, as the insured-increase policy already does), never on Tidemark's billing day; a receipt outside the window moves the change to the standard dating, stated in the rule and computed alike. Each of the six factors of the three policies still bites on task 0's world; no scored value moved; quote-window traces updated. Render items 1–3 and both lower items stay closed (no other window reads a carrier-side date: renewal windows run to the insured's remittance day, cancellation-date limits to the insured's signing date).
REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- render mismatch A: the cancellation credit's scope sentence (rule, baseline.rule and the overwrite's replaced_by alike) now names the rules that exist: the risk premium and reserve fund assessment charges follow the refund-method rule, the HFIAA surcharge and ICC premium the lines rule, endorsement charges and re-rate credits the fractions; the prerequisite effect text no longer mentions returned days.
- render mismatch B: the building-limit, contents-limit and deductible-decrease policies' closing sentence now reads that the change takes effect on the latest of the dates the dating and limit rules give, matching the effective-date sentence and the compute.
- sweep: text-only; compute, tools and scored values unchanged; charter-wide scan finds no other sentence naming a removed rule or binding (returned days, acceptance windows, billing-day measure, superseded dating sentence) and every rule a sentence refers to is defined in its own policy; compute_basis, policy_source, replaced_by and baseline sentences verbatim.
REWORK round 9: gates 7/7 green

## REWORK round 10 claims
- S1: the insured-increase rise rule and its factor ladder now list the no-engine-figure line first (no rise), then the Elevation Certificate re-rate line, then the standard line, and the compute checks them in that same order; one answer, no scored value moved.
- K1 (source check only): the three loan-closing policies' replaced_by for the base earlier-effective-date clause already names the sibling loan-request kinds and the no-loan insured requests as following the rules written for them before restating the base clause; the source is complete and was left unchanged (the dropped carve-out is a rendering matter).
REWORK round 10: gates 7/7 green
