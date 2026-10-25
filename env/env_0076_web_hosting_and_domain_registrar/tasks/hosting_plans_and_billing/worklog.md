# worklog — hosting_plans_and_billing (env_0076), M=2

Draws: task 0 prereq=1 factor_counts=[5,4]; task 1 prereq=1 factor_counts=[4,5].
frozen_time: task 0 `2026-10-18 11:20:00 CDT`; task 1 `2026-10-19 14:40:00 PDT`.

## Design route (why these four problems)
- Cancellation / withdraw / reactivate / settings events carry no amount, so they cannot be problems (each needs a
  4-6 factor computation). Customer-own numeric writes available: manual renewal ("a renewal the customer paid
  manually") and the upgrade purchase. hosting_sla_credit always triggers account:account_service_credit -> never written.
- task 0: root hosting_ext_cloud_upgrade (user, buy_hosting_upgrade_8645a072) <- hosting_ext_overdue_renewal
  (agent, bill_overdue_hosting_renewal_c53aa4e7). State form, affirmative: "An upgrade charge is fixed only after the
  plan's term end date is later than today."
- task 1: root hosting_ext_early_renewal (user, pay_hosting_renewal_early_31233d6b) <- hosting_ext_auto_renew_refund
  (agent, refund_hosting_auto_renewal_84b3efde). State form, negated: "An early renewal is not billed until the plan's
  term start date is on or before today."
- The two renewal rules split base hosting_renewal's pricing sentence by a disjoint record test (term end date on or
  before today / later than today); both tails name both cases (XF 16).
- Honest risk notes for the audit: base hosting gives few amount-varying rules, so several factors are Harborline
  schedule items introduced in params (bundle credits, late fee, outgrown incentive, uptime goodwill/reliability
  credits, advance-payment credit, the refund keep-backs). The refund keep-backs override base "refunded in full"
  (declared overwrite). Cloud 8 tariff numbers sit in the upgrade policy's params (DSL P() reads only the current
  tier) and equal the base Cloud 8 tier parameters. Two tools write hosting_renewal_charge (agent: overdue; user:
  early) — disjoint scopes, but a reviewer may read them as near-synonyms.

## Defining-sentence table (sentence -> binding -> owner)
| policy | sentence (short) | binding | owner |
|---|---|---|---|
| overdue | regular price for the current term length ... rounded | current_term_months, current_tariff, result rounding | baseline |
| overdue | scheduled term change request priced on the requested term | scheduled_term_request, overdue_tariff_price | ovr_term_tariff |
| overdue | reseller discount of the account tier ... rounded before credit/fee | account_tier_name, overdue_reseller_pct (+ overdue_discounted_price plain) | ovr_reseller_pct |
| overdue | domain bundle credit | bundled_domain_status/auto_renew, overdue_domain_credit | ovr_domain_bundle |
| overdue | mail bundle credit | primary_mail_seats, overdue_mail_credit | ovr_mail_bundle |
| overdue | late renewal fee (days late AND declined attempts < 1 month) | days_past_term_end, recent_declined_attempts, cycle_fully_declined, overdue_late_fee | ovr_late_fee |
| overdue | credits and fees fixed USD, never discounted | result | assembly (plain) |
| upgrade | Cloud 8 charge = (term price - paid) x remaining/term, rounded, >= 0; term price; amount paid; days | upgrade_term_months, paying_line_amount, earlier_upgrade_lines, paid_for_current_term, current_term_is_first, cloud8_term_list_price, remaining_term_days, whole_term_days, prorated_upgrade_charge | baseline |
| upgrade | reseller discount on the Cloud 8 term price | upgrade_account_tier, upgrade_reseller_pct (+ cloud8_term_price plain) | upg_reseller_pct |
| upgrade | share billed by term length (months / none / days) | remaining_whole_months, prorated_upgrade_share | upg_proration_unit |
| upgrade | outgrown-plan incentive | over_limit_notices, warning_notices, outgrown_incentive_pct (+ charge_after_incentive plain) | upg_outgrown_incentive |
| upgrade | uptime goodwill credit | latest_uptime_pct, uptime_goodwill_credit | upg_uptime_goodwill |
| refund | most recent auto_renew line; refund = its full amount, rounded | refunded_line_amount, result rounding | baseline |
| refund | processing cost by payment method | refunded_line_method, refund_processing_keepback | rf_processing_cost |
| refund | handling fee by days since charge | refunded_line_date, days_since_refunded_charge, refund_handling_keepback | rf_handling_age |
| refund | reversal fee for an applied scheduled change | refunded_line_start, applied_term_changes, applied_downgrades, refund_reversal_keepback | rf_change_reversal |
| refund | commitment share by months covered | refunded_line_months, refund_commitment_keepback | rf_commitment_share |
| early | regular price for billing_term_months ... rounded | early_billing_months, early_field_tariff | baseline |
| early | term from the line that paid the current term | paying_line_months, early_tariff_price | early_term_source |
| early | reseller discount | early_account_tier, early_reseller_pct (+ early_discounted_price plain) | early_reseller_discount |
| early | advance payment credit (days to end AND auto-renew) | days_to_term_end, plan_auto_renew_on, advance_payment_credit | early_advance_credit |
| early | certificate bundle credit | installed_cert_level, certificate_bundle_credit | early_cert_bundle |
| early | reliability credit | early_latest_uptime, reliability_credit | early_reliability |

