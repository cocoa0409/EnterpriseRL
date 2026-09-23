# KB-document policy audit — closing checklist for crop_input_desk

## revision_1 — 2026-09-18

Difficulty `crop_input_desk`, product `agronomy` ("Crop Input Purchasing Accounts"), M = 2 tasks.
Auditor independent of the render author and of the erl-task-policy-audit auditor. No document, task, blueprint or runtime file was edited; the write domain was `audits/policy_kb/crop_input_desk/` and `audits/runtime_context/crop_input_desk/` only.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **KB-RUNTIME RED** | PASS | PASS |
| 1 | **KB-RUNTIME RED** | PASS | PASS |

**The difficulty's rendering does not pass this audit.** Both bijection and dependency-form hold across the whole product; both failures are on the runtime part, and both have their root on the policy side.

## Closing checklist

| Item | Status |
| --- | --- |
| Audit files correspond one-to-one with the tasks | ✔ `runtime_context/crop_input_desk/{0,1}.md`, `policy_kb/crop_input_desk/{0,1}.md` |
| Blind answer frozen and hashed before any source-layer read | ✔ sha256 `54f8f5f8…f82f` (task 0), `6fcab5d2…cad1` (task 1); no `blind_answer` text was modified after the reveal |
| Old revisions traceable | ✔ no prior revision; this is revision 1 |
| Every comparison section carries a verdict | ✔ |
| Every normative atom of the structured source entailed by the product's docs | ✔ eleven base policies homed; five extended policies' rules, baselines and tool contracts homed; all `params`/`per_tier` tables carried for all six programmes |
| Nothing borne with changed meaning; no claim from outside the source | ✔ |
| All three prerequisite sentences verbatim, in their declared `state` form, on the blocked side, in no other policy's documents | ✔ each occurs in exactly one document, and that document is the blocked policy's own |
| Every hop resolvable at the source's strength from the sentence, the depended-on rules and the records | ✔ all three hops derived **state-derived** in the blind audits, none pre-solved |
| All 24 declared factors' ladders carried in full, every tier exact, in their own factor documents | ✔ swept tier by tier against `factors[].ladder` |
| Every factor findable from the words the customer's records use; the five cross-product factors name their product officially | ✔ "Custom Application and Field Services", "Grain Storage and Conditioning Agreements", "Grain Marketing Contracts" (×2), "Membership and Patronage Equity" |
| No other problem's tool name, route or aggregated chain anywhere | ✔ each of the five tool names occurs in exactly one document, its own policy's hub |
| All eight `overwrite` clauses carried and written as retired; none retired that the source did not retire | ✔ |
| Gates re-run on the final form | not re-run by this auditor, per the brief; no document changed during this audit, so the orchestrator's snapshot of 2026-09-18T11:34 stands: `check_docs.py … agronomy` → **DOCS OK** (53 docs, roles factor 24 / facet 8 / hub 5 / baseline 5 / policy 11, 150 quantitative keys, 5 task tools, 3 prerequisite edges, all mechanical gates PASS, semantic bijection **MANUAL REQUIRED** — discharged by this audit); `check_traceability.py … tasks/crop_input_desk` → **TRACEABILITY OK** (task 0: 29/0; task 1: 17/0) |

## The two runtime failures

**1. Task 0 — the `restocking_rate` ladder's day count has no endpoint in the visible materials.**
*prompt_return_restocking_rates_for_big_buyers_44a0e9d7* renders the source's ladder verbatim — "Where the product came back within seven calendar days of the delivery it was billed on, the delivery date counting as day zero…" — but neither the ladder nor any other visible sentence says what day "the product came back" is read from. The seeded world supplies an approved, member-signed `product_return` order dated 2026-06-15 against a delivery of 2026-06-08, giving day 7 and the 4 percent band; the source's hidden binding is `days_back: DAYS(line_date, NOW)`, giving 10 days and the 8 percent band. Three scored values differ in consequence: `credit_amount` 15513.62 vs 15196.00, `service_charge_amount` 319.35 vs 320.20, `payment_amount` 36850.00 vs 37030.00. The rendering is faithful; the ambiguity is the source rule sentence's.

