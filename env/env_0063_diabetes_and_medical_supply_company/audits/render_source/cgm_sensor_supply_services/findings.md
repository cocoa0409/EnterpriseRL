# Render-source findings — product cgm (difficulty cgm_sensor_supply_services), render round 1

Saved verbatim by the coordinator from the renderer's final report (agent a4f43e9f424d1095d, 2026-10-15); the harness blocked the renderer from writing this file. Rendered as the source stands; locations are in the cgm extended yaml unless stated.

*A. An overwrite that retires more than it replaces*
1. `cgm_ext_medicare_advance_notice_units.overwrite[1]` retires "the customer signs it personally, and no Larkfield representative can sign it for them." from `cgm_liability_notice` for every notice. Its replacement ("For a notice this policy counts, the customer signs it personally through their own signing step … no Larkfield representative can sign it for them.") has no "every other notice remains under the base rule" tail. So for plan member waivers and Medicaid agreements nothing remains in force. `overwrite[0]` of the same policy does have the tail.

*B. A factor reading another factor*

2. `cgm_ext_plan_member_waiver_units` `frequency_edit_rule`: all three tiers read `paid_end_offset = DAYS(NOW, latest_refill_ship) + paid_supply_days - early_refill_days`. `early_refill_days` is the output of the `early_refill_allowance` factor. The rule says "begins before the paid supply, less the early-refill allowance, ends".

3. `cgm_ext_model_change_refill_units` `refill_frequency_rule`: the same pattern, reading `refill_early_allowance`. Its tiers 2 and 3 say only "when that paid supply runs past today".

*C. A rule sentence that disagrees with its compute*

4. Model change grant, `rule`/`compute_basis.result`: "…times the counted blocks, less the deducted blocks and the blocks the follow-up visit requirement removes…" reads as subtracting blocks from units. The compute is `units_per_block * (span_blocks - overlap_blocks - lapse_cut_blocks)`, which nets the blocks first.

5. Model change grant, `superseded_supply_overlap.ladder[0]`: "…documents that the pump requires the new model". The compute checks only `justification_date >= pump_delivery_date`.

6. Model change grant, `approval_period_count.ladder[1]`: "fewer units than the whole blocks of its span". The compute compares against those blocks multiplied by the allowance.

7. Medicare advance notice, `compute_basis.newer_grant_covers`: "a newer grant … the delivery draws on the newest grant". The compute tests only `LATEST(..., date_field='valid_through')`. The rule never says "newest" is ordered by valid-through date, and other newer grants do not count.

8. Medicare advance notice, `compute_basis.notice_credit`: "…on or after the date the customer's insulin pharmacy program closed when the customer has stopped insulin…". The compute gives no credit at all to a customer who has not stopped insulin (closed date set to `'9999-12-31'`). The sentence can also be read as applying the date test only to stopped customers.

9. Waiver: "when the payer paid part of the latest refill's claim". The compute tests a paid sum greater than 0, which also catches full payment.

10. Waiver and refill: "past_due_hold_days divided by 30 whole calendar months". The compute floors it (`// 30`), which the rule never says.

11. Waiver: the rule says "its payments", but `plan_covered` sums every patient payment on the program.

12. Waiver and refill timing: "…before its proof-of-delivery date plus its supply days". The compute falls back to the ship date when no proof of delivery is recorded (`... or latest_refill_ship`); the rule does not say so.

13. Refill, `waiver_coverage_rule.ladder[0]` and `[1]` say "at-risk units". The rule and the compute use exposed units (`risk_units + excess_units`).

14. Payment plan: "rounded to the nearest cent". The compute uses `RND`, which is Python `round()` (`check_compute.py`: `"RND": lambda x, n=2: round(float(x), n)`), so a half cent rounds to the even cent. The rule never says how a half cent rounds.

15. Payment plan: "…and so do the recent remittances and charges of the pump balance taken in". `pump_waiting` subtracts the pump program's recent remittances even in the other-coverage branch, where only patient charges were taken in.

16. Waiver: `pa_left` has an `MX(0, …)` floor the rule does not state. It changes nothing, because the listed units are capped at the delivery.

*D. Undefined branches*

17. Medicare advance notice, rule and baseline rule: "A supply whose CGM program documents a qualifying regimen is expected to be paid by Medicare…". No binding reads the regimen, so a non-qualifying regimen is undefined.

18. Medicare advance notice, `risk_scope`: a customer who stopped insulin but has no insulin refill gets offset `-9999` (every unit at risk). The rule does not cover this.

19. Renewal: with no refill on file, the compute uses `latest_refill_ship … or order_date` and `latest_refill_days … or 0`, which gives a nonzero bridge. The rule does not cover this.

20. Renewal, `coverage_review_horizon`: with no insulin refill, the offset is 0 and the first rung applies. The rule does not cover this.

21. Renewal, `review_visit_practitioner`: with no visit of either purpose, the visit date becomes `'0000-00-00'` and the units become 0 when a horizon applies. The rule does not cover this.

22. Renewal: whole months are defined only "from one date to a later date", but the review start date can fall after the anchor date.

23. Model change grant: with no qualifying visit record, `last_visit_date` becomes `'0000-00-00'`, `lapse_cut_blocks` becomes 999 and the result is 0. The rule does not cover this.

*E. Minor*

24. `baseline.params` lists `sensor_allowance_units_per_30_days` for renewal and model change, but neither `baseline.rule` reads it.

25. Waiver `prerequisite[1]` and refill `prerequisite[2]`, conditions: `plan_covered` covers only aged remittance patient responsibility. An approved plan alone clears the gate only when aged charges and refunds are below the hold minimum. This needed no render change.

Renderer's other notes: gate quirk — `check_docs.py` treats each base policy's `params.per_tier` as a required key, so 12 base docs list `<policy_id>.params.per_tier` in their carries; the waiver and refill frequency docs render an "otherwise" tier matching the computation doc differently (waiver states the tier in full; refill says "no such marking applies"), same meaning.
