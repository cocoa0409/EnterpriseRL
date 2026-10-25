# KB-doc policy audit — protection_plan_claims_and_refunds (product plan) — closing checklist

## revision_1

Auditor kb_d3 (fresh; independent of the renderer and of the policy-side auditor). Run 2026-10-24.

### Entry conditions
- Policy side: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot (`/tmp/erl0080_coord/kb_snapshot.sh protection_plan_claims_and_refunds plan`, executed 2026-10-24T23:25:59Z and re-run 23:35:40Z on the final form): `DOCS OK`; `TRACEABILITY OK` (0.json 22/0, 1.json 14/0); EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; plan.extended.yaml 0cb9cbce…, task_tools.py c0870e92…; docs/plan 62 files, tree hash 133bf99970752a9a.
- Runtime view and DB access path (`.audit_views/runtime/db_query.py`, tool-shaped) supplied and used; blind audits are DB-blind. No contamination.

### Per-task part verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Blind = GT |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | 2322.48 / repair 327.78 / approved 46.75 / prorated_unused_days 216.07 — all equal |
| 1 | PASS | PASS | PASS | 295.54 / prorated_unused_days 74.87 — equal |

Files: `audits/runtime_context/protection_plan_claims_and_refunds/{0,1}.md`, `audits/policy_kb/protection_plan_claims_and_refunds/{0,1}.md`.

### Checklist
- All 6 extended policies of the difficulty (registration, repair authorization, Accident claim service fee, Accident refund, food-loss payment, Standard refund): baseline carried complete in its computation doc; every declared factor's ladder carried in full in its own doc (32 factor docs), findable from the record words it reads; no factor doc names another doc.
- All 5 prerequisite sentences verbatim, state form, on the blocked hub only; every hop resolvable from the sentence, the depended-on hub and the records.
- All 6 overwrites: retired clauses carried as "no longer in force"; replaced_by texts in the policy hubs; no clause retired that the source does not retire.
- No tool name, route or aggregated chain beyond the sentences; titles general.
- Cross-product: order docs not yet published, so the competitor-class reading (`bestbuy_com` = online; `local_competitor_ad` = local) is conditional on the order corpus.

### Findings
- **src1** (policy-side origin; no KB verdict effect): base `parameter_schema` descriptions (`liability_limit_basis`, `service_fee_ladder`, `food_spoilage_max_usd`, `prorated_refund_basis`, plus the in-force base tail "proration follows prorated_refund_basis") stay unscoped beside overwrites that narrow them. They surface as in-force statements in `limit_of_liability_and_settlement_terms_f206a9e4` ("Each covered item has a limit of liability equal to the net price paid for the item before tax"), `service_fee_bands_by_tier_376a5662` ("Service fee per approved claim" for the Accident bands), `covered_perils_and_claim_limits_002d1fa9` ("Most paid for food lost … per claim" $250.00 for the Standard tiers) and `cancellation_refund_terms_by_tier_bee72b1e` ("Unused days" explanation). These compete with scored quantities in both tasks (registered 2322.48 vs net price 2149.99; claim service fee 46.75 vs band $49.00; Standard food-loss limit raised to $400.00 vs "most paid" $250.00). The scoped hub sentences resolve them, so the solution stays unique.
- Policy-side notes: N1 (renderer obs 1) no flat repair charge for food-loss claims, so compute gives 0; the repair policy's "claim settled" can select a food-loss approval on a Standard plan; not engaged. N2 (renderer obs 2) in-home category keys vs the base rule that sends TVs under 42 inches to depot: a sub-42-inch TV would get the in-home trip charge and the in-home minimum and no label although shipped to depot; rule == compute; realism note; not engaged. N3 the source rule sentence "its repair is authorized after the cancellation under the repair rules" orders two problems outside a prerequisite sentence. N4 generic assembly sentences in computation docs are source XF-A2 text. N5 the measure clause "before coverage starts every coverage day is unused" appears only inside the retired proration paragraph; its in-force reach has no member tier.

KBVERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=src1

## revision_2

2026-10-25, auditor kb_d3. Cross-product re-judge, all seven products published.
- Snapshot re-run 2026-10-25T04:52:09Z: DOCS OK; TRACEABILITY OK (22/0, 14/0); EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; source hashes and docs/plan tree hash unchanged.
- Round-1 REDs: none were raised; nothing regressed; src1 persists, since neither the source nor the docs changed.
- Conditional resolved: `bestbuy_com` is an online competitor match. BestBuy.com is on the Same-Day Delivery list, and a local competitor's ad applies only to register purchases (`price_match_and_adjustment_terms_890b32d5`). Registration 2322.48 is confirmed.
- Other-product seeded rows: every order row in both worlds is produced by the published order docs (line pricing, fulfilment fees, haul-away fee, price match/drop windows and amounts, amount paid). Neither customer has membership, card, gift, market or trade rows.
- Owed-at-once writes: none in either world (replacement haul-away credit, missed-appointment credit, late-change items, price adjustments and return-linked plan refunds are all not engaged).
- Cross-product contradictions with the plan docs: none.
- New source-layer findings (own-product seed rows re-priced as of their posting dates):
  - **src2**: task 1 food-loss payment c6da717b (2026-06-19), seeded 86.40, is priced by the retired base peril clause. The published food-loss payment rules give 125.04 (+8.64 spoilage, +10.00 reporting, +20.00 installation; limit $400.00; repeat share whole). It feeds the scored Standard refund through the claims deduction: 74.87 becomes 54.78 under consistent seeding. It moves gold.
  - **src3**: task 1 registration c5072254 (2026-01-24), seeded 2999.99 (the retired activation clause). The published registration rule gives 3373.99 (start 3299.99 for the promotion, +74.00 large-item delivery and haul-away). No scored read moves.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=src1,src2,src3

## revision_3

2026-10-25, auditor kb_d3. KB confirm after the seed-only round 6.
- Snapshot 2026-10-25T05:11:29Z: DOCS OK; TRACEABILITY OK (22/0, 14/0); EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; source and docs/plan hashes unchanged.
- **src2 closed**: task 1 June food-loss payment c6da717b is now 125.04, which the published food-loss payment rules produce as of 2026-06-19.
- **src3 closed**: task 1 registration c5072254 is now 3373.99, which the published registration rule produces as of 2026-01-24. The remaining limit 3248.95 is consistent with both rows.
- Blind-view consistency with the new figures: task 1 recomputes to 295.54 and 54.78 from the visible materials, equal to gold. Task 0 is unchanged (2322.48 / 327.78 / 46.75 / 216.07).
- No new defect: no leak of the new figures, no owed write, no cent-boundary risk. Nothing regressed.
- src1 persists (no action, BLUEPRINT-KNOWN).

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=src1
