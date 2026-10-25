# Render-surfaced source findings, round 2 — pump (insulin_pump_program_services)

Source at render: pump.extended.yaml sha256 2cb90ffa1c232994a1fd2e2523c37094fdbe4b3714d61e0387c82a59369ee015; task_tools.py sha256 01563d460faf3b418857c7fffee1adb4919977a489ddeb51ece168bb72f85042 (unchanged).
Round-1 findings F1–F7 checked against the reworked source: all closed as the coordinator stated (F1 by the waiver-mode restructuring; F2 by the denial routing in the reversal rule; F3 by the newest-notice wording; F4 by the 0-day sentence; F5 by the active-CGM condition; F6 by the narrowed superseded clause; F7 by the month-window sentences).

## R2-1 (low): reversal CO-197 routing — "not valid on its ship date" is tested only against the grant's end date
Location: `extended_policies[pump_ext_unsupported_charge_reversal].rule`; compute `x_gthru`, `x_denied`.
- Rule: "where a PR-204 denial answers it, or a CO-197 denial does and the grant the line drew on was not valid on its ship date so that the denial is not appealed, every unit of the line is denied; otherwise none is."
- Compute: `x_gthru = LATEST('pump_orders', 'valid_through', date_field='valid_from', pump_order_id=x_grant) or ''` and `x_denied = ... x_units if (x_pr204 > 0 or (x_co197 > 0 and (x_gthru == '' or x_gthru < x_date))) else 0`.
- Gaps:
  - A grant whose valid-from date is later than the line's ship date is "not valid on its ship date" under the rule, but the compute treats it as valid, so no unit is denied.
  - Base `pump_evt_denials_and_appeals` makes a CO-197 appealable when "an authorization grant valid on the date of service is on file" (any grant of the program). The rule's "so that the denial is not appealed" reads only the grant the line drew on.
- Rendered as the rule states it.
