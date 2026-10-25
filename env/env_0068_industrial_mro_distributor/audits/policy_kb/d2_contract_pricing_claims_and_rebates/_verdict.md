# KB-doc policy audit verdict — d2_contract_pricing_claims_and_rebates (product `pricing`, Contract Pricing Agreement)

## revision_1 (2026-10-17)

Auditor: fresh KB auditor (not the renderer, not the policy auditor). contamination_disclosure: none — blind answers frozen 2026-10-17T18:56:45Z (runtime_context/…/0.md sha256 4e9835a2…, 1.md 1ac46fa9… at freeze) before any source-layer file was opened; no recursive grep over tasks/ or the scenario root; doc meta never opened.

### Entry conditions (cited from the brief; not re-run by the auditor)
- Policy-side verdict: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.
- check_docs.py env/env_0068_industrial_mro_distributor pricing → DOCS OK (66 docs; docs tree sha256 prefix f77c32ed1ad08c7c).
- check_traceability.py tasks/d2_contract_pricing_claims_and_rebates → 0.json 25 0 True / 1.json 32 0 True / TRACEABILITY OK.
- Instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.
- Hashes verified on disk: pricing.extended.yaml 70d9fe4e…, task_tools.py 063dbb2a…, task0.runtime.json fad8dfca…, task1.runtime.json bc250b4a…, db_query.py b5df0dbd… — all match the brief.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (final rebate check; tree clawback → forfeiture → check) | PASS — blind writes equal GT on every argument (24.61 / 9939.90 / 7823.79 tree, periods, RMA) | PASS | PASS |
| 1 (substitute claim; tree decision → close-out → protection → claim) | PASS — blind writes equal GT on every argument | PASS | PASS |

### Closing checklist
- Audit files one-to-one with tasks: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md; each revision_1, blind sections untouched after reveal.
- Every normative atom of the 7 extended policies (rules, current-basis sentences, baselines, 35 declared factors with every tier, tool contracts) and of the 10 base policies, 3 measures and 48 tier parameters is entailed by docs/pricing; retired clauses (price-basis first clause, E3, (e), (f), (g), C4, R5, R6, R7) are each written retired verbatim, with in-force replacements in their hubs; nothing retired that the source did not retire.
- Every prerequisite sentence (5 edges, all state form) stands verbatim in its blocked policy's hub and in no other document; each hop resolves from that sentence, the depended-on hub's description of its own write in the same words, and the records.
- No other problem's tool name, route, aggregated chain or task-mirroring title anywhere; no gold value in any document example or unlock schema.
- Every fall-back (computation document alone) is definite and differs from gold; every factor document was reached from record words.

### Notes (not KB-side findings; not source rule-vs-compute / seed / docstring items)
- N-0a (policy-structure observation): base `pricing_commitment_review` routes over-maximum removals "with notice under the contract item list rules"; in the KB that list's removal-notice clause (f) is written retired, and the in-force notice for every other removal is restated only in the close-out hub's current-basis sentence. Faithful to the source's overwrite construction.
- N-0b (access view): the supplied `db_query.py --list` shows share read tools only, so the share write tool `verify_caller_identity` (a GT step in both tasks, governed by its scenario-level docstring) was outside the audit view. No pricing-corpus consequence.
- Seed spot-checks against this scenario's order charter (Premier Route opened-item credit 80 % less 10 % restocking → RMA-208152 credit 4084.08; Route Delivery 10 % restocking → RMA-213377 1306.26; RMA-204611 base clawback 46.13 on 2025-Q4) — consistent.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-17, cross-product re-judge after all seven products published)

### Gate snapshot (auditor ran `/tmp/erl0068_coord/kb_snapshot.sh d2_contract_pricing_claims_and_rebates pricing`, execute only)
- check_docs pricing: DOCS OK (66 docs, tree f77c32ed1ad08c7c)
- check_traceability: TRACEABILITY OK; non-unlock misses: 0
- gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; hash 70d9fe4e…, 063dbb2a… (unchanged from revision_1)

### Was revision_1 conditional on an unpublished product?
No. Neither blind derivation read another product's rules, only its records through tools. With all corpora now published, no non-pricing document restates, contradicts or routes any rule the two trees use (scanned every credit/order/vmi/vending passage that names the Contract Pricing Agreement, rebates or price claims). The KB-side verdicts are unchanged.

