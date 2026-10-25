# gift_registry_services — rework round 3 claims

- render_r1 item 1 (completion Finch Circle tier date) → the rule sentence, its compute_basis quote and the circle_tier_bonus ladder now anchor the tier to the date the completion discount is redeemed, which is the date of the completion purchase entry (matching the loyalty charter's "registry completion purchase date"). The compute reads the membership as it stands at redemption, so both faces say the same thing. The card bonus is likewise read for an account active on the redemption date.
- render_r1 item 2 (coupon lines narrower than compute) → the rule, the overwrite's replaced_by, the compute_basis quotes and the markdown_better_of ladder now read "a sale price, or a selling price below the regular price for any reason such as a coupon or promotion allocated to it". This is the exact width of the compute branch.
- render_r1 item 3 (period credit bonus fall-through) → the rule and the ladder fall-through now name both cases the compute's else-branch covers: a line bought before the event date, and a line bought more than the completion window after it.
- render_r1 item 4 (baseline not one passage) → the completion redemption rule is reordered so the baseline sentences stand as one continuous passage. The price-rule overwrite now carries its own rounding clause, so its replaced_by no longer needs the separate rounding sentence. All three overwrites still quote verbatim spans of the rule.
- R2-O1 → the completion redemption's order reads list now names the merchandise class, and its note mentions it.
- R2-O2 → closed by the same change as render item 3.
- R2-O3 → the credit redemption's loyalty read note now says "credit bonus"; no "stretch" label remains in any charter note.
- Class sweep (scope width, date anchoring, fall-through glosses), all four policies:
  - Return credit: the rule names the most recently authorized received return record, which is what the compute selects. The label-fee tier now covers a registrant with no active membership, and the tier is read when the credit is booked. The grace tier names returns authorized before the event date. A duplicate is judged against the requested quantity of the item's most recent item entry, with an item without an entry counting as requesting none, as the compute does.
  - Credit redemption: the Finch Circle bonus is read for the tier held when the credit is applied, and its fall-through names another tier or an inactive or absent membership. The bonus form reads the requested quantity of the most recent item entry.
  - Missed rewards accrual: the post-event ladder's fall-through names gifts entered on or before the event date.
  - Completion redemption: the early window's first tier names lines bought before the event date.
- Proof text → task 0's membership read-step necessity, the discount tracing and the factor trace now cite the redemption date. Both design_rationales carry a round-3 note.
- Scored values → no compute expression changed and no scored value moved in either task.
