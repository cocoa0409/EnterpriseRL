# KB-doc policy audit — season_pass_billing_desk (product `passes`) — closing record

Revision 1. Auditor independent of the render agent and of the policy-side auditor. Corpus audited:
`env/env_0004_ski_resort_operator/docs/passes/`, 72 documents, hash prefix `d0234491b0fee7c6`.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** |
| 1 | **KB-RUNTIME RED** — one scored value | **PASS** | **PASS** |

Files: `audits/runtime_context/season_pass_billing_desk/{0,1}.md` (blind answer frozen before any source
artefact was opened, then `gt_comparison` appended) and
`audits/policy_kb/season_pass_billing_desk/{0,1}.md` (`source_to_kb`, `kb_to_source`,
`bijection_verdict`, `dependency_form`, plus `policy_side_notes` on 0 and `divergence` / `flagged_item`
on 1).

## The one RED, in one paragraph

Reading only the published documents and the records, the resort credit issued on task 1 comes to
**302.90**; the scored value is **302.89**. The whole difference is one intermediate rounding: the
computation document says the figure "is rounded to the cent once at the end", while
`passes_ext_settlement_credit.compute` rounds the gross-times-scan-share product, the retained-charge
offset and the payout offset each to the cent before subtracting, and rounds again at the end. Everything
else on that task — the other two scored values, all three fall-backs, all sixteen factor tiers, the
problem tree, both edges and their order — was derived correctly and blind. The documents carry the
source's own sentence word for word, so this is not a rendering fault: it is a disagreement between the
charter's prose and the charter's compute, and it belongs at the source layer. The same class of drift
exists without effect on `passes_ext_carry_forward_fee`'s fee base.

## Closing checklist

- [x] Audit files correspond one-to-one with the tasks (0, 1), and old revisions are traceable (none yet).
- [x] Every prerequisite's prerequisite sentence stands verbatim, in its declared `state` form, in a
      document of the policy it blocks and in no other policy's — all four edges checked mechanically
      across all 72 documents.
- [x] Every hop is resolvable at the source's strength from that sentence, the depended-on documents and
      the records; all four hops were derived blind, and none was pre-solved.
- [x] Every declared factor's ladder is carried in full, every tier exact, in its own factor document,
      findable from the records its tier rests on — all thirty-two swept, including untriggered tiers.
- [x] No other problem's tool name, route or aggregated chain is stated anywhere: each of the six hidden
      tool names occurs exactly once, in its own facility document's invocation block.
- [x] Every retired clause is written as retired; none vanished; none retired that `overwrite` does not
      name; the unnamed clauses of the same base policies remain in force.
- [ ] **All three parts PASS on both tasks** — not met: task 1's runtime part is RED.
- [ ] `check_docs.py` and `check_traceability.py` re-run on the final form — deliberately not run. The
      brief directs this auditor to check and cite the supplied gate snapshot and to run neither, and
      the corpus is not final while the RED stands. The coordinator's snapshot is cited in
      `policy_kb/0.md` under "Entry conditions".

**The difficulty does not close out on this revision.** The rendering itself is sound — bijection and
dependency form pass on both tasks, and five of the six scored values plus all six fall-backs were
reproduced blind from the documents alone — but one task's visible materials do not entail the value the
source scores, and that must be settled where it originates.

## Observations carried forward (no verdict attached)

1. `passes_ext_cancellation_charge.factors[scan_component]`'s fall-through face reads
   `K('days_component_none')`, a constant no policy declares, while the compute, the compute basis and
   the factor's own baseline all use `scan_component_none`. **Graded documentary**, with reasons, in
   `policy_kb/1.md` under `## flagged_item`. A sweep of all thirty-two factors for undeclared `K(...)`
   references and for fall-throughs that disagree with their own baseline found **no other** such face.
2. "The cycle of the handling date" is used in two policies' prose and in two factor fall-throughs but is
   defined in no document; the compute realises it as one month. Not load-bearing on either task; it
   would be on an untriggered branch.
3. `Relief Against a Granite Ridge Restoration Charge for Refusals Recorded as an Expired Card` closes
   with a hypothetical that is structurally identical to task 0's actual configuration. It states nothing
   about any customer and meets no `KB-EXPLICIT RED` condition, so it is not a finding; it is flagged
   because a reader can take the answer off the example without doing the tier reasoning.
4. Two of task 1's factors depend on figures published in the protection product's corpus (the plan's
   excess and its season-benefit share). Both documents name that product officially and name the records
   they read, and the runtime retriever spans products, so the figures are findable; recorded because
   cross-product correspondence is outside this skill's detection range by construction.

---

# revision_2 — closing record

Round 2, 2026-09-17. Corpus `f82f1037d980a4e2` (revision 1: `d0234491b0fee7c6`), 72 documents.
Revision 1 above is preserved unchanged.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** (revision 1: KB-RUNTIME RED) | **PASS** | **PASS** |

**All three parts PASS on both tasks. The difficulty closes out.**

## Is the round-1 RED genuinely closed?

Yes, and as a class rather than as a case.

- **The value.** `settlement_credit_usd` is now 302.90 — the figure I derived from the documents in
  round 1 — on all three of: a document reader carrying exact decimal arithmetic, the evaluator's own
  IEEE-754 path, and the task's `expected`.
- **The method, which matters more.** The source removed `RND` from nine bindings and four factor
  baselines, so the compute no longer rounds where the prose says it does not. All six scored values of
  this difficulty were recomputed both ways and agree: 226.93, 44.10, 52.38, 127.57, 321.70, 302.90; all
  six fall-backs unchanged at 844.65, 49.00, 129.00, 260.00, 150.00, 1014.39.
