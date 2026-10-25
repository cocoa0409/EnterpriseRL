# Renderer findings — product residency, render round 2 (agent a761eb148a4c8d8d6, 2026-10-15)
Saved verbatim by the coordinator. Gate revision_5 PASS; all round-1 items closed. 68 docs published; one factor doc withheld; check_docs NOT OK only for it.

**Remaining mismatch (blocks one factor document, `redate_anchor_on_return`, in `residency_ext_return_redating`):**
- The rule defines the receipt date of the return notice everywhere it is used: "The return date is the date stated on the accepted return-home notice …, with the date that notice was received, a notice received before the return date it states counting as received on it."
- The first tier reads: "The re-dating anchor is the date of the borrower's confirmation where that confirmation came more than confirm_gap_days calendar days after the return notice was received".
- The compute uses the raw receipt date there: `DAYS(return_received, confirm_day) > K('confirm_gap_days')`, with no `MX(...)` and no substitution of the return date.
- It bites when a return notice is received before the return date it states. Example: return date on the 10th, notice received on the 1st, confirmation on the 20th. The compute gets 19 days, which is more than 14, so the anchor is the confirmation date. The rule counts receipt as the 10th, gets 10 days, and the anchor is the return date.
- The second tier, `DAYS(return_day, return_received) > 7`, gives the same answer either way.
- Fix: clamp the receipt date in the compute, or scope the "counting as received on it" sentence away from tier 1.

**Minor, not blocking and not published:**
- In `residency_ext_call_in_checkin_number`, the prerequisite's `effect` text says "the numbering basis is zero" when no check-in is recorded. The rule and compute give one.
- In `residency_ext_return_redating`, the contact allowance never states a branch for zero check-ins. That case cannot arise once the policy's own prerequisite is met.
- In `residency_ext_cycle_completion_date`, the rule has a "…next closing anniversary; A cycle's…" punctuation slip.
