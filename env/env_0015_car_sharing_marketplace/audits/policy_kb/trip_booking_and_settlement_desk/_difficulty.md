# KB-doc policy audit — closing checklist, trip_booking_and_settlement_desk (product `trips`)

Revision 1. Auditor: fresh KB-doc auditor, independent of the render agent and of the source-layer auditor;
`audits/policy_task/trip_booking_and_settlement_desk/` was never opened.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (mileage top-up: grant → payment) | **PASS** | **KB-BIJECTION RED** | **PASS** |
| 1 (young-driver surcharge → extension quote) | **KB-RUNTIME RED** | **KB-BIJECTION RED** | **PASS** |

The difficulty therefore **does not pass** the rendering audit.

## The findings, in one place

| Id | Severity | Documents | What is wrong |
|---|---|---|---|
| **B-1** | Blocking; decides three ladders, two of them in task 1 | `young_driver_protection_adjustment_94952a2c`; `extension_protection_cover_credit_b9c9275c`; `mileage_topup_block_price_by_protection_47c299c3` | The fee limb of all three factors is carried as every fee charged on the trip's protection election ("taken together"), where the source reads only the election's **daily protection fee** lines (`charge_basis='daily_protection_fee'` in both `inputs.history` and `compute`). The phrase "daily protection fee" occurs in no document of `docs/trips/`. In task 1 the election also carries a 109.20 `young_driver_protection_surcharge` line, so the two readings fall on opposite sides of the 800.00 floor. |
| **B-4** | Blocking; one cent on task 1's scored quote | `extension_young_driver_share_basis_bf64bc7b` | "the daily share is taken to the nearest cent" — an intermediate rounding the source's ladder does not state and its `compute` does not perform (`RND(surcharge_line / reserved_days_b * extended_days, 2)`). |
| **B-2** | Non-blocking in these worlds | `mileage_topup_price_computation_640421d7` | "The rounding happens once, at the end, and not at any earlier stage" — an added emphasis contradicting the source's own `RND` on the line price. |
| **B-3** | Form only; semantics intact | `reservation_pricing_and_line_composition_156172b6` | The residue of the partially superseded young-driver sentence leaves its subject with no predicate; it does not read as grammatical prose. |

Scored consequences in task 1: `surcharge_amount` 86.73 from the documents against 108.42 scored;
`quoted_amount` 179.44 from the documents against 192.53 scored (192.52 with **B-1** corrected but **B-4**
left standing). Task 0's two scored values, every intermediate, the tree, the order, the owners and the
arguments match the source layer exactly.

## What holds

- All 13 base policies of `trips` correspond losslessly over their whole domain, including untriggered
  branches, boundary readings, authority and correlation contracts and state gates; the 10 rate-plan facet
  documents carry the `parameter_schema` figures for all six variants and add no rule.
- The retired surface is exact in both directions: all six `overwrite` clauses are borne and written as
  retired, none vanished, none is still stated as in force, and nothing is retired that the source did not
  retire. The three-fragment residue the brief flagged — "Part packages are not sold." — reads as
  grammatical prose and carries exactly its source content.
- All 4 baselines are complete, self-sufficient and silent about variation, each yielding a definite
  fall-back number (grant 1250 miles, price 1166.00 on the scored grant, surcharge 139.39, quote 285.12).
- 19 of the 21 declared factor ladders are exact tier for tier, every compound condition, window, threshold,
  inclusivity and method pinned; the two exceptions are **B-1** and **B-4** above.
- Both prerequisite sentences stand verbatim, in their declared **state** form, in the hub of the policy they
  block and in no other policy's document; both hops are resolvable at the same strength from the sentence,
  the depended-on policy's own rule and the records, and both were derived **state-derived** in the blind
  audits without any pre-solving.
- No route anywhere: four task-tool names, each only in its own hub's invocation block; no aggregated chain,
  dependency table, checklist or cross-problem example; no task-mirroring title or opening; no task world
  state written in as a policy fact.

