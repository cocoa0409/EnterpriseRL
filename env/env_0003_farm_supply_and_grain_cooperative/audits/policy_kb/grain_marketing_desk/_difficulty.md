# KB-doc policy audit — closeout for grain_marketing_desk (product `grain`, Grain Marketing Contracts)

Auditor independent of the render agent and of the policy-side auditor. Both blind answers were
frozen to disk before any source-layer read; no blind answer was altered afterwards. This is
revision 1 — there is no earlier `policy_kb` or `runtime_context` file for this difficulty.

Corpus audited: `env/env_0003_farm_supply_and_grain_cooperative/docs/grain/`, 73 documents,
sha256 over the sorted per-file sha256 list =
`37a69ea7bedb4de4a13fdd2df2cc6a6ef61565986f68dafd0d56604a347aaf19`.

DB read exclusively through tool-shaped calls against the real engine (the supplied `runtime_view.py`
access path); `initial_state` was never read as a document. The blind stage on the DB side is
therefore **clean**.

## Three part-verdicts per task

| task | runtime blind audit | full-domain two-way scan | dependency-form scan |
|---|---|---|---|
| 0 | **KB-RUNTIME RED** (`runtime_context/grain_marketing_desk/0.md`) | **KB-BIJECTION RED**, findings F2 and F4 (`policy_kb/grain_marketing_desk/0.md`) | **KB-EXPLICIT RED**, finding F3 |
| 1 | **PASS** (`runtime_context/grain_marketing_desk/1.md`) | **PASS** | **PASS** |

**This difficulty's rendering does not pass the audit.**

## What holds

- The **problem tree** of both tasks is derivable from the published documents and the records alone,
  and both trees came out of the blind audit identical to the source's `prerequisite_closure`.
  Task 0: release the payment ← {book the carry, put the roll through}, and the roll ← restate the
  balance. Task 1: buy out ← register the amendment ← countersign. Every one of the five hops is
  **state-derived**: the blind audit read the prerequisite sentence, checked the records, found the
  waited-on state absent, and located the write that brings it about from the depended-on documents.
  No hop was pre-solved, and in both tasks the wrong answer "the customer asked for one thing, do that
  one thing" is excluded by a visible sentence read against a visible record.
- All **five prerequisite sentences** stand verbatim, in the state form the source declares, each in a
  document of the problem it blocks and in no other document of the whole scenario; no depended-on
  document discloses who waits on it. `condition`, `resolved_by`, `effect` and `fallback_reason`
  appear nowhere.
- All **twelve base policies** clause by clause; all **twelve declared retirements** written as
  retired, with none vanished and none invented, and every unnamed clause of those policies still
  carried in force.
- All **seven baselines** with every default rendered, and all **thirty-four factor ladders** — every
  tier, every threshold in figures, every part of every compound condition, every method tier's
  operation and window — including the tiers neither task triggers.
- All **fifty-eight variant parameters plus the entry gates across the seven marketing programmes**,
  checked cell by cell against the thirteen catalogue documents: every figure matches.
- All **seven task-tool contracts**: names, arguments, formats, owners
  (`execute_futures_month_roll_2054762f` and `execute_contract_buyout_11de6ced` customer-run, the
  other five desk-run) and return shapes, verified against `task_tools.py` and against the schemas the
  runtime returns on `unlock`.
- The **eight cross-product factors** name their product by its official name — Grain Storage and
  Conditioning Agreements, Membership and Patronage Equity, Crop Input Purchasing Accounts — and the
  kinds of record they read, and every figure they send the reader to fetch was found in that
  product's corpus.
- **No route anywhere**: no other problem's tool name inside a blocked problem's documents, no policy
  id, no aggregated chain, no dependency table or step list, no wrong-versus-correct contrast, no
  task-mirroring title or opening, no factor document naming a customer's tier, and no task's world
  state or scored value written into any document.

## What fails

**One defect, with three faces.**

Two factor ladders — `volume_free_days` (the free days before the carry runs) and
`crop_year_roll_allowance` (the bushels rolled free) — are gated on *"the net bushels applied to the
contract"*. The source binds that phrase to **every** `grain_delivery_applied` row; the corpus, in
`striking_the_balance_still_owed_512f95c7.json`, adds a gloss the source does not carry —
"…whatever the disposition, **meaning the loads applied to the contract and the loads run straight
through together**" — which defines the same phrase as a set that **excludes** the loads run straight
through. On task 0's contract the two readings differ by 3,986.03 bushels and two loads, which is
exactly the difference between the first and the second band of both ladders.