## Factor-reads table (transitive, mechanical — /tmp/hosting_plans_and_billing_0076/probes.py)
Every factor of every policy: "reads other factors: none". Plain dependencies only: ovr_term_tariff -> current_tariff,
current_term_months; upg_proration_unit -> remaining_term_days, upgrade_term_months, whole_term_days;
rf_processing_cost -> refunded_line_amount; early_term_source -> early_billing_months, early_field_tariff.

## All-pairs method tier table (distinguishing input)
| factor | tier A vs tier B | distinguishing input / operation |
|---|---|---|
| ovr_term_tariff | 1-month request vs 12/24/36 request | single monthly rate (no x months) vs requested-term tariff x months |
| ovr_term_tariff | 12/24/36 request vs no request | requested term (data-selected tariff) vs current term tariff |
| ovr_term_tariff | 1-month request vs no request | single monthly rate vs current tariff x months |
| upg_proration_unit | 24/36 vs 1-month | MONTHS(today,end)/term months vs no proration (share 1) |
| upg_proration_unit | 24/36 vs 12 | whole months vs calendar days (DAYS) |
| upg_proration_unit | 1-month vs 12 | share 1 vs remaining/term days |
| rf_processing_cost | card vs PayPal | percent of the line + fixed vs flat fee |
| rf_processing_cost | card vs credit | percent + fixed vs nothing |
| rf_processing_cost | PayPal vs credit | flat fee vs nothing (PayPal tier is the only non-zero constant) |
| early_term_source | 1-month line vs 12/24/36 line | single monthly rate vs line-term tariff x months |
| early_term_source | 12/24/36 line vs no line | months of the paying line (history input) vs billing_term_months field |
| early_term_source | 1-month line vs no line | single monthly rate vs field tariff |

## T1/T2 (min/max shapes)
No lesser-of / max-of bound factors. MX(0, ...) floors are guards (not factors); they bind only on the skipped-
prerequisite worlds (task 0 upgrade on the ended term -> 0). T1 for every factor = factor_sensitivity (all move).

## Decoy / absent-record probe table (first-match / latest reads)
| read | probe | result | rule outcome |
|---|---|---|---|
| CFIELD domain bundled_hosting_id | domain absent | 961.78 | no credit, as stated |
| CFIELD email seat_count status=active | cancelled 2-seat decoy on same domain | 946.78 | decoy ignored (status) |
| CFIELD email | absent | 966.78 | no mail credit |
| LATEST change request scheduled | later withdrawn 36-month request | 946.78 | withdrawn never counts |
| LATEST change request scheduled | no scheduled request | 514.89 | current term tariff |
| COUNT declines < 1 month | prior-cycle (2025) decline decoy | 946.78 | outside window |
| LATEST auto_renew line (refund) | older 2025 auto_renew line present in seed | 515.69 | latest line taken |
| COUNT applied change requests | extra withdrawn term change | 515.69 | withdrawn ignored |
| COUNT applied change requests | none | 530.69 | no reversal fee |
| CPARAM ssl hosting_id status=active | live cert absent, expired decoy remains | 224.49 | expired ignored, no credit |
| LATEST uptime report | none | 226.49 | no reliability credit |
| outgrown notices < 1 month | storage over_limit 2026-09-18 (one whole month old) seeded | 699.04 | excluded -> warning tier |

## Events written and their base triggers
- bill_overdue / pay_early: hosting_renewal_charge -> hosting:hosting_term_renew (written in the same tool);
  account:account_credit_apply only when payment_method = account_credit (tools accept only card / paypal).
  bill_overdue also marks the scheduled term change request applied (term_renew semantics).
