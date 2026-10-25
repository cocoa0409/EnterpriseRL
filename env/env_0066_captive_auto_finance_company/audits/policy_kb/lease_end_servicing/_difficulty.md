# KB-doc policy audit — lease_end_servicing (product lease), round 1

## Entry conditions (Step 0, from the coordinator brief)
- Policy side: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (only that tail line read from audits/policy_task/).
- Gates: `[check_docs lease] DOCS OK`; `[check_traceability lease_end_servicing] TRACEABILITY OK` (post-publication). Not re-run: the corpus is byte-identical at start and end of this audit (`cat docs/lease/*.json | sha256sum` = `d349746c5433dd4e9db50de0edb6c0056b59da8ada95a25ddd8b0636baea00f2` both times), so the brief's snapshot stands for the final form.
- Runtime view hashes verified: 0.runtime.json `6618c86f5d9d6c13…`, 1.runtime.json `db99295c443cf9c4…`. DB read only through `db_query.py` (blind side clean on the DB).
- Ordering: blind answers frozen 2026-10-16T09:17:10Z (hash lines in `runtime_context/lease_end_servicing/{0,1}.md`) before any source-layer read. No contamination.

## Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Blind = GT |
|---|---|---|---|---|
| 0 (hold payment ← wear forgiveness waiver) | PASS | PASS | PASS | 900.00 / 2093318476; 717.83 — exact |
| 1 (plan opening installment ← excess mileage billed) | PASS | PASS | PASS | 1468.09 / 6383; 826.82 — exact |

## Cross-product
Published now: retail, fleet, care, floorplan, balloon, lease (no docs/preowned). Every lease factor that reads another product's records (retail, balloon, pre-owned, Care) carries its whole ladder inside docs/lease and names that product by its official name, so no scored figure depends on another product's docs. Conditional figures: **none**. Not in scope for this skill: contradictions between lease docs and docs/preowned once it is published.

## Renderer notes (`audits/render_source/lease_end_servicing/render_r1.md`) — current state
| # | Note | Current source | Current KB | Class |
|---|---|---|---|---|
| 1 | qualifying-account tie retail vs balloon | rule: "an active Kestrel new-vehicle retail contract taking precedence over an active Kestrel balloon contract when both meet them" | `return_to_brand_wear_cap` "an active new-vehicle retail contract taking precedence…" + table row 4 | closed; neither |
| 2 | rule vs docstring at the halfway cap | rule "the contract that meets that cap's conditions"; docstring "the qualifying account number the wear forgiveness rule names … or an empty string when the rule names none" | same wording; halfway table row gives the retail contract's number | closed |
| 3 | retirement swallowed the loyalty condition of the disposition waiver | overwrite[1] narrowed to "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" | §6 keeps "where the tier's loyalty disposition waiver applies, the disposition fee is waived…" under "When the loyalty condition is met" | closed |
| 4 | replaced_by deferring to retired clauses | all three replaced_by now restate the in-force remainder (no "as the base rule states") | hold hub, plan hub, mileage hub restate them | closed |
| placement | balance bindings inside shape factors | `end_balance` / `plan_balance` are plain bindings; shape factors bind `shape_balance` / `shape_plan_balance` | balances defined in computation docs | closed |

## XF recipe (`audits/render_source/XF_recipe.md`) — checked on the published docs and source
1 assembly: generic sentences only (KB distributes them per factor without naming another factor) — OK. 2 order: "replace, then add/subtract, fee last" stated — OK. 3 factor independence: no factor reads another's output — OK. 4 ownership: OK. 5 compute_basis quotes: script-checked for all 4 extended policies (whitespace-normalised substring of rule), all verbatim — OK. 6 ties: final-report tie, latest invoice, first-listed contract all stated in KB — OK. 7 counting: whole-month rule and by-day count match MONTHS()/DAYS() (checked against `check_compute.py`) — OK. 8 branches: zero-miles, zero-forgiveness, no-report, out-of-scope stated — OK. 9 base clauses: all retired surfaces written as retired; see SRC-2 for a stale parameter gloss. 10 rounding: floor/half-up placements match — OK. 11 tools: no example values, no ordering words — OK. 12 proof text: computations recompute (all expected values reproduced blind) — OK.

