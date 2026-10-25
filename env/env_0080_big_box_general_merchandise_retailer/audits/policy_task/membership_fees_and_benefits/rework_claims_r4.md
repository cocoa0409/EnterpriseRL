# Rework claims — membership_fees_and_benefits, round 4

| item | status | where changed |
| --- | --- | --- |
| PT-R17 waits and reversal schedules used different "reversal owed" tests | closed (class: all three pairs) | one test clause — "the earning basis recorded on the Northgate Cash earning that points to its line differs from that line's kept-units basis, which is …" — now stated word for word in the owed-reversal sentence of membership_ext_consumer_return_reversal, membership_ext_business_return_reversal and membership_ext_unreturned_refund_reversal ("A reversal is owed on the … this schedule settles when …, and otherwise nothing is reversed") and in the matching waiting sentences: membership_ext_annual_cancel_refund prerequisite[1] (consumer return), membership_ext_business_closure_refund prerequisite[1] (Business return) and prerequisite[2] (refund without return) — policy_source, rule and condition; the earlier "posted on the line's full net amount" wording is removed everywhere. Compute unchanged (it already implemented the schedule-side test). Propagated to tasks/0.json and tasks/1.json prerequisite_closure, design_rationale problem-tree paragraph, necessity and solvability discriminator texts. |
| O-11, O-12, O-13 | kept as observations | O-11 refusal texts restate the scope record test (coordinator route of round 3); O-12 out-of-scope base entries are stated as unpriced by this charter (round-3 route); O-13 line selection by first-recorded line equals XLATEST on lines sharing one order date, which is how the order charter posts lines |
| earlier observations | unchanged | as round 3 |

Gold arguments and computations of both tasks unchanged; every gate re-run green.
