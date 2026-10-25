# render_r3 — erl-kb-doc-render email round 3 (agent a3758ae7c3d161a26), STOPPED at source scan; findings verbatim from /tmp/render_email_0076/findings_r3.txt (saved by coordinator)

RENDER STOP - email (env_0076) rework round 3 - source scan of revision_14 found defects; no document written, published docs/email left untouched.
Source: env/env_0076_web_hosting_and_domain_registrar/tasks/professional_email_seats/email.extended.yaml (sha256 ba4581ac...), task_tools.py (f267ea76...).
Gate line read: VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN. KB-audit items read (XP-1, notes a-c): the rework addresses XP-1 (account-tier rate now applied alone, reduces only the component, never a fee/credit; Pro upgrade takes no rate as a proration line).
Mechanical checks clean: every compute_basis quote, replaced_by, baseline.rule and prerequisite policy_source verbatim in its rule; every superseded_clause verbatim in its base rule; no factor binding reads another factor's binding.

G1 [rule-internal inconsistency; resolving write cannot bring the gate state about] email_ext_unbilled_seat_catch_up + email_ext_term_renewal, annual_monthly_billing plan
  catch-up rule: "it is one added-seat line for the current term on record, from the term start date to the term end date, or on the annual_monthly_billing plan for the instalment month on record that contains today"; tool body books period_end = minus_one_day(add_months(term_start, k+1)), i.e. never the term end date (the last instalment month ends the day before it).
  catch-up rule: "The seats billed for the current term are the seats on the charge that opened the current term plus the seats on added-seat lines whose period end is the term end date." (compute term_added_seats filters period_end=F('term_end_date')).
  term renewal prerequisite (condition): "The seats on the charge that opened the current term plus the seats on added-seat lines whose period end is the term end date are at least the renewed seats".
  Failure: on the annual-billed-monthly plan a booked seat catch-up line is never counted in the seats billed for the current term, so the catch-up seats stay unchanged after it is booked (it can be billed again and again), and a late term renewal's sentence "A late renewal is not collected until the charges of the current term carry at least the seats it renews." can never be met by it. Related: on that plan the catch-up line for one instalment month is priced as 1 month times the calendar days to the TERM end over the term's days (catch_up_months 1, catch_up_fraction days_to_term_end/term_days), so a month line late in the term bills a small share of a month although it covers a whole instalment month.

G2 [rule contradicts its own principle] email_ext_mail_pro_upgrade, credit_basis on annual_monthly_billing
  rule: "where it is the first monthly instalment of an annual term billed monthly, the credit basis is its amount times the calendar months from the term start date to the term end date"; "The term credit is the credit basis less every fee taken off it"; "a fee is part of what that charge billed but never of what a term is credited."
  compute: credit_basis = credit_open_amount * MONTHS(...) (amb), term_credit = RND((credit_basis - carried_late_fee - carried_reinstatement) * billing_fraction).
  Failure: a reactivation or term renewal on that plan bills fees on the first instalment (its amount = rounded component + late fee + reinstatement charge); multiplying that amount by 12 and taking each fee off once credits the fee 11 times, against "never of what a term is credited". Fix: take the fees off the instalment amount before multiplying by the months.

G3 [ladder order vs compute precedence] email_ext_reactivation_renewal.renewal_product and email_ext_term_renewal.renewal_product (factors reactivation_renewal_product, term_renewal_product)
  ladder: tier 1 "the scheduled product is Harborline Mail Starter" -> Harborline Mail Starter ... tier 5 "otherwise, no product scheduled, or the subscription was moved up during the current term" -> current product.
  rule: "a scheduled Harborline Mail Starter, Harborline Mail Plus, Microsoft 365 Business Basic or Microsoft 365 Business Standard makes that product the renewal product; otherwise, where no product is scheduled or an upgrade line whose period end is the term end date belongs to the current term, since a move down never takes effect ... the renewal product is the subscription's current product."
  compute: each scheduled tier requires COUNT(upgrade_proration, period_end=term_end)==0.
  Failure: for a subscription with a scheduled lower product AND an upgrade line in the current term, the ladder (first match) and the rule's first clause give the scheduled product, the compute gives the current product; only the "since" aside points to the compute's reading. Fix: condition the scheduled tiers on "and no upgrade line whose period end is the term end date belongs to the current term" in the rule and the ladders.

G4 [A4, same class as round-1 F3] scheduled_seats sits in the baseline while its only defining sentence is a seat-basis factor tier
  email_ext_reactivation_renewal, email_ext_term_renewal, email_ext_unbilled_seat_catch_up: compute scheduled_seats = F('scheduled_seat_count') is read only by renewed_seats / catch_up_target (factors reactivation_seat_basis, term_renewal_seat_basis, catch_up_seat_basis); baseline.rule never mentions a scheduled seat count; compute_basis.scheduled_seats = "where a scheduled seat count is set, the renewed seats [catch-up target] are the lower of the scheduled seat count and the seat count on the subscription, but never fewer than the mailboxes in use ..." (the factor's tier sentence).
  Fix: move scheduled_seats into each seat-basis factor's bindings.

G5 [rule vs tool docstring scope, low severity] email_ext_term_renewal / pay_late_mail_renewal_a889cd52
  rule: "A term renewal is the renewal of an active email subscription that falls due on its term end date, billed on or before its due date or, as a late renewal, after it while the subscription status is still active".
  tool docstring: "Collect, on the customer's default card on file, the overdue renewal of an active email subscription whose renewal fell due on its term end date and went unpaid."
  Failure: the policy prices term renewals billed on or before the due date, but its only tool describes itself as collecting an overdue renewal only. Fix: widen the docstring (capability text only), or narrow the rule's scope.

Noted, not a stop: the conversion baseline's "no credit convention applies, so the credit fraction is 0" and the Pro upgrade's baseline open_charge_date (shared by two factors, with its own defining sentence) are renderable as they stand.
