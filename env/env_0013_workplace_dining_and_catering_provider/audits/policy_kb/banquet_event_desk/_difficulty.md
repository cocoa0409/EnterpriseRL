# Difficulty closing checklist — banquet_event_desk (product: banquet)

Auditor: independent KB auditor (did not author these documents, did not judge this difficulty's policy side). Revision 1.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | **PASS** (`runtime_context/banquet_event_desk/0.md`) | **PASS** (`policy_kb/banquet_event_desk/0.md`) | **PASS** |
| 1 | **PASS** (`runtime_context/banquet_event_desk/1.md`) | **PASS** (`policy_kb/banquet_event_desk/1.md`) | **PASS** |

Blind derivations were frozen to disk before any source-layer artefact was opened, and were not modified afterwards. Both matched the source layer on every scored value, every argument, every owner and the whole problem tree:

| Task | Quantity | Blind | Source | Baseline (fall-back) |
| --- | --- | --- | --- | --- |
| 0 | `contracted_value_usd` | 69802.20 | 69802.2 | 50726.00 |
| 0 | `guaranteed_headcount` | 268 | 268 | — |
| 0 | `cancellation_charge_usd` | 53211.65 | 53211.65 | 41881.32 |
| 1 | `invoice_amount_usd` | 143520.00 | 143520.0 | 131160.00 |
| 1 | `payment_amount_usd` | 68045.00 | 68045.0 | 143520.00 |

## Closing checklist

- **Audit files correspond one-to-one with the tasks**, two of each, and every comparison section carries a PASS. Old revisions: none — this is the first `policy_kb` revision for this difficulty; `runtime_context` likewise.
- **Every normative atom of the structured source is entailed by the product's docs.** All eleven base policies, their eligibility and evidence contracts, all 55 `parameter_schema` keys across all six variants, all four extended policies' baselines and all 23 declared factors were traced to a prose home. Nothing unborne, nothing borne with changed meaning, no claim from outside the source.
- **Both prerequisite sentences stand verbatim**, in their declared `state` form, in a document of the policy each blocks (`raising_a_cancellation_charge_on_an_agreement_b25b78eb`; `settling_an_event_bill_by_the_client_520cc538`) and in no other policy's document. Each hop is resolvable at the source's strength from the sentence, the depended-on policy's own rule and the records; both were derived blind and marked **state-derived**, neither pre-solved.
- **Every declared factor's ladder is carried in full**, tier for tier, with every threshold stated in figures for all six packages, in its own factor document, findable from the words the customer's records use. The two cross-difficulty factors (`committed_food_value`, `catering_account_food_settled_here`) name the sibling product by its official name and the kind of record they read; the runtime KB is a single corpus over `docs/`, so the sibling's Schedule 1 is reachable.
- **No other problem's tool name, route or aggregated chain is stated anywhere.** Each of the four tools appears only inside its own policy's invocation block; no document names another document or a policy id; no step list, dependency table, checklist or cross-problem example exists in the corpus.
- **All ten `overwrite` entries checked**, including the two charter-wide duplicates (the `banquet_settlement_terms` deposit clause and the `banquet_combination_venue_interaction` mutual-exclusivity clause, each superseded by two policies). One retirement marking per base clause; each superseding policy's own replacement rendered verbatim in its own documents; nothing consolidated, nothing vanished, nothing stated as in force.
- **Referred item R2-O1: resolved at the KB layer.** The published corpus does not leave the retired dispute-window anchor standing; `event_invoice_payment_and_credit_control_cfd5f92c` §4 states that the surviving counting sentence's anchor "governs nothing", and `day_a_billing_dispute_window_runs_from_92b8c540` states the anchor the `overwrite` puts in force. On task 1's world a careful reader lands on one figure (68045.00) rather than the rival 66845.00 the dead anchor would produce. The source-layer looseness that produced the referral is recorded as a policy-side note at `policy_kb/banquet_event_desk/0.md` §E.1.
- **Gates.** The snapshot supplied with the brief is on record in each task file (`DOCS OK`; `TRACEABILITY OK`). Per the brief the auditor runs neither, and this audit modified nothing under `docs/`, `tasks/`, `blueprint/` or `erlbench/`, so the snapshot stands as the final form.

## Policy-side notes carried forward (they do not change this skill's verdicts)

1. The source's `overwrite` retires only the `condition` of `banquet_payment_terms.dispute_window`, leaving that base rule's separate counting sentence naming the retired anchor. (`0.md` §E.1)
2. `banquet_settlement_terms` keeps "Where the deposits applied exceed the gross charge, no bill is raised …", which presupposes the retired deposits-applied-before-issue clause. Inert on both tasks. (`0.md` §E.2)
3. `banquet_ext_cancellation_notice_value.inputs.history` declares `setup_style` from the booking entry while the rule and the compute read it from the guarantee entry — an authoring field only. (`0.md` §E.3)
4. `banquet_msr_cancelled_events_12m` counts a different family over a different anchor than the repeat-uplift factor it appears to summarise, and has no prose home. (`0.md` §E.4)
5. The settlement `compute`'s `billed_count` is the delivered entry's guaranteed count, while the prose the KB renders calls it "the count the bill was priced on"; divergent only in an untriggered branch, and only material for the catering-account tier. (`1.md` §F.2)
6. `deposit_money_set_against_the_bill` states its tiers booking-by-booking while its pool sentence and the compute are agreement-wide; both readings give the same figure here. (`1.md` §F.3)

## Coverage statement

This audit covers only the product this difficulty claims (**banquet**). Cross-product contradictions are outside this skill's detection range by design; sibling corpora were read only where a banquet factor names a sibling figure, and never used as a criterion. Base-type products claimed by no difficulty are entirely outside this skill's scope.

## Difficulty verdict

**Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks.** This difficulty's rendering passes the audit.