- buy_upgrade: hosting_upgrade_charge -> hosting:hosting_upgrade (variant change, same tool); account trigger only for
  account_credit (not accepted).
- refund: hosting_refund (refund_kind auto_renew_refund) -> hosting:hosting_term_rollback (same tool);
  account:account_credit_refund only when refund_destination = account_credit (tool fixes original_payment_method).
No write lands in another category.

## compute_basis verbatim sweep
/tmp/hosting_plans_and_billing_0076/sweep.py: every compute_basis quote, every baseline sentence, every
policy_source and every overwrite replaced_by is a verbatim substring of its rule -> `sweep bad= 0`.

## Gate log
- check_traceability run before any docs existed: only the four unlock tool-name misses (expected).
- Fixes during the run: phone not verbatim in persona; evidence lists lacked source paths; seeded cross ledgers
  unread (added domain/email charge and credit-ledger reads); overdue history floor (LATEST is not zeroed by the gate
  -> late fee evidence moved to a COUNT window); money-back gates retired for auto-renew refunds by scoped overwrites;
  early renewal multi-source tier.
- validate_scenario (scenario-wide): only "required document ... not found" for this difficulty (KB not rendered yet).

## Round 2 tables (supersede the round-1 tables above where they differ)
Factors now: overdue = ovr_reseller_pct (P, account), ovr_domain_bundle (P, domain), ovr_mail_bundle (P, email),
ovr_cert_bundle (P, ssl), ovr_late_fee (M); upgrade = upg_reseller_pct (P, account), upg_proration_unit (M),
upg_outgrown_credit (P), upg_dns_move_fee (P, domain); refund = rf_processor_fee (P), rf_handling_age (P),
rf_change_reversal (P), rf_commitment_share (M); early = early_reseller_discount (P, account), early_advance_credit (M),
early_domain_bundle (P, domain), early_mail_bundle (P, email), early_cert_bundle (P, ssl).
Factor-reads (transitive, /tmp/hosting_plans_and_billing_0076/probes2.py): every factor reads no other factor's binding;
assembly (credit caps, sums) lives only in plain bindings / result.
All-pairs method tiers:
| factor | pair | distinguishing input / operation |
|---|---|---|
| ovr_late_fee | per-day vs percent | days-late input x rate vs regular-price input x percent |
| ovr_late_fee | per-day / percent vs none | input-bearing vs zero (single zero tier) |
| upg_proration_unit | months vs whole difference vs days | MONTHS(today,end)/term months; constant share 1; DAYS ratio with term-days input |
| rf_commitment_share | 36 vs 24 | tariff input monthly_rate_no_commitment vs difference of two tariffs (renewal_rate_12mo - renewal_rate_24mo) x 12 |
| rf_commitment_share | 36/24 vs 12 | input-bearing vs zero (single zero tier) |
| early_advance_credit | >=30 days vs <30 days | whole months x per-month credit vs days x (12-month tariff / 365) |
| early_advance_credit | either vs auto-renew on | input-bearing vs zero (single zero tier) |
T1/T2: no lesser-of factor; MN() credit caps sit in result (assembly) and never bind on the task worlds.
Probe table (round 2): cancelled bundled domain listed first -> ignored (status filter); bundled domain absent -> no
credit; cancelled mail decoy -> ignored; extra active DV listed before the OV -> OV credit kept (EXISTS over OV/EV);
certificate absent -> no credit; no scheduled request -> current billing term; an older same-period renewal line ->
the most recently charged line is the paying line; primary domain not at Harborline -> unregistered DNS move fee;
task 1: live certificate absent with expired decoy -> no credit; extra active OV -> OV credit; mail absent -> none;
deleted bundled decoy first -> ignored.
Events/triggers unchanged: renewal charge -> term_renew (same tool), account trigger only for account_credit (tools take
card/paypal); upgrade charge -> upgrade; refund -> rollback, account trigger only for account_credit destination (tool
fixes original_payment_method). compute_basis/baseline/policy_source/replaced_by verbatim sweep: `sweep bad= 0`.

## REWORK round 2 claims
- P-1: both renewal rules now carry the same three-way case list (holder-paid at checkout, term end on/before today, no
  scheduled downgrade -> overdue; holder-paid, term end later, no scheduled downgrade or term change -> early; every
  other renewal = auto-renew charge, downgrade-applying renewal, early renewal with a scheduled term change -> base).
