# render_r1 — erl-kb-doc-render email (agent a3758ae7c3d161a26), STOPPED before writing; findings saved verbatim by the coordinator from /tmp/render_email_0076/findings.txt

RENDER STOP - email (env_0076) - source scan found defects before any document was written.
Source: env/env_0076_web_hosting_and_domain_registrar/tasks/professional_email_seats/email.extended.yaml
Mechanical checks were clean: every compute_basis quote, overwrite replaced_by, baseline.rule and prerequisite policy_source is verbatim in its rule; every superseded_clause is verbatim in its base rule; no factor binding reads another factor's binding. task_tools.py docstrings and bodies agree with the rules (term dates, seat count, scheduled resets, line type and period).

F1 [A4 / assembly sentence naming a factor quantity] email_ext_reactivation_renewal, compute `reinstatement_charge`
  compute: reinstatement_charge = "renewed_seats * list_month_price * reinstatement_months". This binding is NOT in factor reactivation_reinstatement (bindings [days_suspended, reinstatement_months]), so it falls to the computation document.
  compute_basis.reinstatement_charge: "A reinstatement charge, where one applies, is the renewed seats times the list monthly seat price times the reinstatement months, is never reduced by any rate, and is added after the reduced renewal seat price has been multiplied by the renewed seats and the renewal months and before the rounding."
  baseline.rule: "... plus the reinstatement charge. ... No reinstatement charge is added."
  Problem: the computation document would have to carry a defining/assembly sentence that names "the reinstatement months", a quantity only the factor defines (plus "where one applies"), contradicting its own "No reinstatement charge is added" and signalling the factor. Otherwise the reinstatement factor document must state how its months become a charge, i.e. restate a binding the computation document claims. Either way the render works around the source.
  Suggested fix: move reinstatement_charge into reactivation_reinstatement.bindings (factor owns the charge; baseline keeps "plus the reinstatement charge ... No reinstatement charge is added.").

F2 [A4 / factor-only quantities in the baseline] email_ext_annual_conversion, compute `unused_days`, `month_days`
  unused_days = "DAYS(NOW, F('term_end_date'))", month_days = "DAYS(F('term_start_date'), F('term_end_date'))"; their only reader is conversion_credit (factor conversion_credit_basis, bindings [paid_month_amount, conversion_credit]).
  compute_basis.unused_days: "The conversion credit of an annual conversion is read from the paid month, the renewal charge whose period start is the term start date, and from the calendar days from today to the term end date"
  compute_basis.month_days: "divided by the calendar days from the term start date to the term end date"
  Problem: both bindings fall to the computation document, but their only defining sentences are the conversion-credit factor's sentences; the computation document (which must say only "No conversion credit is given") cannot carry them without describing the credit, so its covers would claim bindings it does not express.
  Suggested fix: move unused_days and month_days into conversion_credit_basis.bindings.

F3 [A4 / factor-only quantity in the baseline] email_ext_unbilled_seat_catch_up, compute `scheduled_seats`
  scheduled_seats = "F('scheduled_seat_count')"; its only reader is catch_up_seats (factor catch_up_idle_seats, bindings [idle_seats, catch_up_seats]); standard_catch_up_seats does not read it and baseline.rule never mentions a scheduled seat count.
  compute_basis.scheduled_seats: "where idle seats are above zero and a scheduled seat count is set, the catch-up seats are the lower of that figure and the scheduled seat count less the seats billed for the current month"
  Problem: the binding falls to the computation document while its defining sentence is a tier of the idle-seats factor; carrying it there leaks the factor tier, omitting it leaves a covered binding unexpressed.
  Suggested fix: move scheduled_seats into catch_up_idle_seats.bindings.

F4 [overwrite scope wording, low severity] email_ext_reactivation_renewal, overwrite of email_suspension_and_retention, replaced_by:
  "A suspended subscription other than one this policy prices is reactivated as soon as the overdue amount is paid, and its term dates are unchanged; a suspended Harborline Mail subscription whose renewal went unpaid is reactivated as soon as its reactivation renewal is paid, and the paid renewal starts its new term on the previous term end date."
  The rule defines a reactivation renewal only where "whose scheduled product is none". The second clause covers every suspended Harborline Mail subscription whose renewal went unpaid, so one with a scheduled product falls under both the first clause (term dates unchanged) and the second (new term from the previous term end date, but it has no reactivation renewal). Suggested fix: add "and whose scheduled product is none" to the second clause, in the replaced_by and in the rule.
