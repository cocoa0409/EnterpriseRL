# Renderer scan-first STOP — product licensing, render round 1 (agent aa8133c94fe9924b4)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`. No documents written.

The mechanical sweep was clean. Every `compute_basis` quote, `baseline.rule` sentence, `replaced_by` and prerequisite sentence is verbatim in its rule, and every `superseded_clause` is verbatim in its base rule. No factor reads another factor's binding, no plain binding reads a factor binding, and no factor id is a substring of a tool name. The tool docstrings have no example values and claim nothing their bodies don't do. These are the findings:

**F1: an active ClearPath agreement in credit falls to three instalments, not six (XF B.8 / B.13)**
- File: `tasks/microsoft_365_subscriptions/licensing.extended.yaml`, policy `licensing_ext_payment_arrangement`, factor `instalment_count`.
- Rule: "The number of instalments follows the client's ClearPath standing: with an active ClearPath agreement that has renewed at least twice and owes nothing, the arrangement runs over six instalments; with an active ClearPath agreement that has renewed fewer than twice or owes a balance, over four; without an active ClearPath agreement, over three."
- Compute: `n_instal: K('n_long') if (cp_renewals != None and cp_renewals >= 2 and cp_owed == 0) else (K('n_active') if (cp_renewals != None and (cp_renewals < 2 or cp_owed > 0)) else K('n_standard'))`
- Example: an active agreement renewed 2 or more times with `balance_due_usd` below 0 "owes nothing", so the rule gives six. Compute fails both active branches and returns three, the rule's "without an active ClearPath agreement" value.
- This case can happen: `blueprint/products/managed.yaml` `managed_payment_application` says "An amount beyond every open invoice stays on the agreement as a credit balance against future invoices."

**F2: no month-end rule for the "one whole month" onboarding window (XF B.12)**
- File: same yaml, policy `licensing_ext_seat_partial_charge`, factor `onboarded_staff_discount`.
- Rule: "when the ClearPath seat ledger records at least as many user onboardings effective less than one whole month before the charge as licenses added, the discount is 3 percent; when it records at least one such onboarding but fewer than the licenses added, 1.5 percent; otherwise none."
- Compute: `onboardings: XCOUNT('managed', 'managed_seat_changes', within_months=1, date_field='effective_date', change_reason='user_onboarding')`
- The window uses `MONTHS()`, under which an onboarding dated Jan 31 is still "less than one whole month" before a Feb 28 charge. The charter's own anniversary rule ("when that day does not exist in the end month, the last day of that month is used") gives the opposite answer.
- Onboarding dates can fall on any day, so this is reachable. The licensing and ClearPath late-fee windows are not affected, because both charters post late fees on the first of the month.

**F3: the Microsoft 365 user count includes users on closed Continuum plans (XF B.14 decoy)**
- File: same yaml, policy `licensing_ext_admin_fee`, factor `backup_bundle_rate`.
- Rule: "with an active Continuum plan protecting at least as many Microsoft 365 users as the licenses counted, the rate is 90 percent; with an active Continuum plan protecting at least one Microsoft 365 user but fewer than the licenses counted, 95 percent; otherwise the whole rate. Microsoft 365 users protected are the Continuum protections of Microsoft 365 users less their removals."
- Compute: `m365_protected: XCOUNT('backup', 'backup_device_changes', event_type='backup_devices_protected', device_class='m365_user') - XCOUNT('backup', 'backup_device_changes', event_type='backup_devices_unprotected', device_class='m365_user')`
- That count covers every Continuum plan the client has held, whatever its status. Closing a plan records no removals: `backup.yaml` `backup_closed` triggers only `backup_dr_days_forfeited`.
- Example: a client with a closed old plan and a new active plan. Compute counts the closed plan's users toward the active plan's tier, while the rule reads as the active plan's own protections.

**F4: two rule phrases depend on facts the records don't hold (XF D.26)**
- (a) Policy `licensing_ext_reduction_credit`, factor `review_miss_goodwill`.
  - Rule: "Where a reduction made in a renewal window shows that Stratton Bay's pre-renewal license review missed licenses, a review goodwill is added to the reduction credit: …"
  - Compute: `review_pct: K('review_high_pct') if (in_renewal_window and vcio != None and vcio >= K('vcio_high')) else (...)`
  - Compute never checks whether a review missed licenses, and no record holds that fact. The "Where … shows that" condition can be read as an extra test that can't be checked.
- (b) Policy `licensing_ext_admin_fee`, factor `security_baseline_upkeep`.
  - Rule: "the client holds an active Sentinel subscription on a tier whose identity_threat_detection is true, which watches the same tenant"
  - Compute: `sentinel_idt: CPARAM('security', 'identity_threat_detection', status='active')`
  - The security holdings have no tenant field, and compute doesn't test one.

After a rework, the render needs a new gate line and a fresh run from Step 0.
