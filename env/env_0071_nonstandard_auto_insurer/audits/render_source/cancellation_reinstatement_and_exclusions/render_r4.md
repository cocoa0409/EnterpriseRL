# render_r4 — auto (Owner Auto Policy), cancellation_reinstatement_and_exclusions

RENDER round 4: STOPPED (source re-scan, before any document was rebuilt)

Gate checked: `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`.
Source re-scanned: auto.extended.yaml (sha256 6d45850b…5880); task_tools.py is unchanged (5a982b7f…a0f).
Read in full: audits/policy_kb/…/{_difficulty,0,1}.md, audits/runtime_context/…/{0,1}.md, rework_r12_claims.md.
No document was rebuilt or touched. docs/auto/ still holds the round-3 corpus, which the round-12 source change
(S-1) has made stale. No staging directory was created.

## S-1 change: verified consistent

- **auto_ext_nonpay_cancel_return and auto_ext_insured_request_cancel_return.** The rule words match the compute
  (`nc_filed`/`ic_filed`, `*_runoff`, `*_sr26_end`/`ic_cert_end`, `*_lag_raw`, `*_lag_max`) on every point:
  - "stood filed on the cancellation effective date" means the first-entered filed certificate has filed_date ≤ CED,
    or the first-entered cancellation_filed certificate has filed_date ≤ CED and sr26_date > CED;
  - the second run-off row needs sr26_date ≤ CED;
  - transmission days are kept only for a certificate standing filed on that date.
  - The run-off and transmission figures read from the filed certificate, else the cancellation_filed one. These
    figures are uniform across FR tiers, so which certificate they come from is immaterial.
- **auto_ext_lapse_reinstatement_rewrite.** The exposure tiers (`rw_cert_filed`, `rw_cert_sent`, end date ≥ the
  reinstatement effective date) and the form/type/state selection ("first-entered filed when filed_date ≤ the
  reinstatement effective date, else first-entered cancellation_filed when filed_date ≤ that date") match
  `rw_form`/`rw_ctype`/`rw_fstate` with their own date bindings.
- **N-1.** The rating dates now sit only in the age-class sentences of exclusion, re-listing and lift. These match
  `ex_age`, `ad_age_then`/`ad_age_now` and `ab_age`.

## G2 (blocking) — auto_ext_insured_request_cancel_return: negative lag (processing date before the cancellation effective date) is not stated

This gap existed in round 3 and I passed it then. It is raised now because the S-1 rework rewrote this exact sentence,
and XF_recipe point 8 lists negative lag as a class that must be stated.

Rule:
> "SR-26 transmission days on a cancellation at the insured's request, when a certificate backed by the term stood filed on the cancellation effective date, read as stated for the days returned: the company stays bound to the state until certificate_runoff_days after the SR-26, which goes out no earlier than the ending date and no later than sr26_transmit_within_days calendar days after it (the ending date counted as day 0), so the calendar days from the cancellation effective date to the processing date, at most sr26_transmit_within_days, are also kept: processed sr26_transmit_within_days or more days after the cancellation effective date, sr26_transmit_within_days days are kept; processed one or more but fewer days after it, those days are kept; processed on the cancellation effective date itself, or with no certificate standing filed on that date, none are."

Compute:
- `ic_eff: MX(ic_req_date, ic_recv_date)`
- `ic_lag_raw: DAYS(ic_eff, NOW) if (... stood filed ...) else 0`
- `ic_lag: ic_lag_max if ic_lag_raw >= ic_lag_max else (ic_lag_raw if ic_lag_raw >= 1 else 0)`

The base rule (auto_insured_cancellation) allows a requested effective date later than the date the request was
received. The cancellation then takes effect on that later date, and the confirmation can be processed before it.
On such a term with a filed certificate, `ic_lag_raw` is negative and compute keeps 0 days. The words name three
cases: "N or more days after", "one or more but fewer days after", and "on the cancellation effective date itself".
None of them covers processing before the cancellation effective date. A reader is left with "the calendar days from
the cancellation effective date to the processing date … are also kept", which is a negative count, and the KB cannot
state the zero without adding a boundary the source lacks.

The same sentence in auto_ext_nonpay_cancel_return is not affected, because that cancellation is never processed
before its effective date ("processed no earlier than the cancellation effective date").

Fix on the source side (smallest): in the insured-request sentence, extend the last case to read "processed on or
before the cancellation effective date, or with no certificate standing filed on that date, none are". Update the
matching ladder "when" and compute_basis quote. Compute already returns 0 here, so no scored value moves.

No other mismatch was found in the changed source.
