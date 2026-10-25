# Renderer findings (verbatim final reply of agent a2011b9cd3ba4cead, saved by the coordinator)

I stopped round 2 before writing anything because one source problem remains. No documents or staging were created and check_docs.py was not run, so there is no DOCS OK line and no document count. I sent the full findings to the coordinating agent (a53a62ebb565a4bbe).

**Gate and source.** The last line of `env/env_0079_property_restoration_contractor/audits/policy_task/rebuild_contracts_and_draws/_difficulty.md` reads `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`, so the gate is met. I rescanned the reworked `env/env_0079_property_restoration_contractor/tasks/rebuild_contracts_and_draws/rebuild.extended.yaml` from Step 0. Only the five extended policies changed; the base section is identical to round 1.

**Round 1 findings.** All 13 items in `env/env_0079_property_restoration_contractor/audits/render_source/rebuild_contracts_and_draws/render_r1.md` are fixed in the new source. That includes the carrier-priced change order being rounded up to whole sheets or minimum hours, which was the edge case you asked about. The mechanical checks also came back clean: quoted sentences match their rules, and no factor reads another factor's values.

**What still blocks rendering.** It is in the additive change order policy (`rebuild_ext_change_order_signature`).
- The rule defines "A carrier-scope line is an insurance_scope change order on an insurance_claim contract that names a supplement the carrier has approved."
- The four calculation steps behind that definition (`cl_kind`, `cl_supplement`, `cl_approved`, `carrier_line`) are not assigned to any factor. That puts them in the calculation document by default.
- Only one factor reads them: the unit-price factor (`co_price_basis`), in its `co_unit_price` step.
- So the calculation document would have to list the supplement the proposal names and the carrier's approved amount, which only one factor uses. Your rules forbid that.
- **Suggested fix:** assign those four steps to `co_price_basis`. They already duplicate that factor's own `up_kind`, `up_supplement` and `up_approved`.

**Lesser points (not blocking).** In these the rule and the calculation agree, so I would render them as written:
- **Supplement set-aside picks the latest request (overdue charge and past-due payment policies).** When no approval is unpaid but there are more supplement requests than approvals, the amount set aside is the latest request's. If supplements are approved out of order, that is the wrong request.
- **Same-day requests.** The latest-request lookups for supplements and depreciation releases have no rule for two requests on the same date.
- **Deductive credit at the carrier's unit price.** The carrier's unit price, taken from the last insurance-scope change order, applies to the whole removed quantity, even when that is more than the change order added.

I found no defect in the frozen base text.
