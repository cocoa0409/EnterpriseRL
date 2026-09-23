# KB-doc policy audit — difficulty closing record: `trade_in_appraisal_desk` (product `tradein`)

## revision_1

Auditor: independent KB auditor, fresh context, never previously exposed to this difficulty's policy, its
GT or the source-layer audit. Per-task files:

- `audits/runtime_context/trade_in_appraisal_desk/0.md`, `…/1.md` — blind answer (frozen first) + gt_comparison
- `audits/policy_kb/trade_in_appraisal_desk/0.md`, `…/1.md` — source_to_kb, kb_to_source, bijection_verdict, dependency_form

Corpus audited: 57 documents under `env/env_0005_consumer_electronics_retailer/docs/tradein/`, hash
`sha256sum docs/tradein/*.json | sha256sum` = `5471a205908fdbc8e54d4461d2af45934c42138a77d76a99ddd846ab40207730`.
Topology from `meta`: 13 `policy` + 10 `facet` + 5 `hub` + 5 `baseline` + 24 `factor`.

---

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Task verdict |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | **`KB-EXPLICIT RED`** (D2) | **`KB-EXPLICIT RED`** |

**The difficulty is not closed out.** Closing out requires all three parts to PASS on every task.

### The one red light

**D2 — `renew_batch_credit_amount_basis_bc847570`, the computation document of
`tradein_ext_batch_settlement_credit`, publishes the tier figures of two of its own factors.** It carries
"**Amounts named in this basis.** The delayed appraisal allowance is 60.00 USD. The late appraisal allowance
is 140.00 USD. The uncertified device holdback is 25.00 USD. The certified device holdback is 8.00 USD",
while the same document's basis paragraph says "no transit settlement, no late appraisal allowance, no
protection premium and no erasure holdback are counted". None of the four is a default of this basis — the
default for both slots is nothing — so the block hands a reader the two-tier shape and the exact value set
of `late_appraisal_allowance` and `erasure_certificate_holdback` without their having looked at a record.
Both tiers bite on task 1. Root cause on the policy side:
`tradein_ext_batch_settlement_credit.baseline.params` declares four factor-tier constants as the baseline's
own defaults, and `check_docs.py` (lines 568–575) then requires them in the computation document; the other
four policies of this difficulty declare `baseline.params` correctly and their computation documents are
clean. Full write-up, evidence and the reasoning in `policy_kb/trade_in_appraisal_desk/1.md`,
`dependency_form` D2.

---

## Rulings on the three claims the renderer asked to have tested

### Claim 1 — the prose-versus-compute divergence on the pallet count: **sound, with a source-side residue**

The renderer reported that one factor's rule says a pallet count is "counted up to the nearest half pallet"
while the structured compute is `int(raw_pallets) + 0.5`, that these diverge above a half pallet (1.625 →
2.0 by the prose, 1.5 by the compute), and that it carried the source phrase but sharpened it to the
computation's reading.

I derived the number from the published prose alone and froze it before opening any formula. **The published
prose yields a definite figure, and it is the compute's figure.** The tier as published reads:

> "**Where the run leaves a part pallet and every freight charge raised on the agreement stands settled or
> waived** the pallets charged for are counted up to the nearest half pallet: the whole pallets the run fills
> are charged for together with a further half pallet for the part, whatever the size of the part."

The colon-expansion is operative and exhaustive — whole pallets plus one half, "whatever the size of the
part" — so 1.625 gives 1 + 0.5 = 1.5, and the document's own worked comparison prints "1.5 pallets" for
exactly that input. Revealed afterwards, the compute is
`(int(raw_pallets) + 0.5) if (part_pallet == 1 and freight_outstanding <= 0) else …`. The two agree. So this
is **not** a render-layer defect, and it is not the worse case either: the prose is definite, not
indeterminate.

