# Renderer findings — product residency, render round 1 (agent a761eb148a4c8d8d6, 2026-10-15)
Saved verbatim by the coordinator from the renderer's final report (mismatch sections). The renderer stopped before writing any computation or factor document (22 docs on disk: 6 facets, 8 base-policy docs, 8 hubs; 49 withheld); check_docs NOT OK only for the withheld docs.

**Mismatches found**
1. **Assembly class, every extended policy (blocking).** Each rule has one sentence that combines several factor quantities, so the computation document would have to name factor-only quantities, or factor documents would have to name each other:
   - `reclass_due_redating`: "The re-dating limits are met when the whole calendar months from the open cycle's due date to the date of death are no more than the overdue-age limit, … survivor limit, … report-lag limit, … handling window." The re-dating date comes from the `redating_anchor` factor.
   - `absence_start_vacancy`: "Every continuity limit is met when a turned-away notice is on file, the calendar days from the departure date to the facility admission date are no more than the transfer window, … corroboration window, … own-notice window."
   - `return_redating`: "Every return limit is met when … confirmation lag limit, … passed-cycle limit, … notice-age limit, … minimum absence length."
   - `mailed_form_standing`: "A form standing on the return date does so only when … pre-return window, … receipt lag limit, … crediting window."
   - `cycle_completion_date`: "A completion date other than the last signature's standing date is used only when … return link limit, … confirmation link limit, … due-date margin."
   - `facility_contact_number`: the top tier of `letter_numbering` assembles the schedule start, standing date, early-answer allowance, first-contact offset and contact interval.
   - `call_in_checkin_number`: the top tier of `call_numbering` assembles the count-from date, call-in allowance, late-contact grace, call-in interval and missed-contact cap.
   - `return_contact_number`: the top tier of `closing_numbering` assembles the closing allowance, first-contact offset, closing interval and missed-contact cap.

   In every case the other factors only take effect through that one sentence or tier. Each baseline (for example "the open cycle's due date as the profile shows it") does not define those quantities. Several `replaced_by` texts point at "the … fixed below" quantities, which pulls the same problem into the overwrite text.
2. **A rule defers to a base clause its own overwrite retires.**
   - `mailed_form_standing` says "the recording of each signer once per cycle and the certification year … remain as the base rule on certifications provides", but its overwrite retires "Each signer is recorded once per cycle, with the signature date as effective_date and the cycle's certification_year."
   - `cycle_completion_date` says "the move of the due date to the next closing anniversary … remain as the base rule", but its overwrite retires "…and certification_due_date moves forward certification_frequency_months months to the next closing anniversary;".
   The base document shows both clauses as retired.
3. **Undefined branch: a notice received before the date it states.** Four ladders read "received no more than N days after": `survivor_limit_months`, `min_absence_length`, `closing_allowance_days` and `first_offset_days`. A negative lag satisfies that wording, but the compute (`lag >= 0 and …`) puts it in the no-notice tier, and each ladder's fall-through is declared as "no such notice on file" only.
4. **Minor:**
   - The `open_absence_monitoring_c2b89a70` docstring says "annual certification requests give way to scheduled absence check-ins", but the tool body only sets the status and the start date.
   - In the `absence_start_vacancy` rule, "Where two records share the date … read." appears twice.
   - The `return_redating` `replaced_by` says "falls due within response_grace_days of the return or of its confirmation", which does not fit when the re-dating date is the notice's receipt date.

Mechanically verified by the renderer: every compute_basis quote, superseded_clause, replaced_by, prerequisite sentence and baseline.rule appears word for word in its rule. No RND anywhere in the compute.