- P-2: the early rule now follows base "The new term length is the current one" (billing_term_months, early scope
  excludes scheduled term changes); the refund rule states the roll-back restores the earlier term's billing length
  and the refund tool restores it; the paying-line term source is gone.
- P-3: the upgrade's reseller discount acts only on the Cloud 8 term price (the list price component the base upgrade
  rule names), the rule says no percentage is ever applied to the prorated line, and the outgrown incentive is now a
  fixed credit, so no percentage compounds with the tier discount.
- P-4: kept as declared scoped overwrites, now stated as what they retire: base's structured money-back window/quota
  gates apply_to every hosting_refund row and the downgrade-fit gate to every term renewal; the replaced_by sentences
  restate the in-force content and limit it to money-back refunds / downgrade-applying renewals.
- P-5: bundled-domain reads filter status active (cancelled/deleted never count); certificate tier uses EXISTS over the
  OV/EV products plus the active level (OV/EV wins); the upgrade's paying line is the most recently charged renewal
  line with the term start (else the initial_term line); the early paying-line MAX is removed.
- P-6: overdue/early/upgrade credits are capped at half the discounted/prorated price in the combination sentence; the
  24/36-month proration tier requires a whole month remaining (else days ratio); every tool rejects non-positive amounts.
- P-7: the early edge's effect text is now general (earlier term's end date and billing length, auto-renew off).
- F-1: ovr_term_tariff removed; the scheduled term change is base content in the overdue baseline; overdue's method is
  ovr_late_fee (per-day vs percent vs none); ovr_cert_bundle (ssl) added.
- F-2: early_term_source removed; early's method is early_advance_credit (per-month vs per-day tariff share vs none);
  early_domain_bundle and early_mail_bundle added.
- F-3: rf_processing_cost replaced by rf_processor_fee (parameter: processor percentage by payment method);
  rf_commitment_share is the refund's method (tariff vs tariff-difference vs none).
- F-4: both uptime credits removed (and the uptime report seeds); upgrade gains upg_dns_move_fee (domain nameservers),
  early gains the bundle credits above.
- T-1: tools enforce positive amounts, the refund line must be an auto_renew line of the plan, a named request must be
  the plan's scheduled term change, the upgrade target must be an official tier name.
- Owner ruling: the overdue renewal and early renewal tools are owner=user payments at checkout; each rule states the
  payment is the holder's own act; personas show the necessity (task 0 stored card expired and PayPal; task 1 PayPal,
  not on file); the upgrade stays owner=user (PayPal checkout).
- O-observations: O-1 kept (domain credit by auto-renew); O-2 kept (one-month decline window); O-3 kept (refund tool
  fixes original payment method to stay inside the category); O-5/O-7 moot after seed edits; O-8 basis added.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- P-5 (residue, upgrade same-day tie): the amount paid is now taken by charge type, not by date order: the checkout
  renewal line (charge_type renewal) with the term start, else the auto_renew line, else the initial_term line; the rule
  states why (a refunded line is always an auto_renew line, since a manually paid renewal is never refundable). Probe:
  a same-day auto_renew line for the new term no longer changes the read.
- N-1 (upg_dns_move_fee): removed with its unrecorded IP-change framing; the upgrade's fourth factor is
  upg_welcome_credit (Harborline's first-upgrade welcome credit read from the plan's upgrade_proration history:
  none ever / only earlier terms / one in the current term), capped with the outgrown credit at half the prorated charge.
- N-2 (early_advance_credit): the per-day-of-tariff tier is gone; the factor is now a flat published early renewal credit
  (parameter: auto-renew off and 30+ days ahead / auto-renew off and under 30 days / auto-renew on), monotone in days.
  Early's method factor is now early_domain_bundle (method: bundled domain on auto-renew -> its TLD renewal_price plus
  ICANN fee; auto-renew off -> renewal_price alone; none -> no credit). The same class is applied to overdue's
  ovr_domain_bundle so both sibling renewal rules credit the bundled domain alike; the sentence says the domain is still
  billed at its normal renewal price under the domain charter.
- N-3 (task 1 seed): the bundled registration is now jandreauweb.com (.com, free_with_hosting_eligible true) with its
  charges priced by the domain charter (18.18 card, then 17.64 from credit with the matching ledger apply); the primary
  domain jandreauweb.ca stays registered elsewhere, so the mail subscription carries no Harborline domain link.
