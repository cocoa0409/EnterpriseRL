# KB-document audit — closing record for supplemental_benefit_allowance_desk (product `allowance`)

Revision 1, 2026-09-21. Auditor independent of the renderer and of the policy-side auditor.
Corpus: 63 published documents under `docs/allowance/`, md5 of the title+content snapshot
`23fc1acd2ada814cf484a61e0d8b483f`. No document, task, blueprint, skill or runtime file was edited.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (closure, Marguerite Kessler) | **PASS** | **KB-BIJECTION RED** (one location, latent) | **PASS** |
| 1 (catch-up load, Rolando Jessop) | **PASS** | **KB-BIJECTION RED** (same location, latent) | **PASS** |

**The difficulty does not close out**, on one finding, recorded once and carried in both task files.

## The finding

`docs/allowance/how_long_an_allowance_stands_4d754845.json`, under "**Worked illustrations, on hypothetical cards.**",
third illustration:

> "A card that carries an allowance forward, is loaded on calendar months, shows two loads and whose current benefit
> period is the first of the benefit year: an allowance stands for 3 further benefit periods, which is what carries it
> to the last day of the benefit year."

The same document's rule sentence, carried verbatim from `allowance_ext_period_end_expiry`'s second ladder tier, says
that on such a card an allowance "stands to the last day of the benefit year". A card loaded on calendar months has
twelve benefit periods in the year, so from the first of them the last day of the year is eleven further periods away.
The illustration's identification of "3 further benefit periods" with "the last day of the benefit year" is entailed
by neither the rule nor the compute, and is the rendering's own claim.

Root cause is on the policy side: the ladder tier says "to the last day of the benefit year" while
`allowance_ext_period_end_expiry.compute` reads
`life_periods: … (K('last_period_index') - current_index) …` with `params.last_period_index: 3`. The two disagree for
the monthly branch, and the illustration takes its arithmetic from one and its label from the other. On that same card
the next step, `dying_index: current_index - life_periods - 1`, evaluates to −4 and `dying_label` becomes the empty
string.

Bearing: **latent on both tasks.** Task 0's card is `Ridgecrest Healthy Options Card - Plus` and task 1's is
`Ridgecrest Healthy Options Card - Premier`, both with `benefit_period_basis` "calendar quarters of the benefit year",
so the first tier applies and the monthly branch is never entered; and task 1 computes no expiry at all.

## The renderer's five leads, answered

The question asked of each was the same: does it bear on either task's scored solution? All five were tested against
the source computes and the gold values; **none bears**. Each is recorded as latent.

| # | Lead | Verdict | Evidence |
|---|---|---|---|
| 1 | `allowance_ext_period_end_expiry.params.last_period_index: 3` goes negative on a monthly card | **Latent, both tasks.** It is also the root cause of the one RED above. | `life_periods` takes that branch only when `benefit_period_basis == 'calendar months of the benefit year'`. Task 0's Plus card is loaded on calendar quarters, so `life_periods = 1` by the first branch and `dying_index = 3 - 1 - 1 = 1` → 2026-Q2, which is the GT label. Task 1 has no expiry computation. Two tiers of the product (Dual Complete, Chronic Care Plus) are loaded monthly, so the branch is reachable in the world. |
| 2 | Rule sentences name only the quarters and months branches while both computes carry a third annual branch (`year_months`, 12) | **Latent, both tasks.** Not a rendering fault. | `period_months` resolves to 3 in all four computations of task 0 and both of task 1, since both cards are quarterly. Rendering the three-way mapping from the compute is what gives the constants a home and lets each baseline compute a definite number; the gap between the rule sentence and the compute is the source's. |
| 3 | `carry_forward` and `owed_total` round inside the computation against a "rounded at the end and at no earlier step" rule | **Latent, both tasks**, verified arithmetically rather than assumed. | Task 0: `carry_base × carry_share = 107.30 × 0.5 = 53.65` exactly, so `RND(…, 2)` is a no-op and the expiry is 53.65 either way. Task 1: rounding inside gives `166.67 + 500.00 = 666.67`, then `666.67 − 83.33 = 583.34`; rounding only at the end gives `666.6667 − 83.33 = 583.3367 → 583.34`. The two readings coincide. |
| 4 | No tier is loaded annually, so every "once a year" branch is unreachable | **Latent, both tasks**, and correctly rendered for losslessness. | `load_and_benefit_period_terms_d07a3774` shows all six tiers loaded quarterly or monthly. The affected tiers — row 2 of `how_many_months_a_benefit_period_has_4fe43aba` and of `counting_the_periods_that_have_passed_385b30c8`, and the 12-month limb in two baselines — are carried in full, which is what the two-way scan requires. |
| 5 | `max_per_customer` (2) and `maximum_programmes_per_member` (2) are the same number under two required keys | **Latent, both tasks**, and not a KB defect. | Homed in `holding_more_than_one_programme_78997370` and `entry_standing_and_holding_limits_bf09de75`; each is the proper home for its own key. No scored computation of either task reads it. Task 1's member holds two programmes, but the 2025 Core stands `closed` and the rule excludes a closed programme from the test. |

