# Policy-task audit — sensor_calibration_desk / charter-global

## charter_global_frozen

- Freeze inputs (sha256, first 16 hex, re-verified by the auditor before reading):
  - `tasks/sensor_calibration_desk/adas.extended.yaml` = `869f67702aa42587`
  - `tasks/sensor_calibration_desk/task_tools.py` = `5965337bcf2beabf`
  - masked views `0.masked.json` = `4342d5b1e3ba4fed`, `1.masked.json` = `2cd8546747a136ef`
- Freeze time (system clock): 2026-10-11 03:37:55 UTC (section written before any task GT was revealed; nothing below is derived from a revealed GT).
- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent.
- Read: `blueprint/blueprint.yaml`, `blueprint/products/adas.yaml` (+ lifecycle/variant lists of retail, estimate, warranty, claim), `blueprint/share_tools.py`, `adas.extended.yaml`, `task_tools.py`, the DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`), and the two masked views.
- Masked / unread: `tasks/sensor_calibration_desk/tasks/*.json` (all fields), `worklog.md`, `audits/` of every other difficulty, any sibling `tasks/` directory, any other `env/` scenario.
- Entry conditions: gate snapshot (check_extended / check_task_tools / replay / solvability / compute / grounding / cross_fire green, traceability deferred), masked views with hashes, and freeze hashes were all supplied in the brief. Cited, not re-run.
- Base section verbatim: `diff <(head -n 1376 adas.extended.yaml) blueprint/products/adas.yaml` → identical.

### policy_conflict_scan

Extended policies (4): `adas_ext_alignment_check_charge` (agent, `post_alignment_check_charge_59500100`, adas_charge), `adas_ext_correction_authorization` (user, `pay_alignment_correction_authorization_61ce2890`, adas_payment), `adas_ext_alignment_comeback_credit` (agent, `post_comeback_goodwill_credit_c6e84f0b`, adas_no_charge), `adas_ext_calibration_acceptance` (user, `pay_calibration_acceptance_f9e8bcf7`, adas_payment).

- Overlapping subjects: the two `adas_payment` policies (correction authorization, calibration acceptance) are distinct payments with distinct triggers (a correction authorization vs. an acceptance of the calibration) and distinct tools; no shared quantity. `adas_no_charge`: the comeback credit vs. base `adas_evt_settlement` goodwill — the comeback overwrite replaces the base goodwill cap (see override_declarations).
- Same base clause superseded twice: `adas_evt_precheck` "on a customer-pay order the check posts an alignment_check charge and a correction an alignment_correction charge" is superseded by both the check-charge policy (check half) and the correction-authorization policy (correction half). Each replacement covers one half; the union is complete and non-contradictory. Observation O-4.
- `adas_evt_settlement` "A customer pays a customer-pay order's balance ... on completion" superseded by both payment policies with compatible replacements (balance after the pre-payment is paid on completion). Compatible.
- Time anchors: the check-charge rule fixes a posting date in the past ("posted on the day of the order's first out-of-spec check, or on the precheck date"), the comeback rule "on the day that charge posts"; the tools date every entry today. No amount depends on the entry date except through the anchors discussed in F-2. Observation O-6.
- Cross-category read boundaries: claim (delivered_date, variant_name), retail (status, opened_date), warranty (issued_date, status, variant_name), estimate (status, closed_date) — all reads are declared in `cross_category` and are values only; no write crosses category.
- Scope: four extended policies; the two prerequisite edges split them into two trees {check charge → correction authorization} and {comeback credit → calibration acceptance}. With M=2 the two trees are disjoint and jointly cover the charter, provided each task claims one tree (confirmed per task at reveal).

### rule_compute_equivalence

All `compute_basis` quotations are verbatim substrings of their policy's rule (scripted check: 0 misses in all four policies). Every factor's `decides` binding exists in compute and every ladder tier has a rule sentence and a branch. Item-by-item sweep:

- `adas_ext_alignment_check_charge`: checks_billed ternary = the three-tier sentence; returning/rack/member ternaries match their sentences; `check_fee` = fee × three rates; `result = RND(check_fee * checks_billed, 2)` = "only that final figure is rounded". **Gaps (F-2)**: (a) the rule's window "each alignment check recorded on the order up to the day the charge posts" / "covering the checks recorded on the order up to that day" is quoted for `n_checks` but `COUNT('adas_events', event_type='adas_alignment_check')` has no date filter; (b) "delivered no more than 730 days before the charge posts" / "issued no more than 365 days before the charge posts" are anchored in the rule on the posting day (first out-of-spec check day or precheck date), while compute anchors `claim_days`/`member_days` on `NOW`.
- `adas_ext_correction_authorization`: all sentences implemented. `check_standing` has no `compute_basis` key (its sentence "The alignment check charge standing on the order is that charge less the write-offs booked against it" is in the rule and quoted for sibling keys) — observation O-1. No floor on `correction_quote` — see F-3.
- `adas_ext_alignment_comeback_credit`: window_end, window_share, class_weight, credit_cap, 180-day eligibility gate, min/MX(0) cap all implemented. **Gap (F-1)**: credit_base tier 2 "where a later out-of-spec check was corrected at its visit" is implemented as `first_check_result != 'out_of_spec' and latest_out_corrected == True`; the rule's condition does not require the first check to be in spec, and it speaks of *a* later out-of-spec check, not only the latest.
- `adas_ext_calibration_acceptance`: all sentences implemented; balance "whether it is an amount owed or a credit" implemented as signed sum.
- DSL semantics (charter-wide): `CFIELD` returns the first matching row (`hs[0]`), so "the customer's most recent estimate booking that ended as a no-show" (correction authorization, acceptance) is not implemented as most-recent, and "the vehicle has a network insurance claim repair delivered ..." / "holds an active ... warranty issued no more than 365 days" read the first row only. Neither task world seeds more than one candidate row, so no consequence here — observation O-2. `RND` is Python float `round`, the rule says half up — observation O-3 (no gold value sits on a half-cent; checked per task).

### action_binding_and_uuids

- `(target_tool, computes)`: four distinct pairs, each claimed by exactly one policy; base policies claim no task tool. PASS.
- Docstrings: each describes one atomic write; none names another tool, a sequence position, or "before/after/first". `pay_calibration_acceptance` and `pay_alignment_correction_authorization` say "which the customer can quote afterwards" — refers to quoting the receipt, not to tool order. PASS.
- Tool bodies: each only `ctx.find`s the order for `customer_id` and `ctx.create`s one ledger row; no validation, no error branch, no hint. The tool layer judges no prerequisite. PASS.
- uuid8: `59500100`, `c6e84f0b`, `61ce2890`, `f9e8bcf7` — pairwise unrelated, no shared prefix or sequence. `59500100` is all-decimal with a run of zeros and reads like it is derived from the 59.95 fee rather than freshly generated — observation O-5 (not demonstrable as batch derivation).

### prerequisite_graph

- `prerequisite` filled on all four (`[]` on check charge and comeback credit). Edges: correction authorization → check charge; acceptance → comeback credit. Both `problem`s are extended ids in this file; no self-loop; acyclic (two disjoint chains of length 1).
- `policy_source` verbatim in own rule: both True (scripted). `form: state`, no `fallback_reason`: correct.
- `kind: value_input`, `gate` names a real binding: `check_charged` (correction authorization compute), `write_offs` (acceptance compute). `resolved_by` equals the depended-on `target_tool` on both edges.
- `effect`: posting the check charge raises `check_charged` from 0, which feeds both `check_applied` and `check_unpaid`; posting the comeback write-off raises `write_offs` and lowers `standing_balance`. Both effects are real in the compute.
- `condition` strength: edge 1 condition "an alignment check charge entry covering the alignment checks recorded on the order up to its first out-of-spec check" vs. sentence "the alignment check charge owed for the checks recorded on it" — the sentence defers what is owed to the check-charge rule, which itself limits coverage to checks up to the posting day; not strengthened or weakened in effect. Edge 2 condition "Where a comeback credit is owed" = sentence "the goodwill write-off owed against its alignment correction charge". PASS.
- No authoring-viewpoint phrasing in any prerequisite field. PASS.

### prerequisite_sentences

1. Correction authorization: "The amount collected when a customer authorizes an alignment correction is not fixed until the order carries the alignment check charge owed for the checks recorded on it." — connective "not ... until"; waited-on item is a record-visible state in the finder's words (find_adas_ledger: "alignment ... charges"); no tool, id, snake_case; state form. Exactly one write of this difficulty produces an alignment check charge entry: `post_alignment_check_charge_59500100` (the other three tools write payments or a goodwill write-off). Derivation: sentence → ledger has no alignment_check charge → the only rule describing that charge is the check-charge rule ("the alignment checks are billed together as one alignment check charge, posted ...") → post it. Single reading. The check-charge rule does not restate the sentence. PASS.
2. Calibration acceptance: "The amount a customer pays to accept a calibration is fixed only after the order carries the goodwill write-off owed against its alignment correction charge." — "only after"; record-visible state (a goodwill write-off naming the correction charge); state form. Only `post_comeback_goodwill_credit_c6e84f0b` writes a goodwill write-off; the only rule making one "owed" against the correction charge is the comeback rule ("it is booked as a goodwill write-off against the alignment correction charge"). Single reading; not restated on the depended-on side. PASS.
- Undeclared cross-problem orders: the correction rule's "an out-of-spec alignment is corrected only once the customer authorizes the correction by paying" and the acceptance rule's "Whatever an accepted order still owes is paid on completion" order a write against events that have no task tool here (the correction, the completion); they ground no edge and order no two writes of this difficulty. Base `adas_evt_payer_approval` "No attempt starts until the payer has agreed" is a base sentence on attempts, grounds no edge. None.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry (finding half only):

- Check charge vs `adas_evt_precheck`: preconditions list and the alignment validity sentence — followed. "An out_of_spec check must be corrected and checked again; on a customer-pay order the check posts an alignment_check charge ..." — declared (superseded). "while on an insurance claim repair the alignment is part of the repair order" — followed (customer-pay only). Glass safe-drive sentence — untouched.
- Check charge vs `adas_evt_charges`: "Charges post on the completion date." — the extended rule posts the check charge on the first out-of-spec day / precheck date; not named in `overwrite`. The same base rule continues "Alignment charges follow adas_evt_precheck", which carves alignment charges out to the precheck rule, and the base precheck rule has the check itself post its charge; seeded history (task 0) posts the alignment charges on the check day. Read with the carve-out the two do not conflict → observation O-7 (a reader who applies the first sentence to alignment charges would hold the charge until completion; no demonstrable scored consequence because the carve-out sentence settles it). Remaining sentences (sublet, diagnostic, warranty rework no charge, transfer on claim repairs) — not the scored quantity / followed.
- Correction authorization vs `adas_evt_precheck`: correction half of the clause declared. vs `adas_evt_settlement`: balance-on-completion sentence declared; fleet-discount, write-off, goodwill sentences — not the scored quantity. The correction charge "posted on the day the correction is made" vs `adas_evt_charges` "Charges post on the completion date" — same carve-out, O-7.
- Comeback credit vs `adas_evt_settlement`: "Write-offs name the charge they reduce and never exceed it" — followed ("never more than the correction charge"). Goodwill cap sentence declared. The declaration supersedes the base cap for all goodwill but its replacement speaks only of the comeback credit; a non-comeback goodwill request is left with no stated cap under a literal merge — observation O-4 (no task asks for a non-comeback goodwill write-off).
- Acceptance vs `adas_evt_payer_approval` (acceptance of calibration_price_usd), `adas_evt_charges` (in-house calibration charge), `adas_evt_settlement` (balance on completion): all three declared. Base sublet cap "the part above calibration_price_usd is written off as sublet_cap" is not reconciled with the accepted (rated) quote — not the scored quantity of any write here; observation O-8.
- Disguised forms: no anonymous intermediate overriding a base quantity; the comeback `result ... if comeback_days <= window_days else 0.0` is the rule's own eligibility sentence, not a 0/1 override of a base amount; no base branch is dropped by an extended selector.

### factor_ladders

| policy | factor | label | tiers | multi-source (every non-fall-through tier over distinct records) | cross_difficulty |
|---|---|---|---|---|---|
| check charge | checks_billed | method (different counting rule per tier) | 3 | no (tier 1 single condition) | – |
| | returning_customer_rate | parameter 0.80/0.90/1 | 3 | no (one claim row) | claim |
| | rack_rate | parameter 0.75/0.90/1 | 3 | **yes** (adas_orders.source_type ∧ retail_repairs.status) | – (retail is no difficulty) |
| | member_rate | parameter 0.90/0.95/1 | 3 | no (one warranty row) | warranty |
| correction authorization | check_applied_toward_correction | method (whole / half rounded / nothing) | 3 | no | – |
| | authorization_share | parameter 1/0.75/0.5 | 3 | no | estimate |
| | correction_returning_rate | parameter 0.85/0.92/1 | 3 | no | claim |
| | correction_rack_rate | parameter 0.80/0.90/1 | 3 | **yes** | – |
| comeback credit | window_end | method (anchor date) | 3 nominal, **2 reachable** (F-4) | no | – |
| | window_share | parameter 0.50/0.35/0.20 | 3 | no | claim |
| | repair_class_weight | parameter 1.0/0.80/0.60 | 3 | no | claim |
| | comeback_cap | parameter 2×/1.5×/1× authority | 3 | **yes** (claim class ∧ window over claim + adas rows) | – |
| | credit_base | method (correction + k × check) | 3 | no | – |
| acceptance | acceptance_share | parameter 1/0.75/0.5 | 3 | no | estimate |
| | record_date | method (anchor date) | 3 | no | – |
| | calibration_returning_rate | parameter 0.90/0.95/1 | 3 | no | claim |
| | calibration_member_rate | parameter 0.96/0.98/1 | 3 | no | warranty |

- Counts per policy: 4 / 4 / 5 / 4 factors; parameter 3/3/3/3; method 1/1/2/1. Bindings disjoint; `decides` is never `result`; every ladder stated in full in the rule; every fall-through equals the factor `baseline`, and each `baseline` is what `baseline.rule` states (rates absent → 1.0; shares 0.5 / 0.20 / 0.60; cap = authority; credit base = correction charge; window to latest out-of-spec check; count = every check; applied = nothing; record date = acceptance day).
- No two tiers of any ladder select the same value or method.
- Labels: `check_applied_toward_correction` reduces to `RND(check_standing × s, 2)` with s ∈ {1, 0.5, 0}, and `credit_base` to `correction_charge + RND(check_charge × s, 2)` with s ∈ {1, 0.5, 0}: each tier substitutes a multiplier into one formula. The authoring standard lists "a transform or multiplier on an intermediate" as a method family, so the label is not demonstrably false under the framework; recorded as observation O-9 (borderline label). `credit_base` also selects "the amount the credit is figured on", i.e. the base the window share and class weight act on, which the authoring standard says is fixed by the product; same observation.
- Realism: loyalty rates for a recent network claim repair (deeper for structural), in-shop bundling rates for an open customer-pay repair, member rates for lifetime-warranty holders, no-show-based deposits, the re-check-is-part-of-the-correction rule, the lapsed-check rule and comeback goodwill scaled by recency and repair class are all treatments a collision/ADAS network could publish. Exception: F-4.
- Per-task requirement (≥1 multi-source, ≥1 cross-difficulty): tree {check charge, correction} carries rack_rate (multi-source) and claim/warranty/estimate factors; tree {comeback, acceptance} carries comeback_cap (multi-source) and claim/estimate/warranty factors. Met structurally; seeding verified per task.

### findings

- **F-4 — SOURCE-FACTOR RED (comeback credit, `window_end` ladder).** Symptom: the ladder's fall-through "otherwise: end the comeback window on the date of the order's latest out-of-spec alignment check" — which is also the factor `baseline` and the `baseline.rule` sentence "The comeback window is measured in calendar days from the claim repair's delivery date to the date of the order's latest out-of-spec alignment check" — applies to no order that can reach this write. Root cause: the policy's scope is "A customer-pay order ... which carries an alignment correction charge". By base `adas_tier_and_payer`, a collision-repair order is paid `insurer_via_repair` and a warranty-rework order is `no_charge`; by base `adas_evt_precheck` "on an insurance claim repair the alignment is part of the repair order" and by `adas_evt_charges` "A warranty rework order posts no charge at all". So the only source types that can carry a customer-pay alignment correction charge are customer_request (tier 1) and customer_pay_repair / glass_replacement (tier 2). Demonstrated consequence: the ladder has two reachable tiers, not three, and its baseline is a treatment the business gives no customer who reaches this write — the straw-man baseline in another form. With it struck, the comeback computation keeps 4 factors (3 parameter + `credit_base` method), so the count bounds still hold only through `credit_base`, whose label is itself borderline (O-9). Affected: `adas.extended.yaml` → `adas_ext_alignment_comeback_credit.rule` (window-end sentences), `factors[window_end]`, `baseline.rule`. Bears on the task that claims the comeback credit (see that task's file for the per-world consequence).
- **F-1 — SOURCE-POLICY RED, latent (comeback credit, rule/compute non-equivalence on `credit_base`).** Rule: "where a later out-of-spec check was corrected at its visit, it is the correction charge plus half the alignment check charge". Compute: `... if (first_check_result != 'out_of_spec' and latest_out_corrected == True) ...`. Situation (in the policy's domain, and the natural one under the correction-authorization rule that a correction waits for the customer's payment): check 1 out_of_spec, not corrected; check 2 out_of_spec, corrected at its visit; check 3 in_spec. Rule → tier 1 fails (check 1 not corrected), tier 2 holds → correction + half check. Compute → `first_check_result == 'out_of_spec'` → falls to "correction charge alone". Two different credit bases. Affected: `adas_ext_alignment_comeback_credit.compute[credit_base]`. Neither task world reaches this situation (checked per task).
- **F-2 — SOURCE-POLICY RED, latent (check charge, rule/compute non-equivalence on the posting-day window).** Rule: "for each alignment check recorded on the order up to the day the charge posts" and rates "no more than 730/1460/365 days before the charge posts", with the posting day defined as "the day of the order's first out-of-spec check, or ... the precheck date". Compute: `n_checks` counts every check with no date filter; `claim_days`/`member_days` use `NOW`. Situation: a Front Radar order (retry_requires_new_precheck true) with in-spec checks, precheck on day P, a failed attempt and a retry check on P+5, charge computed after P+5: rule bills the checks up to P, compute counts the retry check too. Affected: `adas_ext_alignment_check_charge.compute[n_checks, claim_days, member_days]`. Per-task consequence examined in the task that claims this policy.
- **F-3 — SOURCE-POLICY RED, latent (correction authorization, unbounded quote vs. positive charge contract).** Rule: "within 3 days of the order's latest out-of-spec check, the whole of that charge is applied toward the correction and the quote is the rated correction fee less that charge" and "the correction's charge ... is the correction quote the customer authorized"; base event contract `adas_charge.amount_usd: Charge (positive)`. Situation: customer_request Dual-Mode order, checks 1 and 2 in spec, check 3 out of spec all within 30 days, no correction → check charge 3 × 59.95 = 179.85; authorization the next day → quote = 129.95 − 179.85 = −49.90, a negative correction charge the base contract forbids. Affected: `adas_ext_correction_authorization.rule`/`compute[correction_quote]`. No task world reaches it (checked per task).
- Observations (no demonstrable consequence in this difficulty):
  - O-1 `check_standing` lacks a `compute_basis` entry.
  - O-2 `CFIELD` first-row semantics vs "most recent no-show" / existential claim and warranty reads.
  - O-3 Python `round` vs "half up": affects only figures that land exactly on a half cent.
  - O-4 one base clause superseded by two policies, each replacing one half; the goodwill-cap supersession is broader than its comeback-only replacement.
  - O-5 uuid8 `59500100` looks hand-derived (all decimal, fee-like prefix).
  - O-6 posting dates fixed in the past by the rules vs. tools that date entries today.
  - O-7 base "Charges post on the completion date" vs. the extended alignment posting dates — resolved by the base carve-out "Alignment charges follow adas_evt_precheck"; not named in `overwrite`.
  - O-8 base customer-pay sublet cap still keyed to calibration_price_usd after the acceptance overwrite.
  - O-9 `check_applied_toward_correction` and `credit_base` are multipliers {1, 0.5, 0} on an intermediate, labelled `method`; `credit_base` selects the base a rate acts on.

## closing_checklist

Written 2026-10-11 03:42 UTC, after both reveals (03:40:37 UTC). **The difficulty does NOT close**: not every task passes all four relationships.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this file sits alongside; first revision (no older revisions). Comparison sections present in both; verdicts:
  - task 0 — policy PASS, tree PASS, **factors SOURCE-FACTOR RED** (T0-1 = F-4 `window_end` unreal ladder; T0-2 one-cent proof figure), unique solution PASS.
  - task 1 — policy PASS, tree PASS, **factors SOURCE-FACTOR RED (proof figure only)** (T1-1 one-cent `baseline_result`), unique solution PASS.
- Coverage and scope: task 0 claims {comeback credit, acceptance}, task 1 {check charge, correction authorization}; pairwise disjoint, jointly cover all four extended policies; four task tools, each used by exactly one task; uuid8s distinct (O-5 on `59500100`). PASS.
- Trees: each has 1 prerequisite problem, 1 `value_input` edge, an `owner=user` root, no cycle; the difficulty graph is two disjoint length-1 chains. PASS.
- Factors: every declared factor bears weight on its task's world and each baseline alone gives a definite number ≠ gold (9.28, 164.27, 119.90, 103.42). Open: F-4 (comeback `window_end` fall-through unreachable in scope); O-9 (two {1, 0.5, 0} multiplier factors labelled `method`); one-cent proof figures from float rounding (T0-2, T1-1).
- Charter self-consistency: latent SOURCE-POLICY REDs F-1 (credit_base rule/compute), F-2 (check-charge posting-day window/anchor), F-3 (negative correction quote vs positive charge contract). None changes a scored value in either task world, but they make the charter's rule and compute differ for other worlds in the policies' domains.
- Instantiation-stage gate re-run on final form: not performed by this audit (out of scope); the coordinator's snapshot of 2026-10-11 is cited in `charter_global_frozen`.

## revision_2

### charter_global_frozen (revision 2)

- Inputs: `adas.extended.yaml` sha256 `23dff7db5a842c14` (**changed** from `869f67702aa42587`, so every charter-global section below is re-derived in full, not carried forward); `task_tools.py` `5965337bcf2beabf` (unchanged); masked views `0.masked.json` `4342d5b1e3ba4fed`, `1.masked.json` `2cd8546747a136ef` (unchanged); blueprint `products/adas.yaml` `48bb0e7d306be20c`.
- Freeze time (system clock): 2026-10-11 05:01:14 UTC. Written before any round-2 task file was opened. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5).
- Disclosure: the auditor read the round-1 task files (GT) at 03:40:37 UTC, so round-1 gold figures are known. This section rests only on the charter, the tool module, the schema and the DSL. Nothing in it comes from a round-2 GT.
- Base section: still verbatim (`diff` against `blueprint/products/adas.yaml` is empty).
- Method: read all four extended policies again in full. Re-ran the scripted verbatim checks: overwrite clauses, `replaced_by`, `policy_source`, `compute_basis`, baseline sentences, compute/basis key sets. Then evaluated every compute with the `check_compute` `build_env` DSL on the two unchanged masked worlds, together with factor-by-factor baseline substitution (`/tmp/audit0052_scd/dsl_r2.py`). The rework's claims were not used as evidence.

### What changed (observed in the text)

1. Check charge: coverage is now "covering the checks recorded on the order when it is posted" / "for each alignment check recorded on the order when the charge is posted". The rate anchors are now "before the day the charge is posted". "half up" was added to the baseline sentence.
2. Correction authorization: the quote is now "never below zero, and a correction quoted at zero posts no correction charge" (`correction_quote: MX(0, …)`). `check_standing` now has a `compute_basis` entry. "half up" was added at every rounding point. The edge-1 `condition` now reads "covering the alignment checks recorded on the order".
3. Comeback credit: in the window-end ladder, tier 2 is now customer-pay repair only, and tier 3 is "the order was opened on a glass replacement, or on any other customer-pay source" → latest out-of-spec check (`window_end` compute matches). `credit_base` tier 2 is now `n_corrections >= 1` (it no longer requires an in-spec first check). The goodwill-cap `replaced_by` and rule now add "any other goodwill write-off on the order stays capped at the tier's goodwill credit authority less the goodwill already written off on it, beyond which the request is declined".
4. All four computes: every `RND(x, 2)` is now `RND(x + K('half_up_guard'), 2)` with `half_up_guard: 0.000001`.

### policy_conflict_scan (r2)

The round-1 scan is unchanged in substance. Subjects, triggers, tools and cross-category reads are the same. The only added sentence about one subject is the non-comeback goodwill cap. It restates the base cap and conflicts with nothing. The four `(target_tool, computes)` pairs are unchanged and unique. Scope partition: two disjoint length-1 chains, as before.

### rule_compute_equivalence (r2)

- All `compute_basis` quotations are verbatim. Compute and basis key sets are equal in all four policies (this was not true in round 1 for `check_standing`).
- **F-1 re-check (closed):** rule "where a later out-of-spec check was corrected at its visit" ↔ compute `n_corrections >= 1` after the tier-1 test. On the round-1 counter-example (check 1 out_of_spec uncorrected, check 2 out_of_spec corrected), both the rule and compute now give correction + half check. `alignment_corrected` exists only on out-of-spec checks (schema: "Whether an out-of-spec alignment was corrected in the same visit"). So once tier 1 fails, any correction is on a later out-of-spec check. No residual divergence found.
- **F-2 re-check (closed, with a residual observation):** coverage and day anchors are now tied to "when the charge is posted" / "the day the charge is posted". Compute is evaluated at the posting write (`COUNT` of all checks, `NOW`), so for a charge posted at handling time the rule and compute agree. Round-1 retry-check counter-example: if the charge is posted after the retry check, the rule now covers that check too, the same as compute. Residual: the first sentence still says the charge is "posted on the day of the order's first out-of-spec check, or on the precheck date". When posting happens later than that day, "the day the charge is posted" could be read as the prescribed day rather than the actual one. The tool dates entries today, so the actual-day reading is the one the records support. Recorded as observation O-10. It is demonstrable only where a 365/730/1460-day boundary falls between the two days.
- **F-3 re-check (closed):** `correction_quote: MX(0, rated_correction - check_applied)` matches "which is never below zero". "a correction quoted at zero posts no correction charge" keeps the base positive-charge contract intact. Round-1 counter-example: the quote is now 0.00 and no charge posts.
- **O-3 re-check:** the rule says "half up" at every rounding point, and compute adds a 1e-6 guard before Python `round`. On both worlds every scored value, every factor substitution and every baseline evaluates to the decimal half-up figure, including the two round-1 half-cent cases (230.725 → 230.73; 103.415 → 103.42). The guard is an approximation, not a decimal half-up: a true value within 1e-6 below a half cent would round up, and a negative sum is pushed toward +∞. Neither can occur with these worlds' figures. Downgraded to observation O-3′.
- O-2 (`CFIELD` first-row) is unchanged and remains an observation.

### action_binding_and_uuids (r2)

Unchanged tool module (`5965337bcf2beabf`). Carried forward from round 1 on that hash: one policy per pair, docstrings silent about sequence, tool bodies validate nothing, uuid8s distinct (O-5 stands).

### prerequisite_graph (r2)

Both edges are unchanged in `problem`, `kind`, `gate`, `form`, `policy_source` and `resolved_by`. Scripted checks: `policy_source` is verbatim in its own rule, the gate binding exists, `resolved_by` = the depended-on `target_tool`, the depended-on rule does not restate the sentence, and the edge is state form with no `fallback_reason`. The edge-1 `condition` now reads "covering the alignment checks recorded on the order". This matches the reworked check-charge coverage ("checks recorded on the order when it is posted") and the sentence "owed for the checks recorded on it". It is neither strengthened nor weakened. The graph is acyclic. PASS.

### prerequisite_sentences (r2)

Both sentences are unchanged, so the round-1 four-point analysis and the single-reading derivations carry over. The rework adds one new cross-problem sentence: "a correction quoted at zero posts no correction charge". It concerns a charge that no task tool writes. No new undeclared order. PASS.

### override_declarations (r2)

- The comeback `replaced_by` now covers both the comeback cap and every other goodwill write-off. The round-1 O-4 (supersession broader than its replacement) is **closed**. The precheck clause is still split across two overwrites, which is compatible as before (residual part of O-4, unchanged).
- The check-charge `replaced_by` now ends "covering the checks recorded on the order when it is posted". It is a verbatim rule substring and is consistent with the rule.
- O-7 (base "Charges post on the completion date" vs the alignment posting dates) and O-8 (sublet cap keyed to calibration_price_usd) are unchanged observations.

### factor_ladders (r2)

- Counts and labels are unchanged: 4 / 4 / 5 / 4 factors; parameter 3/3/3/3; method 1/1/2/1. Every ladder has 3 tiers, stated in the rule and branched in compute. Fall-through = factor baseline = `baseline.rule`.
- **F-4 re-check (closed):** the window-end ladder's fall-through is now "glass replacement, or any other customer-pay source" → latest out-of-spec check. A customer-pay order opened on a glass replacement can carry an alignment correction charge. Examples are a customer-paid glass job with a camera tier (alignment_required true), or a Front Radar order after glass work (glass_program_billable false → "to the customer otherwise"). So the fall-through and the baseline now describe customers who actually reach this write. The three tiers select three distinct anchors (opening date / first check / latest out-of-spec check), and each is a dated event the business would plausibly use for that kind of order. The "any other customer-pay source" part of tier 3 is still empty, but it adds nothing and takes nothing away.
- `credit_base`'s tier 2 condition changed (F-1). The ladder still has three distinct outcomes.
- O-9 (two {1, 0.5, 0} multiplier factors labelled `method`) stands, unchanged.
- Multi-source factors (rack_rate ×2, comeback_cap) and cross-difficulty factors (claim, warranty, estimate) are unchanged.

### findings (r2)

- Round-1 REDs: **F-1 closed, F-2 closed (residual O-10), F-3 closed, F-4 closed**. Round-1 observations: O-1 closed, O-4 closed apart from the compatible precheck split, O-3 reduced to O-3′. O-2, O-5, O-6, O-7, O-8 and O-9 are unchanged.
- New: **O-10** (described under rule_compute_equivalence) and **O-3′** (the 1e-6 guard is approximate and does not handle negatives). Neither has a consequence on either world. No new SOURCE-POLICY or SOURCE-FACTOR finding at charter level.
- Regression check: the only behavioural compute changes are the guard, `MX(0, …)`, the `credit_base` condition and the `window_end` selector. None changes a scored value on either unchanged world (DSL recomputation: 60.23, 327.71, 38.44, 81.34).

### closing_checklist (revision 2)

Written 2026-10-11 05:03 UTC, after both round-2 reveals (05:02:19 UTC). This replaces nothing above. The round-1 checklist stays as written.

- Per-task files `0.md`, `1.md` each carry `revision_2` with a frozen derivation, a comparison and findings. The round-1 text is untouched. Both comparisons PASS all four relationships.
- Round-1 REDs: T0-1/F-4, T0-2, T1-1, F-1, F-2, F-3 are **all verified closed** by independent recomputation, not by the rework's claims. O-1 is closed. O-4 is closed except for the compatible precheck split. O-3 is reduced to O-3′. The rationale label fix (returning_customer_rate not multi-source) is verified in `tasks/1.json`.
- Coverage and scope: the two tasks cover all four extended policies with disjoint scopes; four task tools, each used by exactly one task; uuid8s distinct (O-5 remains). PASS.
- Trees: each has 1 prerequisite problem, a `value_input` edge, an owner=user root, no cycle. The difficulty graph is acyclic. PASS.
- Factors: 5+4 and 4+4 factors; every one bears weight on its world against an honest baseline. Fall-back baselines 9.28 / 164.27 / 119.90 / 103.42 ≠ gold. Multi-source and cross-difficulty factors are present and seeded in both tasks. Ladders are real (F-4 closed). PASS, with the O-9 label observation.
- Charter self-consistency: no open SOURCE-POLICY finding. Observations O-2, O-3′, O-5..O-10.
- No new defect and no regression found. Gate snapshot (coordinator, after rework): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; traceability deferred to step 3. Cited, not re-run by this audit.
- **The difficulty passes the source-layer audit at revision 2.**