## Policy-side notes (reported, not this skill's verdict)

P-1 the source's factor prose has no words for the `daily_protection_fee` restriction that its `compute`
pins; P-2 the surviving mileage residue is the contrapositive of a fragment the same overwrite withdrew;
P-3 three day-counting conventions the source leaves open; P-4 `verify_member_identity` is scored in both
tasks with no home in this product charter; P-5 the source's `yd_share` ladder states no rounding; P-6
`trips_evt_extension`'s decision-window clause conditions pricing on a recorded host decision and is not
retired, while `trips_ext_extension_quote` prices before the request reaches the register.

## Gate lines on record (supplied with the brief; not re-run by this auditor)

```
.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0015_car_sharing_marketplace trips
🔎 DOCS gate  product=trips profile=extended docs=52 roles={'policy': 13, 'factor': 21, 'baseline': 4, 'hub': 4, 'facet': 10} content[min/mean/max]=1375/2315/4001
   required quantitative keys=151  task_tools=4  prerequisite edges=2
  [PASS] mechanical gates …
DOCS OK

.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0015_car_sharing_marketplace/tasks/trip_booking_and_settlement_desk
🔎 TRACEABILITY gate  (2 tasks)
0.json  15 copied  0 missing  ok True
1.json  16 copied  0 missing  ok True
TRACEABILITY OK
```

Both gates are green and neither can see any of the four findings: `check_docs.py` proves structure,
coverage, leak-freedom, verbatim carriage of the prerequisite sentences and the coarse surface of routed
wording, but cannot tell that "the protection fees … taken together" reads a different set of rows from the
one the charter's compute reads, or that a rounding step has been inserted into a factor's method.

## Files

- `env/env_0015_car_sharing_marketplace/audits/runtime_context/trip_booking_and_settlement_desk/0.md`
- `env/env_0015_car_sharing_marketplace/audits/runtime_context/trip_booking_and_settlement_desk/1.md`
- `env/env_0015_car_sharing_marketplace/audits/policy_kb/trip_booking_and_settlement_desk/0.md`
- `env/env_0015_car_sharing_marketplace/audits/policy_kb/trip_booking_and_settlement_desk/1.md`

No document was edited and no fix was arranged.

---

# revision_2 — closing checklist, round 2

Corpus `28da01f58983ba7669c790f6ad272755ad7fc9423a3de20fd901074d9f07b24a` (was
`ba68007733e42ce82ee8e416b3360d3a3084647b6fd74440bc699660a6fb50c2`); charter reworked twice since round 1.
Revision 1 above is untouched.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | **PASS** (was PASS) | **KB-BIJECTION RED** — one finding, N-2 | **PASS** |
| 1 | **PASS** (was KB-RUNTIME RED) | **KB-BIJECTION RED** — one finding, N-2 | **PASS** |

Round 1's four findings: **B-1, B-2, B-3 and B-4 are all genuinely closed.** One new finding, **N-2**, is
open. The difficulty does not yet close, on that single finding.

## Isolation at round 2

I could not blind-audit these documents again: my context carries round 1's `compute` expressions,
`inputs.history` filters and scored values. Rather than claim an isolation I do not have, I recorded a
`contamination_disclosure` and commissioned **two fresh auditors with no round-1 context and no source-layer
access**, one per task, each restricted to the 52 published documents, the `dbquery.py` lookups, the
blueprint background and the simulator script, and each barred from `tasks/**`, `audits/**`,
`blueprint/products/**`, document `meta` and every other scenario. Both reported opening nothing forbidden.
**Both reproduced the charter's values exactly**, from the published corpus alone:

| | task 0 `granted_miles` | task 0 `purchase_amount` | task 1 `surcharge_amount` | task 1 `quoted_amount` |
|---|---|---|---|---|
| Round-1 documents entailed | 3600 | 814.40 | *86.73* | *179.44* |
| Round-2 documents entail | 3600 | 814.40 | **108.42** | **192.53** |
| Charter `expected` | 3600 | 814.40 | **108.42** | **192.53** |

