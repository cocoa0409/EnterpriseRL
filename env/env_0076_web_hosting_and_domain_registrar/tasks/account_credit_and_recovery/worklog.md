# worklog — account_credit_and_recovery (env_0076)

## Round 1
Delivered 8 policies / 8 tools / tasks 0-1 (see plan.md). Policy-task audit revision_1: RED (C1-C10, T0-F1..F4, T1-F1..F6).

## REWORK round 2 — plan (written before editing)
- C1: the withdrawal root is dropped. Goodwill is never withdrawable, so no goodwill edge can feed a cash return honestly.
  Task 0 root becomes a prefund deposit (holder's own payment) that covers the auto-renew charges credit-first will draw in
  the next 14 days (the plan's renewal, the certificate on the plan, the plan's free domain), each priced the way the
  owning charter bills it on its attempt day. Posted goodwill is spendable credit and lowers the deposit honestly.
- Task 1 root stays a top-up for a declined domain auto-renew retry, re-priced at the published renewal price with
  tier discount and ICANN fee, competing credit-first draws (hosting renewal, email instalment/renewal, certificate)
  priced likewise; refused-in-full limits carried.
- C2: late-reset goodwill posts against the security-change notice reference; late refund-posting goodwill posts against
  the refund line reference; sentences name those references.
- C3: review trigger "more than 7 calendar days" (beyond any 2-business-day span with a holiday); certificate lateness
  counted from documents complete (organisation validation date, order date for DV) with "more than 9 calendar days".
- C4: every schedule owes nothing when its limited amount is zero; every prerequisite sentence carries the condition that
  the yearly goodwill total is below the tier's yearly limit.
- C5..C10, C7, C8, C9 and task items: closed per policy (see claims section at the end).

## REWORK round 2 claims
- C1: withdrawal root and its tool removed; task 0 root is a prefund deposit that goodwill lowers as spendable credit; no rule nets goodwill into cash.
- C2: reset goodwill posts against the security-change notice reference and refund-posting goodwill against the refund line reference; every prerequisite sentence names a reference kind only one schedule posts against.
- C3: review trigger set beyond any business-day review span (more than 7 calendar days, approved requests only); issuance lateness counted from complete documents (organisation validation for OV/EV, order for DV) with a 9-calendar-day threshold.
- C4: every schedule owes and posts nothing when its limited amount is zero; every prerequisite sentence waits only while the yearly goodwill total is below the tier's yearly limit.
- C5: the certificate prerequisite sentence and condition name the active subscription, matching the schedule's scope.
- C6 (a): review schedule reads approved requests only. (b): issuance read from the initial issuance event and the new-subscription charge's years and period. (c): plan/certificate/email selections scoped by exact single-order tests or the most recent initial-term line unique on its date. (d): same-date ties are stated and computed as out of scope for the duplicate and refund-posting schedules. (e): "no more than N days after today" computed as 0..N everywhere; next attempt/retry days follow the charters' offsets. (f): the reset date is a recorded security-change notice, and the schedule stands aside unless exactly one such notice falls in the two-month window. (g): top-ups and prefunds above max_deposit_per_transaction or the balance cap are refused in full (result 0).
- C7: every method factor now passes the shape test (tariff or operation differences); duplicate_basis middle tier is a flat tariff; retry_estimate/competing_holdback/renewal_hold removed.
- C8: R1 release_share, R2 signin_reserve, R3 renewal_hold/competing_holdback, R4 free_domain, R5 card_fallback, R6 declined_renewals, R7 renewals_declined, R8 refund_kind, R9 validation_failures, R10 card_failure_buffer, R11 expiry_buffer, R12 retry_estimate all removed; replaced by published prices (term rates, per-year certificate prices, TLD renewal price and ICANN fee, restore fee, seat prices), reseller discount bands, the money-back and refund windows, Harborline-DNS auto-validation, refund route and priority-support posting promise.
- C9: card_failure_buffer removed with its scope-restating condition.
- C10: goodwill tools refuse a malformed reference (order number format or empty/space-padded reference); deposit tools refuse a non-deposit funding method; the deposit-reference withdrawal tool is gone.
- T0-F1: closed by C1 (no cash-out reading exists).
- T0-F2: lockouts outside the two-month window seeded as the near-miss of the review schedule.
- T0-F3: closed by C7.
- T0-F4: closed by C8 (R1-R6 members removed from task 0).
- T1-F1: failed DCV rows removed; validation shown passed on Harborline DNS.
- T1-F2: near-misses seeded — organisation validation a week after the order (order-date reading lands in the weekly tier) and a later refund to the card (not to credit).
- T1-F3: closed by C7.
- T1-F4: closed by C8/C9 (R3, R7-R12 removed from task 1).
- T1-F5: .ca auto-renew lines re-dated to 35 days before expiry.
- T1-F6: proof text rewritten; no claim of one schedule per reference kind remains unproven.
- Observations: plan_class kept (a tier difference in what the plan is worth to the customer); review/reset severity ladders now ordered the same way (both > email change > two-factor only); duplicate middle tier no longer repays the refunded amount; persona no longer previews holdbacks; blueprint summary vs owner=user deposits noted as deliberate.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- C3 (certificate member): allowed_issue_days raised to the longest calendar span five business days can take (Christmas/New Year inside two weekends), framing sentence now says no span is longer than it, so an EV issued on target is never late; task-1 issuance seeded two days later so the tier taken is unchanged; P-TU prerequisite sentence and condition updated verbatim.
- C6 (f): P-RD keys the reset on records: an approved request decided inside the two-month window, the only security-change notice dated on or after that decision, and a sign-in that shows the requested change (login_email = new_login_email / two_factor none); P-TU sentence and condition restated; probes (own email change, old decision, notice before decision, second notice) all fall outside.
- C7 (new members): every per-term / per-years / per-plan price ladder is now labelled parameter; the methods left are free_domain_charge (restore adds restore_fee, renewal applies the rounded component discount, nothing) in P-PF and site_security_charge (max-pick of hosted-site and tier percentages / tier percentage alone / nothing) in P-TU.
- N1: all six reseller-discount ladders removed; tier discounts are plain rule sentences of each counted charge, following account_tier_benefits and the owning charters; mechanical check finds no ladder with two equal outcomes.
- N2: no factor reads or duplicates another factor's binding (mechanical sweep over all eight policies; the latent P-CD member, a covered-domain read duplicated by site_coverage and validation_route, is now one plain binding).
- N3 (a): plan renewals follow the term of a scheduled term change, scheduled downgrades, email instalment plans and scheduled email product changes put the customer outside the policy, renewals count scheduled seat counts, Microsoft 365 is never discounted, security plans use the higher of hosted-site and tier percentages, servers with add-ons are outside P-TU, certificates renew for the last term capped at max_subscription_years.
- N3 (b): P-PF and P-TU purpose sentences list exactly the counted charges and state that charges of any other holding are not counted; the baseline paragraph of P-TU no longer claims to cover other charges; P-TU now also stands aside when two declined attempts share the latest time.
- N4 (a): P-PF's purpose now names the grace-period renewal or restore the holder pays from credit, so the restore tier is a charge the prefund is for, not an auto-renew it waits on.
- N4 (b): priority_posting removed; replaced by renewal_exposure (active plan / active domain with auto-renew on, which draw on credit first); the PayPal/card election tiers no longer assert processing times.
- N5: P-DU funding_route merges payment and refund destination into three reachable tiers (card->card, card->credit with its ledger refund entry, otherwise credit-paid); P-RP credit_election tiers PayPal / card / otherwise credit-paid, all reachable.
- T0-R2-1: P-PF has five factors, four parameter (plan term rate, certificate renewal price, security plan charge, email renewal charge) and one method (free domain), all load-bearing; P-DU has four (basis, size, funding_route, partner_standing on the tier recorded on the charge date).
- T0-R2-2: certificate charge relabelled parameter and moved off its fall-through by a two-year last term seeded from 2024 with its 200-day issuance chain.
- T0-R2-3: near-misses seeded — P-PG: the free domain on external nameservers (site_outage reads the primary domain) and the scheduled 24-month change (term_commitment reads the current term); P-DU: the same-day twin paid from credit while the refunded duplicate went to the card.
- T1-R2-1: P-TU has five factors (plan term, email plan, server term, certificate years as parameters; security charge as method), all load-bearing; P-RP four (basis, size, election, renewal_exposure).
- T1-R2-2: P-TU's method is site_security_charge; no mislabelled price ladder remains.
- T1-R2-3: priority_posting and its invented posting promise removed.
- Revision_1 re-check: C1 (no withdrawal), C2 (six distinct reference kinds), C4 (zero room posts nothing), C5 (active subscription), C6 a-e/g, C8, C9, C10 still hold; probe table in scratch probe_r3.out (52 cases); compute_basis quotes verbatim (sweep 0); worlds priced on their dates with complete ledgers (new SiteGuard, Mail Pro, VPS, DV and OV rows).
- Sweep of every class named in either revision done over all eight policies before these claims (A1/N2 mechanical, N1 equal outcomes, N5 reachable fall-throughs, C6 first-match/tie reads, N3 owning-charter clauses).
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- R3-1: P-DU partner_standing now reads, in every rule sentence, ladder tier and compute_basis quote, the account's current tier together with its tier changed date on or before the duplicate's charge date; an account whose tier changed after that date adds nothing whatever tier it held before — rule words equal compute, decidable from the account record alone; task values unchanged.
- Sweep of tier-as-of-date readings: no other policy states a tier held on a past date (P-PF and P-TU discount on the current tier with tier reviews in grace or downgrade-due scoped out); quotes verbatim, factor-independence sweep clean, probes rerun.
- Revision_1–3 items: unchanged and still closed (no other charter edit).
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- S1: the combination sentences of account_ext_duplicate_renewal_goodwill and account_ext_refund_posting_goodwill now add the fixed uplifts to "the duplicate-charge goodwill figure" / "the late-posting goodwill figure", naming no factor's quantity; order (uplifts, then limits, then one rounding) unchanged.
- S2: pf_cert_end, pf_cert_due and pf_cert_years are now bindings of certificate_renewal_price; class sweep (plain binding read only by one factor and not by any baseline) found and moved one more member, tu_plan_id, into plan_renewal_term; sweep now clean on all eight policies.
- K1 (source side): P-PF's coverage text is bound — the window and website-running purpose to a plain pf_window binding read by every due test, and "charges of any other holding are not counted" moved into the scope sentence owned by pf_in_scope; no unowned coverage sentence remains for a computation document.
- K2 (source side): P-TU's credit-first coverage sentence is owned by a plain tu_count_window binding (the window every counted charge's due test reads); no unowned coverage sentence remains.
- K3: renderer item; no source sentence carries a worked example or a scored figure.
- Cross-product account_tier_benefits check: every discount stack complies — tier discount on the list/renewal component only, ICANN and restore fees never discounted, Microsoft 365 never discounted, security takes the single higher of hosted-site and tier percentages, ssl renewals take no volume discount, components rounded half up before fees; seeded cross-product rows (registrations, renewals, SiteGuard, Mail, VPS, certificates) priced the same way on their charge-date tier.
- Quotes verbatim, factor-independence and probes rerun; no scored value moved.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- S3: the email charge counted by the prefund and the top-up is now the published email term renewal (the renewal of an active subscription falling due on its term end date): renewed seats are the lower of the scheduled seat count and the seat count, never fewer than the mailboxes in use (seat count less the idle seats of the current term, deletions less their restores, counted by the published whole-calendar-month test), and otherwise the mailboxes in use; price column and account-tier rate as published (Microsoft 365 never discounted). Task 0 now seeds the mailbox history behind its scheduled reduction (one deletion in the term, one deletion restored as a decoy), so the renewed seats and every scored value are unchanged; task 1 has no deletion and is unchanged. Probes: no deletions, prior-term deletion, no scheduled count, scheduled count below the mailboxes in use.
- S4: per the coordinator ruling, the certificate renewal counted by the prefund and the top-up is paid from the credit the deposit provides, and both rules now say so and price it at the ssl charter's renewal price (tier price for the renewed years plus names, tier ssl discount, no volume ladder); no card-paid certificate renewal is counted; values unchanged.
- Cross-product account_tier_benefits re-check: every discount stack (hosting, ssl, domain, email, security, server) and every seeded cross-product row complies; no account-charter sentence is overwritten.
- No scored value or sensitivity moved in either task; quotes verbatim, factor-independence and single-factor-binding sweeps clean.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- Coordinator ruling (one price per renewal whatever pays it), certificate: the certificate auto-renewal counted by the prefund and by the top-up is now priced by the published ssl auto-renew rule — years of the latest term line (latest renewal or auto-renew line, else the purchase line) capped at the product maximum, tier ssl discount on the certificate price component only, extra names at the multi-year name rate and bands without the tier percentage, the reduced amount rounded before the OV/EV re-vetting fee is added and the Harborline domain credit taken off, then rounded; the round-6 base-renewal wording is withdrawn. Scored values moved: task 0 prefund (OV re-vetting fee and Harborline-DNS credit) and task 1 top-up (Harborline-DNS credit on the DV); goodwill values unchanged.
- Re-check of every other counted charge against the published rules: hosting auto-renew (regular rate of the new term, scheduled term change), domain auto-renew (component discount, ICANN never), email term renewal (round-6 seat basis), SiteGuard renewal (higher of hosted-site and tier percentages) and server renewal (term price, tier discount) match; the prefund's grace-period renewal and restore of the free domain did not (both are priced by the domain charter's own published rules), so a free domain in grace or redemption now puts the customer outside the prefund and the free-domain renewal is a plain charge.
- Factor shape after that change (draw unchanged, P-PF still five): the email renewal splits into email_renewed_seats (method: lower-of pick with the mailboxes-in-use floor / seat count less idle seats / seat count, the published rule) and email_seat_price (parameter by billing plan); the certificate keeps its years ladder with all auto-renew-rule bindings inside its own factor; factor-independence and single-factor-binding sweeps clean.
- Sensitivities and proof text recomputed for both tasks (task 0: every prefund figure; task 1: every top-up figure); probes rerun (re-vetting edge at 33 days, external-nameserver credit, multi-domain bands and multi-year name rate, grace/redemption out of scope).
- Cross-product account_tier_benefits check: tier discount only on the price/renewal component (never names on an ssl auto-renew, ICANN, restore or Microsoft 365), single higher percentage on SiteGuard, rounding of discounted components before fees and credits; seeded rows unchanged and compliant.
REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- F1: both certificate sentences (prefund and top-up) now define the reduced amount as the reduced certificate price component together with the extra-name amount, rounded half up once before the re-vetting fee and the Harborline domain credit, then rounded again — the grouping compute uses and the published ssl rule states.
- F2: the published ssl rule defines the re-vetting fee only by the organisation-validation age, so the compute branch that added the fee when no validation date is recorded is dropped in both policies; without a recorded date the age test is not met and no fee is added, as the rule words say (probe added).
- No scored value moved; quotes verbatim, factor-independence and single-factor-binding sweeps clean; account_tier_benefits stacks unchanged and compliant.
REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- S5: the prefund's email charge is again one family factor, email_renewal_charge (method), owning the published seat bases (lower of scheduled and current seats with the mailboxes-in-use floor / seat count less idle seats / seat count) and the seat price of the billing plan, with a not-counted fall-through; no plain binding multiplies two factors' outputs, as in the top-up's single email factor.
- Draw kept (five factors, at least two parameter, one method): the certificate auto-renew charge's price component becomes plain (baseline; the published ssl auto-renew rule), and its two published fixed terms become the counted-charge levers — certificate_revetting_fee (EV fee / OV fee / none, by product and organisation-validation age) and certificate_domain_credit (Harborline DNS credit / external-nameserver credit / none, by the covered domain) — each with three distinct outcomes on producible worlds, passing T1 and T2.
- K4 (source side): with S5 closed no factor sentence names a quantity defined in another factor; the email factor sentence carries its own seats and seat price.
- Class sweep: a factor-alone-against-all-baseline check over all eight policies on both worlds shows every factor moving its result except two top-up factors held at the minimum deposit on task 1's balance (a floor, not a dependency on another factor; they move on any producible world above the minimum); quotes verbatim, factor-independence and single-factor-binding sweeps clean; probes unchanged.
- No scored value moved; prefund sensitivities and dossier text recomputed; account_tier_benefits stacks unchanged and compliant.
REWORK round 9: gates 7/7 green