| face | verdict | where |
|---|---|---|
| The visible materials do not single out one reading, so a careful reader books a carry of 180.39, a roll charge of 808.64 and a payment of 5,416.92 against scored values of 90.19, 691.45 and 5,624.30 — three of task 0's four scored numbers | `KB-RUNTIME RED` | `runtime_context/grain_marketing_desk/0.md` |
| The gloss, and the hedge "where it arises at all" beside it, are two clauses the source does not carry | `KB-BIJECTION RED` (F2) | `policy_kb/grain_marketing_desk/0.md` |
| The hedge tells the reader, from inside a baseline computation document, that a variation on a nil default exists — the one thing the discrete topology reserves to the customer's records | `KB-EXPLICIT RED` (F3) | same file, `dependency_form` |

**One further bijection gap, unrelated and not affecting either task's numbers.**

| finding | verdict | where |
|---|---|---|
| F4 — the crop-year window ("1 September through 31 August", the source's `measures` block) is borne by no document, although two documents make a per-crop-year roll count normative; likewise the "still open" branch of the unpriced-carry-days measure | `KB-BIJECTION RED` | `policy_kb/grain_marketing_desk/0.md` |

## Policy-side notes (reported; they do not change this skill's verdict)

- **The deeper cause of the main defect is on the policy side**: "applied to the contract" is bound to
  `disposition='contract_application'` in `grain_ext_open_balance_reconciliation.compute` and to every
  delivery row in `grain_ext_delayed_price_carry_charge.compute` and
  `grain_ext_futures_month_roll_charge.compute`, and neither ladder's words determine which.
- **"Struck in whole bushels" has no rounding mode** in any source rule or any document; only the
  `compute` expressions `RND(…, 0)` pin it. It bites in both tasks (task 0's balance is 19,750.61,
  task 1's restated commitment 15,136.552) and in task 1 it moves the scored buyout charge between
  830.40 and 830.56.
- `money_released_on_a_settlement_statement` says "rounded to the cent once at the end", verbatim from
  the source, while the source's `compute` rounds each of six deductions individually first.
- `capital_retain_and_the_members_equity_position` clause 1 is the source's `replaced_by` verbatim,
  while the source's `compute` guards it with `equity_ceiling > 0`; on a class whose ceiling is 0.00
  the two diverge completely.
- `closing_out_bushels_already_sold` keeps in force a clause about "the loss" whose defining sentence
  the source retired and whose replacement carries no market-loss term.
- Three catalogue charges are normative and no write in this difficulty books them: the setup fee at
  countersigning, the amendment fee, and the per-bushel extension charge.
- `rolling_rather_than_defaulting` reproduces the retired charging sentence in full and separately
  states its first half (the carriage of the spread) as clause 3 in force; the carriage is
  independently supported by the surviving `params.spread_treatment` and by in-force clause 4, so it
  is not recorded as a retired clause restated in force, but a reader meets the same words on both
  sides of the line.

## Coverage stated plainly

This audit covers the one product this difficulty claims, `grain`. Cross-product contradictions are
outside its detection range; where a grain factor sends the reader to another product's catalogue the
figure was fetched and checked to exist, but the sibling product's own corpus was not audited and was
never used as a criterion. Products claimed by no difficulty are outside this skill's scope
altogether.

## Gates

The documents were not edited by this audit, so the gate snapshot supplied with the brief stands as
the record for the final form (per the brief, the auditor runs neither gate):

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/farm_supply_and_grain_cooperative grain
🔎 DOCS gate  product=grain profile=extended docs=73 roles={'factor': 34, 'facet': 13, 'policy': 12, 'hub': 7, 'baseline': 7} content[min/mean/max]=1097/1834/3247
   required quantitative keys=143  task_tools=7  prerequisite edges=5
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0003_farm_supply_and_grain_cooperative/tasks/grain_marketing_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          31        0  True
1.json          18        0  True
TRACEABILITY OK
```

The `[MANUAL REQUIRED]` line is precisely what this audit discharges, and it does not come back
green for task 0.

---

# revision_2 — closeout for grain_marketing_desk, round 2

**2026-09-18.** Re-audit after the source was fixed and re-audited twice and the corpus re-rendered
from it. Revision 1 above is preserved untouched, including both blind answers and both round-1
comparisons.

Corpus re-audited: `env/env_0003_farm_supply_and_grain_cooperative/docs/grain/`, 73 documents,
sha256 over the sorted per-file sha256 list = `7ea298e6f6a18e70dfedbc2c0b6cc62752cba4814fe40fba018fc7486f3b6930`
(round 1 audited `37a69ea7…`). Source at `grain.extended.yaml` sha256[:16] = `bb74943d5c75f66e`,
`task_tools.py` = `79bf2d18ae73a423`, both as the brief states. DB again read only through tool-shaped
calls against the real engine; both worlds and both `frozen_time`s are unchanged, and no scored value
has moved (task 0 still 19751.0 / 90.19 / 691.45 / 5624.3; task 1 still 19834.0 / 15137.0 / 830.56).

**Round 2 is not a blind audit and is not recorded as one** — the blind stage is not repeatable once
GT has been seen. It is item-by-item verification.

## Three part-verdicts per task, round 2

| task | runtime part | full-domain two-way scan | dependency-form scan |
|---|---|---|---|
| 0 | **PASS** (was KB-RUNTIME RED) | **PASS** (was KB-BIJECTION RED: F2, F4) | **PASS** (was KB-EXPLICIT RED: F3) |
| 1 | **PASS** (unchanged) | **PASS** (unchanged) | **PASS** (unchanged) |

**This difficulty's rendering passes the audit.**

## Each round-1 RED, verified closed

**F1 — the decisive check.** I re-derived all four of task 0's scored arguments from the published
prose and the records alone, taking each phrase at the extension the document itself now states, and
got **19,751 / 90.19 / 691.45 / 5,624.30** — every one matching GT. Task 1 re-derived unchanged at
**19,834 / 15,137 / 830.56**. The fork is gone: the free-days and roll-allowance ladders now read
"the net bushels of **every load standing against the contract, whatever the disposition**", which is
16,954.54 across nine loads, so both reach their first band, and the corpus no longer supplies a
gloss pointing the other way.

**F2 — closed.** Exact-string search over all 73 documents returns **0 hits** for
"meaning the loads applied to the contract and the loads run straight through together" and **0 hits**
for "where it arises at all". The base sentence now stands verbatim from
`grain_ext_open_balance_reconciliation.rule`. Nothing in the corpus defines either phrase; instead I
checked **fifteen** points of use, document by document, against their `compute` bindings — narrow at
three (balance credit components, freight differential, buyout administrative fee), broad at twelve —
and every one matches. No bare use survives ("bushels applied": 0 hits).

**F3 — closed.** The balance computation document now states the conditioned handling shrink flat —
"No handling shrink is taken on conditioned loads" — with no hedge and no base beside it, in the same
register as the six other baselines; the hedge scan over all seven comes back clean. The base
sentence moved verbatim into `handling_shrink_on_conditioned_loads`, which also closes the secondary
note that the factor never pinned its own base.

**F4 — closed.** The crop-year window is carried as clause 3 in force of
`rolling_rather_than_defaulting`, beside the ceiling it bounds, with a boundary illustration; the
lesser half is carried as clause 2 of `carrying_bushels_in_the_unpriced_position`, worded to state
only where the count ends, naming no anchor and no day-zero convention, so it does not revive that
policy's retired anchoring clause — which still stands intact in the same document's retired block.

**The non-RED observation of round 1 — closed.** `loss_multiplier_and_what_was_delivered` no longer
borrows the 0.16 delivered release rate from another factor's ladder; its illustration now uses 0.20,
a programme default penalty, which is the figure the buyout baseline itself names.

## Nothing that passed has regressed

Verified mechanically over the re-rendered corpus: all **five** prerequisite sentences verbatim and
each in exactly one document scenario-wide, on the blocked side, with no depended-on document
disclosing who waits on it; all **seven** tool names each in exactly one document, its own hub's
invocation block; **no** policy id anywhere; **no** task world state or scored value anywhere (28
identifiers and figures searched); all **fourteen** declared retirements present, each in the
document bearing its base policy, each inside a "no longer in force" block, with **no undeclared
quotation** anywhere; all **thirteen** catalogue tables checked cell by cell against
`variants[].parameters` and `entry_gate` with **0 numeric mismatches**; all **twelve** base-policy
clause inventories intact apart from the three intended changes; **no** route, pointer,
mistake-framing, customer-tier language or task-mirroring title.

## The source-side truncation flagged in the brief

`grain_ext_settlement_payment_release.compute_basis.worst_damage_pct` does truncate its own rule
sentence in the source. **Confirmed: the reading is intact for a solver.** The whole sentence survives
in the policy's `rule`, in the opening of `damage_allowance_struck_on_a_statement` ("…and the
allowance is the rate of the lowest band whose ceiling the reading does not exceed"), in that
document's four-band table and edge-reading section, and independently in the base grade policy
document. The band selection is over-determined on the visible surface. Recorded as a source-side
known issue with no document consequence.

## Policy-side notes at their current standing

- **P1** (no rounding mode on "struck in whole bushels") — **closed**; all five striking sentences now
  pin it, each rendered with a half-bushel boundary illustration.
- **P2** (one rounding point or seven on the payment) — **closed**; the settlement baseline now reads
  "each charge and each allowance is worked to the cent as it is formed, and the money released is
  rounded to the cent once when they are brought together", matching the compute.
- **P3** (the class ceiling at zero) — **closed**; the retain tier now requires that the class posts a
  maximum at all, with a reading section spelling out the two limbs.
- **P4** (an in-force clause about a retired quantity) — **substantially closed**; the fallen-market
  clause is itself retired and its replacement rendered. Residual: `closing_out_bushels_already_sold`
  clause 4 still says "on top of the same market loss", an in-force sentence of `grain_buyout` the
  source has not retired. Faithfully carried; decides nothing.
- **P5** (one term, two extensions inside one YAML) — **closed**; two self-defining phrases, every use
  tagged, the two machine spellings of the broad phrase unified into one unfiltered aggregate with no
  figure moved.
- **P6** (three catalogue charges that no write books) — **unchanged and still recorded**.
- **New residual, bounded and quantified.** Four load- and ticket-counting *conditions* remain
  untagged in the source and so in the documents: the elevation allowance (bound narrow), the
  conditioned handling-shrink condition, the hold shrink and the short-crop retention (all bound
  broad). I checked each against both worlds under **both** readings: none moves a figure, because
  task 0's two straight-through tickets were received at the contracted facility and are neither wet
  nor damp, and task 1 has no straight-through ticket at all. The elevation case is additionally
  resolved by the baseline it modifies, which now names its credit component in the narrow phrase.
  The documents carry the source's words exactly, so this is not a KB finding; it is recorded so that
  a later world with a wet straight-through load, or one received elsewhere, is known to touch it.

## Closing checklist

- Audit files correspond one-to-one with the tasks; revision 1 is preserved in full and was not
  rewritten; every comparison section carries a verdict for its round.
- Every normative atom of this difficulty's structured source is entailed by its product's documents,
  with nothing unborne, nothing borne with changed meaning and no claim from outside the source.
- Every prerequisite's sentence stands verbatim, in its declared state form, in a document of the
  policy it blocks and in no other; every one of the five hops is resolvable from that sentence, the
  depended-on documents and the records.
- Every declared factor's ladder is carried in full, every tier exact, in its own factor document,
  findable from the records its tier rests on.
- No other problem's tool name, route or aggregated chain is stated anywhere beyond those sentences
  and their same-form equivalents.
- Gates on the final form, supplied with the brief (the auditor ran neither): `DOCS OK` with
  `docs=73 roles={'factor': 34, 'facet': 13, 'policy': 12, 'hub': 7, 'baseline': 7}`,
  `required quantitative keys=143  task_tools=7  prerequisite edges=5`,
  `content[min/mean/max]=1097/1925/3247`, all mechanical gates `[PASS]`; and `TRACEABILITY OK`
  with task 0 copied 31 / missing 0 and task 1 copied 18 / missing 0. The `[MANUAL REQUIRED]` line is
  what this audit discharges, and at revision 2 it comes back green for both tasks.

**Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, for both
tasks. This difficulty's rendering passes.**
