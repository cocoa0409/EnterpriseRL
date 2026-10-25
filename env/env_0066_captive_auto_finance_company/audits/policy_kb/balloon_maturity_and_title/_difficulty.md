# KB-doc policy audit — balloon_maturity_and_title (product balloon) — difficulty summary

## revision_1 (round 1)

### Entry conditions (Step 0)
- Policy-side verdict (tail line only): `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot from the brief: `[check_docs balloon] DOCS OK`; `[check_traceability balloon_maturity_and_title] TRACEABILITY OK`. Re-run once on the final (unchanged) form at close-out: `check_docs.py env/env_0066_captive_auto_finance_company balloon` -> `[PASS] mechanical gates ... DOCS OK`; `check_traceability.py .../tasks/balloon_maturity_and_title` -> `TRACEABILITY OK`.
- Runtime view hashes verified: 0.runtime.json 96da1665ea211859..., 1.runtime.json 49304fef88bce430... (match brief). DB access path: db_query.py (tool-shaped share reads + KB_search); blind phase not DB-contaminated. Task-tool schemas taken from the runtime registry's openai_schema only.
- Blind phase frozen before reveal: runtime_context/balloon_maturity_and_title/_blind_freeze.sha256 (0.md a64ed6a1..., 1.md 12cb872a..., 2026-10-16T04:48:17Z). No contamination.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Verdict |
|---|---|---|---|---|
| 0 (return balance payment; tree: mileage, wear, return fee billed) | PASS — blind 623.20 / 179.66 / 205.00 / 355.25 = GT | PASS | PASS | **PASS** |
| 1 (balloon refinance; tree: payoff quote -> held payment -> refinance) | PASS — blind 2026-10-22 / 5.32 / 27235.19; 3667.19; 23568.00 / 36 / 8.34 / 742.24 = GT | PASS | PASS | **PASS** |

All hops in both trees were state-derived from the verbatim prerequisite sentences, the depended-on docs' own state sentences and the records; no hop pre-solved. Fall-back numbers are definite and differ (task 0: 450.00 / 1306.75 / 1136.40 / standing+charges; task 1: 27320.13 good through 2026-11-01; 1120.13; 7.99% / 48 months). Every factor doc was reached from record words (lease/retail/pre-owned status and dates, posting-row event types, contract dates), none only through computation-doc wording.

### KB defects
None (kb=CLEAN).

### SOURCE-side items (routed to source; the KB carries each faithfully)
- **SRC-1 (rule-vs-compute, base text; renderer note 1).** balloon_payoff_and_refunds rule: "The per diem is the principal_balance times apr divided by per_diem_day_basis, rounded to the cent" while its formula is `per_diem: round(principal_balance * apr / 100 / per_diem_day_basis, 2)`; balloon_ext_payoff_quote's overwrite replaced_by repeats the base wording for out-of-scope quotes ("every other payoff quote ... keeps the base per diem and payoff amount, by which the per diem is the principal_balance times apr divided by per_diem_day_basis"). Rendered verbatim in payoff_quote_and_refund_rule cl.3 ("the principal balance times the APR divided by the tier's day basis"), so a reader quoting a non-customer payoff quote with apr in percent gets a per diem 100x too large. No effect on task 0/1 (customer quotes use the extended rule's "/100" wording, rendered in payoff_amount_calculation).
- **SRC-2 (rule wording vs compute; renderer note 2).** balloon_ext_return_balance_plan prior-fee share: "where one was assessed or posted in those months but none in the plan_recent_window_months ..." (ladder "one in those months AND none in ...") while compute counts at least one (`prior_share: ... else (K('prior_fee_share_recovering') if (prior_late_recent == 0 and prior_returned_recent == 0) else 1)` after a zero test). Read as "exactly one", two charges in 12 months with none in 6 would fall to "otherwise all" instead of 0.5. KB doc return_balance_prior_fee_collection resolves it with the table row "One or more | None | 0.5", consistent with compute. Same existential "one" in rp_upfront_amount ("but one posted in the plan_long_window_months") and cp_returned_payments ("but one posted in the cp_long_window_months"), where both readings coincide. No task impact (task 0 has exactly one late charge in 12 months).
- **SRC-3 (XF class 1/4, assembly names a factor quantity).** balloon_ext_payoff_quote plain binding post_per_diem: "a post-maturity per diem is principal_balance times that rate divided by 100 divided by per_diem_day_basis, rounded to the cent" — "that rate" is the qt_post_maturity_rate factor's output; and the pre-maturity split ("the quote interest days up to and including maturity_date always accrue at the per diem") sits inside that factor's compute_basis quote though it is the plain binding pre_maturity_days. Carrying the assembly forces payoff_amount_calculation (the baseline doc) to say "a daily rate for days after the maturity date being the principal balance times the rate for those days ...", which tells a reader of the computation document that a separate post-maturity rate exists. KB faithful; numbers unaffected.
- **SRC-4 (realism / persona timing, XF 12).** tasks/0.json user_scenario: "Three and a half years ago you financed a Kestrel Corvalis on a Kestrel Advantage balloon contract" vs contract_date 2023-09-11 and frozen_time 2026-10-14 (3 years 1 month; the term is 36 months). Backstory only; records stay authoritative; no effect on the solution.

### Policy-side notes (no routing needed; not KB verdicts)
- PN-1: the pre-refinance payment rule defines its subject by its order ("This rule sets the payment a customer makes before a Kestrel Advantage balloon refinance is booked"); rendered in pre_refinance_payment's opening. The depended-on side therefore names the order, by the source's own wording.
- PN-2: the refinance rule's in-force remainder "every other amount due is still paid separately before the refinance" (carried in balloon_refinance_installment_calculation) restates the same order in action words beside the state-form prerequisite sentence.
- Observation: complete_balloon_refinance_14b47e8c leaves the held payment row's interest/principal/fees_applied at 0.00 after booking, though the rule says the held payment "is applied when the refinance is booked, accrued interest first, then fees due, then principal"; balances (interest paid to today, fees cleared, principal = amount refinanced) embody the application, so this is a record-detail only.

### Renderer notes (audits/render_source/balloon_maturity_and_title/render_r1.md)
1. Base payoff text vs formula -> SOURCE-side (SRC-1). KB carried the base text verbatim, as required; not a KB defect.
2. Ambiguous "one" in the prior-fee share -> SOURCE-side (SRC-2). KB table follows compute; the existential reading is the natural one, so not a KB closure of an open source boundary.

### XF_recipe.md points, judged against the published docs and the source
1 Assembly sentences: generic in all seven rules and carried in the computation docs; one instance names a factor quantity -> SRC-3. 2 Non-commuting order: stated for wear (replacement -> proration -> credits -> share), return fee (basis -> reductions), return balance payment, down payment (points -> figure -> credits), refinance APR (together, 2 dp, then installment), mileage (forgiveness -> floor -> rate), payoff (courtesy days off post-maturity days -> daily rates); docs carry each — CLEAN. 3 Factor independence: no factor doc reads another's output (proration is a ratio applied by the assembly) — CLEAN. 4 Ownership: CLEAN apart from SRC-3. 5 compute_basis quotes: scripted check, every quote verbatim in its rule — CLEAN. 6 Ties: inspections, elections, late charges, first quote of the day all stated and rendered — CLEAN. 7 Counting conventions: stated per rule, rendered in each factor doc with boundary examples — CLEAN. 8 Branches both ways: scope-out cases rendered as "outside this rule and its tool" — CLEAN. 9 Base clauses: every superseded_clause verbatim in its base rule (scripted), every retired surface rendered scoped and in force for the rest — CLEAN; base-text slip -> SRC-1. 10 Rounding: matches (per diem, post-maturity per diem, prorated forgiveness, final roundings) — CLEAN. 11 Tools: docstrings carry formats only, no example values, no ordering words; bodies match docstrings — CLEAN. 12 Proof text: evaluation figures recompute to my blind values; persona timing slip -> SRC-4.

### Cross-product
Published now: docs/retail, fleet, care, floorplan, balloon (no docs/lease or docs/preowned on disk). Factors read lease and pre-owned **records** (status, lease_date, contract_date, days_past_due, disposition_fee) through share tools; no figure in either task depends on an unpublished product's docs — conditional list: none. Product names used in factor docs match the blueprint display names. Cross-product contradictions remain outside this skill's range.

### Close-out checklist
- Audit files one per task in runtime_context/ and policy_kb/, blind sections frozen and hashed, comparisons appended — yes.
- Every normative atom of the four + three extended policies (and their retired base clauses) entailed; every prerequisite sentence verbatim on its blocked side only; every factor ladder complete and findable — yes.
- Gates re-run on the final form — DOCS OK / TRACEABILITY OK.

KBVERDICT round 1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3,SRC-4

## revision_2 (re-audit round 2, 2026-10-16)

Revision_1 above left untouched (its KBVERDICT line now sits above this section).

### Gating and gates
- `tail -1 /tmp/render_balloon_0066/RENDER.log` gives `RENDER round 2: DOCS OK`. `tail -1 audits/policy_task/balloon_maturity_and_title/_difficulty.md` gives `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
- Re-run by me on the round-2 form: `check_docs.py env/env_0066_captive_auto_finance_company balloon` gives `DOCS OK`; `check_traceability.py env/env_0066_captive_auto_finance_company/tasks/balloon_maturity_and_title` gives `TRACEABILITY OK`.

