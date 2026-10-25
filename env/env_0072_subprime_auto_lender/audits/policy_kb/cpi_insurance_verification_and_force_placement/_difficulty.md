# Policy-KB audit — cpi_insurance_verification_and_force_placement (product cpi)

## kb_round1 (2026-10-20)

Entry conditions: policy-side `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`; gate snapshot re-run via `kb_snapshot.sh` at 2026-10-20T23:11:15 — DOCS OK, TRACEABILITY OK (0 misses), EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; yaml 30ebda6c…, task_tools 0a60f264… (match brief). Runtime views sha256 match. DB access tool-shaped only; blind answers frozen before any source read (hashes in runtime_context/*.md); contamination: none.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (closing-month; feed + upload re-reviews) | PASS (77.27 / accepted / accepted = GT) | RED (KB-01, feed doc) | PASS |
| 1 (closing-period; fax re-review) | PASS (99.76 / accepted = GT) | RED (KB-01, fax doc) | PASS |

### KB defects (exhaustive)
- **KB-01** — state expiry-buffer factor documents do not carry the otherwise tier. Members: `docs/cpi/feed_state_expiry_buffer_6bb4fe3b.json` and `docs/cpi/fax_state_expiry_buffer_11130d97.json`, sentence "For a contract of any other state this schedule sets no expiry buffer." Source: `feed_buffer_days` / `fax_buffer_days` otherwise → `P('min_days_to_expiration_at_verification')` = 15 calendar days. The tier's value is neither stated nor named, and "no expiry buffer" admits a 0-day reading. Untriggered in both tasks (TX, OK); RED under the whole-domain rule. (The upload policy has no buffer factor.)

### Source-side items (exhaustive)
- none. Policy-side note P-1 (not a defect): the re-review rules' own replaced_by text says a closed-record re-review is made "solely to fix the premium refunds owed on the record", which tells the reader that refunds consume the re-review; carried faithfully.

### Notes (non-defects)
- N-1 stacking of allowances entailed only by each doc's "is raised by"; N-2 book-value docs' contract-vs-plan-band disambiguation; N-3 baseline replacement-day term (all allowances 0) carried only in grace docs, result identical at default; N-4 reach-date / covered-days fall-through tiers worded "no such substitution applies" / "no change under this rule", unambiguous.
- Cross-category seeded rows (contract ledgers, payoffs, CPI lapse/notice/placement/billing chains) reproduce exactly under the published contract and CPI rules; no repossession, SCRA, GAP or VSC rows in either world.
- Cross-product: the GAP "borrower maximum deductible of the collateral protection plan" is published per CollateralGuard plan in `borrower_insurance_requirement_terms_7c8e0fa1` (A/B 500.00, C–F 1000.00); plan names, record statuses and notice types other products read are all published in the CPI corpus.
- Not in this view: the runtime unlock mechanism and `verify_customer_identity` (system background); GT uses both, consistent with the hub invocation blocks.

VERDICT kb_round1: task0=RED task1=RED kb=KB-01 src=none

## kb_round2 (2026-10-21)

Gate `RENDER round 3: DOCS OK`. kb_snapshot 2026-10-21T00:17:47: DOCS OK, TRACEABILITY OK (0 misses), EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; yaml 30ebda6c…, task_tools 0a60f264… unchanged (docs-only re-render).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS (KB-01 closed in feed doc) | PASS |
| 1 | PASS | PASS (KB-01 closed in fax doc) | PASS |

- KB-01 closed in both members (`feed_state_expiry_buffer_6bb4fe3b.json`, `fax_state_expiry_buffer_11130d97.json`): otherwise tier now "15 calendar days", stated as the product minimum.
- Exhaustive fall-through sweep over all 24 factor documents: every otherwise tier equals its source ladder value (table in policy_kb/0.md revision_2).
- Regression check: only the 24 factor documents changed, and only in fall-through rows (plus the covered-days and state-buffer openings); hubs, calculation/tests and base documents unchanged; prerequisite sentences, tool placement, gold-free examples and factor isolation intact.
- Source-side items: none.

VERDICT kb_round2: task0=PASS task1=PASS kb=CLEAN src=none
