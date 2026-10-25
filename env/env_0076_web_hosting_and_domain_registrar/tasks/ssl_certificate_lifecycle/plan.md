# plan — ssl_certificate_lifecycle (env_0076), M=2 (rework round 11)

Draw (draw_counts.py --tasks 2): task 0 prerequisite_problems=1, factor_counts=[5,4]; task 1 prerequisite_problems=3,
factor_counts=[5,5,5,4].

## Task 0 (frozen 2026-11-17 10:20:00 CST; DV Multi-Domain; stored card expired)
- root ssl_ext_install_charge (pay_certificate_installation_15b30562, holder pays at checkout) 5 factors
- prereq ssl_ext_support_renewal (renew_certificate_subscription_0365c0e5, holder pays at checkout) 4 factors
- edge install -> renewal: value_input (certs_covered), action form.

## Task 1 (frozen 2026-12-08 09:40:00 EST; EV Multi-Domain; purchases for the new server from a PayPal not on file)
- root ssl_ext_secondkey_order (order_secondkey_certificate_9d8b09ff, holder at checkout) 5
- ssl_ext_autorenew_charge (charge_certificate_autorenewal_c41e0ea2, agent, card) 5
- ssl_ext_names_charge (add_certificate_name_7df48eab, holder at checkout) 5
- ssl_ext_wait_names (grant_complimentary_names_f9ed3e27, agent, ssl_names_update + free reissue) 4
- edges: second-key -> auto-renew (value), second-key -> name (value, action), name -> auto-renew (value),
  name -> complimentary names (state), complimentary names -> auto-renew (state).

## Files
- ssl.extended.yaml generated from /tmp/ssl_certificate_lifecycle_0076/r11/pol_*.py (build.py); task_tools.py; tasks/0.json,
  tasks/1.json; worklog.md. No tool writes a row whose base trigger lands in another category.