## SOURCE-side items (routed to the source; the KB renders them faithfully)
- **SRC-1 (rule-vs-compute, low; no current-task effect)** — `lease_ext_charge_off_hold.rule` and `baseline.rule`: "The invoiced end-of-term balance is the end-of-term charges billed on the day the end-of-term invoice was mailed, less every waiver, security deposit application and end-of-term payment posted on the lease". Compute subtracts only `SUM(... event_type='lease_end_charge_waiver')`. Read literally, "every waiver … posted on the lease" also covers term-fee waivers (`lease_fee_waiver`, e.g. a courtesy late-charge waiver), which compute ignores. Rendered verbatim in `hold_payment_amount_04ee0423` and `hold_payment_structure_9d89d0ec`. Task 0 has no term-fee waiver, so 717.83 is unaffected. Compare the plan rule, which is scoped ("a waiver posted on any of those charges").
- **SRC-2 (overwrite hygiene / parameter gloss, low; no current-task effect)** — `parameter_schema` (same text in blueprint/products/lease.yaml): "loyalty_wear_forgiveness_cap: excess wear forgiven at lease end when the loyalty condition is met" and "wear_forgiveness_cap: excess wear forgiven at lease end without loyalty". These glosses restate the base clause that overwrite[1] of `lease_ext_wear_forgiveness` retired ("loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap"). The current rule applies the loyalty cap only for an active NV retail/balloon contract in the window with dpd 0: a new lease never qualifies, and the halfway cap exists. Rendered as "What the figures mean" in `lease_end_allowances_and_settlement_terms_9f772d2f`. The KB still explicitly retires the replacement (`end_of_term_charges…` §6) and states the current ladder (`return_to_brand_wear_cap`), so a careful reader resolves it. For task 0 both readings give $500.

## Observations (no verdict effect)
- OBS-1: the qualifying-account rule (hub-level in the source) is carried in the brand-return cap factor doc. The hub refers to it as "the qualifying account number the wear forgiveness rule names for it, or none". This is entailed and findable from the same records as the cap tier.
- OBS-2: base pull-ahead sentence "mileage is prorated as for an early termination" sits beside the retired proration clause. Under the current basis both run by the whole month, so the two are consistent.
- OBS-3: the per-item compute is `MN(wear_charge, 100 × count)` and the rule caps "each excess item … up to $100". These differ only for an item charged under $100. The schedule minimum is $120, so no such item can occur.
- OBS-4: `first_installment_structure` hypothetical "$900.00" (= 2 × $450) coincides numerically with task 0's forgiveness. It sits in another policy's doc, is derived from its own hypothetical inputs, and is not a leak.

## Closing checklist
- Audit files 1:1 with tasks (runtime_context 0/1, policy_kb 0/1); revision_1 only; every comparison section carries PASS.
- Every normative atom of the four extended policies and their base refs entailed; both prerequisite sentences verbatim, state form, on the blocked side only; every factor ladder complete and findable from record words; no tool name, route or chain beyond the sentences.

KBVERDICT round 1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2

## revision_2 (re-audit round 2)

