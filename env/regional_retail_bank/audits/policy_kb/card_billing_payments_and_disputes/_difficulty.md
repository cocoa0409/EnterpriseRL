# KB-doc audit closing checklist — card_billing_payments_and_disputes (product `card`)

Auditor: independent KB-doc auditor; did not author the documents and did not judge the policy side of this difficulty. Audit date 2026-09-16. Corpus audited: `env/regional_retail_bank/docs/card/`, 62 documents, `sha256(cat …/*.json) = 0f95c45bf09344cd…`. No artifact was edited and no fix was arranged.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (rewards statement credit ← late fee correction) | **KB-RUNTIME PASS** | **KB-BIJECTION PASS** | **KB-EXPLICIT PASS** |
| 1 (fixed monthly autopay ← temporary dispute credit, ← dispute rebill) | **KB-RUNTIME PASS** | **KB-BIJECTION PASS** | **KB-EXPLICIT PASS** |

Every scored figure the blind audit derived from the published documents, the runtime tool surface and tool-shaped record reads alone matched the source layer exactly: task 0 — `correction_amount` 23.00, `points_redeemed` 33000; task 1 — `provisional_credit_amount` 976.00, `rebill_amount` 276.00, `autopay_amount` 1129.00. Every fall-back figure computed from a computation document alone also matched the source's own `baseline_result`: 11.20, 4144, 898.80, 480.00, 3703.96.

## Closing checklist

- [x] Audit files correspond one-to-one with the tasks: `audits/runtime_context/card_billing_payments_and_disputes/{0,1}.md` and `audits/policy_kb/card_billing_payments_and_disputes/{0,1}.md`. First revision of each; no earlier revision to preserve.
- [x] Each `blind_answer` was written to disk before any source-layer artifact was opened, and none was edited afterwards. One minor contamination is disclosed in both runtime files (a truncated glimpse of three unrelated documents' `meta` blocks during the first corpus dump) and judged not to affect the answers.
- [x] Every comparison section carries a PASS.
- [x] Every normative atom of this difficulty's structured source is entailed by the product's docs: all 15 base policies borne, all `variants` parameters of all six tiers rendered, all 8 measures carried with their windows and counting rules, all 5 extended policies' rules, baselines and tool contracts carried; nothing unborne, nothing borne with changed meaning, and no claim from outside the source (a twenty-marker route/process scan over all 62 documents returned zero hits).
- [x] All 3 declared `prerequisite` edges carried verbatim, in their declared **state** form, each in a document of the policy it blocks and in no other policy's document; every hop resolvable at the source's strength from that sentence, the depended-on documents and the records; `condition`, `resolved_by` and `effect` rendered nowhere.
- [x] All 24 declared factors' ladders carried in full, every tier exact, each in its own factor document, findable from the words the customer's records use for its evidence (including the checking, savings and certificate records of other difficulties) and referenced by nothing.
- [x] All 5 `overwrite` entries: each retired clause has a bearing document that writes it as retired, the surviving clauses of the same policies are still stated as rules in force, and the KB retires nothing the source did not declare retired.
- [x] No other problem's tool name, route or aggregated chain is stated anywhere: each of the 5 task tool names occurs in exactly one document, its own policy's hub.
- [x] Gates on the final form (unchanged by this audit, cited from the brief, not re-run):
  - `check_docs.py`, product `card`, profile `extended` — `docs=62 roles={'policy': 15, 'facet': 13, 'factor': 24, 'baseline': 5, 'hub': 5} content[min/mean/max]=603/1796/3034`, `required quantitative keys=148 task_tools=5 prerequisite edges=3`, `[PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding`, `[MANUAL REQUIRED] …`, `DOCS OK`.
  - `check_traceability.py` — `0.json copied 17 missing 0 ok True`, `1.json copied 27 missing 0 ok True`, `TRACEABILITY OK`.

## Verdict

**The rendering of product `card` for difficulty `card_billing_payments_and_disputes` passes the KB-doc audit** — runtime blind audit PASS, full-domain two-way scan PASS and dependency-form scan PASS, on both tasks.

## Carried forward as policy- and implementation-side notes

These are reported, not repaired, and none moves this skill's verdict.

1. **Banker's rounding against "half up".** The expression primitive is `round(float(x), n)` (round-half-to-even) while every source rule and every rendered sentence says "rounded half-up". No figure on either world lands on a tie (`RND(23.40,0)=23.0`, `RND(976.075,0)=976.0`, `RND(275.93,0)=276.0`, `RND(1128.6435,0)=1129.0`), so nothing scored moves and a reader of the corpus loses nothing here. It is a latent divergence between the published rule and the implementation, on the policy/implementation layer.
2. **`redeem_card_points_9bfb7edb` posts no statement-credit ledger entry.** Verified at runtime: the rewards balance fell 40876 → 7876 while `current_balance` stayed 5981.95, and `task_tools.py` writes only a `card_rewards_redeem` row. The published document claims exactly what the tool does and drops the docstring's unprovable "the statement credit follows on the card" — the correct, conservative rendering. The corpus states nothing the runtime falsifies, and the redemption is the last write on task 0, so the cost to a reader is nil. Recorded as a tool-implementation gap.
3. **Base clauses that themselves state an order** (closure confirmation, redeem-before-closure, merchant-credit resolution then rebill) are rendered as the source has them. Base law may be neither dropped nor softened, so these are policy-side notes rather than dependency-form findings.
4. **The `withdrawn` dispute status has no in-force rebill rule**, because the rebill `overwrite` retires the whole base clause that named it while the replacing rule reaches only "resolved against the cardholder". Faithfully translated; the consequence is the source's.
5. **A retired clause whose parameters remain in a facet table**: `card_rewards_redemption_schedule_21cdc270` still tabulates the redemption types and the travel value per point, whose only operative base clause is retired. The facet renders `variants` under the meanings `parameter_schema` gives them, as the render contract requires, and states no permission of its own.
