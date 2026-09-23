# KB-layer audit closing record — micro_market_desk (product: market)

Auditor: independent KB auditor — did not author the market corpus, did not judge this difficulty's policy
side, and saw no source-layer artifact until both blind answers were on disk.
Closed 2026-09-22. Revision 2 (round 1 recorded a `KB-BIJECTION RED` on both tasks; round 2 closed it).

## Part-verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 — settling an invoice, 4-deep chain with a 2-way fan-in | **PASS** | **PASS** (revision 2; RED at revision 1) | **PASS** |
| 1 — funding the next subsidy lot, 3-deep chain | **PASS** | **PASS** (revision 2; RED at revision 1) | **PASS** |

`audits/runtime_context/micro_market_desk/{0,1}.md` carry the frozen `blind_answer`, the appended
`gt_comparison` and a `revision_2`; `audits/policy_kb/micro_market_desk/{0,1}.md` carry `source_to_kb`,
`kb_to_source`, `bijection_verdict`, `dependency_form` and a `revision_2`.

## Closing checklist

- **Files correspond one-to-one with the tasks, and old revisions are traceable.** Two tasks, two
  runtime-context files, two policy-KB files. Revision 1 stands verbatim in every file; revision 2 is
  appended beneath it. No frozen `blind_answer` was rewritten to accommodate the re-rendered documents,
  and no round-1 verdict was edited — the RED and its evidence remain on record above the section that
  closes it. Every comparison section carries a PASS at its latest revision.
- **Blind before source.** Both `blind_answer` sections were written to disk before any `.extended.yaml`,
  `task_tools.py`, task-JSON GT field, hidden `meta` or raw `initial_state` was opened. The DB side of both
  blind audits was genuinely blind: every record came back from a share-finder call through the supplied
  tool-shaped path, never from `initial_state`. No recursive grep was allowed to reach `tasks/*.json` while
  a derivation was unfrozen. No `contamination_disclosure` was needed.
- **Every scored value derived blind matched the source** — task 1 exactly on all three (2633.70 /
  1249.22 / 19462.41); task 0 exactly on two of four (2.75 / 204.87) and one cent high on the other two
  (400.12 against 400.11, 704.87 against 704.86), a divergence traced entirely to a single half-cent tie
  whose published tie-break the source's own float arithmetic did not follow. Against the re-rendered
  corpus, all four task-0 figures now derive to the source's values from the published wording alone; the
  round-1 miss stands recorded as it was written. Every tool argument, every owner (two user-owned writes,
  five agent-owned across the two tasks), the write order and every fall-back baseline figure matched.
- **Both problem trees were derived from the visible materials alone**, hop by hop, with every hop
  **state-derived** and none pre-solved: task 0's four-edge tree (payment ← product settlement, payment ←
  outage credit, outage credit ← product settlement, product settlement ← catch-up drawdown) and task 1's
  two-edge chain (funding lot ← lapsed funding credit ← standing charge for the shut period). In both, the
  wrong answer "do only the one thing the customer asked for" is excluded by the blocked policy's own
  prerequisite sentence tested against a finder return — the August invoice carrying only its equipment
  line, the ledger carrying no service credit at all — and also produces a different number.
- **Every normative atom of the difficulty's structured source is entailed by the market docs.** All 7
  extended policies: 7 baselines carried complete with their own default constants and every product figure
  named; all **33** declared factors carried as whole ladders, every tier of every ladder exact, including
  the tiers neither seed hits; 11 base policies carried, with all **12** superseded clauses written as
  retired and no clause retired that the source did not declare. The one atom found unborne at revision 1 —
  the sentence that no portfolio discount is taken off a settlement raised for a period the market stood
  shut — is now carried verbatim and single-homed in the hub of the policy whose `rule` states it, and the
  retiring document's successor pointer lands on that hub.
- **Every prerequisite is carried in the source's own form.** All **6** declared edges: each
  `policy_source` sentence appears verbatim, exactly once, in a document of the problem it blocks — its hub
  — and in no other policy's document, in its declared `state` form with its ordering connective and
  strength intact. Each is resolvable at that strength from the sentence, the depended-on problem's own
  rules and the records. No `condition`, `resolved_by`, `fallback_reason`, `effect` or `gate` value appears
  anywhere in the corpus.
- **Nothing beyond those sentences is stated.** Each of the 7 task tool tokens appears in exactly one
  document, its own hub's invocation block. No document names another problem's tool, states a dependency
  or an order between problems, aggregates a chain, contrasts a wrong with a correct reading, or carries a
  title or opening that mirrors a task's situation. No factor document names which tier a customer sits on
  or writes a seeded row in as fact; no computation document hints that anything modifies it.
