# Realism bar (coordinator ruling file, env_0083) — the shared bar instantiators AND auditors apply

The scenario is a US commercial fleet card issuer / processor (B2B). Fleet cards are COMMERCIAL credit: consumer statutes (Reg Z billing-error and $50 liability rules for consumer cards, Reg E, CARD Act fee caps, state consumer late-fee caps) are not the governing law unless they genuinely apply to commercial cards; the fleet card AGREEMENT and the issuer's published schedules govern. Card-network rules (Mastercard / Visa for open-loop fleet products) and real federal tax rules (federal excise tax exemption for qualifying government and tax-exempt fleets) may appear only as they really are.

## Accepted factor kinds
- **R1 — keyed schedules on recorded, publishable keys.** Fee, rate, limit or cents-per-gallon schedules keyed on a field the records hold and the issuer would publish: program tier, card type (vehicle / driver / equipment), network (in-network / out-of-network / partner), product restriction code / fuel product, billing cycle, payment terms, fleet-size band by active card count, site type (self-serve / full-serve), statement delivery (paper / e-statement).
- **R2 — one timing schedule per date dimension.** Days past due, days from statement date to dispute filing, days since card issue / last reissue, cycle position. One ladder per date dimension.
- **R3 — conventions.** Partial-cycle proration of per-card fees, day-count conventions, "a card active on any day of the cycle counts", whole-cycle vs part-cycle. A whole-cycle count plus its part-cycle remainder on the same date is ONE R3 convention (cannot be split into two factors).
- **R4 — real external rules.** Federal excise tax exemption rates for qualifying fleets (real per-gallon figures only), network chargeback / dispute time limits as they really are, IRS / IFTA facts as they really are. Never invent a statute, a regulator's figure or an entitlement.
- **R5 — published caps and minimums.** "The greater of a minimum or a percentage", maximum fee per cycle, rebate caps per period, minimum gallons to qualify — figures plausible for the industry.
- **R6 — thin-charter waiver tier (coordinator-granted only, BLUEPRINT-KNOWN).** Only if the coordinator records an amendment here for a named difficulty. Conditions: keyed on a recorded field; plausible figures; no conflict with law or base; not an X1 mechanism; XF-clean; minimal count, tagged in the claims. Auditors grade such factors R6-WAIVED observations, not REDs.

## Rejected factor kinds
- **X1 — invented perks.** Tenure / loyalty / AutoPay / "new fleet" / relationship discounts, goodwill relief, "board-approved" adjustments that the frozen charter does not already carry as a parameter.
- **X2 — hardship or courtesy cuts on penalty fees** not present in the charter (a courtesy late-fee waiver exists only if the charter's catalogue carries one).
- **X3 — stacking and double counting.** Two discounts / rebates on the same gallons where an account-wide rule says single-higher or no-stacking; a factor already embedded in a recorded amount (a recorded price per gallon that already reflects the network discount; a recorded statement total; a recorded fee amount) is not load-bearing.
- **X4 — implausible figures.** Rates, fees, limits or rebates outside what real fleet card programs charge or pay; credit limits not sized to the fleet's spend and terms.
- **X5 — consumer-law transplants.** Applying a consumer-card statute's figure (e.g. the $50 unauthorized-use cap, Reg Z 60-day billing-error clock) to a commercial fleet account as if it governed, unless the charter itself adopts it as the agreement's own term.

## RULE-7 (count-keeping and sibling mirroring)
A lever added to reach the drawn factor count must be a REAL parameter of the frozen product charter's catalogue that honestly engages the task world (read the charter's parameter catalogue first). Never invent a mechanism only to keep the count. Sibling policies that price the same line mirror each other exactly. Re-price every seeded row under the current rules after any rule change.

## Design consequence
Put trees on writes priced from raw records (gallons, price per gallon, card counts, balances, days), not on rebates or waivers of a posted flat fee.

## Amendments (every coordinator ruling is recorded here, never only in a brief)
(none yet)
