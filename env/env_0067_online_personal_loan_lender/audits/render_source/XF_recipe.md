# XF recipe — source-side classes that renderers / KB audits found after policy PASS in earlier runs

Coordinator checklist (orchestration guidance, not scenario content). Instantiators: apply every point to every
extended policy before declaring gates green, and record the check in your worklog. Policy auditors: check every
point on every policy; any member of any class is a RED, never an "observation".

1. **Factor independence.** Every declared factor contributes on its own against a quantity the baseline
   (standard method) defines. No factor's tier reads another factor's binding or output (check transitively,
   mechanically: list what each factor binding reads). No result is assembled inside a factor binding. Record
   selections shared by several factors go into one plain non-factor binding, stated once in the rule.
2. **Assembly stated once, generically, with order fixed.** Combining adjustments lives only in plain
   bindings / `result`, stated ONCE in the rule without naming factor quantities — but it must still fix the
   order wherever adjustments do not commute (e.g. "replacements first, then caps, then additions"), so no
   second reading exists.
3. **Factor-only quantities belong to that factor.** A quantity only one factor uses is defined in that
   factor's own sentence, not in the baseline. No rule phrase defines a quantity "as another policy figures it".
   No computation/baseline text names or describes a factor quantity; no factor names another factor.
4. **Overwrite hygiene.** Overwrites have no scope field:
   - `replaced_by` restates the still-in-force content for out-of-scope cases and names its own scope
     ("for a <thing> this policy handles, and only for such a <thing>; every other <thing> remains under …");
   - sibling overwrites retiring the same base clause each exclude the sibling's case by name;
   - never an overwrite that retires nothing, or retires a clause that never conflicted;
   - a rule never defers to a base clause its own overwrite retires;
   - an extended rule that departs from an in-force base sentence declares that overwrite (no undeclared departure).
5. **compute_basis quotes are verbatim in the rule** — check_extended does not check this; run a scratch
   sweep that every quote is a substring of its policy's rule.
6. **Rounding:** the rule's rounding sentence matches the RND placement in compute exactly.
7. **Docstrings:** claim only effects the tool body actually has; no concrete example values (describe the
   format only — an example can equal a scored value and leaks via unlock); no ordering words, no other tool names.
8. **Edge branches, each with a rule tier and a probe on a scratch copy:**
   - every CFIELD / first-match / LATEST read probed with a decoy row (cancelled, expired, reversed, second record);
   - the absent-record case of every read;
   - None, zero-division, negative lag / date-difference edges;
   - same-day ties (LATEST keeps the first row — state the tie rule in the rule);
   - month-end conventions for whole-month / whole-year counts vs MONTHS();
   - entries vs periods (a count of rows is not a count of billing periods);
   - every exclusion the rule states (e.g. cancelled / reversed rows) is reflected in the compute filters.
9. **Method tiers change formula shape**, not a multiplier or window length; keep a pairwise tier table with a
   distinguishing input — no two tiers may coincide on their reachable domain.
10. **No factor id is a substring of any tool name** (check_docs then fails with no render fix).
11. **Cross-record date pairing** ("signed within N days of the other holding") cannot be computed in the DSL;
    scope via a self-naming overwrite to a single-record case and use a two-date test inside that scope.
12. **Realism:** factors a real program would use; seeded cross-category rows are states the owning charter can
    produce (its statuses, events, fee schedules); geographic/legal tiers are real or worded as the company's own
    schedules; re-check every tier against the policy's own scope; lender realism — no fee on interest never
    billed, no post-closing fee raise, no fee pyramiding.
13. **Runtime constraints:** frozen_time as `YYYY-MM-DD HH:MM:SS <TZ>`; no datetime/time/random/uuid/secrets
    imports or calls anywhere in task_tools.py source; every write tool calls ctx.create/update/delete in its own
    body; date maths via a class static-method ordinal-day helper (a module-level function is treated as a tool).
14. **Proof text:** after any change, sweep design_rationale, prerequisite_closure, necessity text and trace
    arithmetic for claims the change made stale.