### Round-1 items: closure
Round 1 had no KB RED (kb=CLEAN), so this round checks the four SOURCE items.

| Id | Source | Docs | Status |
|---|---|---|---|
| SRC-1 base per-diem text vs formula | The payoff overwrite[1].replaced_by and its rule copy now say that out-of-scope quotes keep the per diem "as the base formula computes them, by which the per diem is principal_balance times apr divided by 100 divided by per_diem_day_basis". The base clause text is frozen by design. | payoff_quote_and_refund_rule cl.3 italic note and the customer_payoff_quote Scope both state the "/100" formula for every other quote, so the base sentence is adjudicated in place. | **closed** |
| SRC-2 ambiguous "one" | "one or more" now appears in the rule, the ladder labels and the basis for rp_prior_fee_share, rp_upfront_amount and cp_returned_payments. A sweep found no bare "one" left (the remaining "one" uses are "exactly one", "at most one" or "one or two", each matching its compute). | return_balance_prior_fee_collection, return_balance_upfront_amount and refinance_down_payment_returned_payments all read "one or more". | **closed** |
| SRC-3 assembly named a factor quantity | A plain sentence now defines the days after maturity. qt_post_maturity_rate decides post_per_diem with the full daily-rate ladder (baseline: the per diem). The pre_maturity_days basis now points at the plain sentence. | payoff_amount_calculation carries only the plain split sentence and the generic assembly sentence; "rate for those days" no longer appears anywhere in the corpus. post_maturity_interest_rate_on_payoff_quotes carries the whole ladder, including the rounding. | **closed** |
| SRC-4 persona timing | tasks/0.json now reads "A little over three years ago, in September 2023, you financed ...", which matches contract_date 2023-09-11. | n/a | **closed** in source |