- **Re-checked after the round-2 re-render, not assumed.** Fifteen of the 67 documents changed and the
  source did not move. Re-run on the final form: prerequisite sentences 6/6 verbatim, once, in the blocking
  hub, in state form; tool tokens 7/7 single-homed; tier conditions **33/33** matching their ladders
  verbatim; the added-policy sweep still empty; no dependency-form regression in any changed document.

## Gates on the final form

Run by the coordinator on the re-rendered corpus and placed on record here; this auditor ran neither.

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0013_workplace_dining_and_catering_provider market
🔎 DOCS gate  product=market profile=extended docs=67
   roles={'hub': 7, 'factor': 33, 'facet': 9, 'policy': 11, 'baseline': 7}
   content[min/mean/max]=1367/1913/3031
  [PASS] mechanical gates ...
  [MANUAL REQUIRED] ...
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0013_workplace_dining_and_catering_provider/tasks/micro_market_desk
TRACEABILITY OK
```

Corpus audited at close: concatenated-document sha256 `eb54c3c3a6852f576a6c320135438f1013bd91845a249e9b03c4abbca0194d39`
(revision 1 audited `21c0987e869a8ef7370f3090dc8df8c3be888519e7ca653ba110daa84102bc75`).

## Open items carried to the policy side

These are reported, not fixed here, and none of them sets a KB verdict. Each is recorded with its evidence
in the per-task files.

1. **Rule text versus compute on the halved reading window.** The source computes
   `window_subsidy = RND(drawdowns_6m / 2, 2)` while neither `market_ext_period_settlement_true_up.rule` nor
   its `baseline.rule` says the halved figure is rounded. The documents render the rule text faithfully; the
   silence is the source's. Visible consequence on task 0's world: the published shelf value is 103.88 where
   the compute holds 103.85, harmless here but divergent by a cent on a world carrying the standard 100 per
   cent true-up share.
2. **The published even-cent tie-break versus `RND`.** Every computation document publishes "a figure
   falling exactly on the half-cent going to the nearest even cent"; `RND` is `round(float(x), 2)`, which
   resolved task 0's only tie (20.775) downward. The documents copy the source's wording, so this is a
   source-side inconsistency between a published tie-break and the arithmetic that implements it.
3. **`service_period` on the lapsed funding credit.** `task_tools.py` glosses it as "the settlement period
   the credit is allowed in", which on its face names the current period; the gold is the invoice's period.
   The document copies the contract verbatim, so the wording is flagged to the tool surface rather than
   rewritten in the KB.
4. **Drawdown record grain.** `market_subsidy_drawdown_rules` states a per-purchase grain held to a
   per-employee daily ceiling, and the corpus renders it faithfully, while task 1's 26 drawdown rows are
   kiosk-day settlements of 700–830 USD against a 9.00 USD printed ceiling. Recorded at source as an
   accepted residual; no scored value on either task turns on it.
5. **"The settlement charges" is never defined against the records.** The source binds every such quantity
   to `event_type='market_monthly_settlement_invoiced'` — equipment lines, monthly settlement charges and the
   restocking line alike — while its rule text says only "the settlement charges". The render layer may not
   close what the source leaves open.
6. **A base clause and an extended window unreconciled.** `market_service_credit_terms` measures outage
   "for that period"; the extended policy reads the hours over three, six or twelve months to the working
   day. The extended policy governs and no number turns on it.

## Residual recorded at revision 2, judged not RED

`valuing_a_missed_kiosk_discount_for_booking_be608a66.json` defines the mean drawdown but, since the
rounding sentences were narrowed to enumerations, no longer states that the mean is rounded; that rounding
now appears only in `reading_window_for_the_mean_kiosk_drawdown_ffd8b503.json`. Not classified RED because
the baseline calculation values the trip at the most recent drawdown and never takes the mean, so the
computation document remains self-sufficient for everything its baseline computes and the atom is borne by
the corpus. A world is nonetheless reachable — `trip_valuation_basis` tier 1 together with
`mean_reading_window`'s otherwise-tier — where a mean falling on a half-cent would move the booked discount
by a cent, so it is on record.

## Coverage statement

This skill is organised per difficulty and audits only the product this difficulty claimed. The sibling
products `pantry`, `vending`, `meal`, `cafe`, `banquet` and `catering` were readable on disk and were read
only where a market document sends the reader to one of them for a figure (the share of menu price printed
against a cafe service model, and the cafe ledger's own entries); they were never used as a criterion.
**Cross-product contradictions are outside this skill's detection range by design** — that is a stated
coverage gap, structurally suppressed by each document naming its own official product name and by this
difficulty's policy content being single-homed in `market`, not proved absent.
