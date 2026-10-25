# plan — professional_email_seats (category email), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6,5]
- task 1: prerequisite_problems=2, factor_counts=[5,5,4]

## Design constraints found in base (why the trees look like this)
- Only cancellations are lifecycle "by: user"; a cancellation refund of one charge carries 1-2 honest
  factors and the email_refund grain is one row per refunded charge -> cancellations are poor computation
  hosts.  User nodes therefore are the customer's own purchase/payment decisions (principle H: "a payment,
  an instruction, a confirmation"): task 0 = the customer's own product upgrade (Microsoft-style attestation of
  a new product / purchase confirmation), task 1 = the customer pays an overdue amount in person.
- Computed figures must come from records only (no customer-stated quantities in compute).
- Harborline Mail rate card (one schedule applied to every Harborline Mail seat price this charter extends):
  account-tier rate (account charter email_discount_pct, cross-difficulty), seat-volume rate,
  hosting-bundle rate (cross-difficulty hosting), Harborline-DNS domain rate (cross-difficulty domain).
  Rates are first added into one total rate and applied once to the list seat price. Microsoft 365 never.
- Tools never write account_credit payment/refund destinations (cross-category triggers).

## Task 0 — Harborline Mail Plus, expired; customer asks to move up to Harborline Mail Pro
- prereq P1 email_ext_lapsed_renewal (agent, 6 factors): renew the expired subscription inside the expired
  grace days (renewal charge + term roll + expired->active). Factors: tier rate, volume rate, bundle rate,
  DNS-domain rate (parameters), reinstatement scale by days lapsed (parameter), renewal seat basis (method:
  scheduled count / trim seats of deleted, never-restored mailboxes / as is).
- root P2 email_ext_mail_upgrade (user, 5 factors): upgrade proration Plus->Pro. Factors: tier/volume/bundle/DNS
  rates on the price difference (parameters), upgrade billing span (method: full term inside the cancellation
  window / whole remaining months in the last 60 days / remaining days).
- edge P2 <- P1 value_input (term end + seats + status active), state form.

## Task 1 (tentative headroom; finalised after task 0)
- Harborline Mail monthly-plan or annual world; user node = customer pays an overdue amount in person;
  remaining policies: email_refund / email_seat_charge(added_seats) / email_mailbox_restore / email_settings_update
  families, disjoint from task 0 tools and policies.

## Files
- email.extended.yaml (base verbatim + extended_policies), task_tools.py, tasks/0.json, tasks/1.json
- scratch: /tmp/professional_email_seats_0076/ (verification scripts, worklog drafts)

## Task 0 — DONE (per-task gates green; see tasks/0.json design_rationale)

## Task 1 — FROZEN DESIGN (do not re-deliberate)
World: Harborline Mail Plus on the MONTHLY plan, Reseller Silver (8), hosting Harborline Pro on the domain (bundle mid 3),
domain at Harborline on external nameservers (1). seat_count 19; the opening line of the current month (2026-09-20)
billed 15 seats; 4 seats added in early October never billed; 2 mailboxes deleted and never restored. Monthly renewal due
2026-10-20 declined x3; today 2026-10-24 (inside 7 grace days, status active). Customer (Rosa Paredes, Pinecrest
Pottery Studio, pinecrestpottery.com) asks to switch to yearly billing.
- C1 email_ext_unbilled_seat_catch_up (agent, 4f; tool bill_unbilled_mail_seats_5cd17f30): seats on the subscription
  above those billed for the current month, less idle seats, billed for the whole month. Factors: tier rate in force
  on the period start (multi-source), volume rate, bundle rate (params), unbilled-seat method.
- B1 email_ext_late_monthly_renewal (user, 5f; tool pay_late_mail_renewal_a889cd52): the customer pays the overdue
  monthly renewal in person. Factors: tier, volume, bundle, domain rates, renewed-seat basis (method).
  Edge B1 <- C1 state_gate, negated sentence.
- R1 email_ext_annual_conversion (agent, 5f; tool convert_mail_to_annual_cfde09f1) root: 12-month annual term from today
  at the rate card less a credit for the paid month's unused days. Factors: tier, volume, bundle, domain rates,
  conversion credit (method). Edge R1 <- B1 value_input (paid month line + renewed seats), affirmative sentence.
- P1 replaced_by tail now names the late monthly renewal and the annual conversion as siblings (XF16).