**2. Task 1 — no rounding mode is fixed for an intermediate step, and the scored value turns on it.**
*the_money_taken_on_a_prepay_booking_5a4c91f7* renders the source's assembly verbatim — "the product rounded to two decimal places" — with no mode named, as do all five baselines of this product; the only mode anywhere in the runtime-visible view is the tool parameters' "rounded half away from zero". The gross ceiling lands exactly on a half cent (214365.85 × 110 ÷ 100 = 235802.435) and the source's `RND(...)` settles it by binary floating point. `booking_amount` 228137.44 vs the scored 228137.43. Every other item of task 1, including the whole problem tree and `discount_amount = 5083.25`, matched exactly.

## Policy-side problems reported (they do not change the verdicts above)

1. **Two base `formula` blocks survive the retiring of the clauses they implement.** `agronomy_finance_charge.formula.finance_charge_amount` is the per-invoice basis that two `overwrite` entries retire, and `agronomy_returns_and_credits.formula.{discount_amount, amount}` is the restocking basis that another retires; neither formula is itself declared retired, so the KB faithfully carries both as clauses in force. They stand in *service_charges_on_an_overdue_crop_input_invoice_b3517a2c* ("Rate applied to the invoice amount") and *what_comes_back_to_the_plant_and_on_what_terms_e82c40f7* ("The restocking arithmetic"), each contradicting its own document's withdrawal notice and the corresponding basis document. This is an undeclared override on the policy side.
2. **The two runtime failures above are themselves policy-side in origin** — a rule sentence with an unnamed endpoint, and a rounding convention left to the host language.
3. **`verify_member_identity` (blueprint share tool) counts `member_number` among its matching details** while its own docstring states "The membership reference is used only to pull the right profile up and never counts as one of those matching details". Both personas of this difficulty offer exactly the membership number and the mobile, and both GTs pass exactly those two and call them "the two details the caller states". An agent that trusts the prose would judge itself one detail short. Outside this product's charter; recorded for the scenario owner.
4. **Tool-contract format examples are live rows of task 0's world.** `IN-4410287`, `DT-2210554` and `PY-901772` are used as "for instance" examples in five documents, copied verbatim from `task_tools.py`. `IN-4410287` is the older crop protection invoice on the very account the return credit is written on — the closest wrong value for the argument it illustrates. A seeding hazard in the tool contract, not a rendering defect.

## Coverage statement