- **Not luck.** The cent-fraction of every rounded figure sits far from the 0.5 tie where decimal and
  float could part — carry-forward 0.0685 away, settlement 0.4223, the other two exact.
- **The corpus moved too.** `settlement_credit_basis`'s example previously *demonstrated* an intermediate
  rounding ("599.60 when taken to the cent"), which under the stripped compute would itself have taught
  the wrong method. It is rebuilt on figures that divide exactly and now says "neither figure is rounded
  at those steps" and "once at the end, and only there". Two sibling examples were rebuilt the same way.
- **The whole rounding class checked both ways.** Eleven `RND` sites survive; ten are named in prose and
  the eleventh is provably inert (it rounds a minimum of quantities the harness already returns at the
  cent). Every rounding assertion left in the corpus maps to a surviving `RND`. Zero factor ladders in
  the source contain rounding language at all, which confirms on evidence — not on report — that the five
  riders removed from the corpus were render-layer additions and that the source clauses were always
  borne correctly.

## Has anything new been introduced?

Nothing that fails. Every worked figure in the corpus — **thirty-four arithmetic claims** — was recomputed
in IEEE-754 doubles rather than reasoned about, per the coordinator's warning about false rounding
illustrations. **Zero mismatches**, including the six claims that are non-dyadic in float
(1127.3999999999999 → 1127.40; 112.49999999999999 → 112.50; 109.64999999999999 → 109.65; 473.13000000000005;
495.6600000000001; 160.65). None of them is asserted as a rounding, which is what makes them safe: the
corpus no longer claims a rounding at any step the compute does not perform, so no illustration can be a
half-cent case.

The one genuinely new claim — "the cycle of the handling date, **which is the one whole month ending on
that date**" — was checked against the harness (`within_months=1` is implemented as
`0 <= MONTHS(date, NOW) < 1`), not against the wording. It is exact, it reuses the corpus's existing
idiom for `within_months=3`, and it adds nothing to the source's semantics. **Supported.**

## Has anything regressed?

No. Re-verified mechanically on the new corpus: four prerequisite sentences verbatim, in `state` form,
each in exactly one document and that document the blocked policy's own hub; six tool names, one
occurrence each, each in its own invocation block; every retired clause still written as retired and none
added; zero cross-document title references; zero undeclared `K(...)` in any of the thirty-two ladders;
no route, chain, aggregation, added procedure or world-state leak. Both task chains re-run end to end
through the tool harness with the derived figures and land in the right terminal states.

## Observations from revision 1: all four closed

| Round-1 note | Status |
| --- | --- |
| Carry-forward fee base: prose/compute rounding drift | **Closed** — `RND` stripped, rider removed; both sides now carry 123.858 |
| Settlement drift (the RED) | **Closed** — see above |
| "The cycle of the handling date" undefined | **Closed where normative** — pinned in the two computation documents; correctly left unpinned in the two factor fall-throughs |
| `days_component_none` stale face | **Closed** — now `K('scan_component_none')`; fresh sweep finds no other |

`F0-8` and `F1-16`, left open at the source layer, do not reach the corpus: I swept the published
documents for 123.86 and for every superseded worked figure (115.53, 111.95, 756.64, 599.60, 1366.86,
302.89) and none occurs, and I established the same conclusion independently by recomputing all
thirty-four claims. **The corpus states no figure that the stripped bindings no longer produce.**

## Two things recorded for the record, neither a verdict

1. **The change report was inaccurate about two documents.** It reported eight documents edited plus the
   two observation fixes, and stated that the "cycle" pinning was *deliberately not* applied to
   `late_fees_gathered_window` or `uncured_refusal_count_window`. Thirteen documents differ, and those
   two are among them: their rule text was correctly left unpinned, but their worked examples were
   rewritten to use the pinned phrase. The render agent's stated reasoning — that a factor fall-through
   must not restate the baseline's default — is sound and I endorse it; the discrepancy is in the report,
   not in the reasoning. I found it by diffing rather than by reading the report, and the next reviewer
   should do the same. Judged on the merits, the edits are an observation and not `KB-EXPLICIT RED`: the
   phrase locates a fee in time on a hypothetical account, states no rule and points at nothing.
2. **The property that failed in round 1 has no mechanical gate.** "The documents and the compute agree"
   is invisible to `check_docs.py`, which cannot see the compute, and to `check_compute.py`, which cannot
   see the documents. On this difficulty it is held only by this audit having recomputed both sides
   independently. The source auditor's disclosure — that its "independent derivation" `eval`'d the very
   compute it was checking — is the same gap seen from the other side. Nothing in this revision leans on
   the source's round-5 PASS; a coverage observation about the pipeline, not a defect in this corpus.

## Closing checklist

- [x] Audit files correspond one-to-one with the tasks; revision 1 preserved verbatim; revision 2 appended.
- [x] Every prerequisite sentence verbatim, in its declared `state` form, on the blocked side only.
- [x] Every hop resolvable from that sentence, the depended-on documents and the records.
- [x] Every declared factor's ladder carried in full, every tier exact, findable from the records.
- [x] No other problem's tool name, route or aggregated chain anywhere.
- [x] Retired surface correct on all three tests.
- [x] Documents and compute agree on every figure and every rounding, in both directions.
- [x] All three parts PASS on both tasks.
- [x] `check_docs.py` and `check_traceability.py` on the re-published corpus: `DOCS OK`,
      `TRACEABILITY OK` — coordinator's snapshot, cited per the brief, which directs this auditor not to
      re-run them. `check_compute.py` returns `COMPUTE OK` with both tasks matching, cited as a machine
      cross-check only.

**This difficulty's rendering passes the audit at revision 2.**