What remains is that the label the render carried from the source ("counted up to the nearest half pallet")
disagrees with its own gloss for any part above a half pallet — for 1.625 the label alone would give 2.0.
That wording is the source's ladder text (`pallet_count_basis`, tier 2, `method`), carried faithfully, so I
record it as a **policy-side note** and it does not change this skill's verdict. The tier is untriggered in
both tasks: task 0's collection account stands 85.00 unsettled, which selects the "up to the whole pallet"
tier, and task 1's policies have no pallet count. No scored number turns on it. Recorded at
`policy_kb/trade_in_appraisal_desk/0.md`, `dependency_form` D1.

### Claim 2 — "the ordering sentence appears nowhere; the content was carried distributively": **first half false, second half upheld**

**First half: false, and the evidence is verbatim text.** Each extended policy's `rule` contains a sentence
enumerating the factor effects in order. Two of the five are published **verbatim in the computation
document**:

- `renew_buyback_run_unit_count_basis_14bbe607`: "**The order the figure is reached in.** The units one
  collection may carry are worked out in one order and no other. The machines the agreement covers are first
  capped at the batch allowance the carrier books. The machines held back for a claim and the machines held
  back while a service crew is attending are then taken off that capped figure, leaving never fewer than
  none. The share the run lifts is applied last to what that step leaves, that share being taken of it, and
  the result is rounded down to a whole machine."
- `renew_revised_offer_amount_basis_e684148d`: "**The order the figure is reached in.** The revised offer is
  worked out in one order and no other: it starts from the figure the gap treatment reaches, the cover
  deduction is then taken off that figure, and the ageing markdown is applied last to what that step
  leaves…"

