# rework round 2 — claims (installment_billing_and_fees)

Each round-1 item from audits/policy_task/installment_billing_and_fees (revision_1), with how it was closed. Every
policy was rebuilt from per-policy generator modules. The assembler asserts, policy by policy:
- every compute_basis quote, baseline sentence, replaced_by and policy_source is verbatim in the policy's own rule;
- every superseded_clause is verbatim in its base rule;
- factor bindings are disjoint;
- no factor id is a substring of a tool name.

## Charter-global
- **CG-1** (undeclared override of the base installment-schedule sentence S3). Fixed. `billing_ext_draft_notice.overwrite` now retires that sentence. Its scoped replaced_by restates the base content for every plan outside the schedule (non-owner plans). Base S5 (credits reduce the next installments nearest first) is followed, not departed from: it is the credit_carry factor.
- **CG-2** (deposit application vs the notice's carried amount). Fixed.
  - The deposit's application overwrite now says the deposit is held as a credit that reduces the installments not yet invoiced, nearest first, and never touches an issued notice.
  - The notice's credit_carry factor applies such a credit the same way on every later notice.
  - The deposit balance is now net of a credit the plan already holds, so a credit is never counted twice.
- **CG-3** (baseline or plain binding defining factor-only quantities). Closed across all five policies.
  - Deposit: the installment count is moved into its factor sentence, and the dead binding is removed.
  - Returned-item fee: the returned amount is also read by the plain statutory ceiling, so it is not factor-only.
  - Late fee: the baseline paragraph is now only the standard fee; the invoice selection and unpaid amount live in the rule and the factor.
  - Makeup: the next-installment premium is a shared plain binding, stated in the rule but not in the baseline.
- **CG-4** (combination sentences naming factor quantities, or "the first"). Every combination sentence is rewritten generically ("the one that sets how … is figured replaces the standard figure, each of the others adds …"). None names a factor's own quantity or uses "the first".
- **CG-5** (month-end and same-day conventions). Fixed.
  - One month-end sentence is stated in every rule that counts whole months (draft notice, deposit).
  - Same-day tie rules are stated for every LATEST/XLATEST read (late fee invoice and payment, returned payment, driver addition).
- **CG-6** (rule words vs compute, non-owner and paper cases). Fixed.
  - Every package and new-business ladder of the fee and makeup policies now states its outcome for a non-owner plan.
  - The returned-item channel ladder is keyed on payment_channel values in the words exactly as in compute.
  - The draft notice, deposit and makeup scope themselves to owner terms.
- **CG-7** (makeup gates demanding entries the fee policies cannot price). Fixed.
  - Both makeup sentences now wait only on the returned payment the makeup makes good and the invoice that payment had paid.
  - The returned-item fee prices exactly that payment (the most recently returned one).
  - The late fee prices exactly that invoice (the invoice the most recently returned payment paid, else the latest invoice).
  - Every waited-on entry is producible on every plan in scope. The late fee has a floor, so a waited-on entry is never zero (XF20).
  - The deposit's sentence counts an installment covered in full by credit as satisfied, so it cannot deadlock.
- **CG-8** (deposit core method fraction). Fixed. The middle tier is now one installment's share of the balance over the 2 or 3 installments still unbilled. The divisor is selected by the data, so it is no longer a constant fraction. The other tiers are the whole balance and the standard percentage with floor and cap.
- **CG-9** (incoherent makeup baseline). Fixed. The baseline paragraph is now the returned amount plus the fees owed with it, capped at the account balance. baseline.params lists exactly the keys it uses (none).
- **CG-10** (points- and state-keyed billing tiers). The draft notice's state and points fee factors, the late fee's state and points additions, and the makeup's state advance are all struck. Their replacements are real billing mechanics already in the records:
  - the credit standing on the plan (base S5);
  - the installment size behind the fee;
  - the re-collection of a returned payment that also prepaid installments.
  No garaging-state key remains on any fee except the Florida and Georgia returned-check statutes.
- **CG-11** (add-ons above the FL/GA statutory maximum). Fixed. The statutory amounts are now a ceiling the returned-item fee can never exceed, in every state modeled (Florida bands or 5%, Georgia greater-of; elsewhere the plan's nsf_fee). The task-1 world's fee sits under the ceiling.
- **CG-12** (deposit exceeding its balance). Fixed. The deposit is capped at the endorsement balance, and no deposit is taken on a zero balance.

## Task 0 findings
1. CG-1 consequence. Closed by CG-1. The base-schedule reading no longer stands for owner-term notices.
2. Deposit had no valid method factor. Closed by CG-8.
3. violation_points_fee. Struck (CG-10).
4. CG-3 / CG-4 / CG-5 members. Closed as above.
5. Observations:
   - CG-2: closed.
   - CG-12: closed.
   - O-4 (package tier): kept and declared below.

## Task 1 findings
1. Fee above the FL ceiling. Closed by CG-11. The world was rebuilt so that the statutory percentage charge and the ceiling both bear on it.
2. Incoherent makeup baseline. Closed by CG-9 and CG-3.
3. Points late addition and state makeup advance. Both struck (CG-10).
4. CG-3 / CG-4 / CG-5 / CG-6 members. Closed as above.
5. design_rationale misquoted both prerequisite sentences. Closed. The rationale is regenerated, and each sentence is inserted from the rule text itself. The same regeneration covers every closure, tracing and equation text of both tasks, and a sweep found no stale figure.
6. Observations:
   - O-2, O-8, O-9: unchanged behaviour.
   - O-10: persona line kept as a passive reply.

## Other round-2 items
- **Stale Step-0 uuid line in worklog.md.** Corrected.
- **Probes (decoys, boundaries, None/zero division, non-owner plans).** Run on scratch copies of both worlds. The results are recorded in the worklog's round-2 probe table:
  - decoys: second plan, prior-term invoice, later-dated returns, same-day driver tie;
  - absent records: no additional premium, no driver change, no return, a returned payment with no invoice;
  - boundaries: the 12-month and 90-day lines;
  - non-owner plans for every policy.
- **Pairwise method-tier table.** Re-run for every method factor; all pairs pass.

## Residual realism risk (declared, not hidden)
These were kept because the drawn factor counts require them and no real billing dimension was left in the records:
- package-keyed fee and advance tiers (observation O-4);
- new-business additions keyed on the first term and the days since the effective date;
- the returned-item channel and reason additions (company schedule, always under the statutory ceiling);
- the installment-size charge (lesser-of method);
- the points-keyed makeup advance (O-4).
