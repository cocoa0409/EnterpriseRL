# Policy-task audit — order_returns_refunds_guarantee / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11T05:05Z (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (did not author any artifact of this difficulty).
- Freeze hashes (verified by the auditor with sha256sum, all equal to the coordinator's HASHES.txt):
  - `tasks/order_returns_refunds_guarantee/order.extended.yaml` db91e392997c329edbeb508c52f73d8e8639df62838f4a1895863d70a0eca661
  - `tasks/order_returns_refunds_guarantee/task_tools.py` 57a0462108d5881c200db18c77f77f6d555748841ceecb4ad8608ee0add562fa
  - `.audit_views/.../0.view.json` e2dc9c10…be89 (source 0.json 99ece3d6…286e); `1.view.json` 6d02362b…6725 (source 1.json 195fb262…49f0)
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/order.yaml`, `blueprint/products/member.yaml` (cross-category charter the extended policies read), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended yaml, `task_tools.py`, the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (DAYS/MONTHS/XCOUNT/RND definitions).
- Masked and unread at freeze: every task JSON field other than `frozen_time`, `user_scenario`, `initial_state` (the coordinator's views list `design_rationale, db_closure, db_closure_matches_initial_state, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents` under `_masked_keys`). No recursive search was run over `env/` or `tasks/`; every read was of an explicitly named file.
- Entry conditions (Step 0): gate snapshot `gates.r1.txt` supplied with actual output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0; masked views and hashes supplied. Entry conditions met.
- Base-copy check: lines 1–943 of the extended yaml are byte-identical to `blueprint/products/order.yaml` (diff shows only the appended extended-section banner).

### policy_conflict_scan

Extended policies (5) and their single writes:

| id | trigger | subject | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| order_ext_late_delivery_compensation (LDC) | state_due | order_refund | book_late_delivery_compensation_7d003665 (agent) | [] |
| order_ext_guarantee_claim_amount (GCA) | on_request | order_claim_file | file_guarantee_claim_a9e31314 (user) | LDC (value_input, state) |
| order_ext_guarantee_grant (GG) | on_request | order_guarantee_decision | decide_guarantee_claim_becc0a68 (agent) | GCA (value_input, state) |
| order_ext_replacement_charge (RC) | state_due | order_charge | pay_replacement_charge_b3f7fc80 (user) | [] |
| order_ext_replacement_charge_refund (RCR) | on_request | order_refund | refund_replacement_charge_bf6a8eb8 (agent) | RC (value_input, state) |

- Overlapping subjects: LDC and RCR both write `order_refund`. Their triggers are disjoint in kind (a missed guaranteed delivery vs an unreturned-replacement charge collected and the original later received); each computes `amount` on its own tool; the two can co-exist on one order without fighting over the same quantity. No conflict.
- Eligibility/time anchors: LDC (delivered after promise on an FBN guaranteed option, within the late-refund window from delivered date); GCA/GG inherit base `order_guarantee_claim` eligibility (claim window from promised date, one claim per order, return request required for damaged_item/not_as_described); RC (no first scan within unreturned-replacement days); RCR (original came back after that deadline, charge captured). The RC and RCR rules each anchor the unreturned-replacement deadline in two different ways — see finding F3.
- Terminal states: LDC refund row (funded northloop, net_paid down); GCA claim row; GG decision row; RC capture row (net_paid up); RCR refund row (funded northloop, net_paid down). No two policies set the same terminal field to different values.
- Cross-category read boundaries: LDC, GG, RC, RCR read `member` (holding status/plan/dates and member_events); each declares it in `cross_category`; GCA reads nothing cross-category. Declared exactly (the EXTENDED gate agrees).
- Claimed scopes: from the charter alone the problem trees are {LDC → GCA → GG} and {RC → RCR}. Two disjoint trees jointly covering all five extended policies; with M=2 this is the only partition in which each tree is whole. Scope exclusivity and completeness hold at charter level (each task's file confirms against its own world).
- Conflicts against the base section are listed under `override_declarations` (F1, F2) and `findings`.

### rule_compute_equivalence

Swept every `compute` binding against its `compute_basis` quotation and the `rule`, and back from every rule sentence to a binding.

- LDC: every binding has a verbatim basis (shipping_paid, days_late, lateness_allowance, handling_overrun, fulfillment_delay_allowance, member_status, lapsed_membership_allowance, late_credits_counted, repeat_lateness_allowance, order_captures, order_value_allowance, transit/other_fault requests, damaged_arrival_allowance, result). Window semantics: "whole calendar months from its earning date to the handling date are fewer than the repeat-lateness window" ≡ `XCOUNT(..., within_months=12)` with `MONTHS` = whole months (day-of-month adjusted). The "owed nothing" clause ≡ `0.0 if (shipping_paid <= 0 or days_late <= 0)`. Rounding once at the end ≡ single `RND` in result. No invented basis; no empty promise. `member_status` reads the membership's status at handling time while the ladder compares end date with the order date — the rule names no other date for the status, so the reading is the one the rule gives.
- GCA: every tier of claimed_units / shipping_share / tax_basis / refund_offset appears in both rule and compute with the same boundaries; `MX(0, RND(...))` ≡ "rounded half up to the cent and never below zero". Equivalent.
- GG: all five credits, the goodwill cap (rounded before comparison), `MN(credits_added, cap)` and the final `MN(…, net_paid, claim_cap)` are stated in the rule in that order of operations. Equivalent.
- RC: replaced_units, condition_share, charged_items, replacement_tax, plan/tenure courtesy, loop_courtesy, settlement fee, result match. One rule-internal inconsistency in the time anchor (F3): the rule's first sentence anchors the deadline on "after the replacement ships"; the settlement-fee sentence (and the compute's `replacement_shipped_on = LATEST(order_replacement.event_date)`) anchors it on "the replacement date".
- RCR: all bindings quoted; `late_rate_applied` applies relief only when `late_return_rate < 1.0` — equivalent to "only for an original first-scanned inside the grace" (a 0.0 rate times a factor is 0.0). The same deadline anchor as RC ("the replacement date plus …") is used for scan lateness and fee kept (F3).
- Rounding implementation note (observation O8): the DSL's `RND` is Python `round` on binary floats while every rule says half up. Every gold-path rounding in both worlds was re-checked in `decimal` with ROUND_HALF_UP and agrees (see task files); one baseline-substitution value in task 1 (137.14×0.25 = 34.285) rounds to 34.28 in the DSL against 34.29 half up — not a scored value.

### action_binding_and_uuids

- `(target_tool, computes)`: (book_late_delivery_compensation_7d003665, amount), (file_guarantee_claim_a9e31314, claim_amount), (decide_guarantee_claim_becc0a68, amount), (pay_replacement_charge_b3f7fc80, amount), (refund_replacement_charge_bf6a8eb8, amount) — each claimed by exactly one policy; no base policy carries a target tool.
- Tool bodies (read in full): each does one `ctx.create` (+ a `net_paid_amount` update for the three money-moving tools) and checks no eligibility, deadline, earlier booking or prerequisite. The tool layer judges no prerequisite.
- uuid8s: 7d003665, a9e31314, becc0a68, b3f7fc80, bf6a8eb8 — pairwise distinct, no shared prefix beyond a single leading hex digit (three start with `b`), no sequential or adjacent pattern. Pass.
- Docstrings (observation O5): `book_late_delivery_compensation` Args.order_id says "read from the order lookup (find_orders) before the call" — names another tool and carries "before"; both refund tools' `amount` say "rounded … before it is passed"; `decide_guarantee_claim` says "an appeal against an earlier decision"; `refund_replacement_charge` says "once the original unit of that replacement has come back". None names another problem's write or a position in the problem tree, so no second answer follows; recorded as letter-level departures from check 3.
- Enum breadth (observation O6): both refund tools accept all four `refund_component` values, so `refund_replacement_charge_bf6a8eb8` could physically create a `late_delivery_shipping` row. At policy level only LDC's rule describes a late-delivery shipping refund; RCR's rule describes "an item refund", so the hop is resolved uniquely by the rules.
- Observation O7: `decide_guarantee_claim_becc0a68` books only the decision row; base event `order_guarantee_decision` declares a trigger to `order:order_refund` for granted decisions, which no tool of this difficulty performs and no extended rule mentions.

### prerequisite_graph

- `prerequisite` filled on every extended policy (LDC [], GCA [1 edge], GG [1 edge], RC [], RCR [1 edge]).
- Every `problem` points at another extended policy id of this file (never base, never self). Graph: LDC → GCA → GG; RC → RCR. Acyclic.
- `policy_source` verbatim in the blocked policy's own rule (scripted whitespace-normalised containment check: all three True).
- `form: state` on all three edges; no `fallback_reason` (correct for state form).
- `resolved_by` equals the depended-on policy's target tool on all three edges.
- `kind: value_input` on all three; `gate` names a binding that exists in the blocked policy's compute: `shipping_refunds_issued` (GCA), `amount_claimed` (GG), `charge_captured` (RCR).
- `condition` vs sentence: GG and RCR conditions match their sentences exactly in strength. GCA's condition ("An order delivered after its promised delivery date on a Northloop-fulfilled guaranteed option, inside the late refund request window, carries a refund entry of the late-delivery shipping component") omits LDC's zero-shipping exclusion that the sentence's word "owed" imports — slightly broader than the sentence on a zero-shipping order (observation O9). GCA's `effect` asserts "the refund offset deducts nothing because the only refund standing is that compensation", which is true only on an order with no other refund (world-specific phrasing in general text; observation O9). No "in this task / at the opening" phrasing.

### prerequisite_sentences

| Edge | Sentence (verbatim, blocked rule) | Connective | Waited-on state | Single write bringing it about |
| --- | --- | --- | --- | --- |
| GCA ← LDC | "The amount claimed is fixed only after the order's records carry the late-delivery shipping refund owed for a missed guaranteed delivery." | only after | a late-delivery shipping refund row on the order (table words: `order_refund`, component `late_delivery_shipping`) | LDC — its rule is the only rule of this difficulty describing "one late-delivery shipping refund"; RCR's rule describes "an item refund" |
| GG ← GCA | "The guarantee grant is not fixed until a Northloop Guarantee claim with its claimed amount stands recorded on the order." | not … until | a claim-filing row with `claim_amount` | GCA (only `order_claim_file` writer) |
| RCR ← RC | "The refund of a replacement charge is booked only after that charge stands captured on the order." | only after | an `order_charge` row with reason unreturned-replacement on the order | RC (only `order_charge` writer) |

- Four-point test: each joins its own result to a record-visible state with an ordering connective; names no tool, policy id, snake_case token or row id; strength matches the condition (GCA edge: see O9). Pass.
- Depended-on rules do not restate the sentences (LDC rule mentions no claim; GCA rule no grant; RC rule no refund). No second wording, no tool name, no other problem's id in any extended rule.
- Derivations (single reading): (1) GCA sentence → "late-delivery shipping refund owed for a missed guaranteed delivery" → LDC's rule "an order delivered after its promised delivery date is owed late-delivery compensation, booked as one late-delivery shipping refund" → book it, then compute the claim. (2) GG sentence → "claim with its claimed amount recorded" → GCA's rule "files the Northloop Guarantee claim … themselves, and the amount claimed is worked out for them before they file it" → hand the filing to the buyer with the computed amount. (3) RCR sentence → "that charge stands captured" → RC's rule "the replacement charge falls due and the buyer settles it as a payment on the order, captured as an unreturned-replacement charge" → hand the payment to the buyer.
- Undeclared cross-problem orders in rules: none found in the extended rules. Base rules carry no sentence ordering two extended problems (base `order_refund_timing` "Original shipping and tax components are released together with the item component" concerns base components only). No tree rests on a base ordering sentence.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

- LDC (refs: order_agg_return_history, order_cancellation, order_return_deductions, order_refund_amount, order_refund_timing, order_lost_and_undeliverable, order_late_delivery, order_guarantee_claim):
  - `order_late_delivery` s1 (amount = shipping charge actually paid, liability party) — superseded, declared. s2 (request window) — superseded, declared. s3 ("An order whose shipping charge was zero earns nothing … options without guaranteed delivery never earn it") — followed. Merged semantics unique for FBN options.
  - `order_refund_amount`: funded_by sentence does not list late-delivery refunds; LDC's "funded by Northloop" equals the FBN liability party. "Total refunds on an order never exceed its net_paid_amount" — inherited, not binding in any task world. Destination: gift exception covers returns only; LDC's original-payment destination does not conflict.
  - Other refs (return history, cancellation, return deductions, refund timing, lost/undeliverable, guarantee claim) govern quantities LDC does not compute — followed.
  - Not in refs but read by the same KB: `order_agg_multi_holding` "Every order is its own record … never pooled with another order. The only buyer-level figure that reads across orders is the buyer's remorse-return history" vs LDC's repeat-lateness allowance, which counts late-delivery credits each earned on another order (usage_ref) — observation O2 (the count is taken from the Loop+ ledger, not from order rows, so a second defensible amount is not established).
  - Observation O10: superseding s1 wholesale leaves the seller-fulfilled late-delivery refund amount stated only negatively ("stays with the seller and is not late-delivery compensation"); no task of this difficulty is seller-fulfilled.
- GCA (refs: order_guarantee_claim, order_refund_amount; overwrite []): base defines no claim amount; GCA's tax proration equals base `order_refund_amount`'s tax-share method; claim eligibility inherited. No conflict.
- GG (refs: order_guarantee_claim): "The granted amount is the order's net_paid_amount at decision time, capped at the claim cap, and is funded by the option's liability party" — superseded, declared; merged semantics unique (amount claimed + goodwill credits, capped by net paid and claim cap). Appeal, claims-per-order, "A granted claim and a return refund cannot both pay the same units" — inherited.
- RC (refs: order_capture_and_shipping_charge, order_replacement_terms): the unreturned-replacement charge sentence — superseded, declared (amount and settlement form). Capture-once sentence of base capture policy already coexists with base's own unreturned_replacement_item capture. No further conflict. (Deadline-anchor inconsistency inside RC's own rule: F3.)
- RCR (refs: + order_replacement_terms and the eight LDC refs): `order_refund_amount` funded_by sentence — superseded, declared. Two base sentences that govern RCR's scored write are handled differently and are NOT named in `overwrite`:
  - F1 — `order_replacement_terms`: "A replacement and an item refund are mutually exclusive for the same units: once one is booked, the other is not." RCR books "an item refund tied to the return of the original unit" on the very units the replacement was shipped for.
  - F2 — `order_return_deductions`: "Deductions apply only to the item component of a return refund and only when the return reason is not a seller-fault reason." RCR's refund is an item-component refund tied to a return; replacements exist only for seller-fault reasons (defective, damaged_in_transit, wrong_item), yet RCR withholds a late-return rate, a condition rate and a late-label fee from it.
  - The author's own `replaced_by` text separates "return refunds of the item price" from the replacement-charge refund, which shows awareness that the refund sits next to the base return-refund rules; the base sentences above are still not declared.
  - Consequences are demonstrated in `1.md`.

### factor_ladders

Per policy (label as declared → auditor's verdict on label; tiers; multi-source; cross-category):

- LDC (6 factors; 5 parameter, 1 method): lateness_allowance method (per-day × days vs flat constant vs none — different functional forms: honest); fulfillment_delay_allowance parameter; lapsed_membership_allowance parameter, member (status AND end-date-vs-order-date: membership row + order row → multi-source); repeat_lateness_allowance parameter, member (ledger count); order_value_allowance parameter; damaged_arrival_allowance parameter. Each ladder 3 disjoint tiers, stated in the rule, implemented in compute, fall-through = baseline 0.0, which equals what `baseline.rule` gives for that input. Distinct outcomes in every ladder. Conditions and outcomes are recognisable marketplace goodwill practice (lateness, warehouse delay, lapsed/former member, repeated lateness, order value, damaged arrival). Pass.
- GCA (4 declared; 2 parameter, 2 method): claimed_units method; shipping_share parameter; tax_basis method; refund_offset parameter. All in rule and compute; baseline.rule ("item price of every unit ordered, plus the order's shipping charge, plus the order's full sales tax, less every refund already issued") equals every fall-through.
  - F4 (SOURCE-FACTOR, structure): claimed_units' fall-through "any other order is claimed for every unit ordered" requires an order with no return request at all. GCA's scope is a buyer whose order "arrived damaged, defective or not as described"; base `order_guarantee_claim` says "A not_as_described, damaged_item or return_not_refunded claim requires a return request on the order", and the schema's `return_reason` enum has exactly the five seller-fault and three remorse reasons the two upper tiers partition. So every customer who reaches this write is on tier 1 or tier 2; the boundary between {1,2} and the fall-through restates the policy's scope. The ladder has two live tiers. The factor does not count.
  - Observation O3: tax_basis tier 2 ("the order's sales tax less the tax already refunded") and refund_offset tier 1 ("only those item and tax refunds are deducted") together subtract a standing tax refund twice when every unit is claimed (e.g. tax 10.00, tax refund 4.00, item refund 0: tax part 6.00, offset 4.00 → the claim is short by 4.00). Reached by neither task world.
  - Observation O4: base `order_refund_timing` releases original shipping and tax "together with the item component", so an order's refunds are never original-shipping-only; refund_offset's fall-through "every refund issued" is then reachable in scope only with no refunds at all, where it equals tier 2's 0.00. On a world with a late-delivery refund the baseline substitution still differs (shown in 0.md), so the factor is kept.
  - Label check: refund_offset tiers select different sums ("item and tax refunds" vs 0 vs "every refund") — closer to a method than a number; recorded as observation only.
- GG (6 factors; 5 parameter, 1 method): carrier_damage_credit method (per-unit × units vs flat vs none: honest); pickup_wait_credit parameter (no return scans AND latest request age: distinct records → multi-source); winback_credit parameter, member; tenure_credit parameter, member; usage_credit parameter, member; goodwill_cap parameter. 3 disjoint tiers each; all in rule and compute; fall-through = baseline 0.0 / 1.0; baseline.rule (amount claimed capped by net paid and claim cap) self-sufficient. Pass.
- RC (5 declared; 4 parameter, 1 method): condition_share parameter; replacement_tax method; plan_courtesy parameter, member; tenure_courtesy parameter, member; settlement_fee parameter. baseline.rule (item price of the replaced units, no tax) self-sufficient and every fall-through equals it.
  - F5 (SOURCE-FACTOR, structure): replacement_tax' fall-through "where no unit was replaced, no tax" requires replaced_units = 0. RC's own rule says "an order with no replacement shipped owes no replacement charge" and excepts "a lost package", and base `order_replacement_terms` ships replacements only against damaged_in_transit / defective / wrong_item return requests or a lost package. Every customer who reaches RC's write has ≥ 1 replaced unit; the fall-through restates the scope. Two live tiers; the factor does not count, and it is RC's only `method` factor.
  - Observation O12: tiers 1 and 2 of replacement_tax ("full tax × condition share" vs "tax × charged items / (item subtotal + shipping)") coincide whenever every unit is replaced and the shipping charge is 0.00.
- RCR (6 declared; 5 parameter, 1 method): late_return_rate parameter; loop_relief method (member plan AND scan inside grace → multi-source); condition_rate parameter; fee_kept parameter; late_label_fee parameter (scan after deadline AND return method → multi-source); delay_courtesy parameter.
  - F6 (SOURCE-FACTOR, mislabel): loop_relief's three tiers are `late_return_rate × 0.5`, `late_return_rate × 0.75`, `late_return_rate × 1` — one formula with a different multiplier substituted; that is a `parameter` by the skill's own definition ("a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)"). With it relabelled, RCR has six parameter factors and no method factor.
- Counts per tree (before strike-outs): {LDC, GCA, GG}: 16 factors, member cross-category reads in 5, multi-source in ≥ 2. {RC, RCR}: 11 factors, member reads in 3, multi-source in ≥ 2.
- Observation O1: every `cross_difficulty` factor reads `member`. `blueprint.yaml` defines five difficulties (order, selling, fulfill, payout, standing); member is a product of the scenario but owns no difficulty. Read literally ("another difficulty's records"), neither tree has a cross-difficulty factor; read as "another product's records" (the gate's reading), both do. Recorded as an observation; the member rows these factors read are seeded in both worlds.

### findings

| # | Class | Summary | Bears on |
| --- | --- | --- | --- |
| F1 | SOURCE-POLICY RED | Undeclared override: RCR books an item refund on replaced units against base "A replacement and an item refund are mutually exclusive for the same units: once one is booked, the other is not." | task 1 |
| F2 | SOURCE-POLICY RED | Undeclared override: RCR withholds deductions (late-return rate, condition rate, late-label fee) from an item refund tied to a seller-fault return against base "Deductions apply only to the item component of a return refund and only when the return reason is not a seller-fault reason." | task 1 |
| F3 | SOURCE-POLICY RED | RC's rule anchors the unreturned-replacement deadline both on "after the replacement ships" (sentence 1, and base parameter `unreturned_replacement_charge_days`: "Calendar days after a replacement ships") and on "the replacement date plus the option's unreturned replacement days" (settlement-fee sentence; same in RCR); where the replacement order ships a day after the replacement is created the two give different deadlines | task 1 |
| F4 | SOURCE-FACTOR RED (structure) | GCA claimed_units fall-through unreachable in scope → 2 live tiers | task 0 |
| F5 | SOURCE-FACTOR RED (structure) | RC replacement_tax fall-through unreachable in scope → 2 live tiers; RC's only method factor | task 1 |
| F6 | SOURCE-FACTOR RED (label) | RCR loop_relief is a multiplier substitution labelled method → RCR has no method factor | task 1 |
| O1–O12 | observations | as described above (O1 member is not a difficulty; O2 multi-holding sentence; O3 double tax deduction; O4 offset fall-through; O5 docstring wording; O6 enum breadth; O7 decision trigger refund not booked; O8 RND vs half-up; O9 GCA edge condition/effect wording; O10 seller-fulfilled late refund stated only negatively; O11 realism of pay-then-refund (task 1 file); O12 replacement_tax tiers coincide at zero shipping) | as noted |

Each finding: symptom, root cause and evidence are as given in the sections above (quotations are verbatim from `order.extended.yaml` lines 1586–1650 / 1781–1849 / 1189–1220 and `blueprint/products/order.yaml` lines 760–770, 829–837, 906–918); demonstrated consequences live in the task files.

## closing_checklist

Written after both reveals (2026-10-11T05:02:34Z); the section above is the pre-reveal charter-global freeze (sha256 d86f3d708b29436a7f7f0d1c2f00b0f8f2bf37c50e606a6f7ef8ab8e3eb1988d at that time) and is not edited.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; first revision, no older revisions.
- Comparison results: blind derivation = GT on every scored value and call in both tasks (30.99 / 143.30 / 179.13; 144.64 / 85.15). That equality does not clear the findings below.
- Coverage and scope: `charter_scope` task 0 = {LDC, GCA, GG}, task 1 = {RC, RCR} — pairwise disjoint, jointly all five extended policies; every task tool used once in its own task; uuid8s independent (above).
- Trees: task 0 LDC → GCA → GG (2 prerequisite problems, 2 value_input edges, user write GCA); task 1 RC → RCR (1 prerequisite problem, 1 value_input edge, user write RC); the union is acyclic. PASS.
- Factors: task 0 SOURCE-FACTOR RED (T0-1 member seed contradicts member charter; T0-2 GCA left with 3 factors); task 1 SOURCE-FACTOR RED (T1-4 RC no method factor; T1-5 RCR no method factor).
- Policy self-consistency: task 1 SOURCE-POLICY RED (F1, F2, F3); task 0 PASS.
- Unique solution: task 1 SOURCE-TASK RED (F3: RC 144.64 vs 140.64; F1/F2 alternative terminal states); task 0 PASS.
- Post-reveal observation O13 (from `tasks/1.json` design_rationale): the dossier asserts that base would forbid RCR's refund through the late-request-window gate and that the gate was retired by LDC's overwrite — either RCR depends on an override declared in another policy, or the assertion is false; on the auditor's reading the gate concerns late-delivery refunds only.
- Gates re-run on the final form: not applicable — the difficulty does not close; this audit edits no artifact.

**Difficulty status: NOT CLOSED.** Task 0: SOURCE-FACTOR RED. Task 1: SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED.

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 task JSON was opened. Auditor: the same independent auditor as revision 1. Clock at start of round 2: 2026-10-11T07:01:01Z.
- Inputs verified with sha256sum, all equal to the coordinator's `HASHES.txt` (round 2): `order.extended.yaml` 12e11e72c56bcc2ea6491643d7c9541d7dc3698fc5d3b7f98d268667c512d326 (round 1: db91e392…a661 — changed); `task_tools.py` 81bdf6028ce5917b9b160381b1e8f586b40f5e81c09c1c9be16bb49c16ddf55c (round 1: 57a04621…62fa — changed); `0.view.json` 659c7583…4c60 (source 0.json 287065a1…fde5); `1.view.json` 785a9bc3…ae98 (source 1.json 41f72089…4cfc). Both shared inputs changed, so every charter-global section is re-derived in full below rather than carried forward.
- Gate snapshot `gates.r2.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (13/77, 10/17), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0. Entry conditions met.
- Base copy: lines 1–943 of the extended yaml still byte-identical to `blueprint/products/order.yaml`.
- Additional read for this round: `blueprint/products/standing.yaml` (the category the new cross factors read) — a blueprint product charter, not the sibling difficulty's tasks or audits.
- contamination_disclosure: the auditor carries the revision-1 reveal (round-1 gold values, traces and dossier text) in memory. It is prior knowledge, not a leak of round-2 GT; the round-2 derivation below is computed from the round-2 charter and views alone, and every round-2 figure differs from its round-1 counterpart wherever the charter changed.

### policy_conflict_scan (r2)

Same five policies, targets, owners and edges as revision 1 (LDC → GCA → GG; RC → RCR). Changes: GCA's scope now also covers an order that "never arrived"; GG drops the usage credit and adds an account-trust share read from `standing`; RC folds sales tax into its base amount, makes the settlement fee per-day past 14 days, adds an account-trust share (`standing`) and states one deadline anchor; RCR declares two more overwrites, makes the late-return rate per-day and the fee kept per-day, and turns Loop+ relief into a factor. No two policies set one terminal field differently; cross-category reads declared exactly (GG and RC: member + standing; LDC, RCR: member). Claimed scopes still partition into {LDC, GCA, GG} and {RC, RCR}.

### rule_compute_equivalence (r2)

Scripted check: every `compute_basis` quotation is contained (whitespace-normalised) in its policy's rule, except RCR `replaced_on`, whose basis begins "the unreturned-replacement deadline (the replacement date recorded …" while the rule reads "its unreturned-replacement deadline (the replacement date recorded …" — a one-word paraphrase of a sentence that is in the rule (observation R2-O3). Every `baseline.rule` is a verbatim sentence of its rule. Manual sweep of the changed bindings: GCA claimed_units / refund_offset, GG account_trust_share / credits_capped / credits_paid, RC replacement_tax / account_trust_share / account_courtesy / settlement_fee, RCR late_return_rate / relief_factor / fee_kept / deductions — each implements its rule sentence with the same boundaries and rounding; no invented basis, no empty promise. RC's rule says "Four rules of the replacement charge then apply" and then states five factor rules (condition share, plan courtesy, tenure courtesy, account-trust share, settlement fee) — a count slip with no effect on any value (R2-O4).

### action_binding_and_uuids (r2)

Tool names and uuid8s unchanged (7d003665, a9e31314, becc0a68, b3f7fc80, bf6a8eb8); each `(target_tool, computes)` claimed once. Bodies still one `create` (+ `net_paid_amount` update) with no check. Docstrings: `find_orders` and "before the call" removed; "rounded half up to the cent" no longer says "before it is passed"; "an earlier decision" became "a recorded decision on the claim"; "once the original unit … has come back" became "where …". The remaining "later than its promised date" describes a late delivery, not a sequence. O5 closed. O6 (enum breadth) and O7 (decision tool books no triggered refund) unchanged, answered without change; they remain observations.

### prerequisite_graph and prerequisite_sentences (r2)

Unchanged edges, sentences, forms, gates and `resolved_by`; scripted verbatim check True on all three; acyclic. GCA edge `condition` now adds "with a shipping charge above zero" (matches the sentence's "owed"), and its `effect` no longer asserts a world-specific "only refund standing" (O9 closed). Single-writer derivations of revision 1 still hold (no rule of RC/RCR describes a late-delivery shipping refund; only GCA files a claim; only RC captures a charge).

### override_declarations (r2)

- F1: RCR now names `order_replacement_terms` "A replacement and an item refund are mutually exclusive for the same units: once one is booked, the other is not." with replaced_by "A replacement and an item refund of the units' purchase price stay mutually exclusive for the same units; the replacement-charge refund … is the one item refund that may follow a replacement on them." — declared, and the replaced_by sentence is in the rule; merged semantics unique. **Closed.**
- F2: RCR now names `order_return_deductions` "Deductions apply only to the item component of a return refund and only when the return reason is not a seller-fault reason." with replaced_by keeping the base bar for item-price refunds and stating that the replacement-charge refund withholds its own deductions whatever the reason. Declared, in the rule; unique. **Closed.**
- F3: RC's overwrite replaced_by now reads "when the original unit has no first carrier scan by the unreturned-replacement deadline", and its rule defines the deadline once: "the replacement date, the date recorded on the replacement entry, which is the day the replacement ships, plus the option's unreturned replacement days counted in calendar days; a first carrier scan of the original unit on the deadline itself is in time." RCR repeats "the replacement date recorded on the replacement entry". One anchor in the text; whether the world agrees with "which is the day the replacement ships" is checked in `1.md`. **Closed at charter level.**
- RC overwrite (unreturned-replacement charge) still declared; the charge now carries tax, which the superseded clause covered.
- LDC: the seller-fulfilled sentence is now positive ("earns a refund of the shipping charge actually paid on the order, funded by the seller, with none of the allowances below") — O10 closed. GG, GCA unchanged in their override relationship. O2 (multi-holding sentence) answered without change; remains an observation.

### factor_ladders (r2)

- LDC: unchanged (6; 5 parameter, 1 method; member ×2). Pass.
- GCA (4; 2 parameter, 2 method): claimed_units now "both seller-fault and remorse → seller-fault units only / no return request (as on an order that never arrived) → every unit ordered / otherwise → units on every return request"; the rule's scope now includes a never-arrived order, whose item_not_received claim needs no return request, so the second tier is reachable and the fall-through (fault-only or remorse-only requests) is reachable. Baseline "the units on the order's return requests" = fall-through. **F4 closed.** refund_offset: tier 1 now deducts item refunds only ("tax refunds are netted in the tax part") — the double subtraction of O3 is gone (**O3 closed**). O4 persists unchanged: the fall-through "every refund issued" is reachable in GCA's scope only with no refunds at all (base `order_refund_timing` releases original shipping and tax "together with the item component", and a refund with an item component lands on tier 1 or 2), where it yields the same 0.00 as tier 2; kept as an observation, as in revision 1.
- GG (6; 5 parameter, 1 method): carrier_damage (method), pickup_wait, winback (member), tenure (member), account_trust_share (standing), goodwill_cap. All tiers in rule and compute; fall-throughs reachable.
- RC (5; 4 parameter, 1 method): condition_share, settlement_fee (method: per-day × days vs flat vs none — honest), plan_courtesy (member), tenure_courtesy (member), account_trust_share (standing). replacement_tax is no longer a factor (tax is in the baseline). **F5 closed.**
- RCR (6; 4 parameter, 2 method): late_return_rate (method: per-day rate × days vs whole charge vs none), loop_relief (parameter: factor 0.5 / 0.75 / 1 — label now honest), condition_rate, fee_kept (method: per-day × days vs flat vs none), late_label_fee, delay_courtesy. **F6 closed** (the mislabel is gone).
- **R2-F1 (SOURCE-FACTOR RED, pre-existing, missed in revision 1): two RCR ladders have an unreachable fall-through.** RCR's write exists only "When the original unit of a replacement comes back after its unreturned-replacement deadline", and RC's charge — the refund's captured base — falls due only "when the original unit has no first carrier scan by the unreturned-replacement deadline". So every customer who reaches RCR's write has a first scan after the deadline. late_return_rate's fall-through "a first scan by the deadline keeps nothing" is then held by nobody (two live tiers: inside grace / beyond grace). late_label_fee's fall-through "an original scanned by the deadline pays no late-label fee" is likewise held by nobody: replacements exist only on Fulfilled-by-Northloop options, whose `allowed_return_methods` are [ups_dropoff, carrier_pickup], and a returnless return sends no unit back, so every in-scope original lands on tier 1 or 2. This is the same defect class as F4/F5 (the boundary restates the policy's scope). The two ladders and the scope sentence were already in the revision-1 charter; revision 1 missed them. Striking both leaves RCR with loop_relief, condition_rate, fee_kept, delay_courtesy = 4 factors (3 parameter, 1 method) — the count bounds still hold, but the two ladders fail the unreal-ladder test on their own.
- **R2-F2 (SOURCE-FACTOR RED, new in revision 2): the account-trust share ladder (GG and RC) is not one the line of business holds.** Its tiers: "a selling account that is suspended, under appeal or deactivated receives none of the goodwill credits [keeps none of the courtesy]; a selling account at risk receives the at-risk trust share of them [0.5]; any other buyer … in full". The quantity is a buyer-side amount — goodwill on a Northloop Guarantee claim for goods that arrived broken (GG), or a Loop+ plan/tenure courtesy on an unreturned-replacement charge (RC). The at-risk condition is the standing charter's warning state: "A good-standing seller is placed at risk when active violation points reach the warning threshold, or when a metric breaches the limits of the seller's current level" — i.e. listing-policy points or late-shipment and cancellation rates of the person's own shop. A marketplace sizes buyer goodwill and membership courtesies on the buyer relationship (claim merit, membership, buyer-abuse signals), and does not halve them because the same person's shop holds a listing warning. The suspended/deactivated tier can be defended as account-level enforcement reaching linked profiles; the at-risk tier (the one both tasks sit on) cannot. The rule's own justification ("goodwill is a courtesy Northloop extends in full only to profiles not under a selling-account action") names the bridge rather than an industry practice. The factor fails the unreal-ladder test in both policies. Struck, neither task keeps a factor that reads another difficulty's records: the remaining cross factors read `member`, which owns no difficulty (O1). This is a realism judgment, and it is stated as such.
- Counts (before the R2 strikes): task 0 tree — LDC 6, GCA 4, GG 6; cross factors: member ×4, standing ×1. Task 1 tree — RC 5, RCR 6; cross: member ×3, standing ×1. Multi-source: GG pickup_wait, LDC lapsed; RCR loop_relief, late_label_fee (struck), RC account_trust_share/plan_courtesy (single records — membership row only) — RCR loop_relief (membership row + scan row) still supplies task 1's multi-source factor.

### findings (r2, charter-global)

| # | Class | Status |
| --- | --- | --- |
| F1, F2, F3 | SOURCE-POLICY | closed at charter level (F3's world check in `1.md`) |
| F4, F5, F6 | SOURCE-FACTOR | closed |
| R2-F1 | SOURCE-FACTOR RED | new detection (pre-existing since revision 1): RCR late_return_rate and late_label_fee fall-throughs unreachable — task 1 |
| R2-F2 | SOURCE-FACTOR RED | new in revision 2: account-trust share at-risk tier unreal in GG and RC; without it no factor reads another difficulty — tasks 0 and 1 |
| O1 | observation → superseded by R2-F2 | standing is a difficulty, but the only factor reading it fails the realism test |
| O3, O5, O9, O10 | observations | closed |
| O2, O4, O6, O7, O8 | observations | unchanged |
| R2-O3, R2-O4 | observations | RCR `replaced_on` basis paraphrase; RC "Four rules" count slip |

### closing_checklist (r2)

Written after the round-2 reveal (2026-10-11T07:06:42Z); the revision_2 charter-global sections above were hashed at 07:06:35Z before it.

- Round-1 REDs: F1/T1-1, F2/T1-2, F3/T1-3, F4/T0-2, F5/T1-4, F6/T1-5, T0-1 — **all genuinely closed** (verified against the round-2 charter and views; blind r2 values equal GT r2 on every scored argument).
- Reworker's observation claims: O3, O5, O9, O10, O13 closed (verified); O1 — the new cross factor reads a real difficulty (`standing`) but fails R2-F2; O4 — claimed addressed, not borne out (remains an observation); O2, O6, O7, O8, O11 and the 0.md dedup-evidence note — answered without change, accepted as observations; scratch-script references — none found in either dossier. "Proof/rationale text swept for staleness" — incomplete (R2-O5 in `0.md`).
- Regressions: none in the policy-consistency, tree or unique-solution relationships. New defects: R2-F2 (introduced by the O1 rework, both tasks). Newly detected pre-existing defect: R2-F1 (task 1).
- Coverage/scope: unchanged partition {LDC, GCA, GG} / {RC, RCR}; uuid8s unchanged; trees acyclic, each with a user write.
- Gates re-run on the final form: not applicable — the difficulty does not close.

**Difficulty status (r2): NOT CLOSED.** Task 0: SOURCE-FACTOR RED (R2-F2). Task 1: SOURCE-FACTOR RED (R2-F1, R2-F2). All other relationships PASS in both tasks.

## revision_3

### charter_global_frozen (revision 3)

- Written before any round-3 task JSON was opened. Clock at start of round 3: 2026-10-11T08:09:30Z. Same auditor.
- Verified with sha256sum, all equal to round-3 `HASHES.txt`: `order.extended.yaml` 76030d59894a4b1dfd5938eb3bb618199db3ed903e6dc8a40130ccb42047061c (r2: 12e11e72…d326 — changed, so every charter-global section is re-derived); `task_tools.py` 81bdf6028ce5917b9b160381b1e8f586b40f5e81c09c1c9be16bb49c16ddf55c (unchanged since r2 — §action_binding_and_uuids (r2) carried forward on that hash); `0.view.json` 6f46fccd…b83e (source 0.json b6e1d285…34c7); `1.view.json` 8cfee49c…3a9f (source 1.json 841670da…4d45). Base copy lines 1–943 still byte-identical to `blueprint/products/order.yaml`.
- `gates.r3.txt`: all eight gates rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING OK; CACHE-DIFF info; SCOPE OK).
- contamination_disclosure: prior knowledge of the revision-1 and revision-2 reveals only.

### charter delta and re-derived checks (r3)

- **GG** is back to its revision-1 form (five credits incl. usage credit, mid-claim cap share 0.25, member reads only; no `standing` read). Its revision-1 conclusions hold again verbatim against this text (§rule_compute_equivalence, §factor_ladders GG above): 6 factors, 5 parameter / 1 method, all ladders reachable.
- **RC** drops the account-trust share and adds `overdue_day_count` (method): "where a first carrier scan of the original unit stands after the deadline, the count ends on that scan date …; where the return was set up as a carrier pickup and no carrier scan stands, no overdue day is counted …; otherwise the count ends on the settlement date." The settlement fee (method) now reads that count. RC: condition_share (P), overdue_day_count (M), settlement_fee (M), plan_courtesy (P, member), tenure_courtesy (P, member) — 5 factors, 3 P / 2 M. Every tier reachable for customers who reach RC's write (late scan before settlement; pickup set up and never scanned; drop-off never scanned). The "Five rules … (the condition share, the plan courtesy, the tenure courtesy, the overdue-day count and the settlement fee)" sentence now matches the factor list — **R2-O4 closed**.
- **RCR** re-tiers two ladders. late_return_rate (M): "> grace or no scan → rate one; > late courtesy days (5) and ≤ grace → per-day rate × days; within the late courtesy days → none" — every in-scope original is scanned after the deadline, and 1–5 days late is now the reachable fall-through. late_label_fee (P): "carrier pickup → late pickup fee; drop-off first-scanned more than the label validity days (3) after the deadline → late drop-off fee; drop-off within the label validity days → none" — all three reachable for an original that comes back late. fee_kept now uses the same overdue-day rule as RC (count ends at a scan on or before the capture date; none for an unscanned pickup; otherwise to the capture date), so the fee kept equals the fee the captured charge carried. **R2-F1 closed.** RCR: 6 factors, 4 P / 2 M.
- **R2-F2 closed**: no policy reads `standing`; both customers are `buyer` again (views).
- Scripted checks on the r3 text: every `policy_source` verbatim in its own rule (3/3); every `overwrite.replaced_by` in its rule (7/7); every `compute_basis` quotation contained in its rule (RCR `replaced_on` now quotes "its unreturned-replacement deadline (…" — **R2-O3 closed**); every `baseline.rule` in its rule; no two factors of one policy share a binding. Prerequisite graph, sentences, forms, gates and `resolved_by` unchanged — §prerequisite_graph / §prerequisite_sentences (r2) stand. Override declarations F1–F3 unchanged and still declared.
- LDC and GCA: text unchanged from revision 2 in every binding, ladder and baseline exercised (recomputed); §factor_ladders (r2) for them stands. O4 unchanged (observation).

### O1 — auditor's judgment requested by the coordinator

- Facts: every cross-category factor now reads `member` (LDC lapsed/repeat, GG winback/tenure/usage, RC plan/tenure courtesy, RCR loop_relief). `blueprint.yaml` gives difficulties to order, selling, fulfill, payout and standing; member is a tiered product (six plans, own charter, holding and ledger) with no difficulty. The DSL's cross reads (`CFIELD`/`CPARAM`/`XCOUNT` in `check_compute.py::build_env`) are scoped to the buyer's own customer id, so a buyer-only customer has no records in any of the other four difficulties; the only way to read one is to make the buyer a seller too, which revision 2 did and which failed on realism (R2-F2).
- Criterion: the skill asks for a factor "deciding its tier from the customer's holdings or ledger in another difficulty", and spells out the failure as "the other product's holding for this customer, or the ledger rows an XSUM/XCOUNT/XMAX/XLATEST reads, are absent … so the factor tests nothing about that product"; instantiation treats a difficulty as "one tiered product line". What the criterion protects is that the solver must consult another product line's holding, ledger and charter, seeded and weight-bearing on the task's world.
- Judgment: the member reads meet that purpose — Loop+ is a separate tiered product line with its own charter parameters (reactivation window, late-delivery credit amount), its holding and ledger rows are seeded and consistent with the member charter in both worlds, and several of these factors bear weight on each world (see task files). That member owns no difficulty is a property of the blueprint's difficulty selection, not a defect of this task bundle. **O1: accepted as satisfied; closed as an observation.** Recorded as a judgment: if the coordinator applies the literal reading ("one of the five blueprint difficulties"), both tasks fail that bound, and no realistic buyer-side rule found so far satisfies it.

### new observations (r3)

- R3-O1 (realism tension, not task-bearing): RC's overdue-day count spares an unscanned carrier pickup "since collecting the unit is Northloop's carrier's task", but RCR's late-label ladder charges the late pickup fee (9.99) to any late original "collected by a carrier pickup", whoever made the collection late. In the same situation (a pickup Northloop's carrier performed late), one rule treats lateness as the carrier's and the other bills the buyer. Neither task world reaches it (task 1 is a drop-off). Not demonstrable as a second answer on any task.
- R3-O2 (realism, inherited): RC's charge still falls due on an unscanned carrier-pickup return, where the new overdue rule itself says collection is Northloop's task; only the fee is waived. Not task-bearing.

### findings (r3, charter-global)

| # | Status |
| --- | --- |
| R2-F1 | closed (both RCR ladders have three reachable tiers) |
| R2-F2 | closed (standing factor removed; customers buyer-only) |
| R2-O3, R2-O4 | closed |
| O1 | judged satisfied by member reads (see above) |
| O2, O4, O6, O7, O8 | observations, unchanged |
| R3-O1, R3-O2 | new observations, not task-bearing |

### closing_checklist (r3)

Written after the round-3 reveal (2026-10-11T08:12:13Z); the revision_3 sections above were hashed at 08:12:06Z before it.

- Per-task files `0.md`, `1.md` with `_difficulty.md`; revisions 1–3 appended in order, earlier text untouched; every revision-3 comparison carries a PASS.
- Round-2 REDs: R2-F1 closed, R2-F2 closed — verified against the round-3 charter and views. Round-2 observations: R2-O3, R2-O4, R2-O5 closed; O4 left as an observation (the dossier withdrew its unsupported claim). O1 judged satisfied by the member reads (see §revision_3). No regressions: blind r3 = GT r3 on every scored argument (30.99 / 143.30 / 179.13; 140.64 / 89.27); round-1 closures (F1–F6, T0-1) still hold on the r3 text.
- Coverage and scope: extended policies fully covered; task scopes {LDC, GCA, GG} and {RC, RCR} pairwise disjoint; task tools and GT closed; uuid8s independent and unchanged.
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write GCA; task 1 — 1 prerequisite problem, 1 value_input edge, user write RC; the difficulty's prerequisite graph is acyclic.
- Factors: every computation has 4–6 factors (LDC 6, GCA 4, GG 6, RC 5, RCR 6), ≥ 2 parameter and ≥ 1 method each; every ladder has three pairwise-disjoint tiers, all reachable in scope and stated in the rule; every factor bears weight against an honest baseline; every whole baseline gives a definite number ≠ gold (9.99, 194.98, 143.30; 198.43, 140.64); each task has a multi-source factor and cross-category (member) factors — the latter accepted under the O1 judgment.
- Gates on the final form: the coordinator's `gates.r3.txt` (all eight rc=0) on the hashed final artifacts — cited, not re-run by the auditor (the skill assigns gate runs to the brief).
- Open observations (not grounds for rework): O2, O4, O6, O7, O8, O11, R3-O1, R3-O2.

**Difficulty status (r3): all four relationships PASS for both tasks — closed at the source layer**, subject to the coordinator's acceptance of the O1 judgment.
