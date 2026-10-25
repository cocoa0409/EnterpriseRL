# worklog — ssl_certificate_lifecycle (env_0076), M=2

## Progress
- plan.md written; draw: task0 [1 prereq; 5,4], task1 [3 prereqs; 5,5,5,4].
- task 0 (ssl_ext_coterm_order <- ssl_ext_support_renewal): per-task gates green
  (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK).
  Pre-docs traceability: only the two unlock tool-name misses (expected before the KB exists).
- Fixes during task 0: replay closure (added find_ssl_events / find_account_credit_ledger / find_domain_charges reads
  so every seeded row is read); solvability (renewal evidence lists certificate_id; co-termed order takes customer_id;
  subject narrowed to ssl_order; ssl_agg_multi_holding policy_scope; seed rows per ssl event); compute history floor
  (purchase-line years read with MAX, the purchase line being unique per subscription).
- task 1 (ssl_ext_install_charge <- auto-renew, wait credit, added name): per-task gates green on first assembly
  (EXTENDED OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); task 0 re-gated green after the shared
  charter grew (sibling overwrite tails updated in the support renewal and co-termed order rules).

## XF_recipe sweep (applied to all six policies; scratch scripts in /tmp/ssl_certificate_lifecycle_0076/)

### Defining-sentence table (sentence -> binding -> owner)
| policy | sentence (head) | bindings | owner |
|---|---|---|---|
| coterm | "The co-termed charge is price_1yr plus additional_name_price_per_year ... divided by days_per_year, rounded ..." | days_left, n_extra, name_rate, annual_amount, day_weighted | baseline |
| coterm | "The per-year rate of a co-termed charge follows the length of the co-termed term ..." | term_rate | term_class_co |
| coterm | "The extra names of a co-termed charge whose co-termed term is longer than band_min_term_days ..." | names_part | san_bands_co |
| coterm | "The co-termed discount percentage follows the tier ..." | acct_tier, co_disc_pct | acct_tier_co |
| coterm | "A co-termed order whose sibling is an EV product ..." | reuse_credit | org_reuse_co |
| coterm | "A co-termed order whose sibling's domain_id names a Harborline domain registration ..." | dom_status, dom_auto, co_dom_credit | dom_bundle_co |
| coterm | "Every percentage reduction acts once on the day-weighted amount ..." | reduced_amount, result | assembly (generic) |
| support renewal | "A support renewal extends ... by one year ... list amount is price_1yr plus ..." | n_extra, name_rate | baseline |
| support renewal | "The term of a support renewal follows the years of the subscription's latest term line ..." | ren_line_years, pur_line_years, list_amount | term_years_ren |
| support renewal | discount / re-vetting / renewal domain credit sentences | acct_tier+ren_disc_pct / revet_fee / dom_status+dom_auto+ren_dom_credit | acct_tier_ren / revetting_ren / dom_bundle_ren |
| auto-renew | "An auto-renew charge renews ... for the years of its latest term line ... list amount ..." + "The latest term line is ..." | n_extra, name_rate, term_years, year_price, list_amount | baseline |
| auto-renew | bands / discount / re-installation / domain credit / automatic validation credit sentences | names_part / acct_tier+ar_disc_pct / live_installs+reinstall_fee / dom_status+dom_auto+ar_dom_credit / dom_ns+dns_credit | san_bands_ar / acct_tier_ar / managed_reinst_ar / dom_bundle_ar / dns_validation_ar |
| added name | "Names are added one name to an order ... per-name part ... handling fee name_handling_std ..." | n_extra, name_rate, per_name_part | baseline |
| added name | per-year price / paid end / handling / re-installation / name domain credit sentences | nm_rate / paid_end+days_counted / dom_ns+handling_fee / live_installs+nm_reinstall / dom_status+dom_auto+nm_dom_credit | nm_band_rate / nm_paid_period / nm_dns_handling / nm_reinstall / nm_dom_bundle |
| wait credit | "The validation-wait credit is the number of calendar days from the order date ..." | first_cert, raw_wait | baseline |
| wait credit | anchor / multiplier / reseller days / registration days / goodwill share sentences | waiting_days / wait_mult / acct_tier+sla_days / dom_ns+reg_days / goodwill_amt+goodwill_share | wait_anchor_wc / long_wait_wc / sla_days_wc / reg_days_wc / goodwill_settle_wc |
| wait credit | "The waiting days are first multiplied, the added days are then added, and that total is multiplied by the share ..." | credit_total, result | assembly (generic) |
| installation | "... the installation charge is installation_fee for the one certificate installed ..." | list_amount (fee) | baseline |
| installation | cycles / repeat rate / discount / bundle sentences | cycle_days+dom_ns+certs_covered / live_installs+rate_pct / acct_tier+inst_disc_pct / mail_variant+bundle_credit | inst_cycles_mi / repeat_rate_mi / acct_tier_mi / mail_bundle_mi |