- Revision-1 items re-checked, none reopened: P-1 tails unchanged; P-2 early term = billing_term_months; P-3 no
  percentage on the prorated line, all upgrade adjustments fixed credits; P-4 overwrites kept (accepted in revision_2);
  P-6 credit caps in every combination sentence, positive-amount checks in tools; P-7 general effect text; F-1/F-2/F-3
  method factors = ovr_late_fee, ovr_domain_bundle, upg_proration_unit, rf_commitment_share, early_domain_bundle (each with
  at most one zero tier and distinct inputs per pair); F-4 no uptime factor anywhere; T-1 tool checks unchanged.
- Whole-charter class sweep: every LATEST/first-match read re-probed (scheduled request by submitted_at, one per plan;
  refund's latest auto_renew line, one per term; paying line by charge type; bundled domain/email/ssl with status filters
  and OV/EV EXISTS); no rule sentence asserts an unrecorded fact; no factor reads another factor (probes3.py); compute_basis
  verbatim sweep `sweep bad= 0`; proof/rationale/necessity text swept for stale figures and terms.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- N-4 (domain bundle credit, ovr_domain_bundle and early_domain_bundle): the ICANN 0/1 term and the auto-renew condition
  are gone. The credit now follows what the records hold: a renewed bundled registration is credited the amount of its
  most recent domain renewal charge line (as the domain charter billed it, account discount included); a bundled
  registration still in its free first year is credited its TLD's renewal_price; no active bundled registration -> no
  credit. Method shape: history input vs tariff input vs zero (one zero tier). The framing sentence now states exactly
  that basis and that the domain is still billed under the domain charter. Applied identically to both sibling renewal
  rules (class closed). Probes: free-first-year bundled domain -> list price; a later renewal of a non-bundled domain is
  ignored (read keyed on the bundled registration's domain_id); cancelled/deleted bundled decoys ignored; absent -> none.
- upg_welcome_credit kept (accepted in revision_3 as a real first-upgrade promotion).
- Earlier items re-checked, none reopened: P-1 tails, P-2 early term, P-3 no percentage on the prorated line, P-4
  overwrites, P-5 paying line by charge type, P-6 caps and positive-amount checks, P-7 general effects, F-1/F-2/F-3
  method factors (ovr_late_fee, ovr_domain_bundle, upg_proration_unit, rf_commitment_share, early_domain_bundle), F-4 no
  uptime factor, T-1 tool checks, N-1 no DNS fee, N-2 flat early renewal credit, N-3 .com bundle seed.
- Whole-charter sweep for the classes of revisions 1-3: no rule sentence asserts a fact the records do not hold; no
  method tier is a constant multiplier of another; every first-match/latest read probed with decoy and absent rows; no
  factor reads another factor; compute_basis verbatim sweep `sweep bad= 0`; proof/rationale/necessity text swept for
  stale figures and terms.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- N-5 (domain bundle read, both renewal rules): the rule now credits one year of the bundled domain's renewal and says
  exactly which line counts: the registration's most recent domain renewal charge line, divided by the years it renewed,
  only when that line carries no refund and no restore charge line is dated later than it; any other active bundled
  registration (free first year, refunded latest renewal, restored from redemption after it) is credited its TLD's
  renewal_price; no active bundled registration -> none. Compute reads the line's years, its id (XCOUNT of domain_refund
  lines pointing at it) and the latest restore date. Probes (scratch probes5.py / probes5b.py, both tasks): 2-year
  renewal line -> per-year amount; refunded latest renewal -> list price; restore dated after the renewal -> list price;
  decoys (refund of an older renewal line, restore dated before the renewal) -> per-year amount of the latest line;
  free first year -> list price; non-bundled domain's later renewal ignored; absent -> none. Task values unchanged.
- Earlier items re-checked, none reopened (P-1..P-7, F-1..F-4, T-1, N-1..N-4); compute_basis verbatim sweep
  `sweep bad= 0`; no factor reads another factor; task proof/necessity text updated to the new tier wording.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- N-6 (domain bundle per-year credit, both renewal rules): the rule now states the per-year share is rounded half up to
  the cent (compute RND on that division), and states the same-day tie: a most recent renewal charge line counts only
  when it is the only renewal charge line on its charge date; two or more renewal lines on that date send the
  registration to the TLD renewal_price tier (compute XCOUNT on that date). Probes: two renewal lines on the latest date
  -> list price; a 3-year line with a non-cent per-year share -> rounded per-year amount; earlier refund/restore/
  multi-year/free-year/decoy probes unchanged.
