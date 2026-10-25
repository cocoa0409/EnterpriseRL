# render_r1 — erl-kb-doc-render domain (agent aaf61684777c9c6cf), STOPPED at the source scan; no document written. Findings saved verbatim by the coordinator from the renderer's reply.

## Findings

### D1 — Assembly sentences that name the factor quantities (all 8 extended policies)

In every extended policy, the plain binding that sums the credits is defined by a rule sentence (quoted verbatim in its `compute_basis`) that lists each factor quantity by name. The computation document owns that binding, so it would have to name every factor and give away the factor inventory; leaving the sentence out leaves the credits undefined.

On top of that, each `baseline.rule` ends with a sentence that only makes sense against those named factor quantities:
- "In the standard computation the lapsed-year reseller discount and the lapsed-year credits are zero."
- "In the standard computation the grace line's Domain Care credits are zero." The other policies have the same sentence with their own names.

The subtraction order and the floor at zero are part of the assembly, so they can only live in the computation document. A factor document cannot restate them.

The eight sentences, with their yaml lines:

1. `domain_ext_lapsed_registry_year`, `lr_credits` (l.2030): "The lapsed-year credits are the lapsed-year hosting credit, the lapsed-year plan allowance, the lapsed-year volume credit and the lapsed-year autopay credit added together." The baseline (l.2153) also defines the component as "renewal_price reduced by the lapsed-year reseller discount" and sets "the lapsed-year reseller discount and the lapsed-year credits are zero".
2. `domain_ext_grace_line_price_match`, `gl_credits` (l.2274): "The Domain Care credits of a grace-period renewal charge are the grace line's hosting credit, the grace line's plan allowance, the grace line's volume credit, the grace line's autopay credit and the grace line's term credit added together, each read from the account's records on the day of the price match." Baseline at l.2371.
3. `domain_ext_manual_line_price_match`, `ml_credits` (l.2494): the same sentence with "manual line's …" names. Baseline at l.2591.
4. `domain_ext_maximum_term_extension`, `mx_credits` (l.2717): "The maximum-term credits are the maximum-term hosting credit, the maximum-term plan allowance, the maximum-term volume credit, the maximum-term autopay credit and the maximum-term term credit added together." Baseline at l.2837 names the reseller discount and the credits.
5. `domain_ext_redemption_restore_price`, `rs_credits` (l.2962): "The restored-year credits are the restored-year hosting credit, the restored-year plan allowance, the restored-year volume credit and the restored-year autopay credit added together." Baseline at l.3082.
6. `domain_ext_transfer_line_price_match`, `tl_credits` (l.3189): "The Domain Care credits of a inbound transfer charge are the transfer line's hosting credit, the transfer line's plan allowance, the transfer line's volume credit, the transfer line's autopay credit added together, …". Baseline at l.3267.
7. `domain_ext_restore_line_price_match`, `rl_credits` (l.3381): the same shape with "restore line's …" names. Baseline at l.3459.
8. `domain_ext_restore_day_extension`, `rx_credits` (l.3575): "The restore-day credits are the restore-day hosting credit, the restore-day plan allowance, the restore-day volume credit, the restore-day autopay credit and the restore-day transfer price lock added together." Baseline at l.3696.

Suggested fix: define each credits total once, generically, without listing the factor quantities. Each factor would then contribute on its own against a quantity the baseline defines, and the "In the standard computation … are zero" sentences would no longer be needed to make the baseline computable.

### D2 — Rounding: the rule says half up, the compute misrounds exact half-cent ties (latent)

- **Where:** `mx_component` (l.2685) is `int(P('renewal_price') * mx_years * (100 - mx_pct) + 0.5) / 100`. `rx_component` (l.3541) is the same expression with the `rx_` bindings.
- **What the rule says:** "The maximum-term renewal component is the TLD's renewal_price times the maximum-term years, reduced by the maximum-term reseller discount, rounded half up to the cent". The restore-day rule says the same.
- **The difference:** the multiplication is done in floating point with no epsilon, so an exact half-cent tie can round down. Every combination of renewal price, years 1–10 and the reseller discount percentages checked. Two cases differ, both at 5 years on a Harborline Reseller Silver account (5%): .co: compute gives 156.65, half up gives 156.66; .io: compute gives 270.65, half up gives 270.66.
- **Reachability:** both cases can occur in either policy (task files not read).
- **Unaffected:** the tool bodies' `_Fmt.cents` already adds 1e-9, and the lapsed-year and restore components never tie in any combination.

### Checked and clean (renderer's list)
compute_basis/baseline quotes verbatim; 5 prerequisite sentences verbatim; 21 superseded_clause verbatim with in-force replaced_by; no factor reads another factor; ladders cover all branches; mx_exact/rx_exact day-of-month test matches; tools one-per-policy, docstrings/bodies agree; holder-paid extension payments fit owner ruling (b).
