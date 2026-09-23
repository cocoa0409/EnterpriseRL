# KB-doc policy audit — closeout for air_ticketing_desk (product `air`, Air Ticket Fare Brands)

Auditor independent of the render agent and of the policy-side auditor. Blind answers frozen to disk
before any source-layer read; prior revisions preserved in git at `fffc79a` and not read.
Corpus audited: `env/env_0000_online_travel_agency/docs/air/`, 74 documents,
`sha256sum *.json | sha256sum` = `67feea6ef6210220754ec1962a967af55e157b531fa270e81d4fe12b4847f9d7`.

## Three part-verdicts per task

| task | runtime blind audit | full-domain two-way scan | dependency-form scan |
|---|---|---|---|
| 0 | **KB-RUNTIME RED** (`runtime_context/air_ticketing_desk/0.md`, finding R0-1) | **KB-BIJECTION RED**, one atom class (`policy_kb/air_ticketing_desk/0.md`) | **PASS** |
| 1 | **KB-RUNTIME RED** (`runtime_context/air_ticketing_desk/1.md`, findings R1-1, R1-2) | **KB-BIJECTION RED**, same atom class (`policy_kb/air_ticketing_desk/1.md`) | **PASS** |

**This difficulty's rendering does not pass the audit.**

## What holds

Everything the corpus was built to carry, it carries:

- the **problem tree** of both tasks is derivable from the published documents and the records alone.
  Task 0: release ← issue voucher ← {withhold penalty, return taxes}. Task 1: carry forward ← charge
  reissue fee. Every hop is **state-derived** — the blind audit read the prerequisite sentence, checked
  the records, found the state absent, and located the write that brings it about from the depended-on
  documents. No hop was pre-solved; the "do only the one thing the customer asked for" answer is
  excluded by visible sentence plus visible record in both tasks.
- all four **prerequisite sentences** stand verbatim, in the state form the source declares, in a
  document of the problem each blocks and in no other policy's document; no depended-on document
  discloses who waits on it.
- all 16 base policies clause by clause, all 11 declared retirements written as retired with none
  vanished and none invented, all 63 parameters across all 7 fare brands, both measures, all 6
  baselines and all 31 factor ladders — every tier, every threshold in figures, every part of every
  compound condition, including the tiers no task here triggers.
- all 6 task-tool contracts: names, arguments, argument classes, owners (`release_travel_credit_value_2b680572`
  and `reissue_lapsed_travel_credit_f544c035` user-owned, the other four desk-owned) and return shapes.
- **no route anywhere**: no other problem's tool name inside a blocked problem's documents, no
  aggregated chain, no dependency table or step list, no wrong-versus-correct contrast, no
  task-mirroring title, no factor document naming a customer's tier, no computation document hinting
  that a variation exists, and no task's world state written in as a policy fact.
- the two cross-product factors name their product officially and the records they read — **Travel
  Protection Plans** and **Hotel Rate Plans** — and both were reachable in the blind audit from the
  words the records themselves use.

## What fails, and why it fails as one defect

**The corpus never states the order in which declared factors enter a computation's result.** Each
factor document says what its tier does to a named quantity; each baseline states the assembly for the
unfactored case. Neither says where a factor lands once more than one bears on the same quantity. Three
of the six computations turn on that, and their scored numbers are consequently not entailed:

| computation | source assembles | corpus also supports | scored | blind |
|---|---|---|---|---|
| `air_ext_airline_tax_return` | holdback as a share of the tax lines **as posted** | holdback as a share of the amount returned ("held back **from the tax lines returned**") | 674.31 | 676.23 |
| `air_ext_credit_reissue_fee` | per-voucher multiple binds **before** the flat loading and surcharge | multiple taken on "the credit reissue fee" after both are added | 224.00 | 280.00 |
| `air_ext_lapsed_credit_carry_forward` | shares and uplifts on the **value standing**, fee and recovery deducted last, uplifts **summed** | the baseline's own "the largest lapsed credit **less the reissue fee charged**" then the shares; uplifts compounded as the sibling policy compounds them | 1185.59 | 1309.02 with the scored fee |

On task 0 the single tax-return divergence propagates into the voucher value (2363.55 / 2361.88) and
the value released (1129.78 / 1129.03), so three of four scored numbers are wrong for a reader who has
understood every rule correctly. On task 1 both scored numbers are wrong. Only
`air_ext_cancellation_penalty` (205.54) was reached exactly, and only because its baseline's numbered
steps happen to disambiguate where its additive loading sits.

The same prose is also used for two different conventions: `air_ext_cancelled_ticket_credit` composes
its uplift and offset as `(1 + u) * (1 - o)` while `air_ext_lapsed_credit_carry_forward` composes its
two uplifts as `(1 + u1 + u2)`, out of four factor documents whose wording is indistinguishable.

## Gates re-run on the final form

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/online_travel_agency air
  required quantitative keys=158  task_tools=6  prerequisite edges=4
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs,
         non-directory hubs, private compute-binding coverage, quantitative coverage, every
         prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route
         scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at
         the source's strength from the prerequisite sentence, the depended-on docs and the records, no
         state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py \
      env/env_0000_online_travel_agency/tasks/air_ticketing_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          25        0  True
