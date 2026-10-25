# KB-doc policy audit — account_credit_and_recovery (product account) — revision_1

Inputs: account.extended.yaml 9b495d5d…7d77, task_tools.py 7be694eb…ad5b, docs/account 69 documents. The gates were re-run on the final form with `kb_snapshot.sh`: DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK, and the hashes are unchanged. Policy side: VERDICT revision_4 PASS / charter=CLEAN.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 (hosting renewal prefund) | PASS (blind = GT on all goodwill amounts, balance and visible charges; the hosting/ssl/domain figures are conditional) | PASS | RED (K1) | RED |
| 1 (domain retry top-up) | PASS (same; conditional figures) | PASS | RED (K2, K3) | RED |

KB items (renderer):
- K1: the computation document hosting_prefund_amount_calculation_5913d5f3 carries the rule's coverage sentence ("The prefund covers the charges that keep the website on the hosting plan running and that come due within the coming 14 calendar days. Charges of any other holding are not counted by the prefund."). No baseline binding owns it. In the computation document it announces the variations.
- K2: the computation document retry_top_up_amount_calculation_498d36c9, step 2, carries the rule's credit-first coverage sentence ("the top-up also covers in full each counted charge whose next auto-renew attempt falls from today up to the day before the retry …; charges of any other holding … are not counted"). No baseline binding owns it. In the computation document it announces the variations.
- K3: the factor document duplicate_charge_compensation_basis_46cb801c uses a worked-example figure (hypothetical duplicate $22.40) equal to a task-1 scored value.

Source items (instantiator):
- S1: in the rules of account_ext_duplicate_renewal_goodwill and account_ext_refund_posting_goodwill, the combination sentence adds the uplifts "to the compensation basis". That names a factor's output inside the assembly sentence (XF A.2/29). The KB had to reword it, but the rendering is equivalent.
- S2: in account_ext_renewal_prefund, pf_cert_end, pf_cert_due and pf_cert_years belong to no factor, though only certificate_renewal_price reads them (XF A.3). As a result, the computation document's meta.covers lists them while its prose leaves them to the factor document.

Coordinator re-judge pending: findability of the cross-product figures once hosting/ssl/domain are published.

KB-VERDICT revision_1: task0=RED task1=RED kb=K1,K2,K3 src=S1,S2

## revision_2

Gates (r2 snapshot): DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK. Source round 5 d91091f1…192e, task_tools unchanged, docs/account 69 documents. Policy side: VERDICT revision_5 PASS / charter=CLEAN.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- K1, K2, K3, S1 and S2 are all closed (evidence in policy_kb/…/0.md and 1.md, revision_2).
- The regression sweep is clean.
- Observations without ids: the closure clauses ("charges of any other holding …") are carried without an explicit antecedent and are resolved by the specific counted-charge documents. The shared windows are rendered per factor while meta lists them on the computation document.
- Pending, as in revision_1: the coordinator's cross-product re-judge of the hosting/ssl/domain figures once those products are published.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (cross-product re-judge)

Gates (r3 snapshot): DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK. Hashes are unchanged from revision_2. Policy side: VERDICT revision_5 PASS / charter=CLEAN. All 7 products are published.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Every conditional figure of revision_1 is found in its owning product's published corpus and resolves to the scored value.
- Every seeded hosting, domain, ssl, email, security and server row of both worlds is producible by the owning published rules as of its date.

Source items (cross-product; the fix may sit in either charter):
- S3: the account prefund (and top-up) email charge counts the scheduled seat count where one is set. The published Professional Email term-renewal rule never bills fewer seats than the mailboxes in use. Task 0's world shows the gap (3 seats in use, 2 scheduled).
- S4: the account prefund and top-up certificate charge counts the tier price less the tier SSL discount. The published SSL auto-renew charge rule adds the re-vetting fee and the Harborline domain credit. The SSL corpus is itself inconsistent about whether a credit-paid auto-renewal is priced under that rule ("not booked under this rule" vs "Every auto-renew charge is priced under the auto-renew charge rule"). This affects tasks 0 and 1.
- Email may receive one more seed-only round. S3 depends on the email term-renewal seat rule as now published.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S3,S4

## revision_4

Gates (r4 snapshot): DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK. Source round 6 d180cc83…dc21, task_tools unchanged, docs/account 69 documents. Policy side: VERDICT revision_6 PASS / charter=CLEAN. All 7 products are published.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- S3 is closed (the email term-renewal seat rule is carried; seeded mailbox rows are producible). S4 is closed (the credit-paid certificate renewal basis is stated, consistent with the published SSL rules).
- The cross-product re-judge is clean: every seeded row and every counted charge matches the owning product's published rules.
- No regression.
- Observation forwarded (SSL difficulty): the SSL support-renewal clause 1.2 reads more broadly than the SSL auto-renew hub's credit-paid exclusion.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_5

Gates (r5 snapshot): DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK. Source round 8 9cec8a70…d9b8, task_tools unchanged, docs/account 69 documents. Policy side: VERDICT revision_8 PASS / charter=CLEAN. All 7 products are published; SSL re-rendered.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | RED (K4) | RED |
| 1 | PASS | PASS | PASS | PASS |

- The cross-product re-judge is clean. Every seeded row and every counted charge (certificate now under the SSL auto-renew rule, "whatever pays it" on both sides) matches the owning product's published rules.
- S5 (source): the prefund email charge multiplies the outputs of two factors (`email_renewed_seats` x `email_seat_price`) in a non-factor assembly sentence that names both. The renewed-seats factor cannot move the result while the seat-price factor sits at its baseline.
- K4 (KB, caused by S5): the prefund email seat-price factor document says the charge is "the renewed seats times the seat price", naming a quantity defined only in the other factor document, with no default. Closing S5 is a precondition.

KB-VERDICT revision_5: task0=RED task1=PASS kb=K4 src=S5

## revision_6

Gates (r6 snapshot): DOCS OK, TRACEABILITY OK (0 misses), 7 instantiation gates OK. Source round 9 e81a6485…453a, task_tools unchanged, docs/account 69 documents. Policy side: VERDICT revision_9 PASS / charter=CLEAN. All 7 products are published.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- S5 is closed: the prefund email charge is a single factor again.
- K4 is closed: the email document is self-contained and names no other factor's quantity.
- New prefund certificate structure: the reduced amount is in the baseline, and the re-vetting fee and domain credit are separate factors. It is carried completely and matches the SSL published auto-renew rule.
- The cross-product re-judge is clean, and nothing regressed.

KB-VERDICT revision_6: task0=PASS task1=PASS kb=CLEAN src=NONE