## The task-1 benefit-period fix, audited from the rollout's side

The brief asked for this specifically. It holds on all three counts, and was tested blind — the assignment below was
made and frozen to disk before any source-layer file was opened.

1. **Obtainable.** The 2026 programme's ledger is empty and its record carries only `benefit_year: "2026"`, so no
   query returns either label verbatim; the member supplies both when asked what the plan's letter says.
2. **Not volunteered.** `"2026-Q"` occurs exactly twice in `user_scenario`, both inside the one clause governed by
   "Asked what that letter says", and the script closes with "raises nothing the representative has not raised with
   him". No scored amount appears anywhere in the persona.
3. **The caller does not decide which goes on which.** He reads them as an unordered pair and adds "none of it meant
   anything to him". The assignment is forced by the documents and the records, in both directions:
   `first_load_valuation_basis_d785adf9` — "It is placed in the benefit period the programme opened in" — with
   `program_start_date: 2026-09-01` gives 2026-Q3; `catch_up_load_reckoning_basis_dae7e7cf` — "placed in the benefit
   period in which it is made available, because it makes good several benefit periods at once and belongs to none of
   them alone" — with `frozen_time` 2026-10-20 gives 2026-Q4. Neither computation document mentions a label of any
   kind, so nothing is dictated. The GT's own tracing rests on the same two sentences.

## Checklist

- [x] Audit files correspond one-to-one with the tasks: `runtime_context/…/{0,1}.md` and `policy_kb/…/{0,1}.md`.
- [x] Each `blind_answer` was written to disk before the source layer was opened; neither was altered afterwards.
      Both `gt_comparison` sections record corrections to the blind defect lists as appended text rather than edits.
- [x] Contamination: none on either task. No `tasks/*.json` ever entered a grep match domain while a derivation was
      unfrozen; the personas were read through an allow-list reader loading only `user_scenario` and `frozen_time`.
- [x] Every scored value and every scored argument of all six computations was reached blind: task 0 — 56.45, 53.65,
      47.00, 118.90, with 2026-Q4 / 2026-Q2 / 2026-Q4 and 2026-10-12; task 1 — 83.33 in 2026-Q3 and 583.34 in 2026-Q4.
- [x] All four `prerequisite` edges carried: each `policy_source` matched as an exact normalised substring against all
      63 documents, each hitting exactly one file, and each of those files belonging to the policy the edge blocks.
      All four are `form: state` with their ordering connectives intact. `condition`, `effect` and `resolved_by`
      appear in no document.
- [x] All 29 declared factor ladders carried in full, 87 of 87 tiers, each in its own factor document, with compound
      conditions whole and thresholds stated in figures; the six cross-difficulty factors name their sibling product
      officially and say which records are read.
- [x] All six baselines carried with every default, window, base, order and rounding, and every product figure they
      read named; all four fall-back numbers of task 0 and both of task 1 match the recorded `baseline_result`.
- [x] All twelve base policies scanned sentence by sentence (97 rule sentences and eligibility conditions); every one
      has a prose home, and every non-literal match is entailment-preserving.
- [x] Retired surface: six `overwrite` clauses, all carried verbatim and marked retired, none stated as in force, none
      missing, and nothing retired that the source did not retire.
- [x] No addition: the scan for confirmations, reviews, notifications, re-checks and exception procedures returns
      nothing; the three KB sentences that read as added arithmetic all render `formula` entries of the source.
- [x] No route: the six allowance tool identifiers each occur in exactly one file across the whole seven-product
      `docs/` tree, always their own policy's hub. No aggregated chain, no dependency table, no cross-problem
      guidance, no task-mirroring title.