### Factor-reads table (transitive) — sweep.py output
No factor binding reads another factor's binding directly or through a plain binding: every factor reads only its own
bindings plus plain record reads (n_extra, name_rate, term_years, first_cert, live_installs only inside one factor).
Fix made: goodwill_settle_wc first acted on credit_total (which carries four factors' outputs) -> redesigned as a
parameter (goodwill share 0 / 50 / 100 percent) applied in the generic assembly; cycle_days moved into inst_cycles_mi.

### All-pairs method tier table (shape test)
| factor | tier pair | distinguishing input / operation | verdict |
|---|---|---|---|
| term_years_ren | 3y vs 2y vs 1y | different tariff parameter and multiplier | PASS |
| san_bands_co / san_bands_ar | 3-band vs 2-band vs flat | extra band operations | PASS |
| nm_paid_period | to period_end vs end+next_year_days vs end | data-selected end date; added input | PASS |
| wait_anchor_wc | http pass vs approver pass vs order date | data-selected start date | PASS |
| inst_cycles_mi | cycles to end vs cycles to DCV reuse end vs 1 | data-selected window; constant | PASS |

### T1/T2 for min/max shapes
No factor is a lesser-of or greater-of. MN(term years, max_subscription_years) in the auto-renew is a plain cap that
never bites (3-year maximum); MX(1, cycles) in the installation is a floor inside one factor's tiers (T1: the factor
moves 183.92 -> 10.74; T2: tier 2 with a lapsed DCV floors at 1).

### Decoy / absent-record probes (scratch copies, evalc.py)
R gold 1788.37; second deleted domain of the customer 1788.37 (CFIELD keyed by domain_id); domain row absent 1798.37
(credit falls through); account absent 1982.74 (no discount); earlier 3-year renewal line -> treated as latest term
line 2587.45 (rule-consistent). P gold 1615.27; org validation 442 days old 1675.27 (no reuse credit). A gold 592.45;
installation refunded 562.45 (no re-installation fee); external nameservers 598.45. E with goodwill for another order
26 (share 100); no failed checks -> order-date anchor 16. I (opening world) email cancelled 15.74; extra cancelled M365
for the same domain 10.74 (status filter keeps Mail Plus); http_file validation 10.74 (one certificate); lapsed DCV on
external DNS 10.74 (floor). Fix made: the wait-credit anchor tiers now require a passed check by that method (an
absent passed check fell into DAYS(None)).

### Events written and their base triggers
- renew_certificate_subscription / charge_certificate_autorenewal: ssl_renewal_charge -> ssl:ssl_subscription_extend
  (written by the same tool), account:account_credit_apply only when payment_method account_credit (tools fix card).
- order_cotermed_certificate: ssl_order -> ssl:ssl_purchase_charge (written); purchase -> account trigger only for
  account_credit (card).
- add_certificate_name: ssl_names_charge -> ssl:ssl_names_update (extra_names written); account trigger only for credit (card).
- credit_validation_wait: ssl_subscription_extend (no triggers).
- bill_certificate_installation: ssl_install_charge -> account trigger only for account_credit (card).
No write lands in another category. Task 1's auto-renew would try account credit first, but the balance 535.00 does
not cover 592.45, so the card is the funding source the account charter gives.