The charter's values never moved; what moved is what the documents entail. Task 1's repair is therefore
genuine and lands exactly on the two readings that failed.

## The 24 changed documents — verified by content, not mtime

The brief warned that a sibling product's re-render made an mtime mistake. Here mtime happens to split
28/24 the same way the renderer claims, so publication did **not** flatten the directory — but the
verification does not rest on it. I re-read all 24 changed documents in full and compared them against the
round-1 text; I re-read the load-bearing members of the untouched group in full — **all 4 hubs**,
`included_mileage_grants_and_odometer_authority`, `mileage_overage_settlement`,
`extension_requests_and_extended_time_pricing`, `mileage_topup_line_price_basis` — and each is
byte-identical, including **both prerequisite sentences and all four tool contracts**; and I fingerprinted
sections and lengths across the rest, finding nothing new or lost. The gate line corroborates
independently: `content[min/mean/max]` moved `1375/2315/4001` → `1375/2547/4001`, the extremes unchanged and
still the same two untouched documents, the mean up 232 characters. The claimed composition holds: no facet,
no hub and exactly one base-policy document in the changed set.

**No tier was lost, softened, merged or rounded in any of the 24.** Every change is an addition of a
counting convention, a rounding position, a negative restriction or a worked boundary, and every one traces
to charter text — verified mechanically: all 17 `rule` strings probed sentence by sentence against the
corpus, **0 unmatched**.

## The four round-1 findings

| Id | Verdict | Evidence |
|---|---|---|
| **B-1** — fee limb read as every fee on the election | **CLOSED** | The charter now carries the restriction in prose in all three policies ("the **daily** protection fees … however many lines they stand as and whenever they were raised") plus an exclusion sentence naming the excluded kinds, the first of them "a young-driver protection surcharge" — the very row that broke round 1. All three documents carry both verbatim, each with a worked case on the failure mode. The bare phrase "the protection fees charged on it" occurs nowhere. |
| **B-2** — invented "and not at any earlier stage" | **CLOSED**, with its source root | `grep` → 0 corpus-wide. Replaced by the charter's own positioned sentences, including "the line price is brought to the nearest cent **however it is worked out**", which pins the rounding for all three line-price bases without naming the factor that supplies them. |
| **B-3** — a struck fragment leaving a subject with no predicate | **CLOSED** | `~~` occurs 0 times corpus-wide. Judged below. |
| **B-4** — invented rounding of the daily share | **CLOSED** | `grep "daily share"` → 0. The charter's ladder now carries "brought to the nearest cent once the spreading and the taking have both been done **and at no earlier step**", in both tiers, with a worked example (145.00 ÷ 13 × 2 = 22.307692… → 22.31) built to expose the alternative. |

## The two judgement calls

**The withdrawal-note device — faithful, and better than what it replaced.** The surviving text carries
exactly the residue and is grammatical: the orphaned noun phrase is recast as the condition it always was,
with "the young-driver surcharge" supplied as the subject of "is posted", and it states nothing about the
amount or its basis, which is what was retired. Quoting the retired fragment is not re-presenting retired
content but discharging the retired-surface requirement — a retired clause must keep a bearing document that
writes it as retired, and the only way to bear a clause is to state it. It cannot be mistaken for a rule in
force: it is in quotation marks, prefaced "formerly computed", and the sentence containing it ends "is **no
longer in force** and must not be applied." It is also more robust than the strikethrough, which depended on
`~~` surviving into whatever surface the reader sees, and it now matches the device already used on the
other two retired surfaces. **One caveat:** the passage over-reaches by a third sentence, which is N-2.

