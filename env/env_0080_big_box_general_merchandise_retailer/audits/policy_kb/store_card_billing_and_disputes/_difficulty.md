# KB-doc policy audit — store_card_billing_and_disputes (product card) — difficulty close-out

## revision_1

Auditor: fresh KB auditor (kb_d2), independent of the renderer and the policy-side auditor. Blind answers frozen before any source read (runtime_context/store_card_billing_and_disputes/0.md sha 3ed6b8a1…, 1.md sha f75e9dab…); no contamination.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Gold calls reproduced blind |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | settle (1412.84 / 1421.69), catch-up payment (2026-09-09 / 319.49, user), limit 5200.00 |
| 1 | PASS | PASS | PASS | courtesy reversal 23.02, refund 246.58 (user) |

Closing checklist
- One runtime_context and one policy_kb file per task; no older revisions existed.
- Every normative atom of card.extended.yaml's five extended policies (24 factors with every tier, 5 baselines and assembly sentences, 4 overwrites with retired surfaces, 3 state-form prerequisites, 2 coordinator referral routes) and the governing base clauses is entailed by docs/card; nothing unborne, nothing added.
- Each prerequisite sentence stands verbatim, in state form, in a document of the policy it blocks (its computation document) and in no other document of any product; every hop resolved state-derived in the blind audit.
- Renderer placement choices judged: (1) prerequisite sentences only in the blocked computation documents — conforms (a fragment of the blocked policy); (2) shared-quantity sentences restated in each factor document — conforms (consistent restatements, no cross-reference, no factor reads another).
- No other problem's tool name, route, aggregated chain, task-mirroring title, or scored value anywhere in the corpus or tool schemas.
- Final-form gates (snapshot re-run 2026-10-25T04:34:11Z): `DOCS OK`; `TRACEABILITY OK` (0.json 16/0, 1.json 11/0); EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; docs/card 53 files, tree hash 6472c46fd7407d0c.
- Market corpus not yet published: no factor of this difficulty reads marketplace records, so no cross-product figure here is conditional on it.
- Non-blocking notes (no verdict effect): computation documents carry shared definitions the baselines do not use (duplicate excess; 24-month / one-month windows); catch-up fall-back reads gross (0.00, = compute); the retired fee error/ceiling clause's "superseded by the current basis …" lands in the error_late_fee factor document because the source replaced_by is scoped by that factor's output; two catch-up factor documents restate "the missed statement" without its tie rule (carried in the computation document).

KBVERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2

Round-2 re-audit (cross-product re-judge, all seven products published), 2026-10-25T04:53Z.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

- Round-1 REDs: none to close. Regression: none. docs/card, card.extended.yaml and task_tools.py are byte-identical to revision_1.
- (1) Conditional readings: none were conditional. The membership tier, status and enrolled-date reads and the order amount-paid and order-history reads match the published membership and order docs, and the guarantee-closure cross-reference matches the market docs.
- (2) Re-pricing: every seeded other-product row in both worlds (2 memberships, 16 orders, 17 order-linked card postings) is produced by its owning product's published rules. The unseeded fee, Northgate Cash and order-line rows are the accepted residue (rows no gold step reads).
- (3) Owed-at-once writes: none of the other products' owed entitlements is engaged in either world. The one membership schedule that is reachable cannot post without an order line, and it posts to the membership ledger, not the card.
- Gates (snapshot 2026-10-25T04:53:34Z): DOCS OK; TRACEABILITY OK (16/0, 11/0); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
