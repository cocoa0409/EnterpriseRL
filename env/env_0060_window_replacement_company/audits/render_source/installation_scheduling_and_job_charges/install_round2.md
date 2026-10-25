# Render-source findings — install (round 2)

Source: `install.extended.yaml` sha256 5fec328b0a7e9ca75a95a93adf1ad8a967094cdea7d062094ab57a7acb6eabe8; `task_tools.py` d8de31a5… (unchanged).
Inputs read: `install_round1.md`; policy_task `_difficulty.md` (in full) and the findings/revision_2 sections of `0.md` and `1.md`. No task world value or scored figure was used in any document.

## Round-1 items — closure in the KB

- **R1 — closed.** The general sentence "Conditions found or requested at the home are charged on the job, each at the method's rate, on the date the work is done." is now carried **in force** in `site_condition_job_charges_7a9bf5a8.json`, and its round-1 retirement registration is removed. That document now registers exactly the two narrower retired clauses:
  - "New interior casing is charged per opening only where the method does not include it"
  - "exterior trim capping is charged per opening only where the method offers it and does not include it"

  Each is marked **no longer in force** in place of its per-opening row.
- **O-9′ (raised by the policy auditor).** Each extended rule's replacing sentence is carried faithfully in its own hub as a formal term. Only "below" is reworded, to "under these terms":
  - `exterior_trim_capping_approval_7b0ce5ad.json`: "…for exterior trim capping that the customer approves, and only for such capping, the charge is the amount worked out under these terms, built from the method's exterior capping charge per opening, rather than that charge times the openings; new interior casing is not priced by these terms, and every other charge kind keeps its base basis."
  - `interior_casing_approval_883e505e.json`: the casing counterpart, worded the same way.

  The round-1 hub wording ("…remains charged on the job at the method's rate…") is removed.
- **Same principle applied to the other six hubs.** The replaced_by sentences of P1, P2, P3, P5, P6 and P7 ("…rather than the method's flat …" / "rather than as the job's units divided by the method's units per crew day; they are still rounded up to whole days") are now carried in their hubs, again with "below" reworded to "under these terms".
- **R2 — BLUEPRINT-KNOWN.** The parameter description of `openings_per_crew_day` is now carried verbatim, under "Parameter definitions", in `installation_methods_and_crew_pace_1c3bf7d4.json`. It is not repaired and not marked retired, because the source does not retire the description.
- **R3 — closed.** `rebooking_wait_credit_adder_8dcc606e.json` now carries "fewer than 4, or no crew date booked for the job yet → nothing", with a boundary row.
- **R4 — closed.** `rotted_sill_lead_disturbance_197154ef.json` now carries "10 or less (any rot repair up to 10 linear feet) → $30.00", with a half-foot case.
- **R5 — closed.** `held_crew_block_visit_basis_b54f9dd5.json` now carries "1, or none → the method's failed-access fee", with a 0-day row.
- **Note (own_signed) — closed.** `own_signed` moved from the permit computation document's covers to `combined_window_and_door_permit_filings_00431800.json`. That document states the 30 days between this job's contract signed date and the other contract's signed date.

## New findings (round 2)

None that is a mismatch.

Observation, not rendered around: every extended rule states both a replacing sentence ("…the figure worked out below rather than the method's flat …" / "…rather than that charge times the openings") and a `baseline.rule` that is exactly the flat method figure. Both are rendered as the source has them: the replacing sentence in the hub, the standard method in the computation document. A reader who has only the hub and the computation document therefore sees that the flat figure is not the whole price. That follows from the source's own rule text.