Both are word-for-word the ordering sentences of their policies' `rule` (plus a gloss), and both go beyond
their own `baseline.rule`, which names none of those quantities. In the other three policies the same
enumeration is inside `baseline.rule` itself and so appears in the computation document by requirement. The
distributive carriage the renderer described — each factor document naming the base its effect acts on and
its connective — is present in some factor documents (for instance "the member collection relief of 55.00
USD is taken off the charge") and absent in others ("The share the run lifts follows the room the run has
left on the quote" names no base), and it is not what carries the order: the order is carried centrally, in
the computation document. So the deviation the renderer reported did not happen, and the report of it was
inaccurate.

**Is that a defect? No — and I say why, so the judgement can be re-checked.** The framework homes the
assembly of the result in the computation document: this skill's own forward scan makes "an assembly step
moved into a factor document" a bijection failure, and three of this difficulty's five policies put the
enumeration inside `baseline.rule` themselves. Naming each addend slot and declaring it at its default is
therefore the corpus's uniform and mandated form, not an added route. Calling these two paragraphs a route
would be re-judging the design topology rather than this render's translation of it. I record them as
**observations** with the evidence, at `policy_kb/…/0.md` D3 and `policy_kb/…/1.md` D3, and note that this
is the place where a solver most easily learns that variations exist without consulting the records.

**Second half: upheld. The fall-back test works on all five computations.** I masked every factor document
and recomputed from the computation document plus the records alone. Each of the five computation documents
yields a **definite** number, and each differs from the full-corpus number:

| Computation | Fall-back (all factor documents masked) | Full corpus |
| --- | --- | --- |
| machines one collection run carries (task 0) | **34** | 12 |
| the collection charge (task 0) | **230.70 USD** | 240.00 USD |
| the revised offer (task 1) | **5100.00 USD** | 4822.40 USD |
| the amount credited (task 1) | **5100.00 USD** | 4342.40 USD |
| machines the first wave carries (task 1) | **46** | 5 |

And the union of the corpus yields exactly one reading: every scored value and every argument in my frozen
blind answer matched GT (12 / 2026-09-22 / 240.00; 4822.40 / condition_worse_than_declared / 4342.40 /
business_invoice_credit / 2026-12-17 / 5 / 2026-10-01), as did both problem trees, their directions, their
handling orders and their owners.

One observation on the fall-backs: the computation document
`renew_buyback_collection_charge_basis_1c8abc7f` builds its worked figure on "12 machines" and a freight fee
of "145.00 USD" — this task's own run count and this programme's own fee — and prints 230.70 USD, which is
precisely task 0's fall-back. It leaks no scored value, but it hands the wrong number over ready-computed on
the real inputs. Recorded at `policy_kb/…/0.md`, `kb_to_source` K2.

### Claim 3 — does the "Amounts named in this basis" block weaken the computation document's required silence? **Yes**

That is finding D2 above, and it is this audit's only red light. My ruling in short: the block does weaken
the silence, and the justification that "the gate requires a policy's own declared defaults in its
computation document" does not cover it, because these four constants are **not** this baseline's defaults —
its default for both slots is *nothing*, which the document already states in words. The gate does force
them, but only because `baseline.params` mis-declares them; that is a policy-side defect propagating into
the KB through a gate that faithfully enforces the declaration. I name the statement and the semantics it
carries and arrange no fix; in particular I do not suggest deleting the block, since as the source currently
declares it that would put the corpus in breach of the gate.

---

## Closing checklist

| Item | Status |
| --- | --- |
| Audit files correspond one-to-one with the tasks (0, 1), in both `runtime_context/` and `policy_kb/` | yes |
| Blind answer frozen to disk before any source-layer artefact was opened, with hash and forbidden list recorded | yes, both tasks |
| `blind_answer` unmodified after the reveal | yes, both tasks |
| Old revisions preserved | no prior revision exists; this is revision 1 |
| `source_to_kb`, `kb_to_source`, `bijection_verdict`, `dependency_form` frozen separately | yes, both tasks |
| Every normative atom of the difficulty's structured source entailed by the product's docs | yes — 13/13 base policies homed; all 8 `overwrite` entries written as retired with surviving clauses kept in force; all 5 `baseline.rule`s complete in their computation documents; all 24 factor ladders complete, every tier exact; all six programmes' `parameters` exact across all 10 facet schedules |
| No claim from outside the source | none found; the sweep for added confirmations, reviews, notifications and failure procedures returns nothing |
| Every prerequisite's `policy_source` verbatim, in its declared form, on the blocked side and nowhere else | yes — 3/3 edges (`grep -rl` over `docs/` returns exactly one document each, each the blocked policy's hub or fragment) |
| Every hop resolvable from the sentence, the depended-on documents and the records | yes — all three hops marked **state-derived** in the blind answers, with the sentences and query returns recorded |
| No other problem's tool name, route or aggregated chain anywhere | none — each of the 5 task tool names occurs in exactly one document, its own hub; no dependency table, checklist, roadmap, cross-problem step list or chain-walking example exists |
| Every declared factor findable from the records its tier rests on | yes — each of the 24 reached from record vocabulary alone; cross-product factors name the product by its official name (`Northbeam ShieldCare Protection Plans`, `Northbeam TechWorks Installation and Repair`, `Northbeam Circle Membership`, `Northbeam Purchase Orders and Fulfilment`, `Northbeam Returns and Restocking`, `Northbeam Store Credit and Financing Accounts`) |
| Computation documents silent about variation | **4 of 5** — `renew_batch_credit_amount_basis_bc847570` is not (D2) |
| `check_docs.py` / `check_traceability.py` on the final form | the gate snapshot supplied with the brief is on record verbatim in `policy_kb/trade_in_appraisal_desk/0.md`; the commissioning agent ran both and this auditor ran neither, as instructed. They must be re-run on whatever final form follows from D2 |

## Policy-side notes (reported, not re-judged, and not affecting this skill's verdict)

1. **`tradein_ext_batch_settlement_credit.baseline.params`** lists four factor-tier constants
   (`delayed_allowance_usd`, `late_allowance_usd`, `uncertified_device_holdback_usd`,
   `certified_device_holdback_usd`) as the baseline's own defaults, although that baseline counts neither an
   allowance nor a holdback. This is the root cause of D2.
2. **`pallet_count_basis` tier 2** describes as "counted up to the nearest half pallet" a method that is
   `int(raw_pallets) + 0.5`; the label and the method disagree for any part above a half pallet.