**The empty-scope omission — correct, and rendering it would have been the defect.** The charter's new
odometer-reading definition is self-scoping — "wherever **this rule** speaks of the reservation's odometer
readings" — and `trips_ext_extension_quote` never speaks of them: its `inputs.history` touches no
`trips_usage` table, none of its 20 compute bindings reads a usage row, and none of its five ladders
mentions a reading. A conditional definition whose antecedent is never satisfied carries no semantics to
lose, and the semantics is entailed wherever it does bear — the identical sentence is carried verbatim in
**seven** factor documents, which is every factor in the product whose condition counts or reads readings.
Putting it into an extension document would have attached a rule about readings to documents that decide
nothing by them and imported the mileage cluster's vocabulary into the extension cluster. The safeguard that
makes the omission safe is the self-scoping clause; a flatly-worded definition could not have been dropped.

## The one open finding

**N-2 — the KB adjudicates the scope of a withdrawal, where the charter is silent.** Two sentences:

- `reservation_pricing_and_line_composition_156172b6` (**new this round**): "The plan's published
  young-driver percentage and its young-driver threshold remain the plan's figures and are unaffected."
- `included_mileage_grants_and_odometer_authority_7a25439e` (**pre-existing; I missed it at round 1 and
  record that**): "The plan figures themselves — the daily allowance, the ceiling on included miles for one
  reservation, the size and the price of one block of extra miles — remain the plan's published figures and
  stand unaltered."

The charter contains no such claim: `remain the plan`, `stand unaltered`, `unaffected`, `published figures`
and `young-driver percentage` all return **0 hits**. `overwrite` carries only `superseded_clause` and
`replaced_by` and says nothing about the standing of neighbouring `parameter_schema` figures. This is the
mirror image of the failure the retired-surface rule names — the KB deciding on its own authority how far a
withdrawal reaches.

It has teeth in the untriggered domain. After the overwrite, `young_driver_surcharge_percent` (22/20/18/15/
12/10) is applied by **no rule in the charter**, yet the document declares it unaffected, in the same
sentence as a threshold that genuinely is still operative. On the Weekly plan the orphaned figure and the
policy's own constant coincide at 15 per cent, so neither task can expose it; on the Monthly plan they are
12 and 15. The mileage instance is the same shape and interacts with P-7 below.

Neither task's scored value is affected.

## Non-blocking observations recorded

**N-1 — "the block" names two quantities.** `mileage_topup_block_size_bands` raises "the block" to 900 miles
while `mileage_topup_price_computation` fixes "each **priced block of 500 miles**". The documents do
distinguish them ("the block in which included miles are **granted**" against "**priced** block") and all
three derivations took the correct reading, but no sentence says outright that they are different things,
and the alternative gives 440.00 USD against 814.40. Both documents were re-rendered this round. Recorded as
the corpus's weakest remaining link.

Also: a table in `mileage_topup_covered_period_anchor` whose rows 1–2 gained "that day counted" this round
while rows 3–4 did not (the prose settles it); two different "days still to run" values under one name in
one calculation, each now explicitly defined; and two grant-input documents that never use the words
"top-up".

## Policy-side notes

**Closed by the rework:** P-1 (prose/compute divergence on the fee limb), P-3 (unstated day-counting
conventions), P-5 (no rounding stated for the young-driver share).
**Standing:** P-2, sharpened — the surviving mileage residue "part packages are not sold" is the
contrapositive of a fragment the same overwrite withdrew, and now also sits against line-price bases that
price by the mile and drop part blocks for nothing. P-4 — `verify_member_identity` scored with no home in
this charter. P-6 — the extension baseline pins "which is 72 hours" flat against a facet column publishing
6/24/24/72/168/720 for the same named quantity. **P-7 (new)** — `block_standard` 500 and
`block_price_standard` 145.00 are exactly the Monthly column's figures while `ceiling_standard` 5000 matches
no plan, and this reservation has been granted exactly the Monthly published ceiling of 3750, so a reader
trusting the tariff card would refuse the call. **P-9 (new)** — the lead time and decision window are
hours-precise tests against a date-only `trip_end_date`. **P-10 (new)** — the retired extension-pricing
clause differs from its replacement only in where the percentage comes from. P-6 (extension decision window
against pricing before any host decision) stands unchanged.