### compute_basis verbatim sweep
sweep.py: every compute_basis quote of all six policies is a verbatim substring of its rule; every baseline.rule
sentence is a sentence of its rule; no factor id is a substring of a tool name.

### Realism notes (honest)
The base charter prices refunds and cancellations in full and makes certificate validity a lesser-of, so the six
drawn computations had to be priced writes: co-termed second subscription, support renewal, owed auto-renew, added
name, validation-wait credit and managed installation. Several ladders are Harborline's own published schedule items
(SAN bands, domain and DNS credits, re-installation fees, validation-wait credit, reseller issuance days, managed
installation cycles); they are declared as overwrites where they replace a base sentence. CA/B-grounded figures used:
max_cert_validity_days 200 for seeded certificates, the 100-day schedule from 2027-03-15 in installation cycles,
dcv_reuse_days 200 and org_validation_reuse_days 398 in seeds and rules. Owner choices: the co-termed order and the
added name are the customer's own paid orders (owner=user); the blueprint names only order cancellation as a
customer action, and a cancellation refund is flat, so it could not carry a computation.

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 13 acts clos 22 = init 22; 1.json 19 acts clos 26 = init 26);
SOLVABILITY OK; COMPUTE OK (suite means branches 56.00, steps 16.00; history_rows_max 10; branches_max 74);
GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; TRACEABILITY NOT OK only for the six unlock tool names (expected before the
KB is rendered; no other parameter misses). frozen_time: task 0 "2026-11-17 10:20:00 CST", task 1 "2026-12-08 09:40:00 EST".
Gold: task 0 support renewal 1788.37 (2 years) -> co-termed order 1615.27 (3-year class); task 1 auto-renew 592.45
(2 years) -> wait credit 13 days -> added name 23.25 -> managed installation 183.92.

## REWORK round 2 — plan (written before edits)
Audit: audits/policy_task/ssl_certificate_lifecycle/{_difficulty,0,1}.md (REDs OWN, EVT, SHAPE, UNREAL, ACCT-SCOPE, CYCLE,
FUND, ZERO, EDGE, SEED; task REDs T0-TERM/OWN/EVT/UNREAL/SEED, T1-ORDER/SLA/UNREAL/ACCT/CYCLE/SHAPE/EVT/OWN/SEED).
Re-allocation (draw unchanged: t0 [1 prereq; 5,4], t1 [3 prereqs; 5,5,5,4]):
- task 0 (DV Multi-Domain, stored card expired): root managed installation (holder pays at checkout, 5 factors)
  <- support renewal of one year (holder pays at checkout, 4 factors).
- task 1 (EV Multi-Domain): root second-key subscription (whole years to the sibling's end, holder pays by PayPal at
  checkout, 5) <- owed auto-renew (agent, 5), <- one added name (holder, PayPal checkout, 5) <- auto-renew;
  validation-wait credit added with the renewal (agent, 4) <- auto-renew; added name waits on the credit.
Factor levers kept to schedule items a registrar publishes: account tier discount on subscription prices only,
early-renewal promotion (single higher with the tier), SAN volume bands on multi-year terms, EV/OV re-vetting fee,
organisation/DCV validation reuse credits, Harborline DNS automatic-validation credit, Harborline Mail bundle credit,
repeat-installation rate, same-day renewal+installation bundle, CA/B-scheduled reissue count, reseller issuance SLA days
(tier in force on the purchase date), goodwill offset. Dropped: domain auto-renew splits, dcv-method-under-HDNS splits,
registration days, co-terming, names "next year" tier, tier discount on installation.
- round 2: charter rebuilt from /tmp/ssl_certificate_lifecycle_0076/r2/pol_*.py; tools rebuilt; task 0 rebuilt and per-task gates green (EXTENDED, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK).

## REWORK round 2 — XF sweep records (charter rebuilt from /tmp/ssl_certificate_lifecycle_0076/r2/pol_*.py)
- Defining sentences: each policy's rule is assembled from named sentences (scope / base / pay / one sentence per factor /
  assembly / prerequisite); baseline.rule = the base sentence(s); every factor's binding quotes only its own sentence;
  assembly sentences are generic ("every percentage reduction ... before any fixed fee is added or credit subtracted").