3. **`declared_value_cover_uplift`** and **`transit_cover_wave_basis`** state the start anchor of "how long
   the quote has run" but not the end anchor, which the compute fixes at the handling moment. The sibling
   day-count factors name both ends expressly. It is not harmless: in task 0, anchoring the end on the
   collection day named on the shipment request would give 15 days against 14 quote validity days and a
   52.00 uplift instead of 38.00, moving the charge by 14.00.
4. **A day-count convention mismatch** between `tradein_appraisal_grading`, which defines the appraisal
   window in *business* days, and `late_appraisal_allowance` / `offer_ageing_anchor`, which measure against
   that same figure in *calendar* days. The KB states both sides literally and even flags the mismatch in
   words, so the rendering is faithful; the inconsistency is the source's.
5. **A coverage note**, outside the enumerated scan domain: the `lifecycle` transition `accepted → expired`
   ("the accepted device never reached the retailer") is stated as a rule in no document, and in no policy
   `rule` either.
6. **A stale authoring line**, no bearing on the documents: task 1's `design_rationale` describes this
   task's programmes as "Renew Mail In Appraisal rather than Renew Business Asset Buyback", while the
   seeded appraised batch stands on Renew Business Asset Buyback.

## Coverage gap, stated explicitly

This audit is organised per difficulty and audits only the product this difficulty claims (`tradein`).
Cross-product contradictions are outside its detection range: the two cross-product figures this
difficulty's factors depend on were checked and found correct and findable
(`docs/membership/circle_delivery_and_return_concessions_e9b82887` — Circle Business Pro, 12 haul-aways per
year; `docs/orders/business_freight_terms_6011d1a2` — Business Dock and Freight Delivery, 65.00 for each
pallet moved), but the other products' corpora were read only where a `tradein` document named them, and
were never used as a criterion. Base-type products claimed by no difficulty are entirely outside scope.

---

## revision_2 — closing record

Round-2 re-audit, narrow scope: verify the round-1 `KB-EXPLICIT RED` is closed, nothing that passed has
regressed, and neither the source change nor the rewrite introduced anything new. Revision_1 above is
preserved verbatim. No fresh blind derivation was commissioned and none is claimed.

**What moved.** `tradein.extended.yaml` = `b979d1359d4d4710`; `task_tools.py` unchanged at
`45fbe2eeaab3eb4f`; corpus hash `ec9e148471f3cfb125373901672e6e2de6bc492c9a8e25bcdc9f22dd0062dab5`, still 57
documents (13 policy + 10 facet + 5 hub + 5 baseline + 24 factor), **19 changed**. The charter moved, so every
figure was re-derived rather than carried forward. I verified at source, before reading any document, that
`compute`, `params`, `inputs` and `variants` parameters are **byte-identical** to round 1 on all five
policies — so no ladder value, boundary or scored figure could have moved — and that the only `baseline.params`
change is `tradein_ext_batch_settlement_credit` → `[]`. GT is unchanged: 12 / 240.0 and 4822.4 / 4342.4 / 5.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Task verdict |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS (was `KB-EXPLICIT RED`) | **PASS** |

**The difficulty closes out.** All three parts PASS on both tasks.

## The round-1 RED is genuinely closed

Verified at all three layers, independently of the renderer's report:

- **Source.** `baseline.params` on `tradein_ext_batch_settlement_credit` is `[]`. The fix is a removal and
  nothing else: `delayed_allowance_usd` 60.0, `late_allowance_usd` 140.0, `uncertified_device_holdback_usd`
  25.0 and `certified_device_holdback_usd` 8.0 are unchanged in that policy's `params`, still sit in real
  tiers of `late_appraisal_allowance` and `erasure_certificate_holdback`, and those ladders' baselines are
  still `0`. No factor lost weight; the byte-identical `compute` and the unchanged GT confirm no value moved.
- **Gate.** With the list empty, the `check_docs.py` loop that previously forced those keys into the
  computation document iterates over nothing. The tension that made me decline a bare deletion in round 1 is
  gone.
