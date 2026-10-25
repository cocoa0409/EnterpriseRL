# Renderer scan-first STOP — product project, render round 2 (agent ad585938e3674dbac)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`. No documents written. render_r1.md findings 1–3 confirmed fixed.

## Finding 1 (blocking): the "ClearPath billing" test is narrower in compute than in the rule (XF 8 / XF 14)

File: `tasks/project_engagements/project.extended.yaml`. Policy `project_ext_milestone_billing`, factor `clearpath_good_standing`.

- **Rule (line 1534):** "Retainage is extended to clients in good standing on ClearPath: a client with ClearPath billing that shows no late fee posted in the twelve months before the invoice date has a further cp_clean_pct percent of the milestone invoice withheld as retainage, one whose ClearPath billing shows exactly one such late fee cp_one_pct percent, and any other client none, including a client with no ClearPath billing at all."
- **Compute (lines 1562–1563):**
  - `cp_billing: "XCOUNT('managed','managed_billing', event_type='managed_monthly_fee')"`
  - `cp_ret: "K('cp_clean_pct') if (cp_billing > 0 and cp_late12 == 0) else (K('cp_one_pct') if (cp_billing > 0 and cp_late12 == 1) else 0.0)"`
- **The mismatch:** the rule tests for any ClearPath billing. The compute only counts monthly seat fee entries. ClearPath billing has ten entry kinds, and the managed charter (`blueprint/products/managed.yaml`) invoices the onboarding fee at signing for terms other than 36 or 60 months. That fee is invoiced while the agreement is still applied, before go-live, and monthly fees only start after that.
- **Concrete case:** a client whose ClearPath agreement is applied or onboarding, or was cancelled from applied, whose billing holds only an onboarding fee and perhaps a payment, with no late fees. Under the rule, cp_clean_pct (2.5) is withheld; under the compute, `cp_billing == 0`, so nothing is withheld.
- **Fix needed:** either the rule names the entry kind (for example, "a client whose ClearPath billing shows a monthly seat fee"), or the compute counts every ClearPath billing entry.

## Finding 2 (low; possibly not worth a rework): the deposit dates its windows from today, the rule from the signature date

Same file, policy `project_ext_signature_deposit`.

- **Rule (line 1316):** "When the scheduled start date is rush_14_days or fewer calendar days after the signature date, including a scheduled start date on or before the signature date, ..." The twelve-month and six-month windows are likewise counted "before signature", measured "from the signature date" (lines 1309, 1313, 1320, 1332–1334).
- **Compute (lines 1362, 1364, 1366, 1368):** `lead_days: "DAYS(NOW, F('scheduled_start_date'))"`. The window counts `cp_late12`, `hw_late12` and `ach6` also measure from today, not from the recorded signature date.
- **Why it may not matter:** the two only differ if the deposit is posted on a later day than the signature. The base event defines the deposit's posting date as the signature date, and the prerequisite puts the signature in the same session. Reading `F('signed_date')` would make the compute literally match the rule.

## Everything else in the scan was clean (round-1 fixes in place; verbatim quotes; factor independence; method shapes; edge cases; scoped overwrites; schema fields; docstrings).
