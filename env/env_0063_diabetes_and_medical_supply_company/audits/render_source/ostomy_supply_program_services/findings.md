# Render-source findings — product ostomy (difficulty ostomy_supply_program_services), render round 1

Saved verbatim by the coordinator from the renderer's final report (agent a8a04962dea95ace2, 2026-10-15); the harness blocked the renderer from writing this file. Rendered as the source stands.

**Source findings (rendered as the source stands)**
1. **Overwrite retires the wrong clause.** In `ostomy_ext_reship_correction` (overwrite[1]), the policy retires this clause from `ostomy_evt_patient_account`: "A hardship waiver is granted only on tiers where hardship_waiver_allowed is true, only for postings named on a hardship application whose request status is approved". But its replacement text keeps that clause in force for every hardship waiver, and the policy only posts billing corrections. The hardship waiver policy relies on that gate.
2. **Withdrawal date vs request date.** In `ostomy_ext_plan_installment` (`withdrawal_term`), the rule says "a payment plan request of the program withdrawn in the last 24 months". The compute's `withdrawn_24m` uses `date_field='received_at'`, so it dates the window by when the request was received, not when it was withdrawn.
3. **Overturned appeal decisions are undefined.** In `ostomy_ext_plan_installment` (`pending_exclusion`), the rule says "the program's most recent first-level appeal has been filed and no decision has posted on it". The compute's `ap_decisions` counts only denial postings against the appeal filing, i.e. upheld decisions. How an overturning decision is recorded is not defined anywhere.
4. **Which grant a refill draws on.** In `ostomy_ext_refill_units`, the rule says "The refill draws on the authorization grant recorded on the newest written order for the convex barrier." The compute's `grant_id` and `grant_through` take the A4407 grant with the latest decision date, with no link to that order.
5. **"This refill included" is not guaranteed.** In `ostomy_ext_expedite_fee` (`first_expedite`), the rule counts "the program's refills shipped expedited in the last 12 months, this refill included". The compute's `other_expedites` leaves out the charged refill if it shipped 12 or more months ago.
6. **Tier scope missing from the compute (low).** The `ostomy_ext_plan_denial_charge` rule is limited to "on the Medicare Advantage tier", and the `ostomy_ext_hardship_waiver` rule to "a tier where hardship waivers are allowed". Neither policy's `result` checks the tier.

**Base-text notes (carried verbatim, not changed)**
- `ostomy_liability_notice` says the notice must be signed "before the ship date" in one sentence and "on or before the ship date" in another.
- The past-due age parameter says a posting becomes past due "at" that age, while the past-due measure counts postings "more than" that many days old. The holds document follows the measure.

**Rendering decisions noted by the renderer**
- Two extended rule sentences count their factors ("Five expedite reductions…", "adds four parts…"). The counts were left out so no document reveals a factor count; each factor document states how it combines.
- Each base policy document lists its `<policy>.params.per_tier` key in meta to pass the gate; the figures are only in the facet tables.
- The renderer's factor-reads-factor scan flagged `prev_rate_days` → `supply_days`; judged a false positive (it reads the shipment record's supply-days field, not the other factor's value).
