# Closing checklist — erl-kb-doc-policy-audit / air_ticketing_desk (product `air`)

Difficulty 0 of `env/online_travel_agency`. M=2, tasks 0 and 1. Revision 1.

## Part-verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** |

All three parts hold together for both tasks, so **this difficulty's rendering passes the audit**.

## Checklist

- **Audit files correspond one-to-one with the tasks.** `runtime_context/air_ticketing_desk/{0,1}.md` and `policy_kb/air_ticketing_desk/{0,1}.md`. Each task was audited and written to disk separately; neither verdict rests on the other.
- **Old revisions traceable.** This is revision 1; there is no earlier `runtime_context` or `policy_kb` audit for this difficulty to preserve.
- **Ordering discipline held.** Both `blind_answer` sections were frozen to disk (15:04, freeze declaration 14:52) **before** any source-layer material of either task was opened (15:06). No `blind_answer` was modified afterwards. No `contamination_disclosure` was required for either task: no scored value, gold parameter or intermediate reached this audit from the brief, from a side file or from any search, and no recursive grep ever had `tasks/` in its match domain.
- **The DB side was blind for both tasks.** Every fact used was landed by calling a share finder against the loaded task through the supplied harness, seeded from what the caller states; `initial_state` was never read as a document by either audit.
- **Every normative atom of the structured source is entailed by the product's docs.** 16 base policies (98 `rule` sentences), 6 extended policies, 462 brand parameter values, and every untriggered branch. Nothing unborne, nothing borne with changed meaning, no claim from outside the source.
- **All ten base eligibility conditions still read as live.** Each carried verbatim, each in exactly one document, none inside a retired block, none touched by any `superseded_clause`, none softened or hardened.
- **The retired surface corresponds exactly in both directions.** 21 `overwrite` entries → 18 distinct clauses across 9 base policies; 18 quoted-retired blocks in the corpus; no retired clause reads as governing, none vanished, and the KB retires nothing the source did not declare. The three compound base sentences that mix a surviving clause with a retired one are split so the surviving half stays in force.
- **Every prerequisite sentence stands verbatim, in its declared form, on the blocked side and nowhere else.** All four edges of this difficulty are `form: state`; each `policy_source` has exactly one hit across the 72 documents, and that hit is a fragment of the policy it blocks. Each hop is resolvable at the source's strength from the sentence, the depended-on documents and the records.

  | Edge | Sentence homed in | Hop mark (blind) |
  | --- | --- | --- |
  | `air_ext_cancelled_ticket_credit` ← `air_ext_no_show_penalty` | `travel_credit_value_basis` §1 | state-derived |
  | `air_ext_cancelled_ticket_credit` ← `air_ext_unflown_tax_return` | `travel_credit_value_basis` §1 | state-derived |
  | `air_ext_credit_release` ← `air_ext_cancelled_ticket_credit` | `credit_release_accounting_basis` §1 | state-derived |
  | `air_ext_cabin_upgrade_copay` ← `air_ext_outstanding_service_charge` | `cabin_upgrade_copay_basis` §1 | state-derived |

  **On the renderer's structural choice** — homing all four sentences in the blocked policy's *computation* document rather than its hub: judged sound. In every case the sentence is simultaneously the definition of a quantity the baseline computes from (the penalty entry and the payout entry taken off the fare, tax and service lines; the standing value; the travellers counted into the move). A solver cannot produce a number without reading it, so the dependency cannot be missed; and the hub is not left deficient, because the hub governs the write and not the arithmetic. The hop stays unrouted: no tool name, no action stated beside a state, no chain aggregated.
