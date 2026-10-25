# Renderer scan-first STOP — product project, render round 1 (agent adaf83211299cd9a8)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`. No documents written. All three findings are in `tasks/project_engagements/project.extended.yaml`.

**1. `project_ext_restart_repricing`, factor `phases_remaining`: the milestone count has no defined value for classes with no milestone schedule (XF 13).**
- The policy's scope covers every fixed-fee engagement: "For a fixed-fee engagement whose client-caused hold lasted longer than max_client_hold_days and that is resumed rather than terminated, and only for such an engagement, ..."
- Two classes in that scope have no milestones. Assessment Engagement allows only fixed fee, and Quick Start Project allows fixed fee. Both have `milestone_pcts: []`, `deposit_pct: 50` and `final_holdback_pct: 50` (lines 106 and 174).
- The rule (lines 1738–1741) says: "Where the milestones in the class schedule number one plus the shares left after deposit_pct and final_holdback_pct and the last milestone's share, divided by the largest milestone share, phases_three_pts points are added to the restart re-pricing when three or more milestones are not yet recorded complete, phases_two_pts points when exactly two are not, and none otherwise." For these classes there is no last share and no largest share, so the count has no value, and the rule gives no branch for that case.
- The compute (line 1775) reads `ms_total: "1 + (100 - P('deposit_pct') - P('final_holdback_pct') - min(P('milestone_pcts'))) / max(P('milestone_pcts'))"`. That fails on the empty list.
- A reader would most likely take "no schedule" to mean "none", but compute raises an error instead.

**2. `project_ext_restart_repricing`, overwrite of `project_schedule_and_holds`: the replacement text drops the definition of a client-caused hold (XF 16).**
- The retired clause (lines 1084–1086) is: "A client-caused hold (client_request, client_dependency or nonpayment) longer than max_client_hold_days lets Stratton Bay terminate the engagement as a client cancellation or re-price the remaining work by change order."
- The replacement (lines 1687–1691) says only "...every engagement held longer than max_client_hold_days for a client cause may still be terminated by Stratton Bay as a client cancellation...". It does not restate "(client_request, client_dependency or nonpayment)".
- The other base sentence that uses "client-caused" ("when a client-caused hold lasted more than remobilization_threshold_days calendar days...") is also retired, by `project_ext_restart_remobilization`.
- As a result, no in-force sentence defines "client-caused". Yet the term limits the scope of `project_ext_restart_repricing`, `project_ext_restart_change_order_fee` and `project_ext_restart_remobilization`, and appears in the remobilization replacement text. A reader cannot tell whether a non-payment hold counts.

**3. `project_ext_sow_signature_rate_lock`, overwrite of `project_client_signed_changes`: the replacement drops the "never signs" ban for the other items (XF 16; low severity).**
- The retired clause (lines 1095–1096) is: "the service desk registers each as a change request carrying the change order number, type, value delta and new target date, pending the authorized contact's e-signature, and never signs on the client's behalf." It applied to every item.
- In the replacement (line 1098), "the service desk never signs on the client's behalf" sits only inside the statement-of-work clause. The sentence for the other items, "change orders, termination notices, acceptance sign-offs and acceptance rejections are still registered by the service desk as change requests carrying the change order number, type, value delta and new target date, pending the authorized contact's e-signature.", leaves the ban out.
- The ban is arguably still implied by the in-force base sentence "...are the client's own commitments". It is still in-force content the replacement does not restate.

The rest of the scan came back clean: every compute binding of all six extended policies matches its rule (windows, ties, absent-record branches, rounding points, combination order); no factor reads another factor's binding; no factor id is a substring of a tool name; tool docstrings contain no example values; every cross-category field the rules mention exists in the schema; a client holds at most one ClearPath agreement.
