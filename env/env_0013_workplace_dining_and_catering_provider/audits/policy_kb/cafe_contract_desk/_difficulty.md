# KB-layer audit closing record — cafe_contract_desk (product: cafe)

Auditor: independent KB auditor — did not author the cafe corpus, did not judge this difficulty's policy
side, and saw no source-layer artifact until both blind answers were on disk.
Closed 2026-09-22. Revision 1.

## Part-verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 — service credit, 3-deep chain | **PASS** | **PASS** | **PASS** |
| 1 — closing settlement, 3-way fan-out | **PASS** | **PASS** | **PASS** |

`audits/runtime_context/cafe_contract_desk/{0,1}.md` carry the frozen `blind_answer` and the appended
`gt_comparison`; `audits/policy_kb/cafe_contract_desk/{0,1}.md` carry `source_to_kb`, `kb_to_source`,
`bijection_verdict` and `dependency_form`.

## Closing checklist

- **Files correspond one-to-one with the tasks.** Two tasks, two runtime-context files, two policy-KB files.
  No older revision existed; nothing was overwritten. Every comparison section carries a PASS.
- **Blind before source.** Both `blind_answer` sections were written to disk before any `.extended.yaml`,
  `task_tools.py`, task-JSON GT field or raw `initial_state` was opened. The DB side of both blind audits
  was genuinely blind: every record came back from a share-finder call through the supplied tool-shaped
  path, never from `initial_state`. No `contamination_disclosure` was needed.
- **Every scored value derived blind matched the source exactly** — task 0: 8066.07 / 5035.71 / 1511.64;
  task 1: 678.08 / 55283.28 / 26058.24 / 150431.90 — as did every tool argument, every owner (two user-owned
  writes, five agent-owned), the write order, and every fall-back baseline figure but one, where the
  divergence was my own arithmetic slip in a supplementary number and is recorded as such in
  `runtime_context/.../0.md`.
- **Both problem trees were derived from the visible materials alone**, hop by hop, with every hop
  **state-derived** and none pre-solved: the 3-deep chain (service credit ← management fee invoiced ←
  service model change confirmed) and the 3-way fan-out (closing settlement ← late charge, early exit
  charge, standby charge). In both, the wrong answer "do only the one thing the customer asked for" is
  excluded by the blocked policy's own sentence tested against a finder return, and also produces a
  different number.
- **Every normative atom of the difficulty's structured source is entailed by the cafe docs.** All 7
  extended policies: 7 baselines carried complete with their own default constants and every product figure
  named; all **34** declared factors carried as whole ladders, every tier of every ladder exact, including
  the tiers neither seed hits; 13 base policies carried, with all **21** superseded clauses written as
  retired and every other clause carried as in force; nothing unborne, nothing borne with changed meaning,
  and no claim from outside the source (a regex sweep for added-policy language over title+content of all
  71 documents returns 0 hits).
- **All 5 prerequisite sentences stand verbatim, in the declared `state` form, in a document of the policy
  they block and in no other policy's** — confirmed by `grep -rlF` on each sentence across all seven
  products' `docs/`, each returning exactly one file. Every hop is resolvable at the source's strength from
  that sentence, the depended-on policy's own rule and the records; the depended-on side discloses nothing.
- **No route, no aggregated chain, no other problem's tool name.** Each of the seven task tool names appears
  in exactly one document — its own problem's hub, in that hub's own invocation block. No dependency table,
  checklist or ordered step list; no cross-problem operational guidance; no task-mirroring title or opening;
  no factor document disclosing a tier or pointing at another document; no computation document hinting
  that anything modifies it.
- **Cross-product factors are findable from the other product's own vocabulary.** `pantry_colocation_allowance_858c8c96`
  names the Office Pantry & Beverage Program and the records it reads; `continuing_outlet_allowance_on_exit_1d67afff`
  and `subsidy_carry_over_to_a_continuing_outlet_2e92c981` name the Unattended Micro Market Program and
  theirs.
- **The rounding convention** adopted by the source audit is carried where the source puts it, in all nine
  places it bears; the two explicit convention sentences sit in the factor documents whose methods they
  govern, not hoisted; a reader following the published prose lands on one cent, and no sentence authorises
  a rounding at a point it does not name. Detail in `policy_kb/.../1.md`.
- **Gates.** No document was edited and none may be: the corpus is byte-identical to the form audited
  (sha256 of the concatenated 71 `docs/cafe/*.json`, first 16 hex, `15478d08690a8a54`, unchanged at close).
  The gate lines on record are therefore the ones supplied with the brief and run on this same form:

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0013_workplace_dining_and_catering_provider cafe
🔎 DOCS gate  product=cafe profile=extended docs=71
   roles={'factor': 34, 'hub': 7, 'facet': 10, 'policy': 13, 'baseline': 7}
   content[min/mean/max]=1566/2545/3908
   required quantitative keys=124  task_tools=7  prerequisite edges=5
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0013_workplace_dining_and_catering_provider/tasks/cafe_contract_desk
1.json          21        0  True
TRACEABILITY OK
```

  The `[MANUAL REQUIRED]` clause the gate hands over is what this audit discharges, and it is discharged
  for both tasks.

## Verdict

**This difficulty's rendering passes the KB-layer audit.** Runtime blind audit PASS + full-domain two-way
scan PASS + dependency-form scan PASS, for both tasks.

## Problems found

None that this skill's verdict turns on. Four source-side observations are recorded (with evidence, in the
per-task files) and change no verdict here:

1. Six fee-base and window ladders say "management fee invoices standing on the contract's ledger" while
   the ledger's `event_type` `cafe_management_fee_invoiced` is shared by `management_fee`, `admin_fee` and
   `mobilization_fee` rows, which are told apart only by `charge_code`; only
   `exit_fee_base_from_recent_invoicing_d10ed1be` states the counting rule in prose. Material in both tasks.
2. `counting_suspended_days_for_standby_4fd1de58`'s first two limbs pin the suspension side to "the latest
   approved suspension request" but leave the resumption side as "a resumption request"; task 1's contract
   has two approved resumptions straddling the latest suspension, so a literal reading finds a witness for
   both limbs. Rendered exactly as the source words it.
3. Prose and compute diverge on `transition_period_base_fee`: the rule says "took effect within the billing
   period being invoiced", the compute tests `MONTHS(effective_date, NOW) == 0`. They agree on this seed.
4. `issue_service_credit_9f99d1a6`'s contract states two rejections (empty invoice reference, non-positive
   amount) that its implementation does not perform; the KB is faithful to the contract.

Two smaller rendering observations, neither a defect: `opening_project_settlement_on_model_change_b00bac72`
and `counting_pause_months_for_standby_7f4e2c71` say "the months the cafe has been serving" without naming
the day the count closes, where sister ladders name one (source wording, rendered exactly); and the worked
example in `working_out_the_monthly_management_fee_3750a6d5` is exact at every escalation step, so it
demonstrates the compounding method without demonstrating the single-rounding convention that its own
sentence states.

## Coverage note

This audit is organised per difficulty and covers only the product this difficulty claims — `cafe`.
Cross-product contradictions are outside this skill's detection range by design; the `pantry` and `market`
corpora were read only as records a solver would legitimately reach, never used as a criterion. Base-type
products claimed by no difficulty are outside scope entirely.
