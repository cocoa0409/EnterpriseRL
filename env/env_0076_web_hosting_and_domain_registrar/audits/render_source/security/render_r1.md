# render_r1 — erl-kb-doc-render security (base, agent a845a9c6c97b18c1d), STOPPED before writing; findings verbatim from /tmp/render_security_0076/findings.txt (saved by coordinator)

RENDER STOP — security (base type), source env/env_0076_web_hosting_and_domain_registrar/blueprint/products/security.yaml
sha256 1c1f3d5ca651dc73774c42a0d9448196cc845f22ed4f966c4fd5de581f3eb4f0
No document written; no staging dir created.

F1 (BLOCKING, conflicting branches, no precedence) — 1-month plan cancelled before setup completes.
  policies[security_money_back].rule: "a 1-month charge is never refunded, and a cancellation before setup completes is refunded in full."
  parameter_schema.monthly_refundable: "Whether a 1-month term charge is ever refunded, boolean" (false on every tier)
  events[security_setup_cancel].triggers: security:security_refund (charge_type new_plan), unconditional.
  A pending_setup plan on a 1-month term that the customer cancels falls in both branches: "never refunded" vs "refunded in full". The source does not say which wins.
  Fix: state the precedence in the rule (e.g. "a 1-month charge is never refunded except on a cancellation before setup completes", or the opposite) and align monthly_refundable's description.

F2 (BLOCKING, overlapping branches) — cleanup basis when a re-infection falls inside the guarantee window while included cleanups remain.
  policies[security_agg_cleanup_quota].rule: "A cleanup is included while security_msr_included_cleanups_year is below the tier's included_cleanups_per_year, a re-infection within reinfection_guarantee_days of the previous completed cleanup is cleaned free and counted as guarantee, and any other cleanup is paid at extra_cleanup_fee."
  parameter_schema.reinfection_guarantee_days: "Calendar days after a completed cleanup during which a re-infection is cleaned free and not counted"
  On Plus..Enterprise (included 1..12) a re-infection 10 days after an included cleanup with quota left reads as "included" by the rule's clause order and as "guarantee / not counted" by the parameter description. Also undefined: whether "the previous completed cleanup" may itself be a guarantee cleanup (chained windows).
  Fix: one sentence fixing the order, e.g. "A re-infection on or before ... is cleaned under the guarantee and not counted, whatever the included count; any other cleanup is included while ... and otherwise paid ...", and say whether a guarantee cleanup restarts the window.

F3 (edge branch undefined) — Essentials for a site not hosted at Harborline.
  policies[security_pricing].rule / eligibility[essentials_not_on_scanning_plan].condition: "A tier whose not_sold_with_included_scan is true may be ordered only for a site whose Harborline hosting plan tier does not include daily malware scanning"
  parameter_schema.not_sold_with_included_scan: "Whether the tier is withheld from a site whose Harborline hosting plan already includes daily malware scanning"
  With hosting_id null the "only for a site whose Harborline hosting plan ..." reading forbids the order, the "withheld from a site whose ... already includes" reading allows it. Also unstated whether the hosting plan's status matters (e.g. a cancelled Harborline Pro plan still linked).
  Fix: add "a site hosted elsewhere may order it" (or not) and the status the hosting plan must have.

F4 (minor, rule vs formula detail) — upgrade proration.
  policies[security_plan_changes].rule: "... the target's term price minus the current tier's term price for the current term length, after the discount basis of security_pricing, ..." — the date on which the discount basis is judged is not given (security_renewal says "on the renewal date"; the upgrade rule says nothing, and hosting_id can change mid-term via security_settings_update).
  parameter_schema.price_rounding: "Rounding of every computed security amount: half_up_to_cent" vs formula upgrade_amount: round(price_difference * remaining_days / term_days, 2) with price_difference unrounded. With current list prices and 0/10/15/20/25 % the two readings coincide, so this is low risk.
  Fix (optional): "judged on the upgrade date"; "only the final amount is rounded".

F5 (minor, scope) — money-back "refunded in full".
  policies[security_money_back].rule: "An immediate cancellation of a 12-month plan is refunded in full only on or before the plan's opening date plus money_back_days calendar days." — does "in full" include an upgrade_proration charge billed inside the window (security_refund is one row per refunded original charge)? Also refund_destination (original_payment_method or account_credit) has no rule choosing between them.
  Fix (optional): name the charges refunded and the destination rule.

F6 (note) — policies[security_setup_and_lifecycle].rule "A plan whose renewal is unpaid at the term end expires the next day" while events[security_expire].fields.expired_date = "The term end date." and expired_grace anchors on the expired date. Consistent, but a reader may take the expired date to be the day after the term end; consider stating "its expired date is the term end date" in the rule.
