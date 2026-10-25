# KB-doc policy audit — professional_email_seats (product email) — revision_1

Entry: policy verdict `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`; snapshot /tmp/erl0076_coord/kbsnap_professional_email_seats_r1.txt, re-run at close via kb_snapshot.sh (execute-only): DOCS OK; TRACEABILITY OK, misses 0 (0.json 17, 1.json 21); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; email.extended.yaml f9d569fc…, task_tools.py 7eaba5a2…, docs/email 53 documents (corpus hash 165862fa…).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Tree (blind) |
|---|---|---|---|---|
| 0 | PASS (blind = GT on both writes) | PASS | PASS | Pro upgrade ← reactivation renewal (state-derived) |
| 1 | PASS (blind = GT on all three writes) | PASS | PASS | annual conversion ← late monthly renewal ← seat catch-up (state-derived ×2) |

Closing checklist: audit files 1:1 with tasks (runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md); every prerequisite sentence verbatim in its blocked hub only; every factor ladder (25 factors over 5 policies) carried in full in its own document and findable by record words; retired surface correct for all overwritten clauses; no tool name, route or chain outside the source's own sentences; no scored value or gold argument in any document or unlock schema.

Source-side item:
- XP-1 — The email extended policies add the account-tier email discount to the seat-volume, hosting-bundle and domain rates into one combined rate, round once on the final figure, and apply the tier rate to the Pro upgrade's upgrade_proration line. This goes against the in-force Harborline Customer Accounts rule `account_tier_benefits` (published in docs/account/tier_discount_schedule_71039551, terms 1–3: no tier discount on proration lines; only the single higher of tier vs a product's own promotion/volume discount, never added; discounted components rounded before fees are added). No declared precedence covers it, and every scored amount in both tasks moves under the account reading.

Notes (no id): (a) the GT lists supporting reads (find_account_credit_ledger, find_hosting_charges, find_domain_charges) that no visible rule makes necessary — this is a task-layer matter if the scorer requires them; (b) the Pro upgrade tier illustration uses a hypothetical Bronze holder, the same tier as task 0's customer, but gives no figure; (c) hosting/domain cross-product seed rows are conditional until those corpora are published (account rows checked: ledger and credit-first auto-renew behaviour consistent).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=XP-1

## revision_2
Policy verdict `VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN`; snapshot /tmp/erl0076_coord/kbsnap_professional_email_seats_r2.txt: DOCS OK; TRACEABILITY OK, 0 misses (0.json 14, 1.json 18); 7 gates OK; email.extended.yaml 35f667eb…, task_tools.py ff9caa38…, docs/email 53 documents.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Tree (blind) |
|---|---|---|---|---|
| 0 | PASS (blind = GT, both writes) | PASS | PASS | Pro upgrade ← reactivation renewal (state-derived) |
| 1 | PASS (blind = GT, three writes) | PASS | PASS | annual conversion ← term renewal ← seat catch-up (state-derived ×2) |

Round-1: no KB RED; XP-1 closed. No regression found in prerequisite placement, retired surface, tool-name scope or leak checks.

Source-side items:
- SR-1 — The seeded October renewal declines (both tasks) contradict the published credit-first auto-renew rule: at the term-renewal price the published rules give, the account credit on record covers the on-time attempt.
- BL-1 — In the Pro upgrade, the opening charge date is a plain binding read only by the two fee factors. It lands in the computation document with the sentence "a fee is part of what that charge billed but never of what a term is credited", which signals the fee factors from the baseline surface.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=SR-1,BL-1

## revision_3
Policy verdict `VERDICT revision_16: task0=PASS task1=PASS charter=CLEAN`; snapshot /tmp/erl0076_coord/kbsnap_professional_email_seats_r3.txt: DOCS OK; TRACEABILITY OK, 0 misses (0.json 14, 1.json 18); 7 gates OK; email.extended.yaml 86f1a705…, task_tools.py ff9caa38…, docs/email 53 documents (all seven products published).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

Round-2 items: SR-1 closed (full-balance credit withdrawals before the October attempts, valid under the published withdrawal rule, make the declines consistent with credit-first); BL-1 closed (the opening charge date now lives in the two fee factor documents; the computation document carries only the baseline). Cross-product re-judge: the task worlds hold only email and account records, all priced and dated as the owning published rules produce them. No regression; no new defect. Contamination: the revision_3 blind answer is not independent of the revision-15 GT read in revision_2 (records unchanged), as disclosed in the runtime files.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