### Part verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS (caveat: SRC-1 opens a plausible second reading of "discount earned" once the credit rules are consulted) | PASS | PASS |

### Source-side items (seed rows another product's published rules would not produce)
- **SRC-1 (task 1, credit, gold-moving).** Glenmore's eight discount lines on invoices dated inside the live Category Contract term (INV-2260228 … INV-2260930) are each 1 % of merchandise. The published credit catch-up rule gives 1 % × 0.75 contract share, on merchandise less applied return credits: CD-2260912 should be 88.45, not 131.00, and the over-deduction leaves the invoice short-paid. Gold dependence: the settlement multiplier (1.0625 → 1.065748) and the paid-invoice credit (0.75 % → 0 when short). claim_amount 1727.71 → 1721.06 (payments as seeded) or 1732.79 (payment re-seeded to cover).
- **SRC-2 (task 0, credit/order, gold-sensitive).** Fairhaven's credit limit 1,000,000.00 (Net 60 tolerance 10 %) is exceeded by the seeded receivable: 1,290,250.00 from 2025-11-30 to 12-22, peaking at 1,302,935.00 on 2025-12-31. Credit rules place an over-limit hold that stops shipping on terms, yet SO-2104455/2 ships 2025-12-18 and the account shows active, hold_reason none. If the limit is raised to make the history producible (> 1,184,486), the exposure share drops below 0.75, the 2.5 % exposure holdback disappears, and the final check becomes 8048.62 instead of 7823.79.
- **SRC-3 (both tasks, vmi, gold-neutral).** StockSmart go-live outside the tier's go-live business days: VMI-20533 Weekly 23 business days vs 20; VMI-21177 Monthly 19 vs 15.
- **SRC-4 (task 1, vending, gold-neutral).** VendPoint VP-217730 Locker 12 installed 14 business days after the request vs the 10-day installation lead.

### Observations (not routed as src; rules do not pin them)
- O-1 booking-to-ship lags on route ship-tos (route weekdays unspecified).
- O-2 both ship-tos' `last_review_date` older than the latest opening anniversary despite later order activity ("handled" undefined).
- O-3 existence-only StockSmart programs: no bins, activity or monthly minimum fees. Fairhaven's VendPoint machine, active until 2025-11-14, also shows no usage billing. These are missing rows, not wrong rows.
- Task-1 SO-2143380 billed at 72.57 is the overbilling the claim corrects: an intended premise.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3,SRC-4

## revision_3 (2026-10-18, verification of the seed-only rework of SRC-1 to SRC-4)

- Gate: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (policy side). Runtime views refreshed (both hashes unchanged).
- kb_snapshot (auditor-run, execute only): DOCS OK (66 docs, tree f77c32ed1ad08c7c); TRACEABILITY OK, non-unlock misses 0; EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK; hashes 70d9fe4e / 063dbb2a. Charter, tools and docs are unchanged, so revision_1's KB-side scans carry over unchanged.

| Item | Status | Evidence |
|---|---|---|
| SRC-1 (task 1, credit discount lines) | closed | in-term discount lines equal the catch-up figures (CD-2260912 88.45); payments cover each invoice; claim_amount 1727.71 → 1732.79 re-derived and matches GT; second reading eliminated |
| SRC-2 (task 0, over-limit) | closed | receivable peak 890,834.80 < 1,100,000.00; FC-2251231 214.80 and the returned check / fee / certified-funds rows all producible; task-0 gold unchanged (24.61 / 9939.90 / 7823.79) |
| SRC-3 (both, StockSmart go-live) | closed | VMI-20533 Monthly Service live in 13 business days; VMI-21177 in 14 (≤ 15); bins and replenishment billing meet the Monthly gates and minimum |
| SRC-4 (task 1, VendPoint install lead) | closed | VP-217730 installed in 8 business days (≤ 10) |

- New rows (VMI bins and activity in both worlds, VendPoint usage bills in task 0) are producible by their products' published rules and feed no pricing factor. No unlock schema or document example equals a new or old scored value. Nothing regressed.
- Part verdicts revision_3: task 0 RUNTIME / BIJECTION / EXPLICIT = PASS / PASS / PASS; task 1 = PASS / PASS / PASS.
- Observations O-1 (route weekdays) and O-2 (ship-to review date) carry over and are still not routed.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