- Cross-product account_tier_benefits check (coordinator line): the Cloud 8 upgrade line is an upgrade_proration line,
  on which the account charter never applies a tier discount; the upgrade rule now prices the Cloud 8 term price with no
  account tier discount, declared as a scoped overwrite of the base hosting_upgrade_proration sentence ("less the
  account tier's hosting_discount_pct"), and the reseller factor of the upgrade is removed and replaced by
  upg_mail_bundle (parameter, email seats on the primary domain, same published mail bundle schedule as the renewals).
  Every other stack checked: renewals take the tier discount on the renewal price component only, the discounted price
  is rounded half up before any fixed credit or fee, credits and fees are fixed USD amounts, no product percentage
  stacks with a tier percentage, the refund takes no tier discount, benefits follow the tier on the charge date; seeded
  cross rows (domain renewals with the renewal discount on the renewal_price component only and the ICANN fee
  undiscounted, the SSL purchase at the single tier percentage, email at 0 percent on Business-tier dates, hosting
  auto-renewals at the tier recorded on their charge dates) comply. This moves the task 0 upgrade value (unavoidable).
- Earlier items re-checked, none reopened; compute_basis verbatim sweep `sweep bad= 0`; no factor reads another;
  task text swept for the removed reseller-on-upgrade wording.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- N-7 (upgrade overwrite of the base new-term-price sentence): the replaced_by is now scoped. For every upgrade other
  than the Cloud 4 to Cloud 8 upgrade this rule prices it restates the in-force base content (target tier's rate for the
  current term length times its months, less the account tier's hosting_discount_pct, as the hosting upgrade rule and
  its new_term_price parameter state, with the introductory / regular / 1-month cases); for the in-scope upgrade it
  states that the Cloud 8 term price takes no account tier discount and that the new_term_price parameter description
  does not apply, because the account charter never applies a tier discount to proration lines. No task value moves.
- Cross-product account_tier_benefits check repeated: renewals discount the renewal price component only and round it
  before fixed credits/fees; the in-scope upgrade (a proration line) takes no tier discount; the refund takes none; no
  product percentage stacks with a tier percentage; seeded cross rows unchanged and compliant.
- Earlier items re-checked, none reopened; compute_basis verbatim sweep `sweep bad= 0`.
REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- S1 (renewal overwrite tails): both renewal rules' replaced_by now restate the full in-force base content for every
  other renewal: regular rate of the tier and term length the new term will have (renewal_rate_12mo / 24mo / 36mo times
  the months, or monthly_rate_no_commitment for a 1-month term, with no setup fee), less the account tier's
  hosting_discount_pct, rounded half up to the cent; the two tails stay identical case lists.
- S2 (refund destination, rule vs tool): the refund rule keeps the base destination sentence and now states its own
  scope: it books only the refund of an auto-renew line paid by card or through PayPal back to that payment method; an
  elected account-credit refund and the refund of a credit-paid line go to account credit and are credited under the
  account charter's refund-credit rule, not booked under this rule. The tool docstring and body say the same (a line not
  paid by card or PayPal is rejected). The processor-fee ladder now stays inside that scope: card after the charge date /
  PayPal after the charge date / refunded on its own charge date (a voided payment, no fee).
- Sweep of every overwrite and every tool-vs-rule destination/enum: the renewal and upgrade rules now state the
  checkout payment is by card or through PayPal (a payment from account credit is not taken under the rule), matching
  the tools' payment_method enum; the upgrade overwrites (charge formula; new term price) are scoped; the refund
  overwrites (window, money-back gates) restate their in-force content. Probes: same-day void and PayPal-paid lines
  follow the rule; no task value moves.
- account_tier_benefits re-checked across every stack and seeded cross rows: compliant.
REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- N-8 (refund policy's overwrite of base hosting_auto_renew_refund): the replaced_by is now scoped like the rule: the
  window is restated for every auto-renew refund; the keep-backs apply only to a refund this rule books (a line paid by
  card or through PayPal returned to that payment method); the refund of a credit-paid line, or one the customer elects
  to take as account credit, is restated as refunded in full and going to account credit as the base rule states. The
  base destination sentence stays restated verbatim in the rule. No task value moves.
- account_tier_benefits re-checked: the refund takes no tier discount; all other stacks and seeded cross rows unchanged
  and compliant. Earlier items re-checked, none reopened; compute_basis verbatim sweep `sweep bad= 0`.
REWORK round 9: gates 7/7 green
