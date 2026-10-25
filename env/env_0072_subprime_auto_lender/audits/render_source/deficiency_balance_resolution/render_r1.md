# render_r1 -- deficiency (env_0072), erl-kb-doc-render round 1

Gate: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (read OK).
Source: tasks/deficiency_balance_resolution/deficiency.extended.yaml (sha256 1965b769...) + task_tools.py (sha256 da468bc4...).
Outcome: **STOP -- source defect; nothing published.** docs/deficiency/ was not written.

## RED-1 (blocking) -- unstated tie in the hardship-document recording sentence (XF G30 / C11: undefined edge, unstated tie)

Location: `extended_policies[id=deficiency_ext_lump_sum_settlement].rule`, second sentence (yaml line 1265):

> "A lump-sum offer whose amount carries a hardship reduction records as its hardship document the document that reduction rests on, the ssa_award_letter or medical_disability_statement where an offer within the hardship look-back carries one of those, and otherwise the unemployment_determination; an offer without a hardship reduction records none."

This sentence decides the `hardship_document` argument of `record_lump_sum_settlement_offer_7c3d7537` (enum ssa_award_letter / unemployment_determination / medical_disability_statement / none). When the account's offers inside the hardship look-back carry **both** an ssa_award_letter and a medical_disability_statement, the reduction rests on both (`ls_lasting_docs` = COUNT(ssa) + COUNT(medical) > 0), and the sentence names "the document" in the singular without saying which one is recorded. The KB would then have two equally natural values for a write argument. A renderer cannot settle it without adding policy.
Fix (source side, one clause): give the tie an order, for example "the ssa_award_letter where an offer within the hardship look-back carries one, otherwise the medical_disability_statement where one carries that, and otherwise the unemployment_determination" (or "the document on the latest such offer"). Then re-check that each task's seeded world and GT agree with the chosen order, and sweep any proof text that quotes the old sentence (XF F29).
Placement note (no fix needed): the renderer homes this sentence in the lump-sum hardship-reduction factor document, not in the hub/tool document, because it names that factor's quantity. The hub describes `hardship_document` only as "the hardship document the offer rests on" (docstring).

## Observation (low, optional; route only if you are reworking the charter anyway) -- empty last_payment_date in the idle-days definition

Location: `extended_policies[id=deficiency_ext_installment_settlement].rule`, "Installment idle-account surcharge" (yaml line 1492):

> "the premium idle days are the calendar days from the later of opened_date and last_payment_date to today;"

Compute: `DAYS(MX(F('opened_date'), F('last_payment_date') or F('opened_date')), NOW)`. When the account has no unreturned payment, last_payment_date is empty and the compute counts from opened_date. The rule's natural reading gives the same answer, so this is not blocking. A short clause such as "(from opened_date when the account has no such payment)" would close the absent-record edge (XF C11).

## Scan otherwise clean

- compute_basis: every quote is verbatim in its rule. Each baseline.rule sentence is in its rule, policy_source is in its rule, superseded_clause is in its base rule, and replaced_by is in the owning rule.
- No factor reads another factor's binding. Plain bindings read factors only at assembly (dp_pct/result, pi_adjust_pct/pi_adjusted, ls_pct/result, si_extra_pts/si_figure, ss_count). Assembly sentences are generic and fix the order where adjustments do not commute.
- No factor id is a substring of a tool name.
- Rule == compute was checked at the edges: within_months is 0 <= MONTHS < N, which matches "fewer than N whole months before today". MONTHS matches the whole-month wording, MAX empty = 0.00 matches both nil branches, and the LATEST ties are stated.
- Overwrites are scoped, and retained tails are still in force.
- Docstrings carry no example values and claim no effect the bodies lack.

## Staging

Draft scratch for 28 of the 50 planned documents is kept in /tmp/render_deficiency_0072/ (b1-b4.py and build.py), so a round 2 can reuse it. The staging subfolder .doc_render_staging/deficiency/ was removed, and the shared parent was left in place.
