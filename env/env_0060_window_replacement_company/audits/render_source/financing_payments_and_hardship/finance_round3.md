# Render-source findings — finance (financing_payments_and_hardship), round 3

Source: `finance.extended.yaml` sha256 b152d680a19f9e63e7fd56c385d68246684a5cd84eaf050a859ce7a06ce4bdbf;
`task_tools.py` sha256 e9d0c11114277c84afd3ed7b513dfa807060ca7c2c19f8fe7105214723126fc9 (unchanged).
Upstream gate (`_difficulty.md`): "revision_5 verdict: task0=PASS task1=PASS", "charter=CLEAN".
Base sections of the extended charter are byte-identical to `blueprint/products/finance.yaml`.

Inputs read: `audits/policy_kb/financing_payments_and_hardship/{0,1}.md` in full (KB-EXPLICIT PASS both; source-side
S1–S4), `audits/runtime_context/financing_payments_and_hardship/{0,1}.md` candidate and comparison sections (C1–C6;
task-world values not used anywhere in the corpus — a scan for every scored value named in those files finds none).

## S1–S4 and C1–C6 — closure as rendered

- S1 / C6 (promotional catch-up): the new sentence "No catch-up figure is quoted for an account on a promotional
  plan: … referred to a representative." is carried verbatim in the catch-up hub beside the existing scope sentence.
- S2 / C1 / C2 (base plan attributes vs the extensions): the four new plan-attribute sentences are carried in the
  hubs — monthly interest, hardship request and phone fee verbatim; hardship grant verbatim; late fee with the
  component list ("the fixed late fee, the share figure, the way they are combined and the courtesy shares") read
  as "the late fee set out in this policy", because a hub may not inventory its components. The base attribute
  text in the Rate and Promotion Sheet, Schedule of Account Charges and Hardship Deferral Limits stays verbatim;
  each now carries an annotation that, for accounts whose plan carries no promotion, the description is that of the
  base rules and the current basis governs (late fee may exceed the stated share; the flat phone fee is the standard
  amount of the agent-assisted fee; months bounded by the hardship offer and the months asked).
- S3 / C3 (nested record factors): re-rendered from the restructured grant policy. The computation document now
  carries the record adjustment (16 or more plus two months, under 6 less two) over the scheduled-payment entries
  of the twelve months before the grant, and "The request answered is the most recent hardship request on the
  account whose status is submitted." The look-back (span) and the count-by-paying-pattern documents carry their
  own ladders; the removed factor `payment_record_months` lost its document; the new factor `standing_late_record`
  (three or more standing less two months, exactly two less one) has its own document.
- S4 (fee-pool floor): "(a pool below zero counts as zero)" is now carried in the arrears document and all four
  relief documents.
- C4, C5: observations only in the audit; unchanged (the clamps are the result assembly; the retirement of
  `finance_hardship` clause 1 is scoped exactly as `replaced_by`).

## New source mismatches

None found. Re-checked: every `compute_basis` quote, `replaced_by`, `superseded_clause`, `baseline.rule` and
prerequisite `policy_source` is verbatim in its rule; compute-basis keys equal the bindings; the grant's record
adjustment (+2·month_step / −record_step), returned-payment and late-fees-standing ladders, and the result clamp
match the rule sentences.