### Gating and gates (run by this auditor)
- `tail -1 /tmp/render_lease_0066/RENDER.log` → `RENDER round 3: DOCS OK`; policy tail → `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- `check_docs.py env/env_0066_captive_auto_finance_company lease` → last line `DOCS OK` (mechanical gates PASS; manual bijection is this audit).
- `check_traceability.py …/tasks/lease_end_servicing` → last line `TRACEABILITY OK`.
- Corpus sha256 is now `3e68e03f4543ffb9…` (round 1: `d349746c…`). Three docs have changed content: `hold_payment_amount_04ee0423`, `hold_payment_structure_9d89d0ec`, `return_to_brand_wear_cap_8e4dc37f`. The other 48 have identical content length to round 1. `task_tools.py` is unchanged (mtime before round 1). Runtime view hashes are unchanged.

### Round-1 items
- **SRC-1 — CLOSED.** The source rule and baseline now say: "less every end-of-term charge waiver, security deposit application and end-of-term payment posted on the lease, a waiver of a term fee such as a late charge not being taken off". This matches compute `event_type='lease_end_charge_waiver'`. Both hold docs carry it, plus a hypothetical courtesy-late-charge row. Task 0 has no term-fee waiver, so the result is still 717.83.
- **SRC-2 — BLUEPRINT-KNOWN (coordinator); still moves no scored value.** The parameter glosses are unchanged in `lease_end_allowances…`. The source rule now adds "meeting the loyalty condition alone does not put the loyalty cap in place", rendered in `return_to_brand_wear_cap`, so the current ladder explicitly governs over the gloss. Task 0: the loyalty condition reading and the brand-return loyalty tier both give $500, so the forgiveness stays 900.00. Task 1 has no excess wear.
- KB defects from round 1: none existed; none found now.

### Regression scan
- Both scored solutions re-derived through db_query.py with identical worlds: 900.00 / 2093318476 → 717.83 (task 0); 1468.09 / 6383 → 826.82 (task 1). GT is unchanged.
- Prerequisite sentences are still verbatim on their blocked hubs only. Each task tool is still named only in its own hub. compute_basis quotes are all verbatim (script). The leak scan for scored values in docs and task_tools is clean.
- No new route, chain, tier attribution or computation-doc hint. OBS-5: the new cap sentence is source rule text that scopes its own factor ladder, not a renderer-added mistake contrast.
- Cross-product: still no figure conditional on an unpublished product (docs/preowned not yet published; the lease factors carry their own ladders).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KBVERDICT round 2: task0=PASS task1=PASS kb=CLEAN src=NONE

## re-judge (all products final)

### Gates (re-run by this auditor)
- `check_docs.py env/env_0066_captive_auto_finance_company lease` → `DOCS OK`; `check_traceability.py …/tasks/lease_end_servicing` → `TRACEABILITY OK`.
- The lease corpus is unchanged since round 2 (sha256 `3e68e03f4543ffb9…`). All seven product directories are published (386 doc files on disk, of which 70 are docs/preowned).

### (1) Cross-product reads vs. the now-published owning docs
| Lease figure / factor | Reads | Owning-product doc check | Consistent |
|---|---|---|---|
| brand-return wear cap, relationship hold relief (task 0) | active Kestrel New Vehicle Retail contract: status, contract_date, days_past_due | the retail rate sheet defines Tier 3 at 61–72 months / 10.74 %, which matches the seeded active contract; the status and days-past-due vocabulary is the same | yes |
| retail tenure addition (task 0) | paid-in-full NV retail payments_made_count | the seeded 60-month Tier 3 contract at 9.99 % (49–60 band) amortizes exactly to its 459.89 payment, with 60 payments | yes |
| return-to-brand miles, relationship installments (task 1) | active Kestrel Pre-Owned Retail contract: contract_date, days_past_due | the pre-owned rate sheet has Tier 2 at 49–60 months = 9.49 %, and 24180.00 is within $5000–$60000 | yes |
| Care mileage credit (task 1) | active Care plan financed_with_category | the Care sale card and eligibility rule allow Gold financed "in a Kestrel … pre-owned … contract", and the plan records the financing product | yes |
| balloon tenure installments (task 1) | paid-in-full balloon payments_made_count | the balloon rate sheet has Tier 2 at 37–48 months = 7.49 %; the 48-month balloon is 42 % × 26340 = 11062.80, matching the record | yes |
No published product doc states a different rule for these lease figures. The pre-owned, retail and Care docs that read the lease (post-sale rate, settlement percentage, lessee points, Care refund destination) govern those products' own amounts, not any lease scored value.

### (2) Seeded cross-category rows (via db_query.py)
- Task 0, retail `2093318476`: Tier 3, 72 months, APR 10.74 %, 31840.00 → payment 601.81 (amortization recomputed exactly). First due 2026-10-25, so dpd 0 at frozen time.
- Task 0, retail `2015649027`: paid in full, 60/60 payments, 459.89 recomputed.
- Task 0, balloon `2068402215`: Tier 3, 48 months at 9.24 %, balloon 41 % × 27650 = 11336.50, payment 411.62 recomputed; paid in full by pay_balloon.
- Task 1, pre-owned `2074419983`: Tier 2, 60 months at 9.49 %, 24180.00 → 507.71 recomputed. First due 2026-10-17, so dpd 0.
- Task 1, Care KC2049917 Gold: vehicle age 2026 − 2024 = 2 ≤ 8; odometer 21480 ≤ 100000; term 48 months / 60000 miles, both in Gold's lists; price 1895.00 within 1295–3195; deductible 100.00 is a Gold option; expiration odometer 21480 + 60000 = 81480; financed in the pre-owned contract on the same VIN.
- Task 1, balloon `2052287341`: Tier 2, 48 months at 7.49 %, balloon 42 % × 26340 = 11062.80, payment 356.66 recomputed; paid in full.
- All of these are states the owning products' published rules can produce.

### (3) KB_search / grep competition
- I re-ran the task-0 and task-1 probes with record and request words: hold/charge-off, wear forgiveness with a new retail contract, returned payment hold rate, relationship relief, advance inspection, paid-off retail, pre-owned mileage, plan installments, Care mileage, extension allowance.
- The lease doc for each factor still ranks first, or is reachable.
- Other products' hits (the retail "Lessee … points" cards, the balloon wear-forgiveness and return-to-brand docs, the pre-owned lease-relationship docs, the fleet mileage docs) are each titled with and confined to their own product's charge. None states a lease end-of-term amount, cap, credit or installment rule, so none offers a competing reading of 900.00, 717.83, 1468.09 / 6383 or 826.82.

### Result
No new KB defect or SRC item. SRC-2 (blueprint-known gloss) still moves no scored value.

KBVERDICT rejudge: task0=PASS task1=PASS kb=CLEAN src=NONE
