# Renderer findings, disburse render round 1 (renderer agent a22520d3c649aa9f1; saved verbatim by the coordinator — the harness blocked the renderer from writing its findings file). Renderer STOPPED before writing any document.

## F1 (RED, XF B1/B4): "rounded up to the next multiple" moves exact multiples up a full step

Two policies round up with `-((-(x) - 0.000000001) // k) * k`. In Python that is ceil((x + 1e-9) / k) times k, so a value that is already a multiple of k goes up by one whole k. Read naturally, the rule leaves an exact multiple unchanged.

**F1a `disburse_ext_alert_election`** (compute line 1940, rule line 1916, baseline.rule line 2069)
- compute: `result: -((-((base_amount * (1 + (instant_percent + age_percent + returns_percent + final_pay_percent + groups_percent) / 100)) - 0.000000001)) // K('floor_rounding_usd')) * K('floor_rounding_usd')`
- rule: "The replenishment floor is the tier's low_balance_alert_default_usd, rounded up to the next multiple of floor_rounding_usd." and "... and then rounded up to the next multiple of floor_rounding_usd."
- Every tier's default (100, 250, 500, 1000, 5000, 10000) is already a multiple of 50, so the rule's baseline floor is just the default. The compute gives the default plus 50 on every tier: 150, 300, 550, 1050, 5050, 10050.
- Hypothetical witness: a Core service with no payouts, activated more than 6 whole months ago, no returned deposits, no final pay, no live agreement. The rule gives 250.00; the compute gives 300.00.
- Second witness: base 500 with 10% gives 550, a multiple of 50. The rule gives 550; the compute gives 600.
- The percentages often land on exact multiples, so a scored floor may itself be off. The funding deposit and the replenishment debit build on the alert level on file through their prerequisite edges, so the error carries into them.

**F1b `disburse_ext_replenish_debit`** (compute line 2156, rule line 2116)
- compute: `result: MX(P('auto_replenish_minimum_usd'), -((-((debit_size * (1 + (weekend_percent + ewa_percent) / 100) * new_service_multiplier * returns_multiplier) - 0.000000001)) // K('debit_rounding_usd')) * K('debit_rounding_usd'))`
- rule: "... and then rounded up to the next multiple of debit_rounding_usd; it is never below auto_replenish_minimum_usd."
- Hypothetical witness: alert level 2000, ledger balance 1500, a Tuesday, no live agreement, activated more than 6 whole months ago, no returns. The debit size is 500. The rule gives 500.00; the compute gives 600.00.

**Suggested fix:** flip the epsilon sign to `-((-(x) + 0.000000001) // k) * k`, which is ceil(x − 1e-9). I checked it: it keeps 250 at 250 and maps 500 times 1.10 to 550. The tasks' scored, baseline and sensitivity figures for these two policies and the funding deposit then need re-checking. Rewording to "the next multiple above" is the other option, but that would add a step to every default alert level, which seems unlikely to be intended.

## F2 (RED, XF A4/A5): `ledger_balance` is bound inside factor `rd_size` in `disburse_ext_replenish_debit`

- `factors[rd_size].bindings` (lines 2177–2180) are `ledger_balance`, `payouts_month_total` and `debit_size`.
- baseline.rule (line 2268) defines the quantity: "The replenishment debit is the alert level on file less the prefund balance the ledger shows, that is every deposit, returned payout, recall and fee credit less every returned deposit, payout, fee and withdrawal on the service, and it is never below auto_replenish_minimum_usd."
- The `rd_size` baseline is `debit_size: alert_on_file - ledger_balance`, so the standard calculation needs it too. It is also the gate of the platform-fee prerequisite edge (`gate: ledger_balance`, line 2128).
- The sibling `disburse_ext_funding_deposit` keeps the same selection, with the same defining sentence, as a plain non-factor binding.
- For rendering, the computation document must define the ledger balance, but covers would assign it to the `rd_size` factor document, which would then have to define it again.
- **Suggested fix:** take `ledger_balance` out of `rd_size.bindings` so the computation document claims it.

## Checked clean in the same pass
- B5: every compute_basis quote, overwrite replaced_by, prerequisite policy_source and baseline.rule appears verbatim in its rule (scratch sweep).
- B1: rule and compute agree at the edges of: closing-month fee (billed-part thirds, bundle and migration branches); early closure fee (measure order, all five relief ladders); platform fee (activation thirds, bundle scaling); replenishment debit (weekday index; 2000-01-07 is a Friday); funding deposit (tiers, zero-due carve-out).
- B4: the half-up RND(x + 1e-9, 2) sentences match in the closing-month, early-closure, platform-fee and funding-deposit policies.
- C1/C3: sibling overwrites name each other's case; restated tails complete. D1/D3: each tool body enforces its docstring; no forbidden imports. A8: no factor id is a substring of a tool name.