- [ ] **Gates on the final form.** Not re-run by the auditor, per the brief, which supplied the coordinator's own
      output lines and stated that the auditor runs neither. No document was edited in this audit, so the recorded
      state stands: `DOCS OK` (63 docs, 92 required quantitative keys, 6 task tools, 4 prerequisite edges) and
      `TRACEABILITY OK` (0.json 33/0, 1.json 19/0).
- [ ] **Close-out withheld** on the one KB-BIJECTION RED above.

## Policy-side notes carried forward

Reported for the record; none changes this skill's verdict, and none is to be settled by editing a document.

1. `allowance_ext_period_end_expiry.rule`: "the period that ended one whole period before the current one, counting
   back from the periods that have passed and from how long an allowance stands" reads as though the offset were the
   life itself, while the compute applies both (`current_index - life_periods - 1`). Both readings give 2026-Q2 on
   task 0 once the factor applies; they part company on the baseline (2026-Q3 / 21.40 against 2026-Q2 / 66.85).
2. The monthly rule↔compute disagreement behind the RED (lead 1).
3. `allowance_ext_schedule_catch_up_load` counts its baseline periods in months while its period length is three
   months on a quarterly card; the ceiling absorbs it here.
4. The same policy's `baseline.rule` names no period-length branch at all, so the baseline's period length can only be
   rendered from the compute.
5. `allowance_ext_dvh_recovery_credit.baseline.rule` itself contains "worked out on the basis the card's tier gives",
   so the computation document carries a phrase that tells a reader the tier settles a basis. Source wording; the
   rendering had no discretion.
6. Leads 4 and 5 above: an unreachable annual branch, and one figure under two required keys.


---

# revision_2 — closing record, round 2

2026-09-21. **Verification round, not a blind audit**: the source and GT were revealed in round 1, so only
`revision_1` carries blind weight. `revision_1` above is preserved intact throughout all five audit files.

