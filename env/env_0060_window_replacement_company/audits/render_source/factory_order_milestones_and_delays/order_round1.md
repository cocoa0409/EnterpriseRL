# Render-source findings — product `order` (Factory Production Orders), round 1

Source: `env/env_0060_window_replacement_company/tasks/factory_order_milestones_and_delays/order.extended.yaml`
(+ `task_tools.py` beside it). Found while rendering `docs/order/`; the docs carry the source wording as it
stands and do not render around these findings.

## F-1 (undefined branch, rule vs compute) — `order_ext_customer_remake_charge`, factor `build_stage_share`

Location: `extended_policies[id=order_ext_customer_remake_charge].rule` (also `compute_basis.asm_date /
glass_date / stage_share`, `factors[id=build_stage_share].ladder`) vs `compute[stage_share]`.

Rule sentence (verbatim):

> "A build-stage share is applied by how far the order had been built when the remake was recorded: when the
> most recent assembly complete checkpoint on the order is dated on or before the remake date, the full charge
> is due; when there is no such assembly checkpoint but the most recent glass received checkpoint is dated on
> or before the remake date, 70 percent is due; when neither checkpoint is on record by the remake date, 40
> percent is due."

Compute (verbatim):

> `stage_share :: 1.0 if asm_date != '' and asm_date <= rmk_date else (K('share_glass_stage') if glass_date != '' and glass_date <= rmk_date else K('share_early_stage'))`
> with `glass_date = LATEST(... milestone_kind='glass_received')` and `asm_date = LATEST(... milestone_kind='assembly_complete')`.

The three branches of the sentence are not exhaustive. When a glass received checkpoint dated on or before the
remake date exists **and** a later glass received checkpoint is dated after the remake (with no qualifying
assembly checkpoint), branch 2 fails (the *most recent* glass received is after the remake), and branch 3 fails
too (a glass received checkpoint *was* on record by the remake date). The rule then decides nothing, while the
compute charges 40 percent. The same gap opens for assembly complete (an earlier assembly checkpoint on or
before the remake plus a later one after it). This case is realistic in this charter: `order_ext_remake_delay_notice`
explicitly contemplates "the most recent glass received checkpoint on the order is dated after the remake
(replacement glass for the remade units)".

Suggested fix (authoring side): word the third branch as the compute decides it ("otherwise, 40 percent is
due"), or state the tiers on "a ... checkpoint dated on or before the remake date" and align the compute.

Rendering: the factor document carries the three branches as the rule words them and adds no completion for
the uncovered combination.