## Gate lines on record (supplied with the brief; not re-run by this auditor)

```
check_docs.py env/... trips -> DOCS gate product=trips profile=extended docs=52
  roles={'policy':13,'factor':21,'baseline':4,'hub':4,'facet':10}
  content[min/mean/max]=1375/2547/4001  required quantitative keys=151 task_tools=4
  prerequisite edges=2  [PASS] mechanical gates ...  DOCS OK
check_traceability.py .../trip_booking_and_settlement_desk -> TRACEABILITY OK (0.json 15/0; 1.json 16/0)
```

Neither gate can see N-2: a sentence asserting that a `parameter_schema` figure survives a withdrawal is
structurally indistinguishable from a legitimate restatement of a facet figure.

## Rounding: tie-freeness confirmed from the published side

The brief's sibling-difficulty finding was tested here. I re-implemented every rounding point in exact
rationals (`fractions.Fraction`, not `Decimal` — `Decimal //` truncates where the evaluator floors) across
both tasks and every worked figure published in the corpus: **33 rounding points, 0 ties.** The closest
approach to a half-cent tie is 0.1 of a cent (`11.5% of 633.60 = 72.864`, in the reservation-pricing worked
example); the two inexact points in the scored answers are `10% × 1084.16 = 108.416` (0.1 of a cent) and
`108.42 ÷ 14 × 2 = 15.4885714…` (0.357 of a cent). Binary-double evaluation agrees with the exact rational
at every point. **This charter is tie-free on the published side**, so the stated rounding mode is
sufficient, and the source auditor's conclusion is independently corroborated.

## Files

- `env/env_0015_car_sharing_marketplace/audits/runtime_context/trip_booking_and_settlement_desk/0.md`
- `env/env_0015_car_sharing_marketplace/audits/runtime_context/trip_booking_and_settlement_desk/1.md`
- `env/env_0015_car_sharing_marketplace/audits/policy_kb/trip_booking_and_settlement_desk/0.md`
- `env/env_0015_car_sharing_marketplace/audits/policy_kb/trip_booking_and_settlement_desk/1.md`

No document was edited and no fix was arranged.

---

# revision_3 — closing checklist, round 3

Corpus `e475a3d84e4cc02711c52baa43f580f7566fca9a0c953217f5f75ff45212f699`; charter **byte-identical to round
2**. Three documents changed, all base-policy documents bearing a retired surface. Revisions 1 and 2 above
are untouched.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** |

**All three parts pass on both tasks. The difficulty closes.**

## Isolation: what I did, and why

**Forcing analysis, not a fresh blind re-derivation — and the choice is provable rather than a judgement
call.** The charter is byte-identical (197,369 bytes); the seeded worlds are unchanged (re-queried through
the harness); and **none of the three changed documents supplies a computation input** — all 4 computation
documents, all 21 factor documents and all 4 hubs lie outside the changed set, verified per file. With an
identical charter, an identical world and an identical input set, a fresh derivation consumes exactly what
round 2's did and must return the same four values. Commissioning one would have tested nothing.

**What I did commission** is one narrowly-scoped fresh reader, no prior context and no source access,
pointed at the only surface that changed: the three retirement surfaces. The risk a deletion creates is
whether a careful reader can still tell in-force from withdrawn — a reader-perception question I am the
worst possible judge of, having read these documents three times. It produced this round's one substantive
observation, and independently corroborated the dependency-form result.

## The diff, established without relying on mtime

