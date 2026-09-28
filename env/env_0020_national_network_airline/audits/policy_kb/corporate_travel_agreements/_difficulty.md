# Difficulty close-out — corporate_travel_agreements (product business)

## revision_1 (2026-09-24)

### Per-task part verdicts

| Task | KB-RUNTIME (blind audit) | KB-BIJECTION (full-domain scan) | KB-EXPLICIT (dependency form) | Files |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | `audits/runtime_context/corporate_travel_agreements/0.md`, `audits/policy_kb/corporate_travel_agreements/0.md` |
| 1 | PASS | PASS | PASS | `audits/runtime_context/corporate_travel_agreements/1.md`, `audits/policy_kb/corporate_travel_agreements/1.md` |

### Closing checklist

- [x] The audit files correspond one-to-one with tasks 0 and 1. This is revision_1, so there are no older revisions to preserve.
- [x] Both blind answers were frozen and hashed together (2026-09-24T19:27:55Z) before any source-layer read. contamination_disclosure: none for either task.
- [x] Every normative atom of the seven extended policies and of the base section is entailed by the business corpus, with no changed meaning and no unsourced claim. The seven extended policies are late fee, card-paid points, Gold price, retro claim, enrollment bonus, milestone bonus and domestic award price.
- [x] All five prerequisite sentences stand verbatim, in their declared state form, in a document of the policy they block and in no other policy's document:
  - 2 in the Gold hub
  - 2 in the domestic-award hub
  - 1 in the milestone-bonus hub
- [x] Every hop is resolvable from its sentence, the depended-on rule and the records. The blind audit derived all five hops as state-derived.
- [x] All 38 declared factors (16 for task 0 + 22 for task 1) carry their full ladders in their own documents. Each is findable from the words of the records its tier rests on. This matches the gate's role count (factor 38).
- [x] The seven baselines are complete and silent about modifiers. Their fall-backs are definite and differ from the scored values: 279.60, 822, 3800, 486, 2500, 5000, 1600.
- [x] No document states another problem's tool name, a route, an aggregated chain or a task-mirroring title.
- [x] Gate lines on record. These are the coordinator's run on the published corpus; per the brief, this auditor does not run gates:
  - `check_docs.py env/env_0020_national_network_airline business` → "DOCS OK" (71 docs)
  - `check_traceability.py …/tasks/corporate_travel_agreements` → "TRACEABILITY OK" (0.json 21/0 True, 1.json 21/0 True)
  - This audit edited no document, so the corpus the gates saw is the corpus audited. The runtime view hash is `ddf812bd…c8d`; the corpus has 71 files.

### Policy-side notes (reported, not re-judged)

1. Base clause E2 is retired by both the card-paid and the retro-claim policies. No in-force per-segment points formula remains for ordinary (invoice-paid, booked-under) segments.
2. The retro-claim `baseline.rule` embeds a factor tier ("at the outside-channel claim share").
3. "The latest anniversary of the approval date" in the first agreement year is left to the compute (months % 12). The KB mirrors the source wording.
4. World plausibility: both agreements' rosters (2 travelers each) are below their tiers' minimum enrolled travelers at approval (25 and 5).
5. Runtime observation: the task write tools accept an unknown `source_ticket_id` without error. This is by design ("No tool checks a policy condition").

### Coverage

This skill audits only the business corpus against this difficulty's claimed policies. Cross-product contradictions and any unclaimed base-type product corpus are outside its range.

**Difficulty verdict: PASS.** The rendering of corporate_travel_agreements passes the KB audit.