## ROUND 6 — FROZEN DESIGN (coordinator ruling: (A) seat-band list prices, reinstatement fee, late fee; (B) reshape)
Removed: every included-seat factor (hosting/domain/volume seats), every past-tier read. Every seat a line covers is billed.
Shared real dimensions, Harborline's published schedule, worded once per policy:
- T  tier%: account tier on the charge date, Harborline Mail list/renewal components only; never M365, fees, credits,
  proration lines. Applied once, component rounded half up before fees/credits.
- BND seat-band list price: Starter/Plus/Pro x annual/monthly x (10-49, 50+), band set by the seats on the charge that
  opened the current term (SUM evidence). List price, not a discount. Ordinary renewals/seat additions use it too (tails).
- PLN plan table: renewal/charge months + plan seat price by billing plan (annual_prepaid / annual_monthly_billing /
  monthly); MONTHS(term) evidence; M365 in scope so all 3 tiers are reachable.
- RFS reinstatement fee (flat per reactivation, by days suspended: <4 none, 4-14 short, 15+ long).
- LF late-payment fee (flat per late renewal, by days past due: 1-3 short, 4+ long).
- FEE fees carried on the opening charge are never credited (inferred from days between period start and charge date).
Policies / factors (counts):
- P1 email_ext_reactivation_renewal (task 0, agent) 5: T, BND, PLN, RFS, SB(method seat basis, idle trim).
- P2 email_ext_mail_pro_upgrade (task 0, user PayPal) 6: PLN(target price+months), BND(target band), T(only when the
  whole term is rebilled inside the window, fraction 1), span(method), CRED(method: opening line / instalment x months /
  none), FEE. Scope: move up to Harborline Mail Pro or Microsoft 365 Business Premium.
- P3 email_ext_unbilled_seat_catch_up (task 1, agent) 4: T, BND, PLN, idle(method). Whole period at list (not prorated).
- P4 email_ext_late_renewal (task 1, agent) 5: T, BND, PLN, LF, SB(method). Any plan, renewal due at term end paid
  inside grace days. Gate <- P3 (state_gate, negated sentence).
- P5 email_ext_annual_conversion (task 1, user PayPal) 5: T, BND(annual band), credit-days(method), CRED(method:
  opening line / opening+added lines / list), FEE. Gate <- P4 (value_input).
Worlds: task 0 Saltmarsh/tidepoolsurf (Plus annual, 14 seats, 2 idle, suspended 2026-10-22, today 2026-10-28, Bronze);
task 1 Prairie Signal (Plus monthly, 23 seats, opening month line 15 seats, 2 idle deleted in October, today
2026-10-24, due 2026-10-20, Bronze). Hosting/domain rows dropped (no factor reads them). Seeded lines re-priced with
band + tier-on-charge-date + idle trim at renewals.

## ROUND 7 — honest rebuild (coordinator route: no bands, honest baselines, base-verbatim tails)
Factors kept (all real, evidence-backed, honest baselines): reactivation T/reinstatement/seat basis (3); Pro upgrade
span/credit basis/carried fees (3, no tier: proration line); catch-up T/idle (2); term renewal (on-time or late, id
email_ext_term_renewal) T/late fee/seat basis (3); conversion T/credit days/paid month/carried fees (4).
Draw [6,5] and [5,5,4] not met — no further honest dimension in this charter (late fee on a reactivation is a constant;
plan price is the standard method; bands are a volume discount; tier on the upgrade line is barred).

## ROUND 8 — re-tree tabulation (honest factors, honest baselines, base text verbatim out of scope)
Dimensions used (all in the frozen base or Harborline's published schedule): account tier (Harborline Mail only; M365
never), billing-plan seat price (annual-commitment price default; annual_monthly_billing / monthly premiums),
late-payment fee by days past due (1-3 / 4-14 / 15+), reinstatement fee by days suspended, idle seats of the term,
seats kept for mailboxes deleted less than a whole month ago (still restorable; a restore needs a free seat), the
scheduled seat count (catch-up only; base rule elsewhere), upgrade proration span (window / final 60 days / Harborline's
whole-weeks convention on a month with 1-14 days left / days), credit basis read from the opening line, fees carried.
| candidate | honest factors |
| reactivation (suspended, monthly HM) | T, plan price, late fee, reinstatement fee, idle, kept = 6 |
| Pro upgrade after it (monthly, 1-14 days left) | plan price, span, credit basis, late fee carried, reinstatement carried = 5 |
| conversion after a reactivation | T, credit days, paid month, fees carried = 4 (fees one factor) |
| seat catch-up (monthly, scheduled count set) | T, plan price, idle, kept, scheduled = 5 |
| term renewal (late, monthly) | T, plan price, late fee, idle, kept = 5 |
| conversion after a late renewal | T, credit days, paid month, fees carried = 4 |
| cancellation / seat-release refunds, expired renewal | 3-4 each in the worlds that chain naturally |
Chosen: task 0 reactivation (6) -> Pro upgrade (5, user PayPal); task 1 catch-up (5) -> term renewal (5) -> annual
conversion (4, user PayPal). Worlds: task 0 re-seeded monthly (due 2026-10-08, suspended 10-16, today 10-28); task 1
adds a scheduled seat count (21, set 2026-10-03) and moves one deletion to 2026-09-22.

