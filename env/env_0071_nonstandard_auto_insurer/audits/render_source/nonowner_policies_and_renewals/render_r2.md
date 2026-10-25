# render_r2 — nonowner (Named Non-Owner Policy) — STOPPED before any doc

Gate: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN` (present).
Source re-scanned: nonowner.extended.yaml (mtime Oct 20 15:24) and task_tools.py (mtime Oct 20 06:49).

## render_r1 items: all closed
- F1 closed. The illustrative clause naming the package re-rate realignment and the filer class is gone from the increase rule and from its replaced_by.
- F2 closed. `unearned_days: MX(0, ...)` now floors the days at zero. The rule adds "when the unearned days come to zero nothing is returned and the cancellation books no return entry". `cancel_nonowner_term_6aabad38` now takes `return_amount` as "a number of zero or more", and "a zero amount books no return entry".
- F3 closed. The `*_through` bindings are gone (inlined into each `*_fr44_active` / `*_sr22_active` factor binding). `request_reason` is now in `requirement_relief`'s bindings. `offer_window_left` is now a plain non-factor binding.

## F4 (blocking, new): declared params that neither rule nor compute uses, so the corpus cannot carry them without adding policy

The rule rewrite left constants in `params` that no sentence of the rule, no compute line, no ladder and no factor baseline reads (checked by sweeping every `K('...')` in compute, ladders and factor baselines).

- **nonowner_ext_late_renewal_written** `params` still declares
  `lapse_window_months: 6`, `nonpay_recent_months: 3`, `nonpay_window_months: 6`, `rel_nonpay_recent: 1.08`, `rel_nonpay_later: 1.04`.
  The rule now has no lapse window and no nonpayment relativity. Its lapse sentence is "six days or more carry 1.12, three to five days carry 1.06, and one or two days carry no late-renewal lapse relativity", with no window. The compute has no `MONTHS(` and no nonpayment-return read. Its only relativity and credit inputs are `late_filer_change`, `late_lapse_relativity` and `late_plan_change`, in
  `late_rated_premium: F('full_term_premium') * late_filer_change * late_lapse_relativity * late_plan_change`.
- **nonowner_ext_reinstatement_rewritten** `params` still declares `lapse_window_months: 6`.
  The rule's lapse sentence has no window: "six days or more carry 1.12, three to five days carry 1.06, and one or two days carry no reinstatement re-write lapse relativity". The compute has no `MONTHS(`:
  `rewrite_lapse_relativity: (K('rel_lapse_long') if rewrite_lapse_days >= K('lapse_long_days') else (K('rel_lapse_mid') if rewrite_lapse_days >= K('lapse_mid_days') else 1.0)) if (rewrite_lapse_days >= 1) else 1.0`.

Why it blocks: check_docs makes every `<policy>.params.<key>` a required quantitative key, and it must be carried by a doc of that same policy with its value showing in that doc's content ("a policy's own numbers are rendered in that policy's documents"). For these six keys there are only two ways through. One is to write a lapse window or a nonpayment relativity into the late-renewal or reinstatement docs, which is policy the rule does not have. The other is to claim the keys on a doc whose prose happens to contain the digits, which games the gate. I will do neither.
Fix on the source side: delete the six keys from those two policies' `params`. Nothing reads them, so no compute, rule or gold changes.

## F5 (non-blocking; worth tightening while the source is open): selection order of the filer requirement

This affects every filer-class reading: `late_filer_change`, `rerate_filer_class`, `offer_filer_class` and `increase_filer_class`.
Rule (late-renewal wording; the other three are the same with their own date):

> "The requirement counted is the named insured's Operator certificate requirement, an SR-22 Operator Certificate or FR-44 Operator Certificate filing of the named insured whose status is requested, filed or rejected and whose required-through date is on or after the renewal term's effective date or is not recorded; when both forms are recorded the FR-44 one counts, and among several filings of the counted form a requested one is read before a filed one and a filed one before a rejected one, the one recorded first within a status"

Compute (`late_fr44_active` and the others): it first picks one filing of the form by status (requested, otherwise filed, otherwise rejected), then tests that filing's required-through date, with no fall-back:
`(CFIELD(... status='requested') and (not CFIELD('fr','required_through_date', ... status='requested') or ... >= F('effective_date'))) or (not CFIELD('fr','filing_state', ... status='requested') and CFIELD(... status='filed') and (...)) or (...)`.

Read as a filter first ("filings whose required-through date is on or after …", then priority among those), the rule gives a different answer from the compute in one case. That case is a requested filing whose required-through date is already past, alongside a filed filing of the same form that is still current: the filter reading counts the filed one, the compute counts nothing for that form. The same applies to `late_released_form`, where the compute picks the first `cancellation_filed` row, then the first `terminated` row, and tests each one it picks. The rule allows the compute's reading, so on its own this would not have stopped the render; the docs would have stated the compute's order.
Suggested wording: "the filing read for a form is its requested filing, otherwise its filed one, otherwise its rejected one (the one recorded first within a status), and that filing counts when its required-through date is on or after …".