**Scope verified independently.** `allowance.extended.yaml` sha256 begins `c3f352b8ef09af65` (matching the
coordinator's figure) with mtime 2026-09-21 14:55, before my round-1 read; `task_tools.py` and both task JSONs are
untouched. The corpus is still 63 documents, none added or removed, differing in exactly **5** files. A sentence-level
diff of all five is exhaustive at 38 lines, so the change set is fully accounted for.

## Part verdicts

| Task | Runtime | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (closure) | **PASS stands** (reachability, not re-derived blind) | **KB-BIJECTION RED** — 2 findings, both latent | **PASS** (re-verified) |
| 1 (catch-up) | **PASS stands** (reachability; untouched by the change set) | **KB-BIJECTION RED** — same 2 corpus findings, both latent | **PASS** (re-verified) |

## **The difficulty does not close out.**

Two `KB-BIJECTION RED` findings stand. One is the round-1 RED, which I judge **not closed**; one is the item the
reworker deferred to me, which I rule **is** a defect of the same class.

### Finding 1 — the round-1 RED is not closed; it has been restated

The false illustration is gone, but the clause that replaced it carries the same unentailed identity:

> "An allowance that stands to the last day of the benefit year stands for a number of further benefit periods that
> is 3 less the benefit periods of the year that have already passed."

Its subject is restrictively modified by the rule's tier-2 outcome and its predicate is the compute's count, so it
asserts exactly the bridge the reworker reports having avoided. The corpus still contains a sentence equating the
count with the year's end; a direct grep for one returns this line.

It is false wherever it can be reached. Tier 2 admits only cards "loaded on calendar months", and exactly two of six
tiers qualify (`Dual Complete`, `Chronic Care Plus`, both `rollover_permitted: true`). On a twelve-period monthly
year an allowance loaded in period *i* that stands to the last day of the year stands for 11 − *i* further periods;
the clause says 3 − *i*. These never coincide, and from period 4 the clause goes negative.

Weighing the resolution the coordinator asked me to judge: a reader of that document alone gets a **definite** reading
per tier — the clause supplies exactly one count per outcome — and for the monthly tier the definite reading is
definitely wrong. This is worse than two facts that do not meet, because the document presents the count as following
from the outcome, so the source's rule/compute disagreement is not made visible but concealed behind an asserted
entailment. In round 1 the defect was an illustration false at one named point; it is now a clause under a rule
heading, false across the whole tier.

I accept that `last_period_index` must keep a home. That bears on whether the count is rendered, not on what it is
keyed to: in the source, `compute.life_periods` is keyed on the tier's **conditions**, the same conditions the ladder
keys its outcome on, and neither source field mentions the other's output. The rendering re-keyed the count onto the
outcome. I name the mismatch and stop; I propose no wording and do not ask for the count to be dropped.

Tiers 1 and 3 of the same clause are sound and are a real improvement — see "What got better" below.

### Finding 2 — ruling on the deferred item: it is the same defect

`what_the_card_may_be_spent_on_5291aa2b`, Condition 2: "the category is the one the retailer presents, **not the one
the member names**." The source condition, `allowance_eligible_spending/eligible_category_and_size`
(`kind: caller_fact`, `authority: mixed`), draws no such contrast and never mentions the member's word.

The charter's own structure decides it. Of twelve eligibility conditions, ten are `authority: system_record` and
exactly two are `mixed`. The source writes the member-word exclusion into one of the two —
`entry_standing_on_profile`: "the plan has it from the state or from the member's care team **rather than from the
member alone**" — and not into the other. The counter-argument from all-system `evidence_fields` fails on the same
comparison: `entry_standing_on_profile`'s evidence fields are all `customers` fields, yet the source still wrote the
exclusion, so under this charter's conventions system-only evidence does not by itself entail it. The rendering
flattens `mixed` to record-only for `merchant_category`, which is an authority-boundary change — precisely the class
the mechanical gates cannot see. The reworker was right to raise it and right that it fell outside the shape it was
scoped to; the answer is that it is the same defect.

A corpus-wide sweep confirms it is the **last** one: ten contrast-or-rationale constructions stand across the 63
documents, nine trace to the source verbatim, and only this sentence's two distinctive phrases return 0 hits in
`allowance.extended.yaml`.

## What the round got right

**The four swept sentences were genuinely unentailed, and removing them cost nothing.** Verified individually:

- `card_authorisation_limits_59bc4409` — the sublimits and the `*_eligible` booleans are independent literal keys per
  tier with no derivation linking them. The claim is, as conceded, true across all six tiers as published, which is
  exactly why it had to go: a claim that holds of the seeded values is still a claim the source never makes. Both
  parameter families keep their own homes; the 6 × 8 table survives with every figure.
- `eligible_spending_categories_ad4d27a8` — `eligible_merchant_categories` is its own literal key, not computed from
  the eight booleans, and the mapping is not even name-for-name. The replacement lead-in tracks the
  `parameter_schema` gloss almost word for word. All six category lines survive, and "Two distinctions worth
  holding" — a same-source restatement of the table's own columns — was correctly left alone, which shows the sweep
  discriminated rather than cutting indiscriminately.
- `counting_the_card_charge_at_such_providers_d52bf9e6` — two invented rationales, one of them ("the card's
  authorised entries are not to be trusted") a normative claim found nowhere in the charter. All three
  Condition/Result pairs, the rule sentence and the worked figures survive.
- `counting_what_was_spent_in_a_period_71aa65c0` — an invented rationale that was also in tension with a *sourced*
  base clause ("A transaction that is authorised but never settled does not take money off the card"). The operative
  half survives.

**Nothing regressed.** Only 3 of the 5 changed documents are factor documents, covering 9 of 87 tiers; all nine are
intact, and the other 26 factor documents are byte-identical to the corpus verified tier by tier in `revision_1`. No
baseline changed. Both changed facets keep every figure. All four prerequisite sentences remain verbatim and
single-homed in the documents of the policies they block, `form: state`, connectives intact. All six retired clauses
remain marked retired. All 97 base rule sentences and eligibility conditions remain homed. The six tool identifiers
still occur twice each, own hub only, across all seven products. All six scored values remain reachable: 56.45,
53.65, 47.00, 118.90 for task 0 and 83.33 / 2026-Q3, 583.34 / 2026-Q4 for task 1. Task 1 is untouched by the change
set entirely, and its benefit-period-label fix lives in an unchanged `tasks/1.json`.

**What got better.** The new clause states the count for tier 1 outright — "stands for 1 further benefit period" —
which is correct and which puts the source's own decomposition of the closing period on the page. In round 1 I had to
infer that count myself and reached 2026-Q2 by a compensating route. Task 0's expiry derivation is now more direct
than it was, independently of Finding 1.

## Checklist

- [x] `revision_1` preserved intact in all five files; `revision_2` appended to each.
- [x] Round recorded as verification, not blind audit, in every file that carries a runtime verdict.
- [x] Source confirmed byte-identical by hash and mtime, independently of the brief.
- [x] Change set confirmed at 5 of 63 documents, exhaustively diffed.
- [x] Round-1 RED re-tested on its merits rather than accepted as closed.
- [x] Four swept sentences each tested for entailment and for removal cost.
- [x] Corpus swept for remaining sentences of the same shape; one found, ruled on.
- [x] Regression tested in the opposite direction: tiers, baselines, facets, prerequisites, retired surface, base
      clauses, tool names, scored values.
- [x] Dependency-form re-run: PASS, unchanged.
- [ ] **Gates on the final form** — not re-run by the auditor, per standing instruction; the coordinator's round-2
      lines are on record (`DOCS OK`, 63 docs, 92 quantitative keys, 4 prerequisite edges; `TRACEABILITY OK`,
      0.json 33/0, 1.json 19/0). No document was edited in this audit.
- [ ] **Close-out withheld** on the two KB-BIJECTION RED findings above.

## Standing items

The five renderer source leads remain **latent** and settled from round 1; the source is byte-identical, so they are
not re-litigated. The six policy-side notes of `revision_1` likewise stand unchanged — note 2 there, the rule and the
compute disagreeing on the monthly life of an allowance, remains the root cause of Finding 1 and is a source matter
that no rendering can resolve by itself.


---

# revision_3 — closing record, round 3

2026-09-21. **Verification round, not a blind audit**: the source and GT were revealed in round 1, so only
`revision_1` carries blind weight. `revision_1` and `revision_2` are preserved intact in all five audit files.

**Scope verified independently.** The source has not moved across three rounds: `allowance.extended.yaml` sha256
begins `c3f352b8ef09af65`, and `task_tools.py` (`14ef9684…`), `tasks/0.json` (`dce80bdc…`) and `tasks/1.json`
(`a80e79a8…`) all match the digests recorded in `revision_2`. The corpus remains 63 documents — round 1 `23fc1acd…`,
round 2 `2bb52567…`, round 3 `038a9794…` — differing from round 2 in exactly **2** files, both diffed exhaustively.

## Part verdicts

| Task | Runtime | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (closure) | **PASS** (revision_1 blind; reachability re-confirmed) | **PASS** | **PASS** |
| 1 (catch-up) | **PASS** (revision_1 blind; reachability re-confirmed) | **PASS** | **PASS** |

# **The difficulty closes out.**

All three parts PASS on both tasks. Both round-2 findings are closed, no new defect was introduced, and nothing
regressed.

## F1 — closed: the identity dissolved rather than moved

I carried the prior that last round's fix relocated the defect instead of closing it, and put the burden on the new
text. It discharges it. The count clause is now keyed on the three tier conditions that `compute.life_periods` is
itself keyed on, and the outcome phrase no longer appears in it.

**I re-ran the grep test myself rather than accept a reading of it**, since that judgement is what I red-lighted last
round. "Stands to the last day of the benefit year" survives in two documents and in **four** occurrences; in every
one it is the *predicate* of a conditions-keyed statement, never the subject — twice in
`how_long_an_allowance_stands_4d754845` (the source ladder sentence and the conditions table) and twice in
`carry_forward_and_expiry_terms_f7ceee91` (a facet table cell and its prose restatement of
`unused_balance_expiry_basis`, both unchanged since round 1). A targeted search for the defect's actual shape — the
outcome as subject of a count predicate — returns nothing, and every "further benefit period" sentence in the corpus
is keyed on conditions.

The three count sentences render `compute.life_periods` branch for branch: `1` for rollover ∧ quarters ∧ ≥2 loads;
`last_period_index − current_index`, rendered "3 less the benefit periods of the year that have already passed", for
rollover ∧ months ∧ ≥2 loads; `0` otherwise.

**On whether a reader is left with a false count stated as fact** — the question that decided the round: no. The
document makes two statements about the monthly tier, both keyed on the same conditions, which cannot both hold; but
that conflict is the *source's*, already on record as policy-side note 2, and every sentence now traces to a source
field. Round 2's clause asserted a proposition the source does not contain and that was false; round 3 asserts
nothing of its own. A reader who combines the two and finds them irreconcilable has discovered a real charter defect,
which is the desired outcome — concealing it behind an entailment is what made it unreportable. The alternative of
dropping either field is barred twice: Step 4 forbids dissolving a contradiction by hiding one side, and dropping the
count would orphan a required quantitative key. `last_period_index: 3` and `min_periods_loaded: 2` both keep homes,
the monthly tier's value stays derivable, and no arithmetic symbols appear.

## F2 — closed, without overshooting

The clause that flattened `authority: mixed` to record-only is gone, and both source objects survive: the
`eligible_category_and_size` condition verbatim, and the rendering of its `evidence_fields`. The document now says
where the fields are read and no longer whose word governs, leaving the authority where the source leaves it. The
sweep was not over-applied: `entry_standing_on_profile`, the one `mixed` condition whose *source text* does contain
the exclusion, keeps its rendering in `opening_an_allowance_programme_e1e98e76`, so the asymmetry the charter draws
between its two `mixed` conditions is reproduced rather than erased. A fresh corpus sweep returns three contrast
constructions, all sourced; all eight phrases swept in rounds 2 and 3 are gone.

## Regression — nothing lost in the opposite direction

Only one factor document changed, and its rule sentence and conditions table are untouched, so all **87** ladder
tiers stand. No baseline changed. All **four** prerequisite sentences remain verbatim and single-homed on the side
they block, `form: state`, connectives intact, with no `condition` text leaked and no `resolved_by` identifier in any
blocked-side document. All **six** retired clauses remain verbatim and marked retired. All **97** base rule sentences
and eligibility conditions remain homed. The **six** tool identifiers each occur twice, own hub only, across all
seven products.

## Scored values

Task 1's fourteen tree documents are **byte-identical to the round-1 corpus** the frozen blind answer derived from:
83.33 in 2026-Q3 and 583.34 in 2026-Q4 stand untouched, as does the benefit-period-label fix in an unchanged
`tasks/1.json`. Task 0's tree differs from round 1 in three documents, each verified intact in every operative
sentence the derivation used; re-deriving from the round-3 text gives 2026-Q2 and 53.65, and all four figures —
56.45, 53.65, 47.00, 118.90 — remain reachable. The derivability gain first noted in `revision_2` survives the
re-keying.

## Closing checklist

- [x] `revision_1` and `revision_2` preserved intact in all five files; `revision_3` appended to each.
- [x] Round recorded as verification, not blind audit, in every file carrying a runtime verdict.
- [x] Source confirmed byte-identical across all three rounds by hash, independently of the brief.
- [x] Change set confirmed at 2 of 63 documents, exhaustively diffed.
- [x] Both round-2 REDs re-tested on their merits, with the grep test re-run by the auditor rather than accepted.
- [x] The new clause checked branch-for-branch against `compute.life_periods`; required quantitative keys confirmed
      still homed; monthly tier's value confirmed still derivable.
- [x] F2 checked in both directions — flattening removed, and nothing the source states lost.
- [x] Corpus swept afresh for new unsourced claims: none.
- [x] Regression tested: tiers, baselines, prerequisites, retired surface, base clauses, tool identifiers, scored
      values.
- [x] Audit files correspond one-to-one with the tasks; old revisions traceable; every comparison section carries a
      verdict.
- [x] All three parts PASS on both tasks.
- [ ] **Gates on the final form** — not re-run by the auditor, per standing instruction; the coordinator's round-3
      lines are on record (`DOCS OK`, 63 docs, 92 quantitative keys, 4 prerequisite edges; `TRACEABILITY OK`,
      0.json 33/0, 1.json 19/0). No document was edited in this audit.

## Standing items, carried forward unresolved at the source layer

These are **not** blockers on the KB audit and do not affect the close-out. They are recorded for the source layer.

The five renderer source leads remain latent and settled from round 1. The six policy-side notes of `revision_1`
stand unchanged, the source being byte-identical. Note 2 in particular — the ladder tier and `compute.life_periods`
disagreeing on the monthly life of an allowance, with `last_period_index` subtracted from an index that counts 0–11
on a monthly card — remains a genuine source defect that no rendering can resolve from the outside. It is now
correctly *visible* in the published corpus as two unreconciled statements rather than concealed behind an asserted
entailment, and it is latent for both tasks, whose cards are loaded on calendar quarters. Two of the six tiers
(`Dual Complete`, `Chronic Care Plus`) could reach it in a future task, so it is worth settling at step 2 before this
product is used again.

