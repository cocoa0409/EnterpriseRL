# KB-doc policy audit — preowned_repossession_recovery (product preowned) — difficulty close-out

## revision_1 (round 1)

### Entry conditions (Step 0)
- Policy-side verdict (tail line of audits/policy_task/preowned_repossession_recovery/_difficulty.md, the only line read there): `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot supplied by the coordinator: `[check_docs preowned] DOCS OK`; `[check_traceability preowned_repossession_recovery] TRACEABILITY OK` (post-publication). Not re-run by this auditor (Step 0: the auditor runs neither); docs/preowned last written 2026-10-16T10:18:45, source last written 09:59:18, both before the snapshot and unchanged during this audit (corpus sha256 d715a53c9a37abb6).
- Runtime view hashes match the brief (0.runtime.json 07cc8b693f4a7bb4, 1.runtime.json f60801a0b8d764b5). DB access: tool-shaped only (db_query.py share tools + KB_search); task-tool runtime schemas read through the loader's `openai_schema()` only. Input complete.
- Isolation: no other scenario and no other difficulty's tasks/ read; no recursive grep over tasks/ or audits/; no contamination.

### Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (Teresa Kowalski — deficiency settlement; transport → deficiency quote → settlement) | PASS (blind = GT on all 3 writes: 335.00 / 2026-06-30, 3349.01, 2659.51 / 3364) | PASS | PASS |
| 1 (Marcus Lindqvist — discretionary reinstatement; storage → redemption quote → notice → reinstatement) | PASS (blind = GT on all 4 writes: 50.00 / 2, 28430.27 / 18, 37, 6482.22) | PASS | PASS |

Files: runtime_context/preowned_repossession_recovery/{0,1}.md (blind_answer frozen before reveal; sha256 at freeze 074b1378c4098c2d / 1ec005f7b5ab71cd), policy_kb/preowned_repossession_recovery/{0,1}.md.

### Closing checklist (Step 5)
- Audit files one-to-one with tasks 0 and 1; first revision, nothing superseded.
- Every normative atom of the seven extended policies (rules, overwrites with scoped replaced_by, 6 prerequisite edges, 31 factor ladders with every tier and threshold) and of the governing base policies is entailed by docs/preowned; no unborne atom, no changed meaning, no claim from outside the source.
- Six prerequisite sentences: each verbatim, state form, in a document of the policy it blocks and in no other document (script check over docs/*/*.json); every hop resolvable from the sentence + the depended-on hub + records (all hops state-derived in both blind answers).
- No other problem's tool name, route or aggregated chain anywhere; titles general.
- Retired surface: every retired base clause has a bearing document marked no longer in force; no KB-only retirement; unnamed clauses still in force.

### Renderer notes (audits/render_source/preowned_repossession_recovery/render_r1.md, render_r2.md)
| Note | Classification | Evidence |
|---|---|---|
| r1-1 repeat surcharge zero-fee case unstated | closed in source; KB faithful | rule now "a single agency fee, or none posted, carries none"; repeat_recovery_surcharge row "None posted \| none" |
| r1-2 transport date undefined without a condition report | closed in source; KB faithful | rule now "no transport charge is owed while no condition report dated on or after the repossession date is on record"; recovery_transport_charge carries it and the "not yet owed" row |
| r1-3 auction transfer days, same-day report fits no case | closed in source; KB faithful | rule now "shown by a condition report dated on or after the repossession date"; auction_transfer_days row and "condition report on the 3rd → 2" |
| r1-4 good_through_days 0 vs "positive integer" | closed in source; KB faithful | tool schema now "a non-negative integer"; redemption_quote "Reference. A good-through period of 0 days …" |
| r1 obs: which sale date | closed (no defect) | rule "The sale date is the sale date recorded on the contract"; compute reads scheduled_sale_date, the base sale/charge-off clauses use the same field; KB deficiency_figure_calculation carries the sentence |
| r1 obs: settlement posting vs base posting | closed in source; KB faithful | settlement overwrite of the posting clause with scoped replaced_by; deficiency_lump_sum_settlement carries it and payment_posting_and_application (b) marks the base clause retired |
| r1 obs: reinstatement baseline omits the state-right exclusion | closed in source; KB faithful | baseline.rule now "… less the fees a reinstatement the state period grants leaves out of its amount"; reinstatement_amount_calculation |
| r1 obs: placement of single-factor steps / shared storage paragraph | no defect (placement); KB split the release-storage paragraph by subject | storage_free_days_recovery_history + stored_days_lot_intake together carry the whole paragraph |
| r2 yard-hold same-day wording | **SOURCE-side wording item → SRC-1**; KB faithful at entailment | see SRC-1 |

### XF_recipe.md points, judged on this difficulty's source and docs
1. Assembly sentences — each rule states one generic assembly sentence ("Each schedule below … on its own: …") mirrored in `result`; carried once in each computation document. Clean (see PN-1).
2. Non-commuting order — fixed in words for settlement (replacement, points, floor, rounding), sale date (anchor max before adds, weekend last), storage (replacements, sum of daily amounts, multiply), redemption (interest end first), transport (replacement first). Deficiency post-sale days: the interest-free subtraction is stated against the post-sale days the end defines; unique (blind reached the compute's 54). Clean.
3. Factor independence — no ladder reads another factor's output; shared records (most recent storage charge, lot-intake report, recovery type) are plain bindings. Clean.
4. Ownership — clean.
5. compute_basis quotes — scripted check: every quote verbatim in its rule for all 7 policies.
6. Ties — every latest/first read states the first-listed rule (sale, storage charge, condition report, deficiency quote, lease/retail lookup order). Clean.
7. Counting conventions — day windows, whole-year ages from 1 January, 12-month lookbacks stated and matched in KB boundary tables. Clean.
8. Every branch both ways — absent records (no report, no notice, no storage, no lease/retail, no assignment date, no quote) stated in rules and docs. Clean.
9. Base clauses — all conflicts declared as scoped overwrites naming sibling scopes; nothing retired needlessly. Clean.
10. Rounding — matches RND placement. Clean.
11. Tools — docstrings match bodies, no concrete example values, no ordering words. Clean.
12. Proof text — design_rationale skip figures recompute (task 0: 3014.01 / 275.80; task 1: 6418.22). Clean.

### SOURCE-side items
- **SRC-1 (advisory; wording only, no figure, branch or scored effect).** preowned_ext_recovery_transport_charge rule, holding sentence: "a vehicle taken to the lot on the day of the repossession, a contract whose most recent condition report is dated on or before the repossession date (no report yet taken for this recovery), or one with no condition report on record carries no holding charge." The same rule's dating sentence treats a report dated on the repossession date as this recovery's lot intake ("the most recent condition report, dated on or after the repossession date"), so the parenthetical "no report yet taken for this recovery" is false for the same-day case it covers. The compute gives 0 nights either way (`yard_nights … if lot_intake_date > F('repossession_date') else 0`). KB agency_yard_holding_charge resolves it faithfully (same-day listed once as "taken to the lot on the day of the repossession"; the gloss kept only for "dated before the repossession date"); the no-charge set is unchanged. Not a KB defect.

### Policy-side notes (no verdict, not routed)
- PN-1: every computation document carries the source's generic assembly sentence (transport "Composition…", deficiency "credits … subtracted", settlement "a replacement of any figure first, then any percentage points…", storage "Any replacement of a figure comes first…", redemption "The end of the interest period is settled first…", sale date "Where another day anchors the sale…", reinstatement "Each amount added … is added once"). These signal that variations exist, which the skill would otherwise count against a baseline; they are the source's own `result`/rule text the XF recipe requires the computation document to carry, so they are recorded here, not as KB-EXPLICIT. Similarly lot_storage_charge_calculation and redemption_figure_calculation list the recovery type among inputs (a shared plain binding of the source).
- PN-2: depended-on hubs state their own triggers in source words that name what they serve (storage "whenever the company must state an amount the customer has to pay to get the vehicle back"; redemption quote "owed whenever the company must state the redemption amount"; notice "states it with the redemption and any reinstatement amount"). Verbatim rule/base text; no tool, no prerequisite sentence and no route is disclosed; both blind trees were derived from the blocked-side sentences.
- PN-3 (latent, unreachable): reinstatement and settlement rules say funds are applied "as every payment is … then to principal until the past-due amount is satisfied", while the base measure preowned_msr_installments_due adds the next installment when it falls within one month after posting; on a repossessed or deficiency contract the next due date is always in the past, so the two never differ.

### Coverage note
Only this difficulty's claimed product (preowned) was audited; cross-product contradictions are outside this skill's range (all seven products were published and the cross-product factor documents name Kestrel Closed-End Consumer Lease and Kestrel New Vehicle Retail Installment Sale Contract by their official names).

KBVERDICT round 1: task0=PASS task1=PASS kb=CLEAN src=SRC-1