- **Every declared factor's ladder is carried in full, every tier exact, in its own factor document, findable from the records its tier rests on.** 30 factors across the 6 extended policies. Every tier's condition with every part of each compound condition; every window and threshold stated in figures; for each method factor the operation, base, rounding mode, precision, moment, window or day-count and order of steps exactly as the source pins them. No tier dropped, merged, rounded or softened; no threshold named under a business term without its figure; no method tier compressed. All 15 cross-product factors name their sibling product by its official name — Wanderlane Traveller Club, Travel Protection Plans, Corporate Travel Programmes — and the kinds of records they read.
- **Every baseline is complete and unhinted.** Each of the 6 computation documents carries its policy's whole `rule` — every input, default value, rounding, window, base, order and assembly — with the policy's own default constants rendered there and every product figure it reads named. A corpus-wide hedge scan returned no hit: no "unless otherwise", no "adjustments may apply", no "certain customers qualify for", no exception list, no pointer. The existence of every factor is discoverable only from the customer's records.
- **No tool name, route or aggregated chain anywhere beyond those sentences.** Each of the 6 air task tools is named only in its own policy's hub, in that hub's own invocation block. No dependency table, checklist, roadmap, route or cross-problem step list exists in the corpus; no cross-problem operational guidance; no chain-walking example or named mistake.
- **No task's opening world state written in as a policy fact.** 45 identifiers, figures, dates and party names from the two worlds were checked against all 72 documents: not one appears. 61 of 72 documents label their examples "hypothetical", and the worked figures in the computation documents are deliberately off both worlds.
- **Titles name general subjects.** All 72 read; none restates a customer request, labels a procedure for a specific situation, or mirrors a task.
- **Gates.** Per the brief, the coordinator runs both gates from the repository root and this auditor runs neither. The snapshot supplied with the brief describes the final form, because **this audit changed no document and no task**: the `docs/air` corpus sha256 at close is `a9559a298b02a2cd1f2f136cb14581755a22514bb2228b20630a2062113a06ae`, identical to the hash frozen at 14:52, and the only files written were the four audit files in the declared write domain.

  ```
  $ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/online_travel_agency air
  🔎 DOCS gate  product=air profile=extended docs=72 roles={'baseline': 6, 'policy': 16, 'facet': 13, 'factor': 31, 'hub': 6}
     content[min/mean/max]=1276/2243/3838
     required quantitative keys=183  task_tools=6  prerequisite edges=4
    [PASS] mechanical gates
    [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; …
  DOCS OK

  $ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/online_travel_agency/tasks/air_ticketing_desk
  🔎 TRACEABILITY gate  (2 tasks)
  task        copied  missing    ok
  0.json          26        0  True
  1.json          14        0  True
  TRACEABILITY OK
  ```

  The `[MANUAL REQUIRED]` line is answered by this audit: the bijection holds, in both directions, over the whole domain.

## Findings carried to the policy layer (none changes this skill's verdict)

1. **A hold standing past its window.** Task 0's November booking (`RB4TQZ`, Economy Flex, hold window 24 hours) was opened 2026-09-14 and still stands at `held` at `frozen_time` 2026-09-16 10:42 CDT. No clause requires the desk to act on a lapsed hold and no computation reads the hold's age, so the scored solution is unaffected and the documents are faithful to the charter. A world-seeding observation.
2. **Tier-scheduled sibling-product terms described as "read from that programme's own record".** Five Corporate Travel Programmes values (two booking fees, rebate threshold, rebate percentage, approval levels, credit limit) and four Wanderlane Traveller Club values (tier bonus, points per dollar, redemption value, fee waiver) are published per tier in the sibling charter rather than carried on the DB row. The locator phrase is imprecise, but it is not normative, it changes no value entailed — the row's `variant_name` is exactly the key the schedules are indexed by, and the source's own `cross_category.reads` names `variant_name` first — and the blind audit reached every one of the nine by that route before the source was seen. Recorded, not a red light.
3. **A persona/record wrinkle in task 1.** `user_scenario` places the booking on "Monday evening" while `booked_date` is 2026-09-15, a Tuesday. No scored figure turns on it: the lead-time loading is 10.00 USD at either 23 or 24 days.

## Coverage boundary, stated honestly

This skill is organised per difficulty and audits only the product this difficulty claimed, `air`. **Cross-product contradictions are outside its detection range.** The `club`, `care` and `biz` corpora were read here only to confirm that the values the air factor documents name by official product name are in fact published and reachable — never as a criterion against the air corpus. The base-type products claimed by no difficulty remain outside this skill's scope entirely.