- **Document.** `renew_batch_credit_amount_basis_bc847570` no longer contains the "Amounts named in this
  basis" block, `meta.carries` is `[]`, and its worked figure is re-originated to 3275.00 on 9 devices. Each
  of the four constants now occurs only in the ladder that decides it. Corpus-wide string sweeps I ran
  myself: `Amounts named in this basis` **0 files**, `nearest half pallet` **0**, `230.70` **0**, `4822.40`
  **0**, `4342.40` **0**.

## The five fall-back tests, re-run

The property the RED was protecting. Masking every factor document, each computation document plus the
product figures it names and the live records yields a definite number differing from the full-corpus answer:

| Computation | Fall-back | Full corpus |
| --- | --- | --- |
| machines one collection run carries | **34** | 12 |
| the collection charge | **230.70 USD** (or 653.65 if the consented count is itself taken at the masked run count — definite either way) | 240.00 |
| the revised offer | **5100.00 USD** | 4822.40 |
| the amount credited | **5100.00 USD** | 4342.40 |
| machines the first wave carries | **46** | 5 |

All five hold. The charge baseline was the one most at risk, since its worked example no longer prints the
real freight fee: it now uses an expressly illustrative 90.00 and says so. It stays definite because the
operative text still **names** the governing figure — "the freight fee the Renew programme carries for
collecting a palletised batch" — and a `KB_search` on those words returns the tariff schedule first, at
145.00 for this programme. **No computation document now prints its own task's fall-back** (they print
40/22, 345.80, 1836.40, 3275.00 and 60).

## The two surviving `baseline.params` declarations — both pass

Operational form of the test, now that it has been invoked three times and applied to documents for the first
time:

> A key belongs in `baseline.params` iff the baseline's own `rule` sentence fixes the binding to that key,
> **and** the key is that binding's fall-through — the value the deciding ladder's otherwise-tier selects —
> or a structural constant every tier uses. A key naming a **graded, non-default tier** of a binding whose
> baseline is something else fails, because publishing two such figures side by side announces a ladder.

