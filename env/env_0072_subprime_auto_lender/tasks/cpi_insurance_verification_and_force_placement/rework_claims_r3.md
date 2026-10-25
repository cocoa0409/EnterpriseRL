# rework_claims_r3 — cpi_insurance_verification_and_force_placement (policy_task audit revision_2 + coordinator ruling round 3)

- Coordinator ruling (company-chosen schedules struck): cm/cp_lien_share, cm/cp_ded_share, cm_binder_credit cap, cm/cp_gap_allow and the finance part were removed from both refund rules; each refund is now the unearned premium only (the period's capitalised premium times covered days over period days).
- Coordinator route check (held premium / held release): not adopted — the charter holds a premium only while a borrower-submitted proof "received … is still unreviewed", and no table records a received-but-unreviewed proof, so a held charge cannot be evidenced from records; a held release is always "for its full amount". Recorded in plan.md "Round 3".
- R2-A (assembly names factor quantities): the assembly sentences were removed; each refund's standard paragraph states the one formula (premium × covered days / period days), naming no factor-decided quantity.
- R2-B (coinciding tiers): *_lien_route removed from all three re-review rules (the lienholder test is the base own-flag test again; the seeded proofs list the company and were first rejected for their deductibles); cm/cp_finance and cp_post_close removed.
- R2-C (unreachable fall-through): cm/cp_finance removed.
- R2-D (unreal schedules): lienholder share, deductible share, binder cap and tenure grace removed (see ruling line).
- R2-E1 (sibling tails): each re-review tail now places only first reviews and insurance-agent-call proofs under the base open-record restriction and states that a rejected proof of each sibling channel, named, is governed by its own channel's re-review rule with the same tests.
- R2-E2 (reinstatement vs flat cancel): the reinstatement tier of each proof-span ladder now counts the whole period through the closed date for the refunded charge (the same result base continuous coverage gives that charge); flat cancellation of every other charge stays base, named in both tails.
- R2-F1 (reinstatement day count): the reinstatement tier now runs "from the period start through the closed_date" in rule and compute.
- R2-F2 (missing lien release): post-closing days are now the base days after the closed date; no lien-release read remains.
- R2-F3 (compliance start ambiguity): the gap allowance that read it is removed; no rule reads compliance tenure.
- R2-F4 (proof beginning on the closed date): the re-review scope no longer carries a "began before the closed date" condition; the closed-record reach tier ("began on or before the record's closed_date") decides it alone.
- R2-G (finance part booked as premium refund): removed; refunds carry no interest, fee or credit.
- Observation (docstring narrower than rule): rule and docstring both describe not_applicable as nothing to re-review.
- Observation ("a uploaded proof"): wording now "an uploaded proof" throughout.
- Seeds: proofs re-seeded with the lienholder listed and first rejected for deductibles; task 1 lien release removed (no longer read); contracts unchanged (inside tier limits).
- Proof text: design rationales, factor traces, tier_taken, seed_consistency, necessity and argument traces regenerated from replayed bindings.
- Open, stated honestly: with only real CPI rules the computations carry 3 (each re-review) and 1 (each refund) factors, short of the drawn 4..6 with two parameters; check_extended and check_compute report this. No invented schedule was added to reach the count.