- Factor-reads (transitive, sweep.py): no factor binding reads another factor's binding; shared reads (n_extra,
  name_rate, term_years, raw_wait, first_cert, dom_ns inside one factor only) are plain.
- Method all-pairs: discount_family_ren {higher-of pick / single value / none}; reissue_cover_mi {reissues to end on the
  CA/B schedule / reissues to the DCV reuse end / one certificate}; san_bands_* {3-band / 2-band / flat};
  nm_paid_period {to paid end / from the next automatic reissue / from today}; wait_anchor_wc {from the http_file pass
  (ssl_events.event_at) / from org_validated_date / from opened_date} — every pair differs by an input or an operation.
- T1/T2: no lesser-of factor; MN/MX only as plain caps (term years, whole years, reissue floor at 1).
- Probes (probe.py on scratch copies): email decoys (cancelled Mail + cancelled M365 -> no credit; M365 only -> M365
  credit; extra cancelled record ignored by status filter); second domain of the customer ignored (domain_id filter);
  absent domain/account rows fall through; installation line refunded -> no re-installation fee; renewal booked within
  30 days -> no promotion; http_file with lapsed DCV -> one certificate (floor), fresh DCV -> reissues to the reuse end;
  OV product -> installation 0 and not booked; earlier 3-year renewal line -> sets the auto-renew term; registration in
  grace -> no domain credit; later http_file pass after the first certificate -> order-date anchor; goodwill for another
  order -> share 100; tier changed after purchase -> no commitment days; goodwill >= 25 -> 0 days, not booked; no first
  certificate or same-day first certificate -> 0; added name with 1 day left stays positive; DV Single at Platinum
  second-key order stays positive.
- Triggers: renewal and auto-renew lines (ssl_subscription_extend written by the same tool; account trigger only for
  account_credit, never written); second-key order (ssl_order -> ssl_purchase_charge written, card/paypal); added name
  (ssl_names_update written); installation (card/paypal); wait credit (no triggers). Nothing lands in another category.
- compute_basis verbatim sweep: clean for all six; factor ids not substrings of tool names.

## REWORK round 2 claims
- OWN: every owner=user write is now a payment the holder completes at Harborline's secure checkout (owner ruling b);
  each rule states it; personas show the necessity (task 0 stored card expired; task 1 new-server purchases from a PayPal
  not on file); agent writes (auto-renew, wait credit) stay on the stored card / no charge.
- EVT: (a) co-terming removed — the second-key subscription runs whole years from the order date, end = order + years;
  (c) the names "end plus next year" tier removed; (b) the wait credit now comes due with and is added alongside the
  subscription's first renewal (residual: the base event list has no other free end-date move).
- SHAPE: term_years_ren removed (support renewal is one year by rule); support renewal's method is the tier/early-renewal
  single-higher pick; wait_anchor_wc tiers read three different fields.
- UNREAL: U1 domain auto-renew splits removed; U2 dcv-method-under-Harborline-DNS splits removed (DNS credits/handling
  follow nameservers; DCV method matters only where it changes the work: second-key reuse, reissue coverage); U3
  registration days removed; U4 commitment days read the tier in force on the purchase date.
- ACCT-SCOPE: no tier discount on the installation; tier discounts only on purchase/renewal list prices.
- CYCLE: reissue coverage follows max_cert_validity_days before 15 March 2027 and the 100-day limit after, reissue
  auto_reissue_days_before_cert_expiry days before expiry, never replacing a certificate that expires on the end date.
- FUND: the auto-renew rule scopes out charges the credit balance covers (account credit run) and charges the rest to the
  default card, matching the card-only tool.
- ZERO: fixed credits sized below the smallest list amounts; the added-name mail bundle is a percentage; OV/EV
  installations (fee 0) and zero-day credits are carved out and not booked.
- EDGE: E1 email bundles keyed on the certificate's domain_id with active status and family precedence; E2 refunded
  renewal lines stated explicitly in the auto-renew and added-name rules; E3 anchor only from a pass not later than the
  first certificate, else the next tier.