`tradein_ext_collection_handover_units` → `slot_units_full` (40, fixed by "capped at the **full** batch
allowance", the otherwise-tier of `carrier_batch_allowance`) and `full_fill_pct` (100, fixed by "lifts those
machines **in full**", the otherwise-tier of `run_lift_share`). `tradein_ext_collection_freight_charge` →
`pallet_capacity_units` (8, a structural constant used by every tier), `standard_handling_usd` (1.10, fixed by
"the **standard** handling", the otherwise-tier of `machine_handling_rate`) and `freight_fee_usd` (a variant
parameter outside the policy's own `params`, correctly **named** rather than restated). All pass.

And the check only this layer can make: **as rendered, neither discloses a variation.** The two computation
documents print 40 machines / 100 per cent and 8 machines to a pallet / 1.10 USD respectively, and no other
tier figure. Each is the single value the baseline sentence already asserts in words, so a number on it adds
no information about other tiers — unlike the round-1 RED, where 60.00 **and** 140.00, 25.00 **and** 8.00
were *graded* figures for slots whose baseline was *nothing*, and the pairing itself was the disclosure.

## The O-r5.1 rendering — sound

Charter sentence: "…the day it runs out **is written onto it**…", naming no field. Rendered in
`renew_buyback_collection_run_consent_4013e3df` A3 as "…the day it runs out **being recorded on the agreement
as the day its quote ran out**…". I checked whether that names a real field:

- `blueprint/db_schema.json`, `tradein_agreements`: the record carries `quote_expiry_date` and **no** separate
  agreement-expiry column.
- `blueprint/products/tradein.yaml`, event `tradein_quote_expire`: `mutation.transition` covers **both**
  `quoted → expired` and `accepted → expired`; `meaning` is "…**or the accepted device never arrived**";
  `grain` is "the expiry is recorded on the agreement itself"; `fields` is
  `{status: moved to expired, quote_expiry_date: "the day the quote ran out"}`.

So the field the `accepted → expired` expiry actually writes **is** `quote_expiry_date`, and "the day the
quote ran out" is the charter's own wording for what it writes there. The rendering names a real record value
a reader sees in a finder return, invents no column, takes its words from the charter rather than the
renderer, and preserves all three limbs of the sentence's force. **No addition and no `KB-EXPLICIT RED`.**
Charter-side property recorded: `quote_expiry_date` carries two meanings depending on state (seeded as "last
day the quote may be accepted", overwritten as "the day the quote ran out"); nothing turns on it in either
task.

## The retirement count — the registry is right, the arithmetic cited for it is not

Counted from the charter: **12** `overwrite` entries, naming **10 distinct** `superseded_clause` strings,
because two clauses are each retired by two policies — "the units on the list govern what may be collected"
(`…handover_units` and `…refresh_wave_units`) and the new "counted in business days from the day the device
was booked in" (`…revised_offer_amount` and `…batch_settlement_credit`). The documents carry **9** "no longer
in force" markings across **6** documents and all 10 distinct clauses verbatim; 9 markings cover 10 clauses
because `renew_inbound_carriage_and_fees_07af17c2` retires two inside one quotation of the charter's own
semicolon-joined sentence. A machine check located every one of the 10 — **0 missing** — and no document
retires anything undeclared.

So "10 distinct clauses across 6 policy documents" is correct and **not one short**; "against the source's 11
`overwrite` entries" is off by one, the missed duplication being the new business-days clause. The discrepancy
is in the justification, not in the corpus.

## Round-1 items: disposition

| Round-1 item | Disposition in revision_2 |
| --- | --- |
| **D2** — the RED: factor tier figures in the batch-credit computation document | **CLOSED** at source, gate and document |
| **D1** — the half-pallet label disagreeing with its own gloss | **CLOSED at source**, not merely glossed: the charter's tier `method` is now the operative reading and the document carries it verbatim |
| **K2** — the charge baseline's worked example on this task's own inputs, printing its fall-back | **CLOSED**; re-originated to 28 machines at a disclaimed illustrative rate, printing 345.80 |
| **K3** — "that arrangement's own records carry the pallet rate", an added and incorrect evidence-location claim | **CLOSED**; the charter now says it "stands on no order of the profile" and the document carries that verbatim. Findability *improved*: a search on the new wording returns the orders tariff first |
| **K4** — the unanchored quote age, worth 14.00 on task 0's charge | **CLOSED**; both ends named |
| **K5** — business days versus calendar days, worth **60.00** on task 1's credit and sitting **exactly** on the threshold (2026-09-04 Friday → 2026-09-15 Tuesday = 11 calendar days but exactly 7 business days, against 7 appraisal days) | **CLOSED**; retirement registered and the calendar convention stated in both factor documents. `business days` now occurs in exactly one `tradein` document, inside the retired quotation |
| **K6** — the `accepted → expired` transition stated as a rule nowhere | **CLOSED** by the new A3 scope sentence |
| Stale `design_rationale` line naming the wrong programme | **CLOSED**; the string no longer occurs in either task file |
| **D3** — the two assembly paragraphs beyond their own `baseline.rule` | **UNCHANGED**, still an observation, reasoning not revisited |
| Erasure-holdback replacement sentence homed in a factor rather than the hub | **UNCHANGED**, still an observation |

## New or regressed defects: none found

- All 19 changed documents were read in full and every changed sentence traced to the new charter.
- No tier softened, merged or dropped: all 24 ladders re-read against the byte-identical `factors` block. Note
  that `renew_buyback_machine_handling_rate_121f6e03`'s prose illustration moved from the clearing-load tier
  to the full-load tier, but the clearing-load figure remains stated twice (in the numbered ladder and in the
  both-sides table), so all three tiers are still carried.
- Every re-originated illustration recomputed and found arithmetically sound (eleven re-originations plus the
  new both-sides case at 310.00 raised / 262.50 relieved → 47.50 unsettled → 40 machines).
- Corpus sweeps I ran: **zero** calendar dates anywhere; **zero** hits for this difficulty's scored values,
  intermediates, distinctive inputs and fall-backs, apart from three benign substring collisions I checked
  individually ("5 machines" inside "15/45 machines"; "85.00 USD" as a factor's own tier constant; "12
  devices" inside "12 devices were booked in" in a different policy's illustration).
- Route/pointer sweep: **zero** hits. Exactly three "only after" sentences, each in one document on its
  blocked side. Each of the five task tool names in exactly one document, its own hub. No aggregated chain,
  dependency table, checklist, roadmap, named mistake or chain-walking example.
- Both prerequisite edges and all three hops unchanged; the ten facet schedules untouched and re-confirmed.

**New observations, neither a defect nor a regression.**

1. The retired phrase bundled a unit and an anchor, so
   `renew_bench_appraisal_basis_42b4f455`'s operative sentence now reads only "The appraisal is carried out
   within the programme's appraisal days" and no longer names the day the count runs from. The anchor is
   restored by both replacement sentences, carried in `renew_late_appraisal_allowance_949251a5` and
   `renew_offer_ageing_anchor_648d82c9`, so nothing is unborne; but a reader of the base document alone no
   longer learns the anchor from it. Faithful to a charter that retired exactly that phrase.
2. The new A3 is the one sentence in the round-2 corpus a careless reader could over-read into a refusal on
   task 0, the machines indeed not having reached the retailer. The records close it: `status` reads
   `accepted`, not `expired`, and `quote_expiry_date` `2026-09-21` is still ahead of the frozen moment — the
   same figure the lift-share factor reads as the room left on the quote.

## Closing checklist — revision_2

| Item | Status |
| --- | --- |
| Audit files one-to-one with the tasks in both directories; revision_1 preserved verbatim, revision_2 appended | yes |
| Every normative atom of the moved charter entailed by the docs | yes — 13/13 base policies homed; **12** `overwrite` entries → 10 distinct clauses all written as retired across 6 documents, 0 missing, none undeclared; all 5 `baseline.rule`s complete; all 24 ladders complete and exact; all 6 programmes' parameters exact across the 10 untouched facet schedules |
| No claim from outside the source | none found; the five new source sentences are each carried verbatim in exactly one document |
| Every prerequisite's `policy_source` verbatim, declared form, blocked side, nowhere else | yes — 3/3, machine-checked |
| Every hop resolvable from the sentence, the depended-on docs and the records | yes — 3/3, unchanged |
| Every declared factor findable from the records its tier rests on | yes — 24/24; cross-product findability re-tested and improved on the pallet rate |
| Computation documents silent about variation | **5 of 5** (was 4 of 5) |
| Five fall-backs definite and differing; no computation document prints one | yes, re-run |
| `check_docs.py` / `check_traceability.py` on the final form | re-run by the commissioning agent on this corpus — `DOCS OK`; `TRACEABILITY OK` (0.json 20/0, 1.json 24/0). This auditor ran neither, as instructed |

## Policy-side notes outstanding after revision_2

Revision_1's notes 1–5 are all closed by the source change (see the disposition table). Two remain, neither
affecting this skill's verdict:

1. `quote_expiry_date` carries two meanings depending on the agreement's state — seeded as "last day the quote
   may be accepted, inclusive" and overwritten by `tradein_quote_expire` as "the day the quote ran out". It is
   the charter's own design and nothing turns on it in either task.
2. The `tradein_ext_collection_handover_units` and `tradein_ext_revised_offer_amount` `rule` blocks still
   carry an ordering sentence that names factor quantities their own `baseline.rule` does not contain, which
   is what puts D3 in the computation documents. Recorded for whoever revisits the baseline/factor topology.

## Coverage gap, unchanged

Organised per difficulty; audits only `tradein`. The two cross-product figures this difficulty depends on were
re-checked and remain correct and findable (`docs/membership/circle_delivery_and_return_concessions_e9b82887`
— Circle Business Pro, 12 haul-aways per year; `docs/orders/business_freight_terms_6011d1a2` — Business Dock
and Freight Delivery, 65.00 for each pallet moved, now the first hit on the pallet-rate factor's own wording).
Other products' corpora were read only where a `tradein` document named them and were never used as a
criterion. Base-type products claimed by no difficulty remain out of scope.
