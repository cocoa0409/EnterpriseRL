# Render-surfaced source mismatches — product homeplan (difficulty homeowner_claims_and_replacement)
Source: final report of the homeplan render agent (round 1, 2026-10-13), copied verbatim by the coordinator. All are extended-source items routed to rework.

**Source mismatch** (in `homeplan_ext_company_cash_acceptance`):
- `compute_basis.outage_item` quotes: "the days are counted by the item and by how long the request **has** stood".
- The rule says: "the days are counted by the item and by how long the request **had** stood on the date of the accepted offer".
- So the quote is not a substring of the rule. I rendered the rule's wording. Every other `compute_basis`, baseline sentence, `replaced_by` and prerequisite sentence in all five policies matches the rule exactly.

**Possible source issues** (not mismatches by the brief's definition, but worth logging):
1. **Haul-away on zero-allowance tiers.** `homeplan_ext_haul_away_on_completed_replacement` retires "a tier whose allowance is 0.00 pays nothing for that type". Its replacement adds the late-booking credit after the comparison with the allowance. On ApplianceCare, SystemsCare and HomeCare Bronze (haul-away allowance 0.00), the payment is therefore just the late-booking credit, and 0.00 when no credit applies. `book_supplemental_allowance_cce1a240` requires a positive `amount`, so that 0.00 case conflicts with the tool contract.
2. **Haul-away retires more than it replaces.** The same policy retires the whole benefit-caps clause "The remaining item benefit is the item cap less … and the remaining aggregate benefit is …". Its `replaced_by` covers only `aggregate_term_limit`, so the item half of the clause is retired with nothing in its place. This has no effect on any number, because allowances never count toward an item cap.
3. **One sentence lists all of a policy's factors.** Three such sentences (one rule sentence and one overwrite in the acceptance and offer policies, plus the offer policy's `cash_basis` sentence) can't sit in a hub or computation document without naming factors. I split each one across the factor documents, each stating only its own part. The meaning is the same, but no single document carries the sentence whole.