- SEED: no multi-name lines; the task-0 installation line priced under the installation rule as of its date; task-1
  ledger, domain and email lines priced at the tier in force on each posting date, credit-first auto-renews booked
  from credit where the balance covered them; balances equal ledger sums.
- T0-TERM / T0-OWN / T0-EVT / T0-UNREAL / T0-SEED: task 0 rebuilt (installation <- one-year support renewal); no term
  hint in the persona; stamps carry no factor tier.
- T1-ORDER: the added name waits on the wait credit (state sentence), so the chain auto-renew, credit, name, order is
  fixed; T1-SLA, T1-UNREAL, T1-ACCT, T1-CYCLE, T1-SHAPE, T1-EVT, T1-OWN, T1-SEED: closed by the charter items above and
  the rebuilt task-1 world.
- O1-O8: support/auto-renew partition unchanged (no world asks for a renewal while one falls due); O3 prerequisite
  scoped to subscriptions inside their renewal window; O5/O7 gone with co-terming and the names re-install fee; O6 task 0
  keeps the first server, so its re-installation is real.
- Gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max 8,
  branches_max 91); GROUNDING OK; SCOPE OK; traceability shows only the six unlock tool names (pre-KB).
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- EVT: the end-date credit (ssl_subscription_extend without a renewal) is gone; ssl_ext_wait_names replaces it as an
  ssl_names_update write (grant_complimentary_names_f9ed3e27 raises extra_names, no billing line), owed once while the
  billing carries no added-names line; it waits on the auto-renew by a state sentence, so the A/X order is pinned.
- SHAPE: support-renewal discount method now splits the base by tier: promotion-only reduces price_1yr and leaves the
  extra names unreduced; tier-only and both-apply reduce the whole list amount.
- UNREAL/U5: mail bundle credits kept only on the support renewal and the installation; the auto-renew, added name and
  second-key order carry a multi-year names rate (price_Nyr_per_year / price_1yr) instead.
- ZERO: the added-name credited-days tier is removed; no factor tier yields a zero-amount booking in either world.
- EDGE/E5: a second-key order needs at least one whole year to the sibling's end, else nothing is booked.
- SEED: task-1 account events carry the 2026-12-02 grace_started review, so the Bronze tier recorded today is explained.
- PAY: the account-credit payment choice is routed to the credit run in the support-renewal rule.
- HINT: the persona's volunteered line is struck; she names the four order-desk addresses only when asked and raises no
  prerequisite.
- revision_1 items not reopened: partition, CA/B reissue cycle, funding order, owner ruling (b) checkouts, seed pricing.
- Observations: probes cover decoy http_file pass, goodwill for another order, tier change after purchase, full goodwill,
  name-room cap, absent first certificate and a prior added-names line; sensitivities distinct from gold in both tasks.
- Gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max 8);
  GROUNDING OK; SCOPE OK; traceability shows only the six unlock tool names (pre-KB).
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- U6 (T1R3-U6): nm_term_rate now follows the years of the term line the name is billed into (the purchase, renewal
  or auto-renew line whose period_end is the end date), as the auto-renew and second-key rates do; no rate follows
  the days left.
- U7 (T1R3-U7): nm_paid_period (leap-day counting tier) and its reissue-ride tier are removed; the method is now
  nm_renewal_join: a name joining a renewal is priced as part of it (renewed years at the yearly name price less the
  account tier's ssl_discount_pct, plus the days before an unstarted renewal begins prorated; an already begun renewal
  prorated at the reduced price; the purchase term prorated at the plain price).
- E6 (charter, wait_names): the grant now puts the complimentary names on the certificate by a free reissue
  (base: names take effect on a free reissue), recorded as an issuance of kind reissue with the holding's certificate
  dates; the compensation is owed only while the history shows no issuance of kind reissue and the billing no
  added-names line, so after the grant or a paid name the rule's own test reports nothing owed and the added-name
  prerequisite reads a recorded state. The tool takes the reissued expiry date (base validity rule); time gates
  dcv_fresh and org_validation_fresh are covered in temporal_feasibility.
- Observation (r3 problem_chain): the compensation rule now says the complimentary names are places the customer fills
  with the names wanted, only names beyond them being added-name orders.
