# Renderer findings — product encounter (difficulty hospital_account_billing), render round 1
Saved verbatim by the coordinator from renderer agent a8965743c2bd82d6d (2026-10-20). The renderer wrote no documents (scan-first STOP).
Gate read: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.

## Mismatch 1 (RED, rule-vs-compute on an absent record, XF B6/B13)

File: `tasks/hospital_account_billing/encounter.extended.yaml`, policy `encounter_ext_observation_rate_discount`, factor `observation_day_count`.

The rule says that when `service_end_date` is empty, the observation days are 0:
- Baseline sentence: "The observation days are the plain difference in days between service_start_date and service_end_date (0 when service_end_date is empty), …"
- Factor sentence: "… for a stay whose service_end_date equals its service_start_date and that carries observation hours, the observation days are 1; otherwise they stay at the plain day difference."

The compute gives 1 day in that case:
```
- ob_plain_days: DAYS(F('service_start_date'), F('service_end_date')) if F('service_end_date') else 0
- ob_days: -(-ob_hours // 24) if (ob_plain_days > 0 and ob_ed_lines > 0 and ob_hours > 24 * ob_plain_days) else (1 if (ob_plain_days == 0 and ob_hours > 0) else ob_plain_days)
```
With an empty end date, `ob_plain_days` is 0. Any observation hours then fall into the `ob_plain_days == 0 and ob_hours > 0` branch, which gives 1 day. The rule only gives 1 day when the end date equals the start date.

The amount changes. By the rule the discount is the observation-hour charges times the net factor (zero days). By the compute it is the charges less one day of the day rate, times the net factor.

The case is inside the policy's own scope. The scope is any SELF_PAY account with revenue-code 0762 lines and no package price, with no final-bill requirement. The schema says `service_end_date` is "empty while the encounter or series is still open".

The fix is in the source. Either change the compute's same-day test to require that `service_end_date` is present and equals `service_start_date`, or reword the rule to match the compute.

## Note 2 (lower severity, docstring claims an effect the body lacks, XF 21)

File: `task_tools.py`, all six tools.

The `amount` docstring says: "the value is stored rounded half-up to the cent exactly as given".

The body does `amt = round(float(amount), 2)`. Python's `round` rounds a tie to the even digit, and float values add their own errors, so it is not half-up: `round(0.125, 2)` gives 0.12, where half-up gives 0.13. This only matters for amounts with more than 2 decimals, which the docstring already rules out.

## Note 3 (conditional)

Affects: `encounter_ext_noncovered_discount` / `near_eligibility` (`nc_case_*`); `encounter_ext_terminated_coverage_discount` / `coverage_loss_near_eligibility` (`td_case_*`) and `catastrophic_share` (`td_cat_date`, `td_case_income`).

The rule says "… a case not yet determined is not a determination" (and in policy 3, "never a case still awaiting determination").

The compute uses `XLATEST(..., date_field='determination_date')`, which compares `str(row.get(date_field))`. If the seed stores an undetermined case's date as `""`, the compute matches the rule. If it stores `null`, the key becomes `"None"`, which sorts above every date, so the undetermined case wins. The allowance then drops to 0 even when a qualifying denial exists.

(Coordinator check: both current task worlds seed only denied cases with dates; the defect is latent for any producible world holding an undetermined case stored as null.)

## Clean
Every compute_basis quote, baseline rule, replaced_by and prerequisite sentence verbatim; no factor id inside a tool name; no factor reads another factor's output; tie rules, assembly sentences, rounding placement, caps, floors and ladders match the compute; sibling overwrites name each other's cases; no forbidden imports.