This audit covers only the product `agronomy`, which this difficulty claims. Cross-product contradictions are structurally suppressed (every document names its own official product name, and each difficulty's policy content is single-homed) but are **not** proved absent, and lie outside this skill's detection range. Base-type products claimed by no difficulty are entirely outside this skill's scope.

---

## revision_2 — 2026-09-18

Revision 1 above is preserved unaltered. Re-audit of the re-rendered corpus (17 of 53 documents moved, topology frozen) against the moved worlds. Source at `agronomy.extended.yaml` sha256[:16] = `e77a90eb2e24e3a5`, `task_tools.py` = `fb62107a7cae45c5`. Write domain unchanged; no document, task, blueprint or runtime file was edited.

## Part verdicts

| Task | Runtime re-derivation | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | revision 1 RED → **PASS** | **PASS** | **PASS** |
| 1 | revision 1 RED → **PASS** | **PASS** | **PASS** |

**The difficulty's rendering passes this audit at revision 2.**

## The decisive check

Both tasks' scored values were re-derived from `docs/agronomy/*.json` plus tool-shaped queries against the re-queried worlds, and the GT was opened only afterwards to confirm. **All five agree exactly:**

| Task | Write | Derived from the corpus | GT |
| --- | --- | --- | --- |
| 0 | `issue_return_credit_6859ca91` → `credit_amount` | 15196.00 | 15196.00 |
| 0 | `assess_overdue_service_charge_aaf992aa` → `service_charge_amount` | 320.20 | 320.20 |
| 0 | `post_member_arrears_payment_ad47b93a` → `payment_amount` | 37030.00 | 37030.00 |
| 1 | `grant_season_volume_discount_cc5ed557` → `discount_amount` | 5083.25 | 5083.25 |
| 1 | `book_prepay_commitment_189dfe27` → `booking_amount` | 228136.14 | 228136.14 |

Every one of the 24 tier selections matched the GT's `tier_taken`, and every one of the 24 `baseline_result`s still differs from its expected value, so no factor has lost its weight.

## The two round-1 REDs, verified closed

**1. The restocking-rate day count (task 0).** The ladder now names both endpoints in the clause, in the table column header, and in a dedicated sentence that forecloses the competing reading: "The count runs from the date the delivery was invoiced, which is day zero, to the handling date on which the credit is worked out, **and not to any other day**." Applied to the records — `IN-4420915` invoiced 2026-06-08, handling date 2026-06-18 — this forces 10 days and the 8 percent band. The approved return order of 2026-06-15, which produced the divergence in round 1, is no longer a candidate endpoint. **Closed at the document level, not merely on the numbers.**

**2. The half-cent rounding (task 1).** Closed on both legs, and I tested each. *First*, the corpus now names the mode: 34 occurrences of "rounded half away from zero to two decimal places" across the five extended computation documents and the tool-parameter blocks. The only four unmoded roundings left are in the four base-policy documents whose base policies did not move — correct, since naming a mode there would have added to the source; I checked that none of the four lies on a scored path, and that the two which could have been read against an extended basis are now expressly withdrawn for that path. *Second*, I re-ran every rounding moment of both tasks under exact decimal arithmetic and under binary floats: **the two agree at every step of both tasks, and no intermediate lands on a half cent.** The two seeded moves (a payment of 8000.00 → 7999.98 in task 0's ledger, a unit price of 862.00 → 861.98 in task 1's) are what carry the two former boundary values clear.

## Nothing regressed

| Check | Result |
| --- | --- |
| 53 documents, same filenames, same role counts | ✔ |
| All 3 prerequisite sentences verbatim, `state` form, one document each, that document the blocked policy's own | ✔ verified by search over all 53 |
| Both problem trees still derivable from the records | ✔ no service charge for the statement month then running; no credit memo answering the 2026-06-15 return; no volume discount on task 1's ledger |
| All 8 `overwrite` clauses carried and marked retired; none retired that the source does not retire | ✔ verified mechanically against `overwrite[]` |
| All 24 factor ladders complete, every tier figure in its own document | ✔ 24/24, no missing tier figures |
| 8 facet tables × 6 programmes each | ✔ |
| 11 base policies homed | ✔ |
| Each of the 5 tool names in exactly one document, its own hub; no factor document names a tool | ✔ |
| No route, checklist, ordered step list or cross-problem guidance | ✔ |
| No added policy (confirm / review / notify / escalate scans) | ✔ |
| No opening world state as a policy fact; no seeded identifier of either world in any document | ✔ |
| All 53 titles general subjects | ✔ one title moved, to a more general form |
| Tool schemas and owners unchanged; identity still clears at two details | ✔ |

## Other round-1 items

- **Policy-side item 1 (base `formula` blocks surviving the retiring of their clauses) — CLOSED.** Two new source rule sentences are carried verbatim in the two extended hubs, withdrawing the base arithmetic for the extended path. I tested the source auditor's argument rather than taking it: the two base `rule` texts do not contain those formulas as substrings, so `overwrite` genuinely could not name them, and the remedy states the same semantics in the extended policy where it belongs. Examined as prose, neither sentence adds a step, names another problem, a tool or a route.
- **Policy-side item 3 (format examples that were live rows) — CLOSED on the seed side.** `IN-4410287`, `DT-2210554` and `PY-901772` remain as "for instance" examples copied from the tool contracts, but the seeds were renumbered to `IN-4410953`, `DT-2210731` and `PY-903486`. Re-checked against both re-queried ledgers in full: no collision remains.
- **Policy-side item 2 (`verify_member_identity`) — not reopened**, per the coordinator's decision; re-tested and still clearing at two details. Recorded as a known base issue of the frozen blueprint.

## The source auditor's closing statement, tested

*"Nothing in any normative sentence of this difficulty now rests on seeing a binding."* I tested this rather than taking it, by walking each binding that decides a scored value and asking whether the visible prose fixes it: the return-credit day count, the overdue-days baseline and both `overdue_clock_anchor` tiers, the arrears age step, the months-open count, every `RND` moment, the net-versus-gross bushel measure, the whole-life scope of the highest crop-protection price, and every window's endpoint. **All are now fixed by prose**, which is why the re-derivation reproduced all five scored values. The statement holds for everything that decides a number in these two tasks.

It is not, however, unqualified for the corpus as a whole, and I record two residuals honestly:

1. *which_price_a_returned_line_is_credited_at_9c16b4ea* — "the most recent prepay booking standing on the account" does not name the field the ordering is taken on. The tier fires in neither task, so it decides nothing scored. The render agent was right to invent no wording for it.
2. The credit memo's embedded `discount_amount` versus "every discount granted on the account" — decisive for task 1's booking if misread (227728.41 instead of 228136.14). I judge the corpus to determine it against the misreading, but by inference across three documents rather than by a sentence.

Both are policy-side residuals, already named by the source auditor or falling out of the same class, and neither is a rendering defect.

## Closing checklist

| Item | Status |
| --- | --- |
| Audit files one-to-one with the tasks; revision 1 preserved, revision 2 appended | ✔ |
| Every part carries a revision-2 verdict | ✔ |
| Every normative atom of the moved source entailed by the docs | ✔ including the two new withdrawal sentences, every named endpoint and every named rounding mode |
| Nothing borne with changed meaning; no claim from outside the source | ✔ |
| All prerequisite sentences verbatim, declared form, blocked side only | ✔ |
| All 24 ladders complete and findable from the records | ✔ |
| No tool name, route or aggregated chain beyond those sentences | ✔ |
| Retired surface intact and complete | ✔ |
| Gates | not re-run by this auditor, per the brief; no document changed during this audit, so the orchestrator's snapshot of 2026-09-18T15:17 stands — DOCS OK, TRACEABILITY OK (0.json 29/0, 1.json 17/0) |

## Coverage statement (unchanged)

This audit covers only the product `agronomy`. Cross-product contradictions are structurally suppressed but not proved absent; base-type products claimed by no difficulty are outside scope.

---

## revision_3 — 2026-09-18

Revisions 1 and 2 above are preserved unaltered. Source at `agronomy.extended.yaml` sha256[:16] = `7e467c191418fb6a`, `task_tools.py` = `fb62107a7cae45c5`. Both worlds re-queried (the stale-value trap a sibling auditor reported was taken seriously) and confirmed unchanged from revision 2 at every row. Write domain unchanged; no document, task, blueprint or runtime file edited.

## Part verdicts

| Task | Runtime re-derivation | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** |

**The difficulty's rendering passes at revision 3.** All five scored values re-derived from the corpus and the re-queried records, GT opened only afterwards, all five agree: 15196.00 / 320.20 / 37030.00 and 5083.25 / 228136.14.

## Part 1 — the round-3 tightening

The qualification — "*as a discount line of its own, which is an early pay, volume, prepay or programme rebate discount and never the restocking charge withheld inside a credit memo*" — closes the revision-2 residual I declined to sign off. It is carried **verbatim** in the computation document's prior-season-spend step and in both substituting tiers of the prior-spend factor (clause and table). The misreading it bars would have given 227728.41; it is now excluded by the text of the step that performs the subtraction, on both the default and the substituted path, rather than by inference across three documents.

Tested for over- and under-reach against the discount enumeration in *the_three_discounts_a_crop_input_invoice_can_carry_8c4a2df0* (early pay, volume, prepay, plus the programme rebate outside the stacking basis): the four named kinds are exactly that enumeration, so the sentence selects the same set the binding sums. No atom added, none dropped.

**The render agent's fall-through call: correct, and required.** The source carries the qualification in all three tiers of `prior_season_spend_basis`, including the `otherwise` tier — but that tier *is* the baseline (`baseline: {prior_net_spend: 'RND(spend_recent + discounts_standing, 2)'}`) and its prose restates the computation document's default. Hosting the qualification there would have meant restating that default inside a factor document, which is what the corpus's discrete topology forbids, and I would have recorded it under `dependency_form` as a KB-EXPLICIT finding. I checked the convention rather than assuming it: **all twenty-two factor documents with an explicit fall-through use the "no substitution" form, and not one restates its computation document's default.** Nothing is lost — every occurrence of "discount granted on the account" on that path now carries the qualification, and the fall-through restates no measure, so has nothing to qualify.

## Part 2 — OBS-17: **CLOSED — PASS, not a RED**

The route to 36950.00 exists and I reproduced it; it is not defensible.

**Verified first, taken on trust nowhere.** The service-charge limb is inert *exactly* — §2 subtracts the discounts and §5 adds the same set back at 100 percent, so both readings give a rate base of 105956.28 and a charge of 320.20. The settlement limb is not inert: 103106.52 → 103639.58 → 57001.77 → 36946.77 → **36950.00**.

**What excludes it — three legs, the first a sentence in the clause that performs the subtraction:**

1. **The governing sentence names credit memos as a coordinate term of its own.** §1 of *building_the_arrears_settlement_figure_7f13ca8e*: "less every payment posted to the account, **every credit memo written on it** and every discount granted on it." Reaching 36950.00 means deducting the same row under two of those three heads — 1155.00 in all for a row that moved 1016.40. Not a second reading; a misapplication of an unambiguous sentence. The same structure stands in the service-charge baseline §2.
2. **The ledger's running balance.** Summing `amount` down the account reproduces `balance_after` at all fourteen rows, and the credit memo moves the balance by exactly −1016.40. The 138.60 never moved the balance under any head. Checkable from records the agent already holds, without any document.
3. **Corroboration and sign.** The discount enumeration excludes a restocking charge; the returns document identifies 138.60 by its own arithmetic (1155.00 × the Seasonal Terms 12 percent); the `agronomy_discount_granted` rows carry a `discount_type` the credit memo row lacks; and 138.60 is money *withheld from* the member, so calling it a discount *granted* inverts the sign.

**The asymmetry with task 1, verified by reading both bindings side by side:** task 0's sentence has a credit-memo term, so the misreading double-counts; task 1's has none, so it double-counted nothing and the sentence gave no bar. That is why one needed a sentence and the other does not. The referral's characterisation was accurate.

**A fourth route the referral did not name:** taking the credit memo at its `extended_amount` of 1155.00, with no discount misreading at all, also lands on 36950.00 — recorded because it shows the wrong figure has more than one wrong path to it. It fails a step earlier, perturbing the service charge to 319.83 against 320.20, and is foreclosed by leg 2 as well.

**On the record, with its limit.** The exclusion is carried by §1's three-term list, corroborated by the running balance and the two documents above. It is **structural, not lexical**: it holds because the credit-memo term stands in the same sentence as the discount term. Were a later source round to separate those terms, drop the credit-memo term from that sentence, or add a task-0-side binding that subtracts discounts without also subtracting credit memos, the bar would vanish and OBS-17 would reopen on that binding. The dependency is named; no wording is proposed.

## Regression — nothing moved

| Check | Result |
| --- | --- |
| 53 documents, same filenames and role counts | ✔ |
| 3 prerequisite sentences verbatim, `state` form, one document each, blocked side only | ✔ |
| Both problem trees still derivable from the re-queried records | ✔ |
| 8 `overwrite` clauses carried and marked retired; the 2 extended withdrawal sentences still in their hubs | ✔ |
| 24 ladders complete, every tier figure in its own document | ✔ 24/24 |
| 8 facet tables × 6 programmes; 11 base policies homed | ✔ |
| 34 moded roundings; the same 4 unmoded base-policy documents | ✔ |
| Each of the 5 tool names in exactly one document, its own hub | ✔ |
| No route, checklist, added policy or seeded identifier anywhere | ✔ |
| All 53 titles general subjects | ✔ |
| Exact-decimal vs float at every rounding moment of both tasks | ✔ agreement everywhere, no half cents |
| Tool schemas and owners unchanged; identity clears at two details | ✔ |

## Open items at close of revision 3

- **`which_price_a_returned_line_is_credited_at_9c16b4ea`** — "the most recent prepay booking standing on the account" names no ordering field. Fires in neither task, decides nothing scored. Policy-side residual, unchanged.
- **`verify_member_identity`** — counts `member_number` among its matching details while its docstring says the membership reference never counts. Scenario-wide, frozen blueprint, recorded by the coordinator as a known base issue. Not reopened.
- **The four base-policy documents' unmoded "rounded to two decimal places"** — correct, since those base policies did not move; none lies on a scored path.

## Coverage statement (unchanged)

This audit covers only the product `agronomy`. Cross-product contradictions are structurally suppressed but not proved absent; base-type products claimed by no difficulty are outside scope.