1.json          16        0  True
TRACEABILITY OK
```

Both are green, as they were in the brief's snapshot. Neither covers the defect: `check_docs.py` proves
structure, coverage, leak-freedom and the verbatim carriage of every prerequisite sentence, and
`check_traceability.py` proves that every non-computed gold argument is copyable from reachable
context. Whether the prose fixes a discount base or an assembly order is exactly what the manual line
is reserved for.

## Coverage statement

This audit covers the one product this difficulty claims, `air`. Cross-product contradictions are
outside its detection range, suppressed structurally rather than proved absent — each document names
its own official product and each difficulty's policy content is single-homed. Base-type products
claimed by no difficulty are outside this skill's scope entirely.

## Policy-side notes (reported, not counted in the verdict above)

1. `air_cancel_refund`'s clause "Taxes and carrier fees that the airline itself refunds are returned
   even on a non-refundable brand, **and the agency service fee is not**" is not named in any
   `overwrite`, so the KB correctly carries it as in force (`cancellation_and_what_comes_back_21591d6c`
   §10), while the extended `club_service_fee_return` factor returns a share of that same fee on that
   same booking. `air_service_fee`'s parallel clause **is** declared retired; this one is not. The
   documents are faithful to both sides; the tension is source-layer.
2. Under the current render contract a factor document may not name the computation document or another
   factor, and the baseline must be silent about any variation — so there is at present no place for the
   assembly order to be written. This report names the semantics the corpus fails to carry and does not
   prescribe where they should live.

---

# revision_2 — closeout after the source correction and re-render

Corpus: `env/env_0000_online_travel_agency/docs/air/`, 74 documents,
`sha256sum *.json | sha256sum` = `e0f4d98d12ae3778c75c630103305fe53ec34351a866a6fc825038df6b4f4913`
(was `67feea6e…`). Source `air.extended.yaml` sha256/16 `375d1cd4ff2273f9` (was `671ea0fdcc5b7516`),
re-passed its own source-layer audit; `task_tools.py` unchanged at `02f3522169a00614`. Neither task's
world moved. This round is a verification re-audit, not a blind one: both worlds' numbers were already
in hand from round 1. The `revision_1` text of all five audit files is untouched.

## Three part-verdicts per task

| task | runtime blind audit | full-domain two-way scan | dependency-form scan |
|---|---|---|---|
| 0 | **PASS** — R0-1 closed (`runtime_context/…/0.md`, revision_2) | **PASS** (`policy_kb/…/0.md`, revision_2) | **PASS**, unregressed |
| 1 | **PASS** — R1-1 and R1-2 closed (`runtime_context/…/1.md`, revision_2) | **PASS** (`policy_kb/…/1.md`, revision_2) | **PASS**, unregressed |

**This difficulty's rendering now passes the audit.**

## How the round-1 RED was closed

The coordinator judged the round-1 finding a source-layer miss rather than a rendering one, on the
ground that the documents carried the charter losslessly and no re-render could publish an order the
charter never stated, and routed it back to the source. The charter now fixes the assembly in two
layers, and the corpus carries both:

1. **One shared composition convention**, in the rule of all six extended policies and rendered in all
   six computation documents: shares on one figure act one after another, each on the figure the one
   before it gives, never combined into a single rate; uplifts on one figure are combined into a single
   uplift and the figure is increased once by that total.
2. **Named stages** — "the penalty owed for one traveller" / "the penalty withheld", "the amount the
   tax lines are returned at", "the value the booking's lines leave", "the pool available to the
   traveller", "the tariff component" / "the fee charged", "the value standing" — with every one of
   the 31 factor documents naming the stage its outcome enters, in the baseline's own words for it.

All six scored values now derive from the published documents alone by a reader who applies every tier
correctly, and each reading that round 1 could not exclude is now excluded in terms:

| computation | derivation from the documents | scored | round-1 reading now forbidden by |
|---|---|---|---|
| cancellation penalty | 119.00 × 0.80 + 25.00 = 120.20; × 2 = 240.40; × 0.90 × 0.95 | **205.54** | "a share is taken on the flat cancellation penalty before anything is added to it in dollars" (excludes 212.79); "never combined into a single rate" (excludes 204.34) |
| tax and carrier fee return | 637.20 × 0.90 = 573.48; − 573.48 × 0.03; + 35.00 + 24.95 + 60.00 | **676.23** | "that share of the amount the tax lines are returned at, **the figure settled at the first stage**" (excludes 674.31) |
| voucher value | 3553.10 − 676.23 − 49.90 − 102.77 = 2724.20; × 1.02 × 0.85 | **2361.88** | — |
| value released | 2361.88 ÷ 2 = 1180.94; × 0.85; × 1.06; + 65.00 | **1129.03** | — |
| credit reissue fee | 75.00 × 1.60 × 2 = 240.00; + 60.00 + 20.00 = 320.00; × 0.70 | **224.00** | "added once for the booking and never once for each voucher" (excludes 280.00) |
| value carried forward | 3116.00 × 0.70 × 0.60 = 1308.72; × 1.10; − 30.00 − 224.00 | **1185.59** | "taken off last of all, after every share and every uplift" and "combined into a single uplift … increased once by that total" (exclude 1309.02) |

Task 0's scored values moved to the figures my round-1 blind derivation reached — 676.23 / 2361.88 /
1129.03 — after the conversion-holdback compute was changed to my reading. Task 1's are unchanged, so
there the documents had to move to the source's figures, and they did.

## Nothing regressed

Re-verified on the re-rendered corpus rather than carried over from round 1:

- **Retired surface** — the source now declares **13** distinct superseded base clauses; the corpus
  carries 12 retirement statements, one retiring two clauses together, so all 13 are borne, none has
  vanished and none is invented. (Round 1 had 12; my `revision_1` tables said "eleven", an undercount
  by one, corrected in the revision_2 sections rather than by editing that text.) The added clause is
  exactly the undeclared override `revision_1` reported as a policy-side note —
  `air_cancel_refund`'s "…and the agency service fee is not" — now declared and written as retired.
- **All 31 factor ladders** — every tier present, both limbs of every compound condition, every
  constant in figures, every boundary the right way round, no method tier compressed. The values that
  differ between policies (`long_lapse_months` 12 / 6; `long_membership_months` 120 / 60) are rendered
  correctly in each document, with no cross-contamination.
- **All four prerequisite sentences** — verbatim, one home each, in the hub of the policy each blocks,
  state form with connective and strength unchanged; no depended-on document discloses who waits on it.
- **Dependency-form** — six tool names each in exactly one document, its own policy's hub; exactly four
  "only after" sentences corpus-wide matching the four source edges; three same-form "Until"
  restatements in the documents that already carry their sentences; no route, checklist, roadmap or
  ordered step list; no cross-problem example or named mistake; all 74 titles general subjects, no task
  mirroring; no task world state written in as a policy fact.
- **The discrete topology survives the fix.** The thing most at risk was that stage prose would tip the
  solver off that factors exist. Tested directly: none of the six computation documents names a
  factor's subject, a tool, a policy or another document, and none contains "unless otherwise
  provided", "adjustments may apply", "set out elsewhere", "certain customers qualify" or an exception
  list. What they state is a convention with no content about which variations exist; a solver must
  still discover every factor from the customer's records.
- Base policies, 63 parameters across 7 brands, both measures and all six tool contracts unchanged in
  substance and still borne.

## The renderer's own closures

The render agent claimed it closed five ambiguities beyond my list. A renderer that settles what the
source leaves open is adding policy, so these were verified against the source rule text and the
compute rather than accepted. All five are set out with quotations in `policy_kb/…/0.md`, revision_2.
In summary: the voucher document's "and of no other line posted on it"; the release document's
"counted whatever term the voucher it raised runs for"; the penalty ceiling "applied to the penalty
withheld as it finally stands"; the "acting in turn … never netted" elaboration of share-then-uplift
sequencing in all six computation documents; and the retirement notice in
`cancellation_and_what_comes_back_21591d6c` §10 naming the subject matter where the live basis now
sits. **Each is entailed by the source and none moves an outcome away from the compute.** The second
is the one that deserved the sharpest look — no source sentence states it, and the sibling
carry-forward policy does filter issue lines by a retention window — but the source quantity it
renders is unrestricted and the compute applies no filter, so the exclusion is faithful.

## Gates re-run on the final form

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/online_travel_agency air
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs,
         non-directory hubs, private compute-binding coverage, quantitative coverage, every
         prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route
         scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at
         the source's strength from the prerequisite sentence, the depended-on docs and the records, no
         state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py \
      env/env_0000_online_travel_agency/tasks/air_ticketing_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          25        0  True
1.json          16        0  True
TRACEABILITY OK
```

## Coverage statement (unchanged)

This audit covers the one product this difficulty claims, `air`. Cross-product contradictions remain
outside its detection range — structurally suppressed, not proved absent. Base-type products claimed by
no difficulty are outside this skill's scope.

## Policy-side notes carried forward (reported, not counted in the verdict)

1. **The baselines now disclose that shares and uplifts may bear on the figure**, because the source's
   own rules do. Faithful rendering, and not a KB finding, but it changes what the fall-back
   counter-proof means: a reader of a computation document alone now knows adjustments of those two
   kinds can exist, though nothing tells them which. A design trade for the source layer to weigh.
2. **Two source names for one figure.** The voucher baseline calls its quantity "the fare, tax and
   service lines collected on the booking" while the `rework_carry_share` factor says its share is
   "added to the money collected". The mismatch is in the source's own rule and ladder and is carried
   faithfully; the outcome is unambiguous, since that computation builds only one such figure.
3. Round-1 policy-side note 1 (the undeclared override on the agency service fee) is **resolved** at
   the source. Round-1 policy-side note 2 (that the render contract left the assembly order nowhere to
   live) is **resolved** by the convention-plus-stages design, which puts it in the baselines without
   naming any factor.