Coordinator-side note: `.audit_views/runtime/balloon_maturity_and_title/0.runtime.json` (sha 96da1665ea211859...) still has the old backstory sentence and was not regenerated after SRC-4. Only that sentence differs, and it does not affect the derivation.

### Regression and new-defect checks
- Source hygiene sweep on the reworked yaml:
  - every superseded_clause is verbatim in its base rule;
  - every replaced_by is verbatim in its rule;
  - every compute_basis quote is verbatim in its rule;
  - every policy_source is verbatim in its blocked rule.
  The sweep found 0 misses.
- Two-way scan of every changed atom is in policy_kb/0.md and 1.md revision_2: all equivalent. A scripted phrase sweep over all 83 balloon docs (ladder figures, thresholds, windows, assembly sentences, retired-clause notes, prerequisite sentences, tool sections) found nothing missing.
- Each tool name appears only in its own doc. Each prerequisite sentence appears verbatim only on its blocked side. No scored figure appears in any of the 303 published docs.
- Scored solution re-derived through db_query.py on unchanged records: task 0 is 623.20 / 179.66 / 205.00 / 355.25; task 1 is 2026-10-22 / 5.32 / 27235.19, then 3667.19, then 23568.00 / 36 / 8.34 / 742.24. Both are unique and equal GT. Fall-backs are still definite and different.
- Cross-product: docs/lease is now published. Every balloon factor still reads lease and pre-owned records, not their docs, so no figure is conditional. Cross-product contradictions remain outside this skill's range.
- PN-1 and PN-2 (source wording) and the held-payment record-detail observation are unchanged; no routing needed.

### Per-task verdicts (round 2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | **PASS** |

Close-out: all three parts pass for both tasks, the gates were re-run on the final form, and the audit files are one per task with revisions preserved.

KBVERDICT round 2: task0=PASS task1=PASS kb=CLEAN src=NONE


## re-judge (all products final), 2026-10-16

- Gates: `check_docs.py ... balloon` gives `DOCS OK`; `check_traceability.py .../balloon_maturity_and_title` gives `TRACEABILITY OK`.
- Corpus: 373 docs, all seven products published.
- Runtime view 0.runtime.json was regenerated after SRC-4 (sha 2e7e4c1b...) and now matches tasks/0.json. 1.runtime.json is unchanged and matches.
- (1) Cross-product reads are consistent with the published lease, retail and pre-owned docs: same field and status vocabulary; the lease disposition fee is a booked figure, $395. No other product's doc governs a balloon answer.
- (2) Seeded rows are producible:
  - task 0 lease: arithmetic, tier fees and exposure cap check out;
  - task 0 closed retail and task 1 closed pre-owned: closed 3 business days after paid in full, consistent with the electronic lien release;
  - task 1 active retail: payment count and exposure cap check out.
- (3) Rollout searches surface other products' docs only within their own product scope; there is no competing reading of any scored value.
- No new KB or source item.

KBVERDICT rejudge: task0=PASS task1=PASS kb=CLEAN src=NONE
