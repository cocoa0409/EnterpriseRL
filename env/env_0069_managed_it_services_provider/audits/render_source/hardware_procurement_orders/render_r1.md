# Renderer scan-first STOP — product hardware, render round 1 (agent acb2b325ad1bdcf90)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`. No documents written. Source: `tasks/hardware_procurement_orders/hardware.extended.yaml` (7 extended policies) and `task_tools.py`.

## Findings

**1. Blocking: a rule filter that compute does not apply, resting on something the records lack.**
- **Where:** `hardware.extended.yaml`, policy `hardware_ext_lapsed_quote_reissue`, factor `managed_bench_staging_rate`.
- **Rule sentence:** "The bench staging charge per unit of a re-issued infrastructure quote is staging_project_usd when the client's active ClearPath agreement covers firewall, switch and wireless configuration changes and the client holds an in-progress project engagement whose network design the bench configures from, staging_managed_usd when it holds such an active ClearPath agreement and no in-progress project engagement, and the order type's staging_fee_per_unit_usd for every other client."
- **Compute lines:**
  - `b_ri_project: "EXISTS('project', status='in_progress')"`
  - `f_ri_staging: "K('staging_project_usd') if (b_ri_network_mgmt and b_ri_project) else (K('staging_managed_usd') if (b_ri_network_mgmt and not b_ri_project) else P('staging_fee_per_unit_usd'))"`
- **The mismatch:** "whose network design the bench configures from" restricts which engagements count, but compute counts any in-progress engagement. Project records have no network-design field (`project.yaml` has none).
- **Example that splits them:** an active ClearPath Essentials client (network device management included) with one in-progress Assessment Engagement, re-issuing a Network Equipment Order quote.
  - The rule fails tier 1 (no network design) and tier 2 (it does hold an in-progress engagement), so it falls through to staging_fee_per_unit_usd, which is 145.00 per unit.
  - Compute gives staging_project_usd, which is 95.00 per unit.
- **Corroboration:** the policy's own `cross_category` note says "An in-progress project engagement, with an active ClearPath agreement covering network device configuration, sets the staging charge.", with no design qualifier. Compute's reading is the intended one.

**2. Secondary: a lead phrase that refers to data the records lack.**
- **Where:** policy `hardware_ext_staged_requote_total`, factor `defender_onboarding_rate`.
- **Rule sentence:** "The security preparation charge per unit of a staged re-quote follows the Microsoft 365 plan that licenses the units' users: nothing for a client holding an E5 plan whose active ClearPath agreement covers Microsoft 365 tenant administration, ..."
- **Compute line:** `f_edr_per_unit: "0 if (b_lic_e5 and b_def_tenant_admin) else (K('edr_essentials_usd') if (b_lic_e5 or b_lic_bp_e3) else K('edr_standard_usd'))"`
- **The mismatch:** compute reads the client's plans across all its active subscriptions, and E5 wins when the client holds both E5 and Premium/E3. No record says which plan licenses the units' users. For a client holding both plans, the lead phrase opens a second reading. The tier sentences themselves are client-level and consistent with compute.

**3. Minor overwrite hygiene: the out-of-scope clause drops content that is still in force.**
- **Where:** policies `hardware_ext_endpoint_approval_deposit` and `hardware_ext_infrastructure_approval_deposit`. Both retire the base clause in `hardware_approval_and_purchase_order`: "On approval a required deposit of deposit_pct percent of the quote total is invoiced, rounded half up to the cent, due on receipt (deposit_due)."
- **Replaced-by tails:** endpoint policy: "...and every other order's required deposit stays deposit_pct percent of the quote total." Infrastructure policy: same wording.
- **What is dropped:** for out-of-scope orders (Special-Order Equipment, Accessory & Peripheral Order, and endpoint or infrastructure orders approved over the credit limit), the tail no longer says the deposit is invoiced on approval, rounded half up to the cent, and due on receipt.
- **What it says instead:** the unqualified "stays deposit_pct percent" sits awkwardly against `hardware_agg_credit_exposure`, which makes over-limit orders 100 percent prepaid. That rule's "whatever its order type's deposit_pct ... say" still overrides it.
- **Effect:** this changes no figure today, but under XF recipe item 16 the tail should restate the whole in-force content for the out-of-scope cases.

## Checks that came out clean
- Every `compute_basis` quote, prerequisite sentence, baseline rule and `replaced_by` appears verbatim in its own policy's rule; every superseded clause is verbatim in its base policy.
- No factor reads another factor's binding; no factor id is a substring of a tool name; sibling overwrites name each other.
- The `MONTHS` month-end convention and the `within_months` "fewer than twelve whole months" boundary match the rule wording.
- Tool docstrings carry no example values.