mtime splits 49/3 across a **one-second** boundary, which is worthless as evidence, so the verification
rests on content and arithmetic. The three edits are −323, −122 and −50 characters; the corpus total moved
from an implied 132,453 to a measured 131,958. **The three edits account for all 495 characters of
corpus-wide change; the residual attributable to the other 49 documents is exactly 0.** Two of the three
round-2 lengths are figures I recorded myself at round 2, and both reconcile to the character (3576 + 323 =
3899 ✔; 3423 + 50 = 3473 ✔). Load-bearing content re-checked directly: both prerequisite sentences and
restatements, four tool names each in its own hub, all four baseline constants, and every round-2 repair.

## N-2 — closed at all three sites

| Site | Edit | Verified |
|---|---|---|
| `included_mileage_grants_and_odometer_authority_7a25439e` | the "remain the plan's published figures and stand unaltered" sentence deleted, with the "What survives of the clause…" sentence beside it | ✔ |
| `reservation_pricing_and_line_composition_156172b6` | the "remain the plan's figures and are unaffected" sentence deleted | ✔ |
| `extension_requests_and_extended_time_pricing_1ad7935c` | the meta-phrase deleted, residue re-seated | ✔ |

**The re-seating preserves exactly the residue and adds nothing** — I checked it by arithmetic, not by
reading: the charter's base sentence minus its `superseded_clause` is, normalised, **character-for-character
identical** to the re-seated clause, which occurs once in the corpus. It was also **necessary**: here the
residue was carried only inside the deleted meta-statement, so deletion alone would have dropped a clause in
force. That was correctly caught, and it is the reason the third site could not be handled by deletion.

**I re-ran the sweep myself with 26 patterns, against the 5 hits reported: 11 hits, and I traced every one.**
None is a withdrawal claim — two are the blocked policy's own tool contract carried verbatim in its hub
(confirmed by regex; a naive substring test fails because the docstring line-wraps mid-phrase), four are
charter text verbatim, and five are the ordinary phrase "plan figures" introducing a tariff card. Direct
checks on every offending phrasing return 0 documents.

**All four retirement surfaces re-checked by residue arithmetic**: each residue stands as a clause in force,
all six superseded clauses are still quoted — each in exactly one document, its base policy's bearing
document — each under a "no longer in force" marker. None vanished, none stated as in force, none retired
that the charter did not retire.

**Full-domain forward re-scan after the deletions: 260 source sentences, 0 unmatched.** The deletions
removed only KB-originated text.

## N-1 — judged: a source matter; I agree it should be routed there

I verified the disjointness claim myself in both directions. The charter's grant policy uses `priced block`
**0** times; the pricing policy uses it 11 times, and every bare `the block` match in it is inside the
compound "the block price" — the money, not a size. The corpus mirrors this exactly, with the priced block's
500-mile figure stated in the document that needs it.

I agree with the argument for changing nothing, and for the reasons given: a sentence contrasting the two
blocks would be either an **unsourced claim** about a relationship the charter never states — the N-2 class
just removed — or a **cross-policy reference** the discrete topology forbids. There is no third option open
to a renderer. And the ambiguity is resolvable as it stands: the price baseline defines its own unit with
its own figure, and both uncontaminated derivations at round 2 took the correct reading. **N-1 is not a KB
finding**; it is a property of the charter's naming scheme, recorded as **P-11**.

## Did the three changed documents introduce a new defect? No

Two are pure deletions; the third is a deletion plus a re-ordering whose re-seated text is character-
identical to the charter's residue. One substantive observation, which is a pre-existing hazard the
deletions have **unmasked** rather than a new defect — and I record it against myself, having passed over
its ingredients twice:

