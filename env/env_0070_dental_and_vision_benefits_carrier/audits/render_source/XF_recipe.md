# XF recipe — source classes that renderers and KB auditors have found after policy PASS

Coordinator file. Every instantiator applies every point to every extended policy before declaring green;
every policy auditor checks every point on every policy — any member is RED, not an observation.

1. **Factor independence (XF).** Each factor contributes on its own against a quantity the baseline defines.
   No factor's tier, binding or ladder reads another factor's binding or output, transitively (check it
   mechanically: list what every factor binding reads, then close the list). A factor is never gated
   through another factor ("only if the renewal rate applies…").
2. **Shared selections and assembly.** A record selection several factors use is a plain non-factor binding
   stated once in the rule. Assembly lives only in plain bindings / `result`, stated ONCE generically without
   naming factor quantities ("the adjustments below are applied to the standard amount in this order: …").
   No rule sentence assembles named factor quantities; factor-only quantities belong to that factor; the
   baseline (standard method) never defines a quantity only a factor uses.
3. **Non-commuting order.** Wherever adjustments do not commute, the generic combination sentence fixes the
   order ("replacements first, then caps, then additions"); otherwise a second reading of the result exists.
4. **Method tiers change formula shape**, not a multiplier or a window length relabelled `method`. Give a
   pairwise tier table with a distinguishing input for every method factor, so no two tiers coincide on the
   reachable domain.
5. **Rule words == compute, in every case.** Every rule sentence has its compute and every compute branch has
   its rule sentence: counts vs periods, exclusions (cancelled/voided/reversed rows), "later than" vs whole
   months, inclusive/exclusive bounds. No undefined branch.
6. **Edges stated with a tier.** For every CFIELD / first-match / LATEST read: the absent-record case, None,
   zero-division and negative date differences each have a rule sentence and a tier. Same-day ties are stated
   (which row LATEST keeps). Month-end conventions of whole-month/year counts are stated and match MONTHS().
7. **Decoy-row probe table.** For every read, probe on a scratch copy with a decoy row — cancelled, voided,
   reversed, expired, prior-term/prior-benefit-year, second record of the same kind — and with the record
   absent; record the probe outcome in the worklog. Fix every read whose answer moves.
8. **Overwrite hygiene.** An overwrite retires only clauses that really conflict, and retires something.
   Overwrites have no scope field: `replaced_by` restates the in-force content for out-of-scope cases and
   names its own scope ("for a … this policy …, and only for such a …; every other … remains under the base
   rule"). Sibling overwrites of the same base clause each exclude both their own and the sibling's case by
   name. A rule never defers to a base clause its own overwrite retires. No extended rule contradicts an
   in-force base clause without a declared overwrite; no undeclared departure from a base sentence.
9. **Verbatim quotes.** Every `compute_basis` quote is verbatim in its rule (check_extended does not check
   this — run a scratch sweep). The rule's rounding sentence matches the RND placement in the compute.
10. **Names and docstrings.** No factor id is a substring of any tool name. No concrete example values in
    tool docstrings or parameter descriptions (describe the format only); no docstring claims an effect the
    body lacks. No worked example or proof text whose figures equal a scored value.
11. **Coordinator routes are record tests or state-form waits** — never "if policy X would compute …", never
    a copy of another policy's compute.
12. **Cross-product seed realism.** Every seeded row of another category is a state its owning charter can
    produce, priced with that charter's own formulas (premiums from the rate tables, coinsurance/allowances,
    fee shares, proration), with the supporting records that charter implies (requests, invoices, payments,
    claim lines, estimates, remittances). Legal and geographic tiers are real, or worded as the company's own
    schedule. Re-check every tier against the policy's own scope, not just the world.
13. **Stale text sweep.** After any change, sweep design_rationale, prerequisite_closure, necessity text and
    every stated equation for claims the change made stale.
14. **Trigger rule.** List every event your task tools write together with that event's base `triggers`;
    none may land in another category (a write whose base trigger books rows in another category is
    forbidden, even when no gate catches it).
15. **Method-shape test.** Count any aggregate of the same field as one input whatever its window or filter,
    and ignore constant multipliers. A pair of method tiers FAILS if both are the same combination of the same
    windowed sums; it PASSES if one tier adds an input or an operation (floor, max/conditional pick,
    data-selected window, tariff parameter). A "nothing" tier fails where another tier is also 0 across its
    whole domain. Give the all-pairs table.
16. **Bindings and fields.** No plain binding reads a factor-owned binding. No rule word names a field the
    records lack. Each factor names the result it modifies.
17. **Complete ledgers.** Every billable row is invoiced, every payment applied, every periodic review or
    accumulator reproducible from the seeded records; supporting rows the owning charter implies exist.
