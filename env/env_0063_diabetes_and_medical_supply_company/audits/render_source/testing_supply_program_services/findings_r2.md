# Render-surfaced source findings, round 2 — bgm (testing_supply_program_services)

Source: `bgm.extended.yaml` sha256 98c8f6f7d92efe2cb78ae27c0eff1fd367f67c25ab3357085015819a1192bdfd; `task_tools.py` unchanged (ff767d51…f617c).

Mechanical checks on the revised source:
- Every compute_basis quote is a verbatim substring of its rule.
- Every prerequisite `policy_source` is a verbatim substring of its rule.
- Every baseline.rule is a verbatim substring of its rule.

Re-checked against the compute: F1–F8 are closed in the revised source. The rule sentences now agree with their compute lines for the hardship shares, the courtesy reship's 30-day standard with bridge_shape, the noncovered overwrite, the held-shipment tie and no-POD cases, the PA window's 1-block floor and no-authorization case, the new-meter definition, the prior-plan dating and the refill's notice-gate measure.

## R2-1 (low; no effect on the KB) — a ladder's `when` text is broader than its rule and compute
- Location: `extended_policies[bgm_ext_noncovered_strip_charge].factors[unit_price_basis].ladder[0].when`
- Quote: "the tier's notice is abn_cms_r_131 and the denied claim carries a remittance"
- The revised rule says: "when the denied claim carries remittances whose allowed amounts total more than 0 and the treatment-class allowance gives at least one unit for the supply days". The compute says the same: `remit_allowed > 0 and class_allowance_units > 0`.
- The ladder summary was not updated with the rule. The KB renders the rule sentence, so the rendered rule and the compute agree.
