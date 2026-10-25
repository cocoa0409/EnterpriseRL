# render_r1 — nonowner (Named Non-Owner Policy) — STOPPED before any doc

Source: env/env_0071_nonstandard_auto_insurer/tasks/nonowner_policies_and_renewals/nonowner.extended.yaml
Gate: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (present). The pre-render source scan found the items below, so no doc, staging or plan was written.

## F1 (blocking) — nonowner_ext_package_increase_premium: the rule's scope sentence names another policy and a factor quantity (XF 2, XF 15; dependency-form)

Rule sentence, carried word for word in `overwrite[0].replaced_by`:

> "a move to a lower base rate whose increase charge by this rule is above zero, as when the package re-rate rule's DUI realignment brings a filer class and other relativities onto the remaining days, is charged as additional premium and not returned, and only such a move"

Compute: there is no separate case. The charge test is the plain
`result: RND(MX(0, increase_rated_share - increase_deduction), 2) if increase_days >= K('minimum_increase_days') else 0.0`,
and `increase_filer_class` is a declared factor (`factors[0].id: increase_filer_class`).

Why it cannot be rendered: this scope and retirement sentence has to live in the hub, because it says which package-change charges this rule books. But the hub may not name a factor ("a filer class"), and it may not name the depended-on problem or its action beside its own state-form prerequisite sentence. That sentence is "The increase charge for a package change is worked out only after the term carries the package it moves to." (edge `problem: nonowner_ext_package_rerate`). Naming "the package re-rate rule's DUI realignment" there tells the reader which write produces that state. The computation document cannot hold it either, because it must say nothing about adjustments. Rendering the clause leaks a factor and routes the chain. Dropping it silently would be rendering around the source.
Fix on the source side: delete the illustrative clause ", as when the package re-rate rule's DUI realignment brings a filer class and other relativities onto the remaining days," from both `rule` and `overwrite[0].replaced_by`. The operative test "whose increase charge by this rule is above zero" stays as it is.

## F2 (blocking) — nonowner_ext_insured_cancel_return: unearned days have no floor, so the return can be negative or zero on reachable worlds (XF 8 negative lag, XF 20 zero amount)

Rule sentence:

> "The unearned days shorten while the company stays certified to the state: when the named insured has an Operator certificate on file, the unearned days are reduced by the filing charter's SR-26 transmission days plus its certificate run-off days for that certificate; when the named insured's Operator certificate has had its SR-26 sent (status cancellation_filed, the FR-44 one when both forms have), the unearned days run from the later of the cancellation effective date and that certificate's end date to the expiration date; with neither, the unearned days stand."

Compute:
`unearned_days: (standard_unearned_days - certificate_runoff) if operator_certificate_on_file else (DAYS(MX(cancellation_date, sent_certificate_end), F('expiration_date')) if sent_certificate_end else standard_unearned_days)`
`certificate_runoff: (CPARAM('fr','sr26_transmit_within_days', ...) + CPARAM('fr','certificate_runoff_days', ...)) if operator_certificate_on_file else 0`. In the fr charter these are 3 and 10 for every tier, so the reduction is 13 days.

Edge: suppose a named insured with a filed Operator certificate asks to cancel with 13 or fewer days left on the term. Unearned days come out at 0 or below, so the unearned premium and the return come out at 0.00 or negative. The rule still says the return "is booked as one return entry", but `cancel_nonowner_term_6aabad38` takes `return_amount` as "a positive number" and `premium_days` as "an integer of 0 or more". The same thing happens in the SR-26-sent branch when the certificate's end date falls after the term's expiration date. The rule says nothing about either case, so a faithful KB would teach an amount the tool cannot book.
Fix on the source side: floor the unearned days at zero in both rule and compute, and say what happens to a zero return. One option is a record test that carves it out, for example "a return of 0.00 books no return entry". Another is a realistic cap. The fix must not depend on posting a 0.00 line.

## F3 (lower severity; binding allocation) — quantities only factors use sit outside their factor, and a quantity the standard figure uses sits inside a factor (XF 1)

XF 1: "A factor-only quantity belongs to that factor; the baseline defines no quantity only factors use."
- Non-factor bindings read only by the filer-class factor: `late_fr44_through`, `late_sr22_through` (nonowner_ext_late_renewal_written); `rerate_fr44_through`, `rerate_sr22_through` (nonowner_ext_package_rerate); `offer_fr44_through`, `offer_sr22_through` (nonowner_ext_renewal_offer_premium); `increase_fr44_through`, `increase_sr22_through` (nonowner_ext_package_increase_premium). Each is read only by its `*_fr44_active` / `*_sr22_active` factor binding, and each policy's `compute_basis` quotes the filer-class sentence for it. Example: `late_fr44_through: CFIELD('fr','required_through_date', variant_name='FR-44 Operator Certificate', status='requested') if ...`.
- `request_reason` (nonowner_ext_insured_cancel_return) is a non-factor binding read only by factor `requirement_relief`: `requirement_relief: K('relief_requirement') if (request_reason == 'requirement_ended' and ...)`. Its basis quotes the requirement-completion sentence.
- The reverse case: `offer_window_left` is listed in factor `offer_lapse_window`'s bindings, yet that factor's own baseline (the standard figure) reads it: `baseline: offer_lapse_factor: offer_lapse_value if offer_window_left > 0 else 1.0`. `baseline.rule` also defines it: "the window's remaining months at the renewal are six less the whole months from the first lapse day to the renewal effective date".
Effect on the render: the computation document's hidden `covers` must claim bindings whose rule only a factor document states, and the factor document must claim a quantity the computation document defines. Nothing reaches the solver, but coverage stops matching what each document's prose actually says.
Fix on the source side: move each `*_through` binding and `request_reason` into its factor's `bindings`. Take `offer_window_left` out of `offer_lapse_window`'s bindings so it becomes a plain non-factor binding.