**P-2, sharpened again.** The fresh reader reached the right answer cold — "Part packages are not sold." is
in force — but reported that its confidence "rests only on the formal exhaustiveness of a four-row table,
and a careful reader who reasons about substance has nothing in the document to stop them from concluding
the opposite." The withdrawal table lists the surviving sentence's near-equivalent; the provenance column
announces that a whole three-limb clause on buying further miles was withdrawn; the word "packages" is
**orphaned**, its introducing clause being the withdrawn one; and the preamble's "fragments of the wording
above" is accurate only on the charitable reading, since none of the four appears in the body. The root is
P-2 — the residue is the contrapositive of a fragment the same `overwrite` withdrew, so that withdrawal is
normatively empty and the survivor necessarily reads like debris. The KB carries both sides exactly as the
charter leaves them and the forward scan confirms the residue stands as a clause in force, so this is **not
a bijection failure** and does not change the verdict. It does strengthen the case for routing P-2 to the
source layer.

**On the deletion that unmasked it:** removing "What survives of the clause on buying further miles is…" was
**not compelled** by my N-2 ruling — N-2 named claims the charter cannot supply at all, whereas "what
survives is X" is derivable by arithmetic from the base sentence and the `superseded_clause`, making it a
same-source restatement. Removing a derivable restatement is never itself an omission, so the deletion is
**not a defect**, and it is independently defensible: the KB should not smooth over a charter oddity. I
record only that it was not required and that it had a cost an independent reader detected. I propose no
restoration.

**One reported claim confirmed only in part.** "All three retirement surfaces now use one device" is true of
the **residue-placement** device — all three now state the residue as a plain clause in force with the
withdrawal marked separately — and I verify it. It is **not** true of the **withdrawal-marking** device: one
document uses a titled section with a counted preamble, a table and a provenance column; the other two mark
their single fragment inline. The fresh reader identified the same split unprompted. Not a defect — the
document with four fragments drawn from two sentences is better served by a table, and all three share the
exact quotation and the bolded "no longer in force" — but the claim holds only narrowly.

## Closing the difficulty

- The audit files correspond one-to-one with the tasks; revisions 1, 2 and 3 are all on record and older
  revisions are untouched; every comparison section carries a verdict.
- Every normative atom of the charter is entailed by the product's documents — 260 sentences, 0 unmatched —
  with nothing unborne, nothing borne with changed meaning, and no claim from outside the charter.
- Both prerequisite sentences stand verbatim, in their declared **state** form, in the hub of the policy
  they block and in no other policy's document; both hops are resolvable from the sentence, the depended-on
  documents and the records, and were derived **state-derived** at round 2 by readers who had never seen the
  charter.
- All 21 declared factor ladders are carried in full, every tier exact, each findable from the records its
  tier rests on; all four baselines are complete, self-sufficient and silent about variation.
- No tool name, route or aggregated chain is stated anywhere beyond the four hubs' own invocation blocks.
- The corpus is **tie-free** on the published side — 33 rounding points in exact rationals, 0 ties, closest
  approach 0.1 of a cent — so the stated rounding mode is sufficient.
- Gates on record: `DOCS OK` (`docs=52 roles={'policy':13,'factor':21,'baseline':4,'hub':4,'facet':10}
  content[min/mean/max]=1375/2538/4001 required quantitative keys=151 task_tools=4 prerequisite edges=2`)
  and `TRACEABILITY OK` (`0.json 15/0; 1.json 16/0`), re-run by the coordinator and not by this auditor.

**Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks.
This difficulty's rendering passes the audit.**

## Routed to the source layer, not for this skill's verdict

P-2 (a residue that is the contrapositive of its own withdrawn fragment, leaving "packages" orphaned),
P-4 (`verify_member_identity` scored with no home in this charter), P-6 (the decision-window clause against
pricing before any host decision), P-7 (the ceiling trap: `ceiling_standard` 5000 matches no plan while the
facet publishes 3750 for the plan this reservation is on), P-9 (hours-precise tests against a date-only
`trip_end_date`), P-10 (a retired clause and its replacement differing only in where a percentage comes
from), **P-11 (the charter names two different quantities "block")** and **P-12 (the extension-ceiling rule
states no consequence for exceeding the maximum)**.

