# worklog — domain_renewals_and_transfers (env_0076)

Round 1: 8 extended policies, 2 tasks (see tasks/*.json design_rationale and plan.md). Round 2 rework below.

## REWORK round 2 claims
- C1 → every out-of-scope tail (grace-period renewal, maximum-term extension, restore-day extension, restore) names the sibling rules that price their own cases and states the real base rule (tier discount or bulk step, ICANN fee; restore with no discount) for every other charge.
- C2 → the four correction policies are replaced by the Domain Care price match: a look-back refund of the difference between a 2022-01-01..2025-11-30 line billed under the base rules and its Domain Care price; no historical price is redefined and the base pricing sentences stay true of those lines.
- C3 → each prerequisite sentence on a price match carries exactly the resolver's scope (most recent line of the kind, billed 2022-01-01..2025-11-30, card or PayPal, above its Domain Care price).
- C4 → maximum-term and restore-day years are the greatest whole number keeping the new expiry within max_registration_years (one more month is taken off when the days of the month differ); compute matches the sentence.
- C5 → subjects narrowed (grace renewal: domain_grace_renew; extensions: domain_expiry_update) so the auto-renew and grace gates are no longer retired; every replaced_by restates the in-force content for out-of-scope cases; the non-discount transfer clause is no longer retired; the remaining refund-gate retirements are scoped to the price match and restated.
- C6 → the zero-window sentence ("a TLD whose window is 0 never refunds that charge type") is declared superseded for the price match and restated for every other refund.
- C7 → no certificate (or mailbox) first-match read remains; hosting reads filter status active (one live plan per primary domain by base); probe tables in the task rationales.
- C8 → every credit is a bounded per-year amount (largest per-year credit sum below the smallest discounted per-year component, smallest restore amount positive); zero extension years bill nothing by rule.
- C9 → payment-method, retention and win-back ladders removed; the always-constant restore-day term step removed; every remaining ladder's fall-through is reachable within its policy's scope.
- T0-R1 → closed by C1 (single reading of the grace-period renewal and extension amounts).
- T0-R2 → closed by C2 (the price-match amounts have one reading; base prices of the 2022 and 2024 lines unchanged).
- T0-R3 → closed by C9 (payment credits removed).
- T0-R4 → near-misses seeded for both price matches: cancelled Starter plan (status filter), 2024-11-12 deposit outside 12 whole months, 2021-08-30 manual line outside the period.
- T0-O1 → persona's refund-destination line now conditional on the agent saying money is coming back.
- T1-R1 → closed by C1.
- T1-R2 → closed by C2 (transfer and restore lines stay at their base prices; the price match refunds the Domain Care difference).
- T1-R3 → closed by C9 (payment credits, retention count and restore-day term step removed; the transfer and restore price matches carry four live factors each).
- T1-R4 → near-misses seeded: cancelled Starter plan, 2024-11-12 deposit outside 12 whole months.
- T1-O1 → persona's refund line made conditional.
- O1 / realism note → mailbox, certificate, card/PayPal, retention and win-back credits replaced by registrar/host dimensions: reseller tier, hosting-plan credit and plan allowance, reseller deposit volume, autopay saver, multi-year term credit, transfer price lock, late fee, early-restore/courtesy waiver, ERRP notice make-good.
- O2 → corrections no longer exist; the price match states it leaves the expiry date where it stands and the rollback clause is superseded only for it.
- O3 → unchanged (docstring names the restore day; no ordering word).
- O4 → the "never billed two such charges on one day" sentence stays as the stated tie rule of the price match.
- O5 → unchanged (the customer pays the extension in person; persona authorises it).
- O6 → the extension is stated as a one-domain order; the bulk rule is untouched and restated in the tails.
- O7 → zero extension years now bill nothing by an explicit rule sentence.
- O8 → unchanged (transfer/settings/registrant/AGP event types carry no computable figure; not used).
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- N1 → every price match's out-of-scope sentence names its three sibling price matches as set by their own rules and states the base refund rule only for every other refund.
- N2 → the price match no longer prices a line: it refunds the Domain Care credits the line earns today, never more than billed; no reseller discount or transfer/restore discount sits in any price match.
- N3 → each price match supersedes only clauses governing its own line type (full amount and destination for all; window, zero-window and rollback for grace/manual lines; cancellation-only bar for transfer lines; never-refunded bars for restore lines); registration and auto-renew windows are no longer retired and stand as vacuous satisfied preconditions in both tasks.
- N4 → plan allowance is an honest method in every scope (Business/Cloud: TLD price less registration_price, two tariff inputs; Starter/Plus/Pro: flat once; none); the restore-day price lock is now a parameter.
- T0-N1 → the grace-line and manual-line refunds follow N1/N2; the late fee reads the grace-line price match as the only standing refund.
- T0-N4 → lapsed_year_plan_allowance follows N4 (tariff-input method); late_fee stays the second method.
- T1-N1 → the transfer-line and restore-line refunds are the lines' Domain Care credits with no tier discount; the restore fee reads the restore-line price match only.
- T1-N2 → transfer_line / restore_line / restored_year / restore_day plan allowances follow N4; every computation keeps at least one honest method.
- T1-N4 → the restore's credits take an autopay credit in place of a tier step (no account-tier discount on a restore, as the base and the account charter say).
- O9 → volume thresholds 250 / 5,000 no longer coincide with tier minimums.
- O10 → closed with T1-N4 (no restored-year tier discount remains).
- O11 → ladder typo fixed.
- O12 → kept: the term factor's own line-years read is what grounds its tier in records (check_extended/check_compute require a record read in a factor binding); no scored value depends on the duplicate.
- Owner ruling → both user tools take checkout_method (paypal / new_card); both extension rules state the holder pays at Harborline's secure checkout after the agent quotes, never to the method on file; personas show the need (task 0: card on file declined, pays through PayPal; task 1: card on file near its limit, pays with a business card not on file).
- Probes → decoy (cancelled plan listed first) and absent (no active plan, missing notice) runs recorded in both dossiers; absent plan lowers credits with no floor added.
- Revision 1 C1–C9, T0/T1-R1..R4, observations → not reopened (tails, gate scope, years formula, subjects, restatements, bounded credits re-checked after regeneration; sweep clean).
- Proof/rationale text swept: dossiers carry a revision 3 record; stale Domain Care price, premium-tier and all-four-tier-discount wording removed.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- N5 → every Business/Cloud plan allowance (all eight policies) is "the amount by which" the TLD's price exceeds its registration_price, never less than plan_allowance_standard per year, so a negative or zero tariff difference (e.g. .co transfer_in_price below registration_price) never lowers the credits or puts a Business/Cloud plan below Starter; probe over .co/.us/.net with Cloud 8 and Starter recorded.
- N5 class sweep → the only other two-price difference, the transfer price lock (both extension policies), is stated as the amount by which renewal_price exceeds transfer_in_price and is nothing where it does not; the remaining subtractions are amount clamps already floored at zero by their rules; no floor creates an amount where nothing is owed.
- O17 → the "(the year is priced at the first-year registration price)" ladder phrase removed from every plan-allowance ladder and from the matching task tracing text.
- O3, O8, O12, O13, O14, O15, O16 → observations left as they are (no RED; O14 lock zero on .us now reads as the rule's own "nothing" tier; O16 history blocks stay dated).
- Revision 1–3 items → not reopened; both task worlds' scored figures and sensitivities unchanged; dossiers carry a revision 4 record; sweep clean.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- D1 → in all 8 policies the credits total is one generic sentence ("the credits below that apply …, added together") with no factor quantity listed; components say "the percentage discount that applies" instead of naming the reseller discount; every standard-computation sentence is generic ("no discount and no credit applies"; restore "no credit and no make-good applies"; price matches "no Domain Care credit applies to the charge, so nothing is refunded"), so each baseline is computable from its own sentences; the restore's assembly says "the make-good that applies"; combination-sentence order unchanged.
- D2 → every half-up rounding in every policy carries the XF 28 epsilon: the four renewal/restore components add 1e-7 in cent units before truncation and the eight results add 1e-9 dollars inside RND; checked against exact half-up for every renewal price, 1–10 years and tier percentages (the .co/.io 5-year Silver ties now round up); tool bodies already use the exact half-up helper.
- Class sweep → no other rounding, sum-of-factors sentence or factor-naming baseline sentence remains; compute_basis quotes re-pointed to verbatim phrases; sweep clean.
- Scores → no scored value, baseline, sensitivity or tier outcome moved in either task; dossiers carry a revision 5 record.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- N6 → in all 8 policies every quantity entering a credits total names itself, in its own factor sentence, as one of the credits of the result it reduces (hosting credit, plan allowance, volume credit, autopay credit, term credit and the restore-day transfer price lock: "…, one of the … credits, is …"; price-match quantities: "…, one of the charge's Domain Care credits, is …"); the reseller discount, late fee, restore fee and make-good stay outside the totals by their own sentences.
- XF 29 kept → each total reads "the amounts this rule names as one of the … credits, added together": no list of factor quantities is reinstated in any assembly sentence; combination-sentence order unchanged.
- O19 → the positional "the credits below" is gone from every rule; it survives only inside the dated revision 5 history record of the dossiers.
- account_tier_benefits (cross-product) → checked every discount/credit stack: the tier discount applies to the renewal component only (never ICANN, restore fee, refunds — the price matches and the restore carry none), no percentage is added to or compounded with another (base tails keep the bulk step as the higher of the two), discounted components are rounded half up before fees are added, the tier read is the account's tier on the charge date; every seeded domain and hosting row (pre-tier lines undiscounted, Bronze lines 3% domain / 10% hosting on the term price only) follows the tier recorded on its charge date; no extended overwrite touches an account-charter sentence.
- Scores → no scored value, baseline, sensitivity or tier outcome moved in either task; dossiers carry a revision 6 record.
REWORK round 6: gates 7/7 green
