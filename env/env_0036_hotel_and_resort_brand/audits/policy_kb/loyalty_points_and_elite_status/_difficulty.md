# Difficulty close-out — loyalty_points_and_elite_status (product loyalty, "Ashbury Rewards"), revision 1

## Per-task part-verdicts

| Task | Runtime blind audit | Two-way translation scan | Dependency-form scan |
|---|---|---|---|
| 0 (largest transfer; prereqs relocation compensation, award redeposit, award-stay night credits) | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT RED (E1–E3, low severity) |
| 1 (largest purchase; prereqs elite bonus, welcome points, stay credit reversal) | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT RED (E4–E6, low to medium-low severity) |

Files: `audits/runtime_context/loyalty_points_and_elite_status/{0,1}.md` (blind_answer frozen with hash, then gt_comparison) and `audits/policy_kb/loyalty_points_and_elite_status/{0,1}.md` (source_to_kb, kb_to_source, bijection_verdict, dependency_form).

## Closing checklist

- Audit files one-to-one with tasks 0 and 1: yes. Revision 1 (no earlier revision existed).
- Every normative atom of this difficulty's source entailed by the loyalty docs, with nothing unborne, changed or added: yes (both scans PASS).
- Every prerequisite sentence verbatim, in state form, in its blocked policy's hub and in no other document; every hop resolvable from it, the depended-on hub and the records: yes (6/6 edges).
- Every declared factor ladder complete and exact in its own document, findable from the records: yes.
- No other problem's tool name, route or aggregated chain anywhere: yes.
- Computation documents silent about variation: **no** — four computation documents carry assembly bounds that are vacuous under their baseline (E1, E2, E4, E5, E6), and one factor document presupposes another factor ("further reduced", E3).
- Gate re-run on the final form: not performed — the difficulty does not close because of the KB-EXPLICIT findings. The gate lines on record are the orchestrator's snapshot (`DOCS OK`, `TRACEABILITY OK`).

**Difficulty verdict: not closed (KB-EXPLICIT RED on both tasks).** Solutions are unique and match the source; the open items concern form only.

Policy-side notes recorded (do not change the verdict): PN1 singular `relocated_reservation` selector with two relocated reservations in task 0; PN2 the night-credit overwrite retires the general per-night clause with an award-stay-only replacement; PN3 booking-product plan flags; PN4 reversal baseline defines factor-only terms.

Coverage note: only the loyalty product claimed by this difficulty was audited; cross-product contradictions (booking rate-plan flags) are outside this skill's detection range.

## revision_2

Re-audit round 2 (corpus sha256 `973111af…a4a980d`; gate snapshot "DOCS OK", "TRACEABILITY OK"). The revision-2 blind answers came from fresh clean-context subagents, because the revision-1 auditor had already seen the source layer.

| Task | Runtime blind audit | Two-way translation scan | Dependency-form scan |
|---|---|---|---|
| 0 | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT RED: E1–E3 closed; new N3 (low, pre-existing, missed in revision 1) |
| 1 | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT RED: E4–E6 closed; new N2 (low, pre-existing, missed in revision 1) |

- All six revision-1 findings are genuinely closed. The moved bounds keep the source semantics, and E3's rewording is equivalent at the level of entailment.
- No regression found.
- Remaining open items: N3 (`relocation_compensation_points_amount`, the note "whatever the number of nights booked on it" tied to the Member tier) and N2 (`stay_welcome_points_amount` item 3, "A tier whose welcome amount is zero receives nothing."). Both are computation-document sentences that signal a variation. They are of the same class as E2 and E4–E6.
- Policy-side notes PN1–PN4 stand unchanged, as source notes.

**Difficulty verdict (revision 2): not closed (KB-EXPLICIT RED on both tasks, one low-severity item each).** Gates are not re-run, because the difficulty does not close.

## revision_3

Re-audit round 3 (corpus sha256 `864f64b2…fe14e3`; gate snapshot "DOCS OK", "TRACEABILITY OK"). As in revision 2, the blind answers came from fresh clean-context subagents.

| Task | Runtime blind audit | Two-way translation scan | Dependency-form scan |
|---|---|---|---|
| 0 | KB-RUNTIME PASS | KB-BIJECTION PASS | **PASS**: E1–E3 and N3 closed; nothing new |
| 1 | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT RED: E4–E6 and N2 closed; new N4 (low, pre-existing, missed in revisions 1–2) |

- Both revision-2 findings (N2, N3) are genuinely closed.
- The two changed observations (redeposit term 4; the award-stay "whole credits" sentence) keep the bijection: the removed text was vacuous on every branch, and term 4 now equals the source prose.
- No regression found.
- Open: N4. `stay_elite_bonus_amount` item 5 states the brand rates in the computation document, although the standard elite-bonus rule never uses them. The rate-plan factor document already carries them.
- Residual reading risk (not a defect): the KB never says outright that the 1 January year-end reset is not a "night credit reversed". All blind answers across three rounds took the source reading.
- Policy-side notes: PN1–PN4 unchanged; PN5 added.

**Difficulty verdict (revision 3): not closed.** Task 0 passes all three parts. Task 1 is KB-EXPLICIT RED on N4 alone. Gates are not re-run, because the difficulty does not close.

## revision_4

Re-audit round 4 (corpus sha256 `9dfe8f1d…a2b9`; gate snapshot "DOCS OK", "TRACEABILITY OK"). The blind answers came from fresh clean-context subagents.

| Task | Runtime blind audit | Two-way translation scan | Dependency-form scan |
|---|---|---|---|
| 0 | KB-RUNTIME PASS | KB-BIJECTION PASS | PASS |
| 1 | KB-RUNTIME PASS | KB-BIJECTION PASS | PASS: N4 closed |

### Closing checklist (revision 4)

- Audit files one-to-one with tasks 0 and 1, with revisions 1–4 traceable and earlier text untouched; every comparison section of revision 4 carries PASS: yes.
- Every normative atom of this difficulty's source entailed by the loyalty docs, with nothing unborne, changed or added: yes.
- All six prerequisite sentences verbatim, in state form, only in the blocked policy's hub; every hop resolvable from it, the depended-on hub and the records (state-derived in every blind round): yes.
- Every factor ladder complete and exact in its own document, and findable from the records: yes.
- No other problem's tool name, route or aggregated chain anywhere: yes.
- Computation documents silent about variation: yes. Every finding E1–E6 and N2–N4 is closed.
- Gate re-run on the final form: this auditor did not run the gates. Under the brief the auditor runs neither gate, and the orchestrator's fresh snapshot of the final form is on record: `check_docs.py … loyalty` → "DOCS OK" (mechanical gates PASS); `check_traceability.py …/loyalty_points_and_elite_status` → "0.json 27 0 True", "1.json 28 0 True", "TRACEABILITY OK".

Residual reading risk (not a defect): the KB never says outright that the 1 January year-end reset is not a "night credit reversed". All eight blind answers across four rounds took the source reading.

Policy-side notes PN1–PN5 stand as source notes (they do not change the verdict).

**Difficulty verdict (revision 4): CLOSED — runtime blind audit PASS + two-way translation scan PASS + dependency-form scan PASS for both tasks.**