- Class sweep r1-r3 across all six policies: multi-year rates (autorenew, second-key, names) all by term years; method
  factors (reissue_cover_mi, discount_family_ren, san_bands_ar/sk, nm_renewal_join, wait_anchor_cn) all real pricing
  or attribution dimensions, none a counting convention; every owed/carries test (auto-renew line, renewal past the
  window, compensation, complimentary names) reads records its resolving write leaves; no 0.00 booking; EVT, SHAPE,
  ZERO, SEED, PAY, HINT, OWN, ACCT-SCOPE, CYCLE, FUND unchanged. Task 0 untouched (charter text of its two policies,
  tools, world and gold unchanged).
- Gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  traceability shows only the six unlock tool names (pre-KB).
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- ACCT-SCOPE (T1R4-ACCT): the added-names line carries no account-tier discount (a proration line under the account
  charter); the tier read and its cross-category declaration are removed from the added-name rule.
- SHAPE (T1R4-SHAPE): the method factor is now nm_billing_span on Harborline's published added-name schedule, each tier
  keyed on a record test: no more than nm_min_term_days days left -> prorated but never below the minimum added-name
  charge (max shape); more days left on a two- or three-year term line -> whole name-years for the years left, a part
  year counting whole (step shape); otherwise prorated by days to the end date (baseline).
- INDEP (T1R4-INDEP): the method decides only bill_span and name_floor, read from the end date and the term line; the
  per-name assembly (yearly price x span, floor) lives in a plain binding; no factor reads another factor's output.
- O10: add_certificate_name_7df48eab now says the name takes effect on the certificate's next free reissue, which the
  call does not record; only the complimentary-names grant performs and records its reissue.
- Sweep (stale text): the second-key prerequisite condition now says the sibling's names are carried by complimentary
  names or added-names lines; the names-on-auto-renew edge effect and all task-1 traces, sensitivities and the dossier
  restated for the new schedule.