## ROUND 9 — CG-12 / CG-13 and the draw
Kept seats and the catch-up idle count were two-valued counts (0 shared by two tiers) and are removed; one seat-basis
method replaces them in the reactivation, the term renewal and the catch-up target: schedule set -> the lower of the
scheduled count and the seat count, never fewer than the mailboxes in use (seat count less idle seats); no schedule and
idle seats -> seat count less idle; otherwise the seat count. Added (honest, base proration of added seats): the
catch-up billing span (whole ended term / short-month whole weeks / base days).
Honest counts now: reactivation 5, Pro upgrade 5 (draw 6,5: one short); catch-up 4, term renewal 4, conversion 4
(draw 5,5,4: two short). The coordinator's list was checked: billing plan table is already a factor in four
computations (the conversion's target is always annual_prepaid); refund/cancellation-window basis has no refund or
in-window credit in either tree (both worlds are month-to-month, which the base never refunds); grace/retention state is
already carried by the late-payment and reinstatement fees (the renewed term starts on the previous term end in every
state); payment route (card / PayPal / credit) never changes an amount in either charter (account_credit_spending,
account_refund_credit).

## ROUND 10 — the eight suggested base parameters, checked against parameter_schema, the base rules and the schema
| parameter | values in the frozen charter | why it cannot be an honest load-bearing ladder in these trees |
| payment_grace_days | 7 (Harborline Mail), 10 (Microsoft 365) | already read by the late fee, the suspension date and the carried-fee inference; a "no fee inside grace" ladder would remove the term renewal's late fee instead of adding a factor |
| instalment_day_rule | term_start_day for every product | applies to annual terms billed monthly; every due date these computations use is already recorded as term_end_date; one value, no tiers |
| price_protected_for_term | true for every product | one value; a protected-vs-list ladder needs a list price change the charter never states, so any seeded old price is a row the charter cannot produce (XF 19) |
| shared_mailboxes_included | 0 / 2 / 5 / 25 by product | the schema records no shared mailbox or conversion (email_events: declines, deletions, restores only), so no tier can rest on records |
| migration_assistance_min_seats, migration_fee_per_mailbox | 5 or 10 seats; 9.99 or 14.99 | booked only on a cross-family new order (email_order / email_subscription_charge), which no problem of either tree writes |
| mailbox_restore_fee | 0.00 for every product | constant zero |
| dns_auto_config_with_harborline_dns | true for every product | decides who sets the MX records, never an amount; the base says a domain's state changes no billing |
| hosting_mailbox_coexistence (+ hosting mailboxes_included) | false for every product | decides that cPanel mailboxes stop receiving mail, never an amount; an included-seat reading was ruled out as an invented entitlement (CG-9) |

## ROUND 12 — task 1 draw: annual-start factor in the annual conversion

- Candidate (1), the catch-up back-billing limit keyed on the seat-addition date, is not taken: an email_seat_update event records no added-seat row the catch-up could date, so the tier would rest on no seeded record.
- Candidate (2) is taken, with its tiers given distinct outcomes. As offered, "starts at the paid month's end with no credit" and "already in its last day starts tomorrow" give the same result on the last day: no credit, and a start one day ahead. The three tiers of conversion_annual_start (parameter, date, bindings days_into_month / credited_days) are now:
  - the paid month began fewer than conversion_start_days (5) days before today: the annual term starts on the term start date and the whole month is credited;
  - the term end date is conversion_end_days (3) or fewer days after today: the annual term starts on the term end date and nothing is credited;
  - otherwise the annual term starts today and the days left are credited (baseline).
- conversion_credit_days becomes the credit convention (method; bindings unused_days / credit_mode): day by day, whole weeks, or none. The assembly binding credit_fraction combines the two factors, and neither factor reads the other's binding.
- The convert tool sets the term from the same annual start date, and the charge date stays today.
- The task 1 world is unchanged. Today is 4 days into the paid month that the late renewal opens, so the first tier is the one that bears load.
- Task 0 is untouched.

## ROUND 13 — CG-14 / F0-5, CG-15, CG-16 (minimal edits)

- **CG-14 (reactivation renewal and term renewal).** The "so a scheduled product still on record is one that passed it" sentence is gone.
  - Each policy now says: at its own renewal, a scheduled lower product is applied even where a mailbox does not fit the lower product's mailbox_storage_gb. Such a mailbox is full and, where send_block_at_full is true, stops sending until space is freed.
  - Both policies add email_plan_changes to base_policy_refs. Each declares a scoped overwrite of the base clause "where retention_on_downgrade is true ... otherwise the change is skipped at that renewal."
  - The replaced_by restates that clause verbatim for every renewal other than a reactivation renewal or a term renewal.
- **F0-5.** Task 0's persona now gives bigger attachments and more shared inboxes as the reason for Pro, not more mailbox space.
- **CG-15.**
  - The convert tool's docstring no longer carries the thresholds.
  - annual_start_date is now an argument the agent supplies and the tool records, checked for format only.
  - The renewal product is likewise an argument the agent supplies to the reactivation tool and the late-renewal tool, so no tool decides a factor tier.
- **CG-16.** Dropping the date condition from compute leaves the renewal-product factor without a record read, which check_extended rejects. So the condition was replaced, not dropped, and it is now stated in the rule.
  - A scheduled product applies unless an upgrade line whose period end is the term end date belongs to the current term. A move down never takes effect at the renewal that closes a term in which the subscription was moved up.
  - Probes: an in-term upgrade line keeps the current product; a prior-term upgrade line does not match.
- Both worlds and every scored figure are unchanged.

## ROUND 15 — renderer scan render_r3 (G1–G5)

- **G1 (catch-up on annual_monthly_billing).** The catch-up is one added-seat line from the term start date to the term end date on every plan. Its catch-up months are the term's calendar months, so the line is priced for what it covers.
  - The line's period end is the term end date, so it counts among the seats billed for the current term.
  - That makes the late renewal's wait reachable on every plan.
  - Probe on a Microsoft 365 annual-billed-monthly world (scratch r15t/probe15.txt): 6 seats before booking, 0 after.
- **G2 (Pro upgrade credit basis).** A new credit_count binding inside the credit-basis factor: the term's months for the first instalment of an annual term billed monthly, otherwise 1.
  - The term credit is now (credit basis − fees) × credit_count × billing fraction, so each fee comes off once, before the instalment is counted for the term's months.
  - The rule and the ladder say "counted once" / "counted for each of the calendar months".
- **G3 (renewal-product tiers).** Each scheduled-product tier now requires that no upgrade line whose period end is the term end date belongs to the current term. Rule words, ladder and compute now agree.
- **G4 (scheduled_seats).** scheduled_seats is now a binding of each seat-basis factor (reactivation, term renewal, catch-up).
- **G5 (term-renewal tool scope).** The pay_late_mail_renewal_a889cd52 description now covers a renewal billed on or before its due date or overdue after it, matching the rule's scope.
- **Task worlds.** No world row or scored value moved. The only task text change is the renewal-product quote in each task's tracing, made verbatim again by an in-place string patch.

## ROUND 16 — KB re-audit revision_2 (SR-1, BL-1)

- **SR-1 (seed realism).** In both worlds the unused deposited credit is withdrawn to the deposit's card before the October attempts, so the published credit-first auto-renew finds a 0.00 balance and goes to the card.
  - Task 0: 73.35 withdrawn on 2026-09-24, day 167 of the 180-day window.
  - Task 1: 73.34 withdrawn on 2026-09-30, day 175 of the 180-day window.
  - The ledger sums to the recorded 0.00 balance.
  - account_msr_deposits_365d still counts the 500.00 deposit, so Bronze stays qualified.
  - Each attempt was re-priced as a term renewal under the published rules: task 0 40.21 on 10-01 and 37.85 on 10-07; task 1 49.68.
  - The other seeded rows re-check: order and pre-Bronze renewals at list; Bronze renewals at the 5% tier; the April added-seat proration line without the tier rate.
- **BL-1 (Pro upgrade baseline surface).** The opening-charge-date binding and its sentence ("...; a fee is part of what that charge billed but never of what a term is credited") are removed.
  - Each fee factor's first binding now reads the opening renewal charge's date itself.
  - Its sentence reads "to the charge date of the opening renewal charge (the renewal charge whose period start is the term start date)".
  - The computation document is left with baseline sentences only.
- **Scored values.** None moved.
