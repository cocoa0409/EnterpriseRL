# Render pre-scan findings — product dental (difficulty dental_ppo_member_services), render round 1
Source: renderer agent a9b3e9d2e959dbe32, 2026-10-19; saved verbatim by the coordinator. The renderer STOPPED before writing any document.
Gate line read: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.

The scan covered all six extended policies in `env/env_0070_dental_and_vision_benefits_carrier/tasks/dental_ppo_member_services/dental.extended.yaml`: rule against compute, overwrites, prerequisites and the XF_recipe classes.

**What checked clean**
- Mechanically, no factor binding reads another factor's binding in any of the six policies.
- Every compute_basis quote, superseded_clause, replaced_by and prerequisite sentence matches its source verbatim (whitespace-normalised).
- All four prerequisites are in state form.
- I did not treat the "The adjustments below are applied to the standard amount in this order: …" sentences as defects. They follow the recipe's template and can be rendered without naming factor quantities.

**Finding 1 (RED, XF #2/#16), `dental_ext_upgrade_paid_reprocess`: the baseline defines a quantity only one factor uses, and that factor's own sentence leaves it out**
- `baseline.rule` (also the compute_basis of the plain binding `oop_used`): "The pediatric out-of-pocket postings a reprocessed prior-level line counts are those net of reversals for the line's benefit year, after any posting the replaced decision made to that benefit year is backed out."
- `oop_used` is read only by `share_cap`, which belongs to factor `priorlevel_share_adjustment`. The standard calculation never uses it.
- That factor's own rule sentence (compute_basis `share_cap`) defines the room without the back-out: "…first limited to the pediatric out-of-pocket room (the pediatric out-of-pocket maximum for one child less the person's pediatric out-of-pocket postings net of reversals for the benefit year)…". Its ladder likewise says "less the person's net pediatric out-of-pocket postings".
- The compute does back the posting out: `oop_used: … - SUM(…'dental_ped_oop_posting', benefit_year=t_year, dental_claim_line_id=tline)`.
- Consequence:
  - Rendered from its own sentence, the factor document gives a number different from compute whenever the replaced decision made a pediatric out-of-pocket posting.
  - Rendering the baseline sentence in the computation document makes it describe a quantity its own calculation never uses, which reveals that the factor exists.
- Suggested fix: move the back-out wording into the `priorlevel_share_adjustment` sentence and ladder, make `oop_used` a binding of that factor, and drop the sentence from `baseline.rule`.

**Finding 2 (RED, XF #6 unstated same-day tie), `dental_ext_claim_appeal_dispute`**
- Rule (compute_basis `ap_line`/`tline`): "the first-level filing is the one decided by the enrollment's most recently decided first-level appeal decision with outcome upheld, and the decision under appeal is the latest decision on that line's claim number and line number, a reprocessed decision of it included."
- The rule says nothing about ties in either case:
  - two upheld first-level decisions on the same decided date;
  - two decisions on the same claim number and line number with the same decision date.
- The other five policies all carry "where several such lines share that latest decision date this rule is not used"; this policy has no such sentence.

**Lower-severity notes for the coordinator to judge**
- **Factor-only quantity kept as a plain binding (XF #2, binding level only):** `oop_used` is a plain binding read only by one factor in `dental_ext_initial_wait_reprocess`, `dental_ext_estimate_request`, `dental_ext_grace_denial_reprocess` and `dental_ext_upgrade_denial_reprocess`. The prose is fine there, because the definition sits in the factor sentence, not the baseline. But the meta `covers` would place it in the computation document while its prose lives in the factor document.
- **Possible undeclared departure from a base rule (XF #8):** `dental_ext_claim_appeal_dispute` takes the requested-payment deductible as "the plan's individual deductible less the person's deductible postings…". It has none of its siblings' family-deductible sentence ("on an account with no more than three enrolled persons…"), and it does not exclude accounts with more than three enrolled persons. Base `dental_agg_family_deductible` also caps the deductible by the family's remaining amount.
- **Minor unstated ties in `dental_ext_estimate_request`:** "the service class is the one recorded on the person's most recent claim-line decision for the same benefit category" and "the extraction date is the one recorded on the person's most recently decided claim line for that tooth" have no tie sentence. Ties there are unlikely to matter.

The six policies, dental_ext_initial_wait_reprocess, dental_ext_estimate_request, dental_ext_upgrade_paid_reprocess, dental_ext_grace_denial_reprocess, dental_ext_upgrade_denial_reprocess and dental_ext_claim_appeal_dispute, have no defects beyond the items above.