- Class sweep r1-r4 across all six policies: ACCT-SCOPE (tier pct only on purchase, renewal and auto-renew list
  prices), SHAPE (every method factor's tiers pairwise distinct in structure), INDEP (no factor binding reads another
  factor's output), U1-U7, E1-E6, OWN, EVT, ZERO (minimum charge only where a name is bought), SEED, PAY, HINT, CYCLE,
  FUND unchanged and clean. Task 0 untouched (its policies, tools it calls, world and gold unchanged; tasks/0.json
  content identical — replay_tasks write-back only reorders db_closure, so final gates ran replay with --check).
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- EVT (T1R5-EVT): the whole-name-year tier is removed; the added-name schedule now states that no added name is billed
  beyond the subscription end date, and nm_billing_span keeps only tiers inside the remaining subscription, each keyed on
  a record test: no more than nm_min_term_days days left -> prorated but never below the published minimum added-name
  charge (max); more days left on an unstarted renewal or auto-renew line -> prorated but never more than that renewal's
  years at the yearly price, the days before it begins covered free (min); otherwise prorated (baseline). The task-1
  world takes the cap tier; the opening world (before the auto-renew) takes the minimum tier.
- COND (T1R5-COND): the second-key -> added-name condition now reads "extra_names on the sibling has risen by the names
  the customer says the new server serves beyond those the sibling covers" (no billing-line clause), in the charter
  and in tasks/1.json. The round-5 claim of this fix was wrong: the policy file was edited but the charter was not
  rebuilt; this round rebuilds the charter before every gate run.
- Cross-product rule (account_tier_benefits): the auto-renew and second-key rules now apply the tier percentage only to
  the certificate price and the names at full rate; banded names take the single higher of the band reduction and the
  tier percentage (never compounded); reduced components are rounded before fixed fees and credits; tier as recorded
  on the charge date. The added-names line (a proration line) carries no tier discount; the support renewal already
  takes the single higher of tier and promotion; the installation carries none. Seeded task-1 domain and email lines
  re-checked (.ca has no ICANN fee; Harborline Mail is not a Microsoft 365 seat).
- Tier probe against the base event meaning (names): every nm_billing_span tier bills time only up to the end date;
  band, multi-year rate, handling and vetting tiers bill no time; probes cover the minimum boundary (90 days), begun
  renewal, one-year unstarted line (cap binds), 730/731 days, refunded renewal and absent account.
- Class sweep r1-r5 across all six policies: OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED, ACCT-SCOPE, SHAPE, INDEP,
  U1-U7, E1-E6, COND (every prerequisite condition re-read against its sentence) clean. Task 0 untouched; tasks/0.json
  bytes restored after the replay write-back and gates run with replay --check.
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
- COND class sweep: the added-name -> complimentary-names condition restated to the case the compensation rule owes
  names (the grant's reissue and raised count leave the rule owing none); every other condition matches its sentence.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- ACCT-SCOPE (revision_6, support renewal): where both the tier percentage and the early-renewal promotion apply, the
  rule and compute now go price component by price component as account_tier_benefits states: price_1yr takes the
  single higher of the tier percentage and the promotion (never added), the extra names take the tier percentage alone
  (the promotion never covers them); the discount_family_ren ladder tier is restated in the same words. Tier-only,
  promotion-only and neither tiers unchanged; task 0 (Business Account, promotion only) keeps its tier and values.
- Probes added: Bronze both-apply (31 days ahead) and tier-only (20 days), Gold both-apply and tier-only (tier above
  the promotion, so the price component takes the tier).
- Cross-product rule sweep (account_tier_benefits) across all six policies: auto-renew and second-key apply the tier
  only to the certificate price and full-rate names, banded names take the single higher; support renewal per
  component as above; added-names line (proration) carries no tier; installation and complimentary names carry none;
  reduced components are rounded before fixed fees and credits; tier as recorded on the charge date. Seeded rows of
  both worlds re-checked (task-1 domain and email lines at the tier in force on each charge date; task 0 Business
  Account has no tier percentage).
- Class sweep r1-r6 (OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED, SHAPE, INDEP, COND, U1-U7, E1-E6): no policy other
  than the support renewal changed; clean. tasks/0.json and tasks/1.json unchanged (no world or gold moves).
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- F1 (second-key) and F3 (auto-renew): restructured so the bands and the tier percentage never meet: the tier
  percentage reduces only the certificate price component (stated in the tier factor's own sentence), the extra names
  are priced by the band schedule alone, so no two percentages reduce one price component (account charter
  single-higher holds trivially); the plain bindings that rebuilt band membership (banded/b1/b2/full_names,
  tier_part/band_part) are removed; assembly is plain (certificate component, names component, reduced amount) and
  its sentence is generic ("every percentage reduction acts once on the price component it reduces, every
  multiplier of a name's yearly price acts on that yearly price ...").
- F2 (and the auto-renew twin in F3): the multi-year name-rate sentences no longer name the bands ("that multiplier
  acts on the names part after its bands" removed); the multiplication commutes with the band prices.
- F4 (added names): the band factor's ladder is now a multiplier of the added name's yearly price (nm_band2_pct /
  nm_band1_pct percent, or none); the yearly price is defined generically as "additional_name_price_per_year with
  every multiplier that applies to it"; no sentence names two factors' quantities.
- F5 (second-key overwrite 3): replaced_by restores "at most max_subscription_years" for every other subscription.
- F6 (complimentary names): the combination sentence is generic by kind: every multiplier of the waiting days first,
  every number of days added to the credit next, every percentage share on that total, rounded down to a whole day.
- A1 (installation): baseline.rule now defines the per-certificate rate (installation_fee) and the certificates
  covered (the one certificate installed) that the assembly reads.
- A2 (installation): the renewal bundle credit states the same-day tie (a renewal line and an auto-renew line billed
  the same day take inst_renew_credit), matching compute.
- A3: note only; unchanged.
- XF 1-5, 29 sweep: mechanical factor-read check (no factor binding reads another factor's output) in all six
  policies; every assembly/combination sentence generic (installation, support renewal, auto-renew, second-key,
  added names, complimentary names); every overwrite tail re-read for in-force content.
- Cross-product rule (account_tier_benefits) re-checked: tier percentage only on certificate price components
  (auto-renew, second-key) or per component with the promotion (support renewal); no tier on proration lines or
  installation; seeded rows unchanged and compliant.
- Values moved: task 1 auto-renew and second-key amounts (names no longer take the tier percentage); task 1 added
  name, complimentary names and all of task 0 unchanged; tasks/0.json byte-identical.
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- SR1 (KB re-judge revision_2): the task-1 .ca domain auto-renew lines are re-dated to the published .ca first attempt,
  35 days before each expiry (2024, 2025 and 2026 renewals), and the two matching account-credit apply entries carry
  the same dates; ledger order and running balance reconciled (balance unchanged, equal to the ledger sum); the tier
  in force on each date is unchanged (Business before 2024-12-02, Bronze after), so the amounts stand.
- S4 (account KB revision_3): the support-renewal scope no longer claims every auto-renew charge for the auto-renew
  rule; it now says an auto-renew charge the credit balance does not cover in full is priced under the auto-renew
  charge rule, while one the balance covers in full, paid by the account's credit run, stays under the base renewal
  rule with dashboard renewals; this matches the auto-renew rule's own funding sentence ("not booked under this
  rule"). The overwrite's replaced_by carries the same text.
- Seed re-check: every seeded row of both worlds against its published rule as of its date (KB re-judge tables);
  no other row moves. Cross-product rule (account_tier_benefits) unchanged since round 8 and compliant.
- Values: no scored value moved (both tasks); tasks/0.json byte-identical; tasks/1.json changes only in the re-dated
  seed rows.
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 9: gates 7/7 green

## REWORK round 10 claims
- SIB (revision_9): one decidable funding test, the same sentence verbatim in the auto-renew rule, the support-renewal
  rule and the replaced_by of each one's sibling overwrite: an auto-renew charge is paid by the account's credit run
  and priced under the base renewal rule (not booked under the auto-renew charge rule) when the account credit
  balance on the day it falls due is at least the base renewal price of that renewal (tier's price for the years plus
  the extra names for those years, less the tier percentage, rounded half up); otherwise it is charged in full to the
  default card and priced under the auto-renew charge rule. The universal claims are removed ("only such a charge is
  priced under this rule" from the auto-renew scope, the separate funding sentence, and the support-renewal clause
  assigning covered and uncovered auto-renew charges). The auto-renew compute now reads the credit balance (declared
  account read) and the base renewal price, and books nothing where the balance reaches it.
- Probes: balance 1720.00 and one cent below the base renewal price -> card under the auto-renew rule; balance equal
  to it and above -> credit run, nothing booked; absent account -> balance 0, card. Task 1's balance stays below
  the base renewal price.
- Cross-product rule (account_tier_benefits) unchanged since round 8 and compliant; class sweep r1-r9: no other
  policy changed.
- Values: no scored value moved; tasks/0.json byte-identical; tasks/1.json changes only in trace and rationale text.
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 10: gates 7/7 green

## REWORK round 11 claims
- FUND (revision_10): the round-10 funding test is replaced, per the coordinator ruling, by one sentence verbatim in
  the auto-renew rule, the support-renewal rule and the replaced_by of each one's sibling overwrite: every due
  auto-renew charge is priced under the auto-renew charge rule whatever pays it, and account credit pays it first
  (account charter): where the credit balance on the day it falls due covers that amount in full the account's credit
  run books it at that amount, otherwise it is charged in full to the default card at that amount and booked under
  the auto-renew charge rule. The base-renewal-price comparison, the credit_balance read and the zero branch are
  removed from the auto-renew compute: the price never depends on the balance; the card-only tool books only the
  card-funded case (no account-category write).
- Probes: the price is the same at balances below, one cent below, equal to and above it, and between it and the
  former base-price threshold; funding is card below the price and credit run from the price up.
- Cross-product rule (account_tier_benefits) unchanged since round 8 and compliant; class sweep r1-r10: no other
  policy changed; no stale threshold text left in either task.
- Values: no scored value moved; tasks/0.json byte-identical; tasks/1.json changes only in trace and rationale text.
- Gates (no --task; replay --check): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK.
REWORK round 11: gates 7/7 green
