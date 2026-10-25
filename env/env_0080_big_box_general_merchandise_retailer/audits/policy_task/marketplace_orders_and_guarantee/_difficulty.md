# Policy-task audit — marketplace_orders_and_guarantee / charter-global

## charter_global_frozen
- freeze time: 2026-10-23T20:56Z (written before any task GT field was read); auditor: erl-task-policy-audit (independent auditor agent, revision_1)
- `market.extended.yaml` sha256 a7ec400cb5d6329bb1cb155faa22692ac1a987121e54b0570225a2ca92f2f366; `task_tools.py` sha256 af06b5a0fe439cf093faee65f8881807e980bb9dec72d5f84c78e4b5b2a4cafb; `blueprint/products/market.yaml` 162199553456280c258087c31fda26b34fa090a07e8bf1d0818923a1a6b9707a (hashes recomputed; they match the coordinator snapshot `/tmp/erl0080_coord/snaps/marketplace_orders_and_guarantee.r1.txt`).
- Entry conditions (cited, not re-run): snapshot round=1 2026-10-23T20:40:20Z lists EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views task0 7700756f…ce2c, task1 fc21bdc9…eee (recomputed, identical). Traceability deferred by the coordinator.
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/market.yaml, products/gift.yaml (cross-category reads), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), the DSL evaluator in skills/erl-task-instantiate/scripts/check_compute.py (semantics of LATEST/SUM/XLATEST/CFIELD only), the coordinator checklists XF_recipe.md and owner_ruling.md.
- Masked / not read: tasks/*.json, worklog.md, plan.md, any other audit. No recursive search touched tasks/.
- Scratch work: /tmp/erl0080_audit_market/ (sim.py replays the charter's own compute on copies of the views; probes.py holds every probe quoted below).

### policy_conflict_scan
Seven extended policies, keyed by `(target_tool, computes)`:

| id | tool (owner) | computes | subject | scope test |
|---|---|---|---|---|
| return_refund_claim_amount (u) | file_return_refund_claim_24f7de0f (user) | amount_claimed_usd | market_open_claim | return_not_refunded, non-FBN, selects the request most recently answered `authorized_return` |
| return_refund_claim_reimbursement (h) | grant_return_refund_claim_d58e2e3e (agent) | amount_reimbursed_usd | decide+reimburse | latest undecided return_not_refunded claim |
| unresponsive_claim_reimbursement (g) | grant_unresponsive_seller_claim_064f9cf7 (agent) | amount_reimbursed_usd | decide+reimburse | latest undecided seller_unresponsive claim |
| keepit_unit_refund (r) | refund_keepit_units_1db7244d (agent) | amount_refunded_usd | market_seller_refund | request most recently answered `refund_without_return` |
| item_condition_claim_amount (q) | file_item_condition_claim_763dfc78 (user) | amount_claimed_usd | market_open_claim | latest not_as_described request |
| missing_item_reimbursement (n) | grant_missing_item_claim_35c21a00 (agent) | amount_reimbursed_usd | decide+reimburse | latest undecided not_received claim |
| restocking_topup (s) | refund_restocking_shortfall_469f1911 (agent) | amount_refunded_usd | market_seller_refund | latest changed_mind request on the order |

- Overlapping subjects: h/g/n all write decide+reimburse; they are separated by claim reason in both rule and tool body (`_Kit.claim_check` checks `claim_reason`). u/q both write market_open_claim with distinct reasons. r and s both write `market_seller_refund` `return_refund` rows on a request's line. They overlap on a changed_mind request answered `refund_without_return` that has no unit refund yet: on the task0 opening world, s's selector picks that request (L4, 199e2457) and prices a "top-up" of 19.80 on it, which is exactly r's keep-it figure (probe P8). s's own scope sentence excludes it ("has refunded … but withheld"), so a careful reader does not write it. This is a symptom of finding CG-3.
- Time anchors: u and q net unit refunds dated on or after the request date. h, g and n net them from the filing date. See CG-17.
- Cross-category reads: gift only, the same five bindings in every policy (XLATEST load by `source_record_id=HID`, CFIELD variant, XSUM redeem/refund).
- Scope split between tasks (checked again after reveal): task0 is the tree {u ← h, g, r} and task1 is {q ← n, s}. The two sets are disjoint and together cover all 7 policies; no policy is shared and no edge crosses tasks.

### rule_compute_equivalence
- `compute_basis` sweep (script `static.py`): every quotation of all 7 policies is verbatim in its own rule; every `replaced_by`, `baseline.rule` and `policy_source` is verbatim in its own rule.
- Sweep back sentence by sentence: the selectors, set-price test, kept/held/in-hand units, merchandise total, order units, room, restock schedule, partial, promo, shipping share, setoff, rounding (RND(x+1e-9) on non-negative values; no gold-path value is within 1e-6 of a half cent in either world) and the floor at zero all have their compute counterparts. Defects found:
  - CG-5: "claims that carry no decision yet" is read off the claim row's own `claim_decision='not_applicable'`. Base records decisions as separate `market_decide_claim` rows.
  - CG-6: "the most recent unit refund" is read as any `return_refund` row, which includes the top-up rows with "no units".
  - CG-7: there is no tie rule for any "most recent" selector.
  - CG-8: the g/q/n line-pricing rule has a gap.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed once. The uuid8s 24f7de0f, d58e2e3e, 064f9cf7, 1db7244d, 763dfc78, 35c21a00 and 469f1911 are pairwise distinct, share no prefix or tail and form no sequence.
- No forbidden substrings in task_tools.py. Date is taken from `ctx.now()[:10]`. Rounding uses `_Money.cents` (Decimal ROUND_HALF_UP, static method). Every write tool calls `ctx.create`/`ctx.update` in its own body. Docstrings carry formats only, with no example values. Event triggers stay in category: decide→reimburse is booked by the tool itself, and the card triggers do not fire because every row is `external_card`.
- No tool body checks a prerequisite. The only refusals are id/type/reason, external-card payment and a positive two-decimal amount.
- Defects: CG-15 (docstring vs body and policy for the two refund tools) and CG-2 (the tools refuse Northgate-Card-paid orders that the rules cover).
- Docstring ordering words, recorded as an observation: the file tools say "The claim then waits for the seller's response period". The top-up tool says "the units were already refunded by the seller". Neither names another tool.

### prerequisite_graph
- `prerequisite` is filled everywhere: u has 3 edges, q has 2, and h/g/r/n/s are `[]`. The graph u→{h,g,r} and q→{n,s} is acyclic, and every `problem` is an extended id of this file.
- Every `policy_source` is verbatim in the blocked rule. All edges are `form: state` with no `fallback_reason`. Each `resolved_by` equals the depended-on `target_tool`.
- `value_input` gates `u_room` and `q_room` are real bindings, and granting moves them (the claim stops being reserved and its reimbursement is counted instead).
- `state_gate` edges name `gate: market_events.refund_type`, which is a column rather than an eligibility gate id. Recorded as an observation.
- `condition` texts match the sentences' strength: "every … whose seller response period has run out", "every … answered with a refund without return", "every change-of-mind unit refund … above … schedule".

### prerequisite_sentences
| blocked | sentence (connective) | waited-on state | writing tool |
|---|---|---|---|
| u | "…is fixed only after every earlier return-not-refunded claim on the order whose seller response period has run out carries a granted decision and its guarantee reimbursement." | claim row granted + reimburse row | only h's grant tool (body pins `claim_reason`) |
| u | "…is not fixed until every seller-unresponsive claim … carries a granted decision and its guarantee reimbursement." | same, seller_unresponsive | only g's grant tool |
| u | "…is not fixed before every return request on the order that the seller answered with a refund without return carries its unit refund." | return_refund row on the request's line for its units | only r's tool (s writes quantity 0) |
| q | "…is fixed only after every not-received claim … carries a granted decision and its guarantee reimbursement." | same, not_received | only n's grant tool |
| q | "…is not fixed until every change-of-mind unit refund on the order whose restocking fee is above Northgate's changed-mind schedule is followed by a restocking top-up refund on its line." | a later quantity-0 return_refund on that line | only s's tool |

- Each sentence plus the depended-on rule leads to its resolver in a single reading. No other tool, id or route appears in any rule, and no depended-on rule restates a sentence. No other cross-problem order appears in any rule.
- Defects: CG-4 (the "granted" gates cannot be met in engaged worlds where base denies) and CG-3 (the q top-up gate cannot be met in engaged worlds).
- Observation: "restocking top-up refund" is not a table word. The tables only show a `return_refund` with quantity 0.

### override_declarations
Sentence by sentence against `base_policy_refs`:
- `market_returns` refund clause ("The seller must refund within … never for changed_mind.") is retired by u, h, r and s.
  - r and s: genuine conflict. Their refunds add a set-saving clawback, a partial offset and promo recovery to "price of the returned units less a restocking fee of at most …". Declared, and the out-of-scope content is restated, including shipping and "never for changed_mind".
  - u and h: the replaced text only substitutes the 14-day half/full schedule for "a restocking fee of at most seller_restocking_fee_max_pct percent". A schedule at or below the maximum never conflicts with "at most the maximum". The base clause governs seller refunds, and the replaced_by itself keeps every seller refund under it. Nothing is retired. **XF C17 member → CG-1.**
- `market_guarantee_decision` reimbursement clause is retired by h, g and n. Each replaced_by names its two siblings and restates the in-force clause for every other claim (XF C16 satisfied on siblings). But the tender sentence changes from "paid to the original payment" to "paid to the external card the order was paid with" for every non-FBN claim of that reason, with no payment-method record test → **CG-2**.
- `market_guarantee_eligibility` card-dispute clause is retired by u and q for external-card orders, through a payment-record test. This changes the evidence route. It weakens base only for an external-card chargeback, which no table records. Declared, recorded as observation O2.
- Inherited base sentences checked and followed:
  - claim window, the not-received wait, contact-then-wait, claims_12m < 4;
  - "seller resolves by refunding in full first → denied_seller_resolved" (relevant to CG-4);
  - "Each claim is reimbursed at most once" (h/g/n select undecided claims only);
  - the units cap in returns;
  - the order-to-refunded transition (not reached in either world).
- Base sentence with no record field (O3): "the return delivered to the seller more than seller_refund_business_days business days earlier". No market event records the delivery of a return to the seller.
- Base event meaning of `market_open_claim.amount_usd` ("the price of the affected items plus their shipping") differs from the u/q amounts. An `overwrite` can only name a policy sentence, so this cannot be declared (O4).

### factor_ladders
Counts per policy as declared (P = parameter, M = method, X = cross_difficulty):
- u: line_pricing M, restock P, partial P, promo M X, ship M, refunds_received P → 6
- h: the same six → 6
- g: line_pricing M, partial P, promo M X, ship M, setoff P → 5
- r: line_pricing M, keepit_schedule P, partial P, promo M X → 4
- q: same shape as g → 5
- n: same shape as g → 5
- s: line_pricing M, restock P, partial P, promo M X → 4

In every policy the bindings are disjoint and `decides` is an input. Each fall-through equals the factor `baseline`, which equals what `baseline.rule` states. Every ladder is stated in full in its rule, and every rule tier has its compute branch. Multi-source: the line-pricing tiers join the line row (set-priced) with the request reason or the refund rows. Read-set check (static.py): no factor binding reads another factor's binding (A1 ok). No factor id is a substring of a tool name (A9 ok).

Structural defects (XF A/F; every member listed):

- **CG-11 "nothing" tiers (A7).**
  - partial (u, h, g, r, q, n, s): "otherwise 0" sits on the domain "no partial refunds", where tier 1 (partials × units / units bought) is also 0.
  - promo (all 7): "no recovery" sits on "no promotional card / nothing spent", where tier 1/2 give value spent = 0. XSUM over an absent card returns 0. A non-promotional card whose load names a marketplace order is not producible.
  - So both ladders have 2 real tiers (<3).
  - setoff/refunds_received (u, h, g, q, n): tiers 2, 3 and 4 are tier 1's sum "qualifying unit refund + shipping-refund share" with one or both parts absent. The four tiers select one method.

- **CG-12 mislabel.** The partial ladders (prorate / whole / none) are labelled `parameter`. The promo ladders have the same prorate / whole / none shape and are labelled `method`. One label set is dishonest. Under A7 a proration adds an operation and input (units, qty), so the partial ladders are `method`. If they are relabelled, g, q and n keep 1 parameter (setoff), r keeps 1 (keepit_schedule) and s keeps 1 (restock), all below the floor of 2.

- **CG-13 s ladders restate its scope.**
  - `s_req` is filtered `return_reason='changed_mind'`. So s_restock_schedule's third tier ("otherwise 0") and its "reason changed_mind" conditions hold for every customer s reaches.
  - In s_line_pricing, tier 2 ("reason is not changed_mind") and tier 3 ("set-priced and neither") are unreachable: every set-priced line falls in tier 1.
  - Both ladders have 2 reachable tiers.

- **CG-14 realism, r_keepit_schedule.** The rule takes "half the program's maximum restocking percentage / the maximum" off a refund-without-return, an item that never comes back and is never restocked. Base's own response options keep `refund_without_return` distinct from a `partial_refund_offer`. No retailer or marketplace publishes a restocking percentage on a returnless refund.

- **CG-9 realism, setoff/refunds_received (u, h, g, q, n).** These take "the most recent unit refund recorded on the line" (LATEST) rather than all unit refunds after the anchor. The base clause they retire says "less everything the seller already refunded on them".
  - Probe P6 (task0 world, seller also refunds the 2nd cold-brew unit, 318.44 on 10-13): u still claims 349.62 for a return refunded in full.
  - Probe P9 (task0 opening, both L2 units refunded after filing): h still reimburses 241.43 where base says denied_seller_resolved.

- **CG-10 realism / seed (F27, F28; all 7 promo factors).** The tiers need "the Northgate Promotional Gift Card the order earned". Every policy is scoped to non-FBN programs. Base `market_fbn_benefits` says: "Only Fulfilled by Northgate items share Northgate's own benefits … Items from every other seller program pay the seller's prices and shipping with no membership benefit and no cardholder discount. No marketplace item earns Northgate Cash …". The gift charter's promotional card is a Northgate-store program (`redeemable_on_marketplace: false`). A Northgate promotional card earned by a Seller-Fulfilled or International-Seller order is a state no charter produces, and real big-box marketplaces exclude third-party-seller items from gift-card promotions. This is the only cross-category factor in every policy.

- **CG-16 A3 placement.** These quantities are defined in plain bindings but used by one factor only:
  - g_in_hand, q_hand, n_hand ("units … still in the buyer's hands / with the buyer"): partial only;
  - r_merch_total / r_order_units and s_merch_total / s_order_units: promo only.

- Observation O7: the restock schedule is inert on 0% programs (Pro Seller, Certified Renewed), where all three tiers are 0. T2 holds on Seller-Fulfilled, Freight and International.
- Observation O1: `cross_difficulty: gift`. No difficulty of this scenario claims the gift category. It is a product with its own charter, so I treat it as "another product". The coordinator may rule otherwise.

### findings
Charter-global, each listing the tasks it bears on (each task's file demonstrates the consequence):

- **CG-1 SOURCE-POLICY (XF C17).**
  - Symptom: u and h overwrite `market_returns` "The seller must refund within … never for changed_mind." with a restocking schedule that never conflicts with "at most the maximum".
  - Evidence: u.overwrite[0] and h.overwrite[1]. Both replaced_by texts keep "every refund a seller books itself still follows the return rule".
  - Consequence: an overwrite that retires nothing. Under the coordinator's binding checklist any C17 member is RED. Task0.
- **CG-2 SOURCE-POLICY (C16/C19 scope).**
  - h/g/n replaced_by: "…the granted reimbursement is the … reimbursement this policy fixes, paid to the external card the order was paid with". The scope is "a seller program other than Fulfilled by Northgate", with no payment-method test.
  - For a non-FBN order paid with a Northgate Card, the base tender sentence ("paid to the original payment", which also drives the `card:card_post_credit` trigger) is retired and the replacement has no referent. `_Kit.claim_check` returns "Error: this reimbursement can be credited only to an order paid with an external card."
  - r and s also refuse such orders in their bodies, though their rules cover them.
  - Bears on task0 (h, g, r) and task1 (n, s). Both seeded orders are external-card, so no gold value moves.
- **CG-3 SOURCE-POLICY (s scope vs selector; D20).**
  - s's rule says "the refund Northgate books when a seller … has refunded a change-of-mind return but withheld a restocking fee above Northgate's changed-mind schedule; the return handled is the change-of-mind return request most recently made on the order". The selector does not test the scope.
  - Task0 opening world: the two above-schedule refunds (L3 10-12 withheld 79.61 = 20%, L2 10-16 withheld 54.91 = 20%; requests made 11 and 4 days after delivery, so the schedule is 10%) cannot be reached. The selector picks the unrefunded keep-it request L4 and prices 19.80 (P8).
  - q's gate "every change-of-mind unit refund … above … schedule is followed by a restocking top-up refund" therefore cannot be met by its resolver in such worlds. It also cannot be met where the clawbacks absorb the excess: P5, the task1 world with the L2 partial at 30.00, gives a top-up of 0.00, the tool rejects 0, and the refund still withheld 20% against a 10% schedule.
  - Task1.
- **CG-4 SOURCE-POLICY (D20).**
  - The u and q gates demand that every earlier claim of the reason "carries a granted decision and its guarantee reimbursement".
  - Base decides some of those claims as denied ("A claim the seller resolves by refunding in full first is denied as denied_seller_resolved"; denied_seller_not_contacted; denied_window). The h/g/n rules never test denial and still price a positive amount (P9 241.43).
  - In such worlds the gate is either unsatisfiable or forces a grant that base forbids.
  - Task0 and task1.
- **CG-5 SOURCE-POLICY (B10).**
  - u/q/h/g/n room and selectors read "claims that carry no decision yet" as `claim_decision='not_applicable'` on the claim row. Base records a decision as its own `market_decide_claim` row.
  - P2: on the task0 world with g's claim denied by a decide row (base style), u = 242.24 instead of 349.62.
  - Task0 and task1.
- **CG-6 SOURCE-POLICY (B10 decoy).**
  - A top-up (quantity 0, "with no units" per its tool) is selected as "the most recent unit refund recorded on the line" by u/h/g/q/n.
  - P1: one 5.00 top-up on L3 moves the task0 root from 349.62 to 383.33.
  - Task0 and task1 (s writes such rows).
- **CG-7 SOURCE-POLICY (B10 ties).** No "most recent / most recently" selector states a same-day tie rule (u_req, h_claim, h_req, g_claim, r_req, q_req, n_claim, s_req, latest unit refund). P3: a second authorization dated 09-26 inserted first switches the task0 root to the L2 return (241.43). Both tasks; neither seeded world has a tie.
- **CG-8 SOURCE-POLICY (B10/A8 gap).** g/q/n rule: "…where the line is set-priced and carries no unit refund, it is the price paid…". Compute's else-branch also covers set-priced lines with unit refunds on all units bought. The rule states no tier for them. Task0 (g), task1 (q, n).
- **CG-9 SOURCE-FACTOR** (above). Task0 (u, h, g) and task1 (q, n).
- **CG-10 SOURCE-FACTOR** (above). Task0 and task1. It removes the only cross-category factor of both tasks.
- **CG-11 SOURCE-FACTOR** (above). Every policy of both tasks.
- **CG-12 SOURCE-FACTOR** (above). Both tasks.
- **CG-13 SOURCE-FACTOR** (above). Task1.
- **CG-14 SOURCE-FACTOR** (above). Task0.
- **CG-15 SOURCE-TASK / tool contract (E24).**
  - `refund_restocking_shortfall_469f1911` arg: "request_event_id: … the return request the seller answered with a refund without return". The s policy handles "the change-of-mind return request most recently made", which s's own scope requires to be refunded (an authorized return). The body checks only `event_type == market_request_return`.
  - `refund_keepit_units_1db7244d` declares the same "answered with a refund without return" constraint, and its body does not enforce it.
  - The top-up Returns text promises "for <units> unit(s)", but the body prints no units.
  - Task1 (and task0 for r).
- **CG-16 SOURCE-FACTOR (A3).** Members listed above. Task0 (g, r) and task1 (q, n, s).
- **CG-17 SOURCE-TASK root (charter).**
  - No rule states what units a return-not-refunded claim records. u prices "the requested units" and nets the latest unit refund dated on or after the request date.
  - h later reimburses "claimed units" and nets only refunds dated on or after the filing date. So on a return already partly refunded before filing, h double-pays if the claim records the request's units.
  - Task0 demonstrates the two readings.
- Observations O1–O14 are listed in the task files where they bear, and O1–O7 above.

## closing_checklist
Written after both reveals. The difficulty is **NOT closed**: no task passes all four relationships.

| check | result | evidence |
|---|---|---|
| audit files | pass | 0.md and 1.md correspond to tasks 0–1; this file sits alongside them |
| policy coverage and scopes | pass | charter_scope task0 = {u, r, h, g}, task1 = {q, s, n}. The two scopes are disjoint and cover all 7 extended policies; tools as scoped |
| uuid8s | pass | independent |
| trees | pass | task0 has 3 prerequisites, 2 value_input; task1 has 2 prerequisites, 1 value_input. Both have an owner=user root; the global graph is acyclic |
| factors | fail | CG-9, CG-10, CG-11, CG-12, CG-13, CG-14, CG-16 |
| self-consistency | fail | CG-1 through CG-8 |
| unique solution | fail | CG-15 (task1), CG-17 (task0) |
| proof assertions | fail | T0-C1 and T1-C1 (false net-paid figures in edge_load_bearing) |
| gates on the final form | not re-run | the difficulty did not reach a final form |

Revision note: this is revision_1, with no earlier revision to compare. The GT comparison changed no blind conclusion. Every gold figure equals the blind figure.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11,CG-12,CG-13,CG-14,CG-15,CG-16,CG-17

## revision_2

### charter_global_frozen (revision_2)
- Freeze time: 2026-10-24T13:33:20Z. Written before any round-2 GT field was read. Auditor: erl-task-policy-audit revision_2. The revision_1 text above is untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 2` (round=2, 2026-10-24T13:27:00Z). Masked views: task0 66332be4…f7434f7 (changed), task1 fc21bdc9…eee (unchanged). Sources: `market.extended.yaml` d89a7bca…cfc06 and `task_tools.py` efb35c0e…de9d8, both changed; every blueprint product hash is unchanged. All seven gates are OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE).
- Both shared inputs changed, so every charter-global section is re-derived in full below. Nothing is carried forward.
- Read: rework_claims_r2.md (item ids and claims only), the new charter, the new tools, the views. worklog.md and plan.md were not read; rework_claims cites "worklog.md § REWORK round 2", and I did not open it. No search ran over tasks/.
- Scratch: /tmp/erl0080_audit_market/r2.py (replays) and r2probes.py (probes Q1–Q8, Q2r, Q2br).

### policy_conflict_scan (r2)
- The 7 policies, tools and `computes` are as in revision_1.
- New scope tests:
  - h, g, n, r and s: "paid with an external card".
  - u, h, g, n and q: "line carries no unit refund dated before the request / filing".
  - u: "seller has not refunded every unit it names".
  - h, g, n: "seller has not refunded everything paid on the claimed units".
  - s: "every unit of a returned request" refunded, with restocking withheld above the schedule.
- r and s no longer collide: s's object is now the request most recently answered `authorized_return`.
- Both trees and the task scopes are unchanged (task0 {u ← h, g, r}, task1 {q ← n, s}).

### rule_compute_equivalence (r2)
- `compute_basis` sweep: every quote, replaced_by, baseline.rule and policy_source is verbatim in its own rule.
- Tie sentences ("where two such entries share a date, the one recorded first counts") match the evaluator's first-row rule (Q4).
- The decision on the claim record is now stated by the rule and written by every grant tool.
- Top-up rows are excluded from unit-refund amounts in u and h (Q1: a decoy top-up on L3 leaves u at 356.39). g, n and q no longer read unit-refund amounts.
- The g/n/q line-pricing gap is closed: tier 2 now reads "no unit refund, or unit refunds on every unit bought".
- Defects:
  - **R2-1 (B10/C19).** The scope test "the line carries no unit refund dated before the request" (u, q) or "before the claim's filing date" (h, g, n) is stated in each rule but tested by no compute binding. Out of scope, compute still prices the extended figure:
    - Q2r: an L2 unit refund dated 09-17, before the 09-18 request, gives h = 191.18. The h replaced_by sends every other granted claim to the base reimbursement ("price paid … plus their shipping, less everything the seller already refunded"). That pre-request refund is also counted against the claimed units through `h_open`.
    - Q2br: an L3 unit refund dated 09-20, before the 09-25 request, gives u = 356.39 although u's rule puts the request outside its scope.
  - **R2-2 (B10).** The value-worded tests do not match the unit-count compute:
    - The h, g and n scopes and the u/q gate sentences say "the seller has not refunded everything paid on the claimed units".
    - Compute tests units instead (`h_open`, `g_units`, `n_units` > 0). Q3: the seller refunds both L2 units at 219.64 each with restocking withheld (439.28 refunded of 549.10 paid). The rule keeps the claim in scope, and its owed formula gives 26.45. Compute gives 0, which the grant tool rejects. The u gate still demands "a granted decision and its guarantee reimbursement" for that claim, so the gate cannot be met.
    - Same class: q's top-up sentence says "refunded in full while withholding more restocking", which is unit-based, against the value-based "everything paid" elsewhere.

### action_binding_and_uuids (r2)
- The uuid8s are unchanged and independent. No forbidden substrings appear in task_tools.py, and every write tool writes in its own body.
- keep-it tool: the body now requires a `refund_without_return` answer. top-up tool: the body requires `authorized_return`, its argument text matches, and its Returns text carries no units.
- No tool checks a prerequisite.
- **R2-5 (E24, contract vs policy).** The top-up docstring still reads "Book Northgate's top-up of a seller's change-of-mind return refund that withheld too much restocking". s now also covers seller-fault refunds that withheld any restocking (its schedule allows 0 for any other reason). A reader of the docstring would decline a defective-return top-up. Task1's request is changed_mind, so no gold value moves.

### prerequisite_graph and prerequisite_sentences (r2)
- The graph is acyclic and every field is filled. q→s is now `form: action` with a fallback_reason ("When the top-up figure comes to zero the settlement books nothing…"). The fallback is tested and justified: a zero settlement leaves no record, so no record-visible state could name it.
- Each of the five sentences passes the four-point test, and each state edge has one writing tool.
- Defects:
  - **R2-4 (D20).** The u and q gates are not payment-scoped: u and q cover every non-FBN order. Their resolvers h, g and n, and the grant tools (`_Kit.claim_check` "can be credited only to an order paid with an external card"), act only on external-card orders. On a Northgate-Card-paid order with an earlier claim past its seller period, the gate "carries a granted decision and its guarantee reimbursement" can never be met. Base is in force there ("still reimburses … paid to the original payment"), but no tool of this difficulty books it.
  - **CG-3 (remaining members).**
    - q's sentence covers "every return on the order that the seller refunded in full while withholding more restocking". s settles only "the return request most recently answered on the order with a return authorization". Q8, the task1 world plus an earlier above-schedule CM refund on L3: s reaches only the L2 request (4.11), and the L3 return cannot be settled, so the gate cannot be met.
    - s's scope says "refunded every unit of a returned request", but its engagement test counts every unit refund on the line. Q7, a later-authorized, unrefunded defective request on L2: s prices a 15.44 top-up for a request the seller never refunded, because it counts the change-of-mind request's refund.
  - **R2-3 (no once-rule).** s nets only the seller's unit refunds ("an entry that refunds no units not being a unit refund"). Q6: re-evaluated after its own 4.11 top-up, s still owes 4.11. No rule says a top-up is booked once or nets earlier top-ups. q's action gate "Northgate has settled the restocking top-up" thus admits a second booking.

### override_declarations (r2)
- CG-1 is closed: u and h no longer overwrite `market_returns`.
- Declared and genuine:
  - h, g and n retire the reimbursement clause, with the scope "paid with an external card", their siblings named, the seller-resolved denial restated, and Northgate-Card orders restated under base.
  - r and s retire the refund clause, with Northgate-Card orders restated.
  - u and q keep the card-dispute evidence routing (O2, unchanged).
- Inherited base sentences: as in revision_1. O3, O4 and O14 are unchanged and accepted as blueprint residue.

### factor_ladders (r2)
- Counts:
  - u and h: 6 factors (line M, restock P, partial P, promo P/gift, ship M, setoff P).
  - g, q and n: 5 factors (line M, partial P, promo P/gift, ship M, setoff P).
  - r and s: 4 factors (line M, restock P, partial P, promo P/gift).
- Labels are now consistent: promo and partial are both `parameter`, the tiers swapping a multiplier of the recorded amount. CG-12 is closed.
- Reachability and placement:
  - s's ladders are reachable on every tier (reason no longer filtered). CG-13 is closed.
  - g_kept, q_kept and n_kept sit inside the partial factor. r and s define merchandise total and order units inside promo. CG-16 is closed.
  - The A1 read-set check and the A9 substring check are clean.
- Remaining:
  - **CG-11 (A7 "nothing" tier; every member):**
    - partial "otherwise 0" in u, h, g, r, q, n and s;
    - promo "otherwise 0" in all 7;
    - g/q/n setoff "otherwise 0", which coincides with the share tier at zero shipping refunds;
    - u/h setoff, whose four tiers are still one sum, "unit refunds + shipping-refund share", with parts absent.
    - The reworker's ruling request is noted: "no non-zero default for an absent record". The checklist test is not whether a non-zero default exists. A tier that coincides with another tier's formula on its own domain is not a tier. Coordinator ruling pending.
  - **CG-10 (realism / seed): RED, coordinator ruling pending.**
    - A Northgate Promotional Gift Card "earned" by a Seller-Fulfilled or International-Seller order. Base `market_fbn_benefits` opens "Only Fulfilled by Northgate items share Northgate's own benefits".
    - The same gift charter makes the promotional card `redeemable_on_marketplace: false`, which marks it a Northgate-store promotion.
    - Real big-box marketplaces exclude third-party-seller items from gift-card promotions.
    - The reworker argues that the list after the colon is exhaustive and that promotions are not named. I read the opening sentence as the rule and the list as its instances. The coordinator must rule.
  - **CG-14 (realism): RED, coordinator ruling pending.** The keep-it deduction is still the changed-mind restocking schedule taken off a refund-without-return, where nothing is returned or restocked.
  - **CG-9 is closed.** u and h now set off every unit refund on the line, and g, n and q price the units still unrefunded. Q5: one L1 unit refunded after filing → g 910.42.

### findings (revision_2, pre-reveal)
| round-1 id | revision_2 status | evidence |
|---|---|---|
| CG-1 | closed | overwrite removed |
| CG-2 | closed | external-card scope; base restated for Northgate-Card orders; tools match the scope |
| CG-3 | **RED, remaining members** | Q7, Q8 |
| CG-4 | closed for the listed seller-resolved member | new members of the class are filed as R2-2 and R2-4 |
| CG-5 | closed | decision on the claim record stated by the rule and written by every grant tool |
| CG-6 | closed | Q1 |
| CG-7 | closed | Q4 |
| CG-8 | closed | tier 2 now covers unit refunds on every unit bought |
| CG-9 | closed | every unit refund set off; Q5 |
| CG-10 | **RED, ruling pending** | promotional card on non-FBN orders |
| CG-11 | **RED, ruling pending** | every member listed above |
| CG-12 | closed | labels consistent |
| CG-13 | closed | all s tiers reachable |
| CG-14 | **RED, ruling pending** | keep-it deduction |
| CG-15 | closed for its listed members | new contract member R2-5 |
| CG-16 | closed | definitions moved inside their factors |
| CG-17 | closed | u's rule: "the claim records that request's line and its units"; h nets every unit refund since the request |

- New: R2-1, R2-2, R2-3, R2-4 and R2-5 (each above, with its probe).
- T0-C1 and T1-C1 are to be checked after the reveal.

### post-reveal (revision_2)
- Both reveals matched every blind figure. T0-C1 and T1-C1 are closed: the closures now cite net paid 2346.54 and 2856.87, which the tool replay reproduces.
- Regressions: none against the round-1 closures.
- New defects introduced by the rework: R2-1, R2-2, R2-3, R2-4 and R2-5. Each came with the new scope, top-up and docstring text.
- Coordinator rulings requested by the reworker and still open: CG-10, CG-11 and CG-14. Until a ruling, they stand RED under the XF A7 and F28 checklist.

### closing_checklist (revision_2)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| audit files, scopes, coverage | pass | 0.md and 1.md match the two tasks; scopes disjoint; all 7 policies covered |
| uuid8s | pass | independent |
| trees | pass | 3 + 2 value_input and 2 + 1 value_input; owner=user roots; acyclic |
| factors | fail | CG-10, CG-11, CG-14 |
| self-consistency | fail | CG-3, R2-1, R2-2, R2-3, R2-4, R2-5 |
| unique solution (task1) | fail | R2-3 |
| gates on the final form | not re-run by me | the round-2 snapshot reports all seven OK |

VERDICT revision_2: task0=RED task1=RED charter=CG-3,CG-10,CG-11,CG-14,R2-1,R2-2,R2-3,R2-4,R2-5

## revision_3

### charter_global_frozen (revision_3)
- Freeze time: 2026-10-24T13:52:19Z. Written before any round-3 GT field was read. The revision_1 and revision_2 text above is untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 3` (round=3, 2026-10-24T13:48:44Z).
  - Views: task0 66332be4…f7434f7 and task1 fc21bdc9…eee, both unchanged since round 2.
  - Sources: `market.extended.yaml` f034a6e8…090c5 and `task_tools.py` b931c130…586c, both changed. The blueprint is unchanged and the base copy is verbatim.
  - All seven gates are OK.
- Both shared inputs changed, so every section is re-derived.
- Read: rework_claims_r3.md (claims only) and the coordinator's rulings as relayed. rework_claims cites "worklog.md § REWORK round 3", and I did not open it.
- Scratch: r2.py (replays on the new charter), r3probes.py.

### checks per section (r3)
- **compute_basis / replaced_by / baseline.rule / policy_source:** verbatim in their own rules (script). A1 and A9 are clean, and no A3 member remains. The tools carry no forbidden substrings, and the uuid8s are unchanged.
- **Scope bindings (`*_in_scope`, `*_engaged`):** they now test the external-card payment, the non-FBN program, the line-refund anchor and the open or unrefunded units. Out of scope the result is 0, and the rules say "elsewhere it fixes nothing and its figure is zero".
- **Prerequisites:** u and q are now scoped like their resolvers, external card and non-FBN. The u and q wait sentences carry the grants' unit tests and anchor tests. q's top-up wait names "the return request most recently answered on the order with a return authorization", which is s's own object. q→s stays action-form, with a fallback I tested and justify.
- **Top-up (s):**
  - It subtracts every return-refund entry, earlier top-ups included. Re-run after its own booking it owes **0.00** (r2.py N4).
  - It requires a single return authorization on the order. So the round-2 Q7 decoy (a later unrefunded authorized request on the same line) and the Q8 case (two engaged returns) are both "settled with nothing booked", and q's gate can always be met.
- **Tool docstring:** the top-up text now covers "withheld more restocking than allowed for the request's reason".
- **Factors:**
  - Shipping allocation and shipping-refund set-off: freight per piece / value share / none charged or refunded. Per the coordinator's CG-11 clarification, the absent-record tiers are legitimate. No other tier coincides with another over its reachable domain: per piece vs value share differ whenever a line's value share differs from its unit share.
  - The unit-refund set-off is now a plain binding and appears in the baseline ("less the refunds already received").
  - The keep-it restocking deduction is replaced by the return-shipping keep-back: freight per piece / value share / none. This complies with the coordinator's CG-14 ruling.
  - Labels: u and h have 2 P + 4 M; g, q and n have 2 P + 3 M; r and s have 2 P + 2 M.

### CG-10 conditions (coordinator ruling: accepted with conditions)
| condition | met? | evidence |
|---|---|---|
| (a) the issue record names the earning order | met, as the card's initial-load ledger row | the `gift_load_value` / `initial_load` row carries `source_record_id` = the order; the rule says "the card's initial load naming that order". `gift_holdings` itself has no source field |
| (b) the promotion is stated as Northgate's own | met | "Northgate's marketplace promotion issues a Northgate Promotional Gift Card on an order whose merchandise total reaches promo_qualifying_total_usd"; the test is computed (`*_merch_total >= K('promo_qualifying_total_usd')`). Both seeded orders qualify (5033.10 and 5008.46) |
| (c) clawback only as `gift_promo_expiry_and_clawback` states it | **NOT met → R3-4** | see below |
| (d) no gift-side write owed at the opening | met | both seeded cards are depleted (balance 0.00), so there is no unused value to void |

On (c): the gift rule says "Where promo_clawback_on_return is true and the purchase that earned the promotional card is returned, any unused promotional value is voided as promo_clawback, and value already spent is deducted from the return's refund." The market rules depart from it twice:
- Their terms sentence widens it to "when any part of that order is returned or refunded, whether by a seller refund or by a guarantee reimbursement, the promotional value already spent from the card is recovered from that refund".
- Their ladder then prorates ("value spent times the price paid for the requested units divided by the order's merchandise total"). The gift rule states no proration.

### findings (revision_3)
| id | status | basis |
|---|---|---|
| R2-1 | closed for its listed members | scope tests are now computed; Q2r/Q2br-type worlds give 0. One remaining member is filed as R3-1 |
| R2-2 | closed | the sentences speak in units, matching the unit tests |
| R2-3 | closed | 0.00 after the booking |
| R2-4 | closed | u and q now scoped external-card and non-FBN |
| R2-5 | closed | docstring covers the request's reason |
| CG-3 | closed | single-authorization engagement; q's gate names s's own object |
| CG-11 | closed under the clarification | the remaining unreachable tier is a different class, R3-3 |
| CG-14 | closed under the ruling | restocking deduction removed |
| CG-10 | conditions (a), (b), (d) met; (c) not | R3-4 |

New defects:

- **R3-1 (B10 decoy; members: u, h, g, n, q `*_last_refund_date` and s `s_last_unit_refund`).**
  - The scope test reads "the most recent unit refund on the line" as LATEST over every `return_refund` row, quantity-0 top-ups included. The rules say "an entry that refunds no units not being a unit refund".
  - Probe R3-a (task0 copy): the only real L2 unit refund is dated 09-17, before the 09-18 request, so h is out of scope (0). Add a 5.00 top-up row on L2 dated 10-20 and compute puts h back in scope (246.09); the rule still says 0.

- **R3-2 (rule self-contradiction and realism; a regression from the R2-1 fix; members: u, h, g, n, q, and s for its unit coverage).**
  - The scope is now "the most recent unit refund … dated on or after the request". So a line may carry an earlier refund for another request.
  - Yet "the refunds already received on the requested units are every unit refund entry recorded on the line", and "the units of the line refunded are counted the same way". This nets refunds and units that belong to other requests against the claimed units.
  - Probe R3-b (task0 copy, L3 also carries a 09-20 refund of the damaged unit from request 349c4e5c): u = 0. The buyer's unrefunded cold-brew unit cannot be claimed because the seller refunded a different unit on the same line. Round 2's "no unit refund dated before the request" excluded this world.

- **R3-3 (unreachable tier; promo ladder in u, h, g, n, q, r).**
  - Tier 1, "every unit of the order already refunded → the whole value spent", cannot occur where the scope requires an unrefunded unit: `u_open`/`h_open`/`*_units` > 0, or r's keep-it units still unrefunded before booking.
  - Those six promo ladders therefore have 2 reachable tiers (< 3), and the promo factor does not count. In s, tier 1 stays reachable.
  - Consequences:
    - none of task0's four computations keeps a cross-difficulty factor;
    - g, n, q and r keep 1 parameter (< 2).

- **R3-4 (CG-10 condition (c) unmet + second reading).** The terms sentence ("the promotional value already spent from the card is recovered from that refund") and the prorating ladder give different numbers:
  - task0 root: 356.39 prorated vs 272.21 with the whole 100.00 recovered;
  - task1 root: 367.20 vs 274.72;
  - n: 2097.33 vs 2039.82;
  - s: 4.11 vs 0.00.

### post-reveal (revision_3)
- Both reveals match every blind figure.
- No regression in any closed round-2 item.
- Regression introduced by the R2-1 fix: R3-2. The round-2 scope "no unit refund dated before the request" was weakened to "most recent unit refund on or after".
- New: R3-1, R3-3, R3-4.
- Coordinator rulings honoured and not re-opened: CG-10 (conditions checked; (c) unmet → R3-4), CG-14 and CG-11.

### closing_checklist (revision_3)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| audit files, scopes, coverage | pass | |
| uuid8s | pass | |
| trees | pass | |
| factors | fail | R3-3 |
| self-consistency | fail | R3-1, R3-2 |
| unique solution | fail | R3-4 |
| gates | not re-run by me | the round-3 snapshot reports all seven OK |

VERDICT revision_3: task0=RED task1=RED charter=R3-1,R3-2,R3-3,R3-4

## revision_4

### charter_global_frozen (revision_4)
- Freeze time: 2026-10-24T18:34:47Z. Written before any round-4 GT field was read. Revisions 1–3 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 4` (round=4, 2026-10-24T18:32:25Z).
  - Views: task0 bdea9a06…89050 and task1 55fdbaef…4f139, both changed.
  - Sources: `market.extended.yaml` bbce6c33…b70c5 (changed) and `task_tools.py` b931c130…586c (unchanged since round 3). The blueprint is unchanged and the base copy is verbatim.
  - All seven gates are OK.
- The charter changed, so every charter-global section is re-derived. The tools are unchanged, so the tool-contract section is carried forward from revision_3 on the matching hash.
- Read: rework_claims_r4.md (claims only). worklog.md was not opened; the claims cite "worklog.md § REWORK round 4".
- Scratch: r2.py (replays) and r4probes.py (A0–A3).

### checks (r4)
- **Static:** the compute_basis, replaced_by, baseline.rule and policy_source sweep is clean, as are A1, A3 and A9.
- **New plain bindings:** `*_line_requests` and `*_line_partial_refunds` (COUNT), plus the request-answer reads of h and q. These selections are shared by scope, not owned by any factor.
- **Prerequisite sentences:** u's two value_input sentences and q's not-received sentence now carry the same partial-offer and count tests as their resolvers' scopes. Each still passes the four-point test, and each edge has one writing tool. The q→s action edge is unchanged.
- **Overwrites:**
  - h, g and n: the "within this policy's scope" replaced_by restates base for every other claim and the seller-resolved denial.
  - r and s: they restate the return rule for every other refund.
- **Factors:**
  - Every factor still moves on both worlds.
  - The ladders are as in revision_3 except promo, whose terms are now one sentence.
  - The absent-record tiers fall under the coordinator's CG-11 clarification.

### status of round-3 REDs
- **R3-1: closed.** The date tests are removed. A 0-unit top-up on the claimed line leaves the figure unchanged (A1: 356.39).
- **R3-2: NOT closed.** The count test "the return requests recorded on the line other than that request are no more than the partial refunds recorded on the line" stands in for "every other request on the line was settled by a partial refund". The two are not the same record set. Members: u, h, q and s (other requests vs partial refunds) and g, n (requests vs partial refunds). The test holds whenever partial refunds outnumber the other requests, whichever requests those refunds settled.
  - **Probe A2 (task0 copy).** L3 carries two partial refunds (18.00 and a 5.00 goodwill refund on the damaged request) and a second request (defective, 1 unit) refunded at 398.05 on 10-01.
    - The count test passes: 2 other requests ≤ 2 partial refunds.
    - The defective unit's 398.05 is netted as a "refund already received on the requested units", and its unit is counted against the claim's units. u = 0, so the buyer's unrefunded change-of-mind unit is unclaimable.
    - The reworker's claim that "every unit refund on such a line belongs to the request … the policy concerns" is falsified by this record set. Base does not limit a request to one partial refund.
  - **Probe A3 (task0 copy).** A later damaged request on L2, for the unit not returned, answered by a partial offer with a 4.00 partial refund, becomes "the return request behind the claim" for h: the most recent request on the claimed line.
    - h goes out of scope (0, against 246.09), because its own request now "was answered with a partial refund offer".
    - u's gate drops that claim, which still reserves 476.64 of room.
    - The claim's actual request is the 09-18 change-of-mind return.
- **R3-3: NOT closed (disputed; no ruling relayed this round).** The promo tier "every unit of the order already refunded → the whole value spent" is still unreachable in u, h, g, n, q and r: their scopes need an unrefunded unit, or for r a not-yet-refunded keep-it unit. Those six ladders keep 2 reachable tiers. Task0 still has no surviving cross-difficulty factor, and g, n, q and r keep 1 parameter.
- **R3-4: second reading closed; coordinator route NOT complied with.**
  - Closed: the separate terms sentence is gone, and the promo terms and ladder are one sentence ("in the shares this sentence fixes and never more"). The whole-value second reading of revision_3 no longer exists.
  - The coordinator's route is not implemented: "spent promotional value is deducted only when a refund leaves the merchandise kept on the earning order below the promotion's qualifying total, then the whole spent value once, net of earlier clawbacks". The rules still prorate on every refund of the order's units, whatever merchandise is kept.
  - Demonstration: on both worlds the merchandise kept stays far above promo_qualifying_total_usd 1000.00 (merchandise totals 5033.10 and 5008.46). So the route recovers nothing, and each figure becomes its promo-baseline value:

| policy | figure under the charter | figure under the route |
|---|---|---|
| u | 356.39 | 372.21 |
| h | 246.09 | 257.00 |
| g | 1871.34 | 1909.47 |
| r | 26.21 | 26.89 |
| q | 367.20 | 374.72 |
| n | 2097.33 | 2139.82 |
| s | 4.11 | 5.99 |

  - CG-10 condition (c) therefore remains unmet. The reworker's dispute is noted, and the ruling is not re-opened here.
- **Seeds:** the first redemption is now dated after the seeded unit refunds (task0 10-17, after 10-12 and 10-16; task1 10-10, after 10-09). The seeded refunds therefore carry no recovery consistently. The earlier task0 claim was repriced to 476.64 on its 10-14 world, where nothing had been spent yet.
- **New defects:** none found beyond the remaining members above. Tie reads and decoy reads were probed (A1, A3), and the new COUNT reads have no tie dimension.

### post-reveal (revision_4)
- Every blind figure equals GT in both tasks.
- R3-1 is closed, and the R3-4 second reading is closed.
- Still open:
  - R3-2: the count proxy does not attribute refunds to requests (A2, A3).
  - R3-3: disputed, and no ruling has been relayed.
  - R3-4: the coordinator's threshold-and-whole-once route has not been implemented, so CG-10 condition (c) is still unmet.
- No regression and no new defect class.

### closing_checklist (revision_4)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| audit files, scopes, coverage | pass | |
| uuid8s | pass | |
| trees | pass | |
| unique solution | pass | |
| factors | fail | R3-3 |
| self-consistency | fail | R3-2, R3-4 |
| gates | not re-run by me | the round-4 snapshot reports all seven OK |

VERDICT revision_4: task0=RED task1=RED charter=R3-2,R3-3,R3-4

## revision_5

### charter_global_frozen (revision_5)
- Freeze time: 2026-10-24T18:59:09Z. Written before any round-5 GT field was read. Revisions 1–4 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 5` (round=5, 2026-10-24T18:56:03Z).
  - Views: task0 85298b36…c1b27 and task1 f42ea4f3…28c06, both changed.
  - Sources: `market.extended.yaml` 164b683b…02358 (changed) and `task_tools.py` b931c130…586c (unchanged). The blueprint is unchanged and the base copy is verbatim.
  - All seven gates are OK.
- The charter changed, so every charter section is re-derived. The tools are unchanged on the matching hash.
- worklog.md was not opened. Scratch: r2.py and r5probes.py (P1a–P1c, P7).

### checks (r5)
- **Static:** the compute_basis, replaced_by, baseline.rule and policy_source sweep is clean, as are A1 and A9.
- **A3 — R5-2, one member:** `r_order_units` ("the order's units", defined in a plain sentence of the keep-it rule) is now read only by the factor `r_return_ship_keepback`. Promo no longer reads it.
- **Scopes (coordinator R3-2 ruling): complied with.**
  - The requested, claimed or returned line "carries exactly one return request" (u, h, q, s), or "carries no return request" (g, n). Compute is `*_line_requests == 1` or `== 0`.
  - Out of scope, every rule quotes its base text verbatim: the base claim-record meaning for u and q, the `market_guarantee_decision` clause for h, g and n, and the `market_returns` clause for r and s.
  - "No more than ten lines" is a coarse exact test, needed for the line-by-line enumeration (`line_number` = 1…10).
  - Probe P7: a second request on q's line puts q out of scope (0). The round-4 A2 and A3 worlds fall out of scope by the same test.
- **Waits:** u's sentences on h and g and q's sentence on n carry the same tests; the four-point test passes; each state edge has one writing tool. The q→s action edge is unchanged.
- **Seeds:**
  - The damaged-reason requests are now `contact_seller` entries settled by partial refunds.
  - Each card is fully spent before the seeded unit refunds (task0 by 10-05, task1 by 10-05).
  - Each seeded unit refund carries its proportional share: task0 310.53 and 214.19, task1 73.39. The two task0 figures recompute exactly; task1's 73.39 recomputes from the unrounded restocking.
  - task0's earlier claim was repriced to 465.73.
  - Nothing gift-side is owed: the cards are depleted.

### R3-3 / R3-4 (coordinator route revised round 5)
- **R3-3 is closed.** The promo ladder of every policy is now "no card or nothing spent / proportional share / whole remaining spent value when the merchandise kept falls below promo_qualifying_total_usd". Every tier is reachable in every scope (P1a: n on a two-rug claim takes the whole-remaining tier). Every computation of both tasks carries the cross-difficulty factor, and g, n, q and r carry 2 parameters again.
- **R3-4: partly complied; one member open (R5-1).** These parts follow the route: the single sentence, the proportional share ("in proportion to the merchandise refunded over the order's merchandise total"), and the whole remaining value on a refund that leaves the merchandise kept below the qualifying total. One part does not:
  - The route says the whole remaining spent value is "spent less the shares earlier refunds recovered".
  - Every rule says "the value spent less the shares that the order's earlier refunds recovered **under the same proportion**". Compute does the same: `spent × (total − merchandise refunded other than on the units) / total`.
  - The two coincide only when no earlier refund was itself a below-threshold, whole-remaining recovery. Once one was, the next refund recovers again and the order's total recovery exceeds the value spent.
  - **Probe P1c (task1 copy).** The seller refunds both rugs on 10-10 and, under the terms, recovers the whole remaining 98.12 (1.88 was already recovered by the 10-09 bowl refund). On the NAD claim the merchandise kept is then 282.18, below 1000.00, and q recovers a further 13.15. That is 113.15 recovered of 100.00 spent, and q = 361.57. Under the route the remaining value is 0.00 and q = 374.72.
  - Members: the promo binding of all seven policies (u, h, g, r, q, n, s).
  - On both task worlds the merchandise kept stays above 1000.00, so no gold figure depends on this tier.

### status of round-4 REDs
| id | status | basis |
|---|---|---|
| R3-2 | closed | per the ruling |
| R3-3 | closed | |
| R3-4 | open, as R5-1 | the "under the same proportion" member |

- New: R5-1 (above) and R5-2 (A3).

### post-reveal (revision_5)
- Every blind figure equals GT in both tasks.
- Closed this round: R3-2, R3-3 and the R3-4 route except one member.
- Open:
  - R5-1: the remaining value is netted "under the same proportion", where the route nets the shares actually recovered. Over-recovery P1c: 113.15 recovered of 100.00 spent.
  - R5-2: A3, `r_order_units`.
- No regression.

### closing_checklist (revision_5)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| audit files, scopes, coverage | pass | |
| uuid8s | pass | |
| trees | pass | |
| unique solution | pass | |
| factor weight | pass | |
| factor structure | fail | R5-2 |
| self-consistency | fail | R5-1 |
| gates | not re-run by me | the round-5 snapshot reports all seven OK |

VERDICT revision_5: task0=RED task1=RED charter=R5-1,R5-2

## revision_6

### charter_global_frozen (revision_6)
- Freeze time: 2026-10-24T23:17:49Z. Written before any round-6 GT field was read. Revisions 1–5 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 6` (round=6, 2026-10-24T23:15:54Z).
  - Views are unchanged since revision_5: task0 85298b36…c1b27, task1 f42ea4f3…28c06.
  - `market.extended.yaml` 016ef0a4…d9241 (changed); `task_tools.py` b931c130…586c (unchanged). The blueprint is unchanged and the base copy is verbatim.
  - All seven gates are OK.
- The charter changed, so every charter section is re-derived. The tool section is carried forward on the matching hash. Each task's per-task sections are re-derived against the new charter, since the task files were rebuilt.
- worklog.md was not opened. Scratch: r2.py, r5probes.py (P1a/P1b/P1c/P7 re-run), r6resid.py.

### checks (r6)
- **Static:** the compute_basis, replaced_by, baseline.rule and policy_source sweep is clean. A1, A3 and A9 are clean (no A3 member remains).
- **R5-2: closed.** "The order's units" is now defined in the keep-back sentence, and `r_order_units` is owned by `r_return_ship_keepback`.
- **R5-1: closed.** In all seven policies the promo sentence now reads:
  - "the whole remaining spent value, that is the value spent less what the order's earlier refunds recovered under this sentence";
  - "a refund made when the merchandise kept on the order was already below promo_qualifying_total_usd recovers nothing, so that no more than the value spent is ever recovered".
  - Compute: the crossing tier `spent × kept_before / total` applies only when kept before ≥ Q > kept after. It is followed by the proportional tier when kept after ≥ Q, and by 0 otherwise, which includes the already-below case. Proportional shares precede the single crossing, so `spent × kept_before / total` equals spent less what was actually recovered. The route's wording is met.
  - The ladder (3 tiers, every one reachable: P1a crossing, gold proportional, P1b already-below/absent) restates the sentence.
- **Re-run probes:**
  - P1b: after the two-rug crossing grant, q's promo is 0, and the total recovered is 98.12 of the 100.00 remaining.
  - P1c: the seller crossing refund recovers 98.12; q then recovers 0 and q = 374.72, as the route requires.
  - P7: a second request on the line → out of scope.
- **"Counts as the refund of the units, made after every other refund":** u, h and s net their own units' earlier refunds against shares recovered on those refunds. I worked the identity: the claim's net recovery equals the remaining value whatever the history.
- **The `*_settles` guard (u, h, s):** it applies when the order is already below Q and some covered units are refunded. The figure is fixed only if no seller refund or guarantee reimbursement is dated after the most recent return refund on the line; otherwise the figure is 0 and the base rule stands, which is C19-compliant.
  - The reads are LATEST event dates. "Dated after" is strict, and compute's `>=` treats same-day entries as not after, which matches the rule.
  - The rule says "return refund", so a quantity-0 top-up counts on both sides, consistently with the rule's words.
  - The guard is inactive on both worlds (merchandise kept ≥ Q).
- **Observation O-r6 (no consequence):** `*_settles` is a scope guard listed among the promo factor's bindings and read by `result`. Substituting the factor's baseline leaves the guard in place. It changes no figure on either world, and no factor test reads it.

### status of round-5 REDs
| id | status |
|---|---|
| R5-1 | closed |
| R5-2 | closed |

- No regression in R3-2, R3-3 or the earlier closed items: scopes, tie sentences, top-up idempotence (0.00 after booking) and the external-card scopes all re-checked.
- New defects: none.

### post-reveal (revision_6)
- Every blind figure equals GT in both tasks.
- R5-1 and R5-2 are closed. No regression and no new defect.
- Observations carried forward, with no RED consequence:
  - O1: the gift category is claimed by no difficulty and is treated as another product.
  - O2: card-dispute evidence routing.
  - O3: no record field for a return's delivery to the seller (base residue).
  - O4: the base claim-record meaning is now quoted for out-of-scope claims.
  - O14: the contact_reason enum has no seller_unresponsive value (base residue).
  - O-r6: the `*_settles` guard sits among the promo factor's bindings.

### closing_checklist (revision_6)
| check | result | evidence |
|---|---|---|
| audit files | pass | 0.md and 1.md correspond one-to-one to tasks 0–1; `_difficulty.md` alongside; revisions 1–6 preserved; every revision_6 comparison is PASS |
| coverage and scopes | pass | the 7 extended policies are fully covered; task scopes {u, r, h, g} and {q, s, n} are pairwise disjoint over the whole trees |
| tools and uuid8s | pass | task tools and GT are closed; every uuid8 is independent and frozen (24f7de0f, d58e2e3e, 064f9cf7, 1db7244d, 763dfc78, 35c21a00, 469f1911) |
| trees | pass | task0: 3 prerequisites, 2 value_input; task1: 2 prerequisites, 1 value_input. Each has an owner=user root. The difficulty-wide prerequisite graph is acyclic, with no cross-task edges |
| factors | pass | every computation has 4–6 factors (≥ 2 parameter, ≥ 1 method), multi-source line pricing and the cross-difficulty promo factor (gift). Every ladder has ≥ 3 reachable tiers and is stated in full in its rule. Every factor moves its scored value against an honest baseline, and each all-baseline fallback is definite and differs from gold |
| gates on the final form | pass | the round-6 snapshot (2026-10-24T23:15:54Z) shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK |

The difficulty passes the source-layer audit at revision_6.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global_frozen (revision_7)
- Freeze time: 2026-10-24T23:33:36Z. Written before any round-7 GT field was read. Revisions 1–6 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 7` (round=7, 2026-10-24T23:31:40Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` b5f1270f…99e70 (changed); `task_tools.py` b931c130… (unchanged).
  - All seven gates are OK.
- worklog.md was not opened. Scratch: r7probes.py.

### checks on the changed text (r7)
- **What changed:** the resolver rules of h, g, n and r gain a settlement sentence. u's three waits and q's not-received wait become action form with fallback_reason. The figures are unchanged: r2.py gives the same gold on both worlds and every factor still moves. The static sweep (compute_basis, A1, A3, A9) is clean.
- **Action-form test:** where the figure is positive, the grant or refund leaves a record-visible state, but the zero case leaves none. So the fallback is justified *given* the zero-settlement rule, and that rule is itself defective (R7-1).

### findings (revision_7)
- **R7-1 SOURCE-POLICY (undeclared override of an in-force base sentence; members h, g, n).**
  - The new sentence in h, g and n reads "Northgate settles such a claim by granting it … or, where the … reimbursement comes to zero, with nothing booked, its claim record then keeping no decision". The base sentence of `market_guarantee_decision` is still in force; each overwrite retires only the reimbursement clause: "After a claim is filed the seller has guarantee_seller_response_business_days business days to resolve it, and Northgate decides within guarantee_decision_business_days business days after that deadline."
  - For a zero-figure claim, base requires a decision within the window, and the extended rule says the claim is settled while its record "keeps no decision".
  - The schema offers decisions that book nothing (denied_seller_resolved, denied_not_covered and the others), so a decision is producible without a positive money row.
  - The edge `effect` texts then make the settled claim keep "reserving its claimed amount" against the per-order guarantee maximum indefinitely.
  - Not declared in any `overwrite`.
- **R7-2 SOURCE-POLICY (D20: a waited-on claim or request the resolver can never select; members h, g, n, r).**
  - Each resolver's selector designates only the most recent undecided claim of its reason (h, g, n), or the request most recently answered with a refund without return (r). Nothing excludes an entry the policy fixes nothing for, or one already settled.
  - A later out-of-scope entry, or a zero-settled one (which "keeps no decision"), therefore hides every earlier waited-on entry for good. For r, so does the latest keep-it request after it is booked.
  - Probes (r7probes.py, copies of the task worlds):

| member | added to the world | selector picks | consequence |
|---|---|---|---|
| h | a 10-15 return-not-refunded claim on L1, a line with no return request (outside h's scope) | `rnr2`, figure 0 | e6c0ae8e, which u waits on, is never handled |
| g | a 10-15 seller-unresponsive claim on L2, which carries a return request (outside g's scope) | `su2`, figure 0 | 447fea97 is never handled |
| n | a 10-14 not-received claim on L2 (task1) | `nr2`, figure 0 | d2cfaae6, which q waits on, is never handled |
| r | a second keep-it answer on 10-05 | `kreq2` (814.67), even after it is booked | 199e2457 is never handled |

  - In each case the root's wait ("settled every earlier … claim" / "the keep-it refund on every return request …") can never be met.
  - h, g and n carried this since the scope tests entered in revision_3, and r since revision_1. It was **missed by revisions 1–6**; the revision_6 PASS did not test it.
- **R7-3 SOURCE-TASK (no once-rule on the keep-it refund; member r).**
  - The keep-it figure does not net a keep-it refund already booked, and the rule says nothing of booking it once.
  - On the task0 gold world, after the gold 26.21 booking, r re-evaluated still selects 199e2457 and owes **26.21** again. A reader can book a second keep-it refund.
  - This is the R2-3 class, closed for s in round 3 but never for r. It has been latent since revision_1 and was **missed by revisions 1–6**.

| id | status |
|---|---|
| R5-1 | stays closed (unchanged sentence) |
| R5-2 | stays closed (unchanged sentence) |
| D20 zero-figure waits (reworker's item) | the zero-settlement route introduces R7-1; the class is not closed |

### post-reveal (revision_7)
- Every blind figure equals GT in both tasks.
- New: R7-1, the zero-settlement route.
- Found this round but present earlier: R7-2 (selector reachability; h, g and n since revision_3, r since revision_1) and R7-3 (keep-it once-rule, since revision_1). I record openly that the revision_6 PASS missed both.

### closing_checklist (revision_7)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| self-consistency | fail | R7-1, R7-2 |
| unique solution | fail | R7-3 (task0) |
| everything else | pass | as listed in revision_6 |

VERDICT revision_7: task0=RED task1=RED charter=R7-1,R7-2,R7-3

## revision_8

### charter_global_frozen (revision_8)
- Freeze time: 2026-10-24T23:52:47Z. Written before any round-8 GT field was read. Revisions 1–7 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 8` (round=8, 2026-10-24T23:50:13Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` 26377611…a4c8 (changed); `task_tools.py` a114d891…2ec4 (changed: the three grant tools).
  - All seven gates are OK.
- worklog.md was not opened. Scratch: r8probes.py and r2.py. Gold figures and factor figures are unchanged on both worlds, and every factor moves.
- **Tools re-checked:** the grant tools accept 0.00 and then record `denied_not_covered` on the claim plus one decision row, with no reimbursement and no change to net paid. The docstring states exactly this, so the body enforces what the docstring declares. No forbidden substrings; every write is in its own body. The tools still check no prerequisite.

### one exhaustive pass over all seven policies (coordinator's three classes)

**(a) Zero-figure handling against the base decision rule**

| policy | zero handling | verdict |
|---|---|---|
| u, q (claim filing) | "Where the amount claimed … comes to zero there is nothing to claim and no claim is filed." | no wait depends on them; OK |
| s (top-up) | zero → "settled with nothing booked"; q's wait on it is action form with a justified fallback | OK |
| h, g, n (grants) | zero with booked reimbursements at the maximum → decided `denied_not_covered`, a decision with no money row consistent with base "capped at guarantee_max_per_order_usd per order across all claims"; **zero otherwise → "the claim is not decided in this conversation and is referred to a human representative"** | **R8-1** |
| r (keep-it) | zero with no return refund on the line → "the request is not settled in this conversation and is referred to a human representative" | **R8-1** |

- **R8-1 (D20).** u's state-form waits and q's not-received wait require the claim to "carry a decision on its claim record". u's keep-it wait requires the line to "carry a return refund for the request's units". In the zero-otherwise case the resolver leaves both states unmet, so the root can never be fixed in those engaged worlds.
  - Probe (a), task0 copy: a 600.00 partial refund on L2 keeps h in scope (open 1, room 558.14) but owed −148.46 → 0. That is a referral, and u's wait on e6c0ae8e can never be met.
  - The reworker's own sweep calls the zero-otherwise figure unreachable only for the promo/partial routes without a record test; it is reachable.
  - Members: the h, g and n grant sentences (waited on by u and q), and the r keep-it sentence (waited on by u).
  - R7-1 itself is closed. Decisions are now recorded or the case is referred, and nothing contradicts "Northgate decides within … business days".

**(b) Every resolver selector against every waiting sentence**

| resolver | scope test | waiting sentence | decoy probes |
|---|---|---|---|
| h (u waits) | "the order carries exactly one return-not-refunded claim whose claim record shows no decision" | carries the same test, verbatim | a second undecided claim → h out of scope and the wait inapplicable; a later already-decided claim → h selects e6c0ae8e (251.54) |
| g (u waits) | same, seller-unresponsive | same | as h |
| n (q waits) | same, not-received | same | as h |
| r (u waits) | "exactly one return request the seller answered with a refund without return" + "the requested line carries exactly one return request" | same; state form again | a second keep-it answer → out of scope and the wait inapplicable |
| s (q waits) | single authorization | names s's own object | as revision_6 |

- Other-line decoys are excluded by the line tests. The tie sentences are unchanged.
- **R7-2 is closed.**

**(c) Booked-once netting for every booking policy**

| policy | after its own booking | probe |
|---|---|---|
| r | nets every return refund on the requested line (`r_line_refunds`) | 26.21 → 0.00 |
| h, g, n | a decided claim leaves the undecided count | 0 after grant |
| s | nets top-ups | 0.00 (since round 3) |
| u, q (filings) | the requested line must carry no claim of their reason | simulated filing → u = 0 |

- **R7-3 is closed. No member remains.**

### other checks (r8)
- Static sweep clean except **R8-2 (XF A3):** `r_line_unit_qty` (units of the requested line already refunded by unit) is a plain binding read only by `r_promo_recovery` (inside `r_settles` and the promo kept-before term).
- **Observation O-r8a (latent, not RED; the task worlds are non-binding):** the guarantee room of h and g counts the other claim's reserved amount. On a world where one claim's reserved amount is large, the grant figure depends on the order of the grants. Probe (a'): g's claim filed for 2400.00 gives h = 100.00 if h goes first and 251.54 after g. No rule pins the order. On both gold worlds every order gives identical figures.

### status
| id | status |
|---|---|
| R7-1 | closed |
| R7-2 | closed |
| R7-3 | closed |
| R8-1 | **new, RED** |
| R8-2 | **new, RED** |

### post-reveal (revision_8)
- Every blind figure equals GT in both tasks.
- Closed: R7-1, R7-2, R7-3.
- Remaining after this single exhaustive pass over the three classes:

| id | members | gap |
|---|---|---|
| R8-1 | h, g, n, r | the zero-otherwise referral leaves a waited-on state unreachable |
| R8-2 | r (one binding) | `r_line_unit_qty` is plain but read by one factor only |

- No other member of classes (a)–(c) exists in the charter.
- O-r8a is recorded as latent.

### closing_checklist (revision_8)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| self-consistency | fail | R8-1 |
| factor structure | fail | R8-2 |
| everything else | pass | as in revision_6 |

VERDICT revision_8: task0=RED task1=RED charter=R8-1,R8-2

## revision_9

### charter_global_frozen (revision_9)
- Freeze time: 2026-10-25T00:02:48Z. Written before any round-9 GT field was read. Revisions 1–8 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 9` (round=9, 2026-10-25T00:00:52Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` c8098421…cfcb0 (changed); `task_tools.py` a114d891… (unchanged).
  - All seven gates are OK.
- Scope as bounded by the coordinator: R8-1, R8-2 and the decide-in-filing-order sentence, plus a regression check and one exhaustive pass for further members.
- worklog.md was not opened. Scratch: r2.py and r9probes.py.

### verification (r9)
- **R8-1: closed.** Each of u's three waits and q's not-received wait now ends, verbatim, "where that claim (that request) is referred to a human representative under its own policy, the filing is referred too and nothing is filed". The zero-otherwise referral of h, g, n and r therefore resolves the root in every engaged world: the root is handed off and nothing is filed. The edge conditions carry the same clause. No other wait depends on a referral, so there is no further member.
- **R8-2: closed.** `r_line_unit_qty` now belongs to `r_promo_recovery`, and its definition sits in that factor's sentence. The static sweep (compute_basis, A1, A3, A9) is clean on all seven policies.
- **Regression check:** both worlds give the same gold, all 35 factor substitutions move their figure, and the fallbacks are unchanged. The scope, once-rule, tie and promo probes from revisions 6–8 were re-run with unchanged outcomes.
- **Decide-in-filing-order sentence: R9-1 SOURCE-POLICY RED (undeclared cross-problem dependency; members h, g, n).**
  - The sentence in h, g and n reads "claims on one order are decided in the order they were filed, earliest first, and of claims filed on the same day the one recorded first comes first". Their rooms now count only the undecided claims that "come before it in the order of decision".
  - This fixes a cross-problem order between the grants (h, g, n), and between those grants and any other claim decision on the order. Yet no `prerequisite` edge declares it: h, g and n all carry `prerequisite: []`. On task0's tree, h and g are still parallel prerequisites of u.
  - **Demonstration (r9probes.py, task0 copy).** The seller-unresponsive claim covers all 3 espresso units (claimed 2900.00). The 10-14 claims tie on date, and e6c0ae8e is recorded first.

| order | h | g | root u |
|---|---|---|---|
| the rule's order (h first) | 251.54 | 2248.46 | 0.00 |
| g first | 251.54 | 2034.27 | 214.19 |

  - Two orders give two terminal states, and the order is stated in a rule but grounds no declared edge.
  - On the gold world both orders give h 251.54 and g 1871.34 (non-binding), so no gold figure moves.
  - Same-day ties also rest on "recorded first". No table field carries a record time, so a reader depends on the lookup's row order. This is noted under the same finding.
- **New coarse tests:** "no two claims of one reason whose claim records show no decision and no three such claims filed on the day that claim was filed". They are carried verbatim in every grant scope and every wait on a grant, and compute matches: `*_n_* <= 1`, `*_same_day <= 2`. Decoys: a second undecided claim of one reason, or a third claim on the same day, puts the grant out of scope and the wait inapplicable.
- **Further members:** none outside R9-1. u and q also compute rooms, but they are filings, not decisions, and they reserve every undecided claim.

| id | status |
|---|---|
| R8-1 | closed |
| R8-2 | closed |
| R9-1 | **new, RED** |

### post-reveal (revision_9)
- Every blind figure equals GT in both tasks.
- R8-1 and R8-2 are closed, and nothing regressed.
- Remaining: **R9-1**, the decide-in-filing-order sentence of h, g and n. It is a cross-problem order stated in a rule that grounds no declared edge. A binding copy of task0 gives two terminal states for the two orders (g 2248.46 vs 2034.27; root 0.00 vs 214.19). No further member exists.

### closing_checklist (revision_9)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| self-consistency | fail | R9-1 |
| everything else | pass | |

VERDICT revision_9: task0=RED task1=RED charter=R9-1

## revision_10

### charter_global_frozen (revision_10)
- Freeze time: 2026-10-25T00:10:14Z. Written before any round-10 GT field was read. Revisions 1–9 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 10` (round=10, 2026-10-25T00:09:23Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` 4ae2a5ed…a6a2 (changed); `task_tools.py` a114d891… (unchanged since round 8).
  - All seven gates are OK.
- Coordinator route: the round-9 filing-order sentence is withdrawn, and the grants' order dependence under a large reservation returns to observation O-r8a (latent, not RED).
- worklog.md was not opened.

### verification (r10)
- **Revert exactness:** I diffed my round-8 dump of every scope, wait, edge-condition, settlement, room and result sentence and binding (`/tmp/erl0080_audit_market/r8.txt`) against the same dump on the round-10 charter (`r10.txt`).
  - The only differences are the R8-1 referral clauses, added in round 9 and kept: in u's three waits and q's not-received wait ("…; where that claim (that request) is referred to a human representative under its own policy, the filing is referred too and nothing is filed") and in their four edge conditions.
  - The decide-in-filing-order sentence, the order-of-decision room bindings (`*_res_*`, `*_first_same`, `*_same_day`, `*_n_*`) and the "no two … no three … on the day" tests are gone from every grant scope, wait and edge.
  - The grant rooms are again "less the amounts claimed on the order's other claims whose claim record shows no decision yet" (compute: `… − SUM(undecided claims) + own claimed`), exactly the round-8 read.
- **R8-1 stays closed:** the referral clause is present in all four waits.
- **R8-2 stays closed:** `r_line_unit_qty` is a binding of `r_promo_recovery`, and the static sweep is clean.
- **No regression:**
  - Both worlds give the same gold, all 35 factor substitutions move their figure, and the fallbacks are unchanged.
  - The round-8 three-class probes reproduce the revision_8 outcomes: zero-otherwise → referral, now resolved by the referral clause; the second-claim decoy → out of scope; booked-once → 0.00.
  - The round-5/6 promo probes reproduce: P1c q = 374.72, and the total recovered stays within the value spent.
- **O-r8a** reproduces as recorded in revision_8 (probe (a'): h = 100.00 if granted first, 251.54 after g). Per the coordinator route it is a latent observation, not RED: both gold worlds give identical figures in every order.
- **R9-1: closed.** The sentence it concerned is withdrawn.
- **New defects:** none.

### post-reveal (revision_10)
- Every blind figure equals GT in both tasks.
- R9-1 is closed by withdrawal, and the revert to the round-8 room reads and scopes is exact.
- R8-1 and R8-2 stay closed. No regression and no new defect.
- Observations carried, none RED: O1, O2, O3, O4, O14, O-r6 and O-r8a (latent order dependence of the grants under a large reservation; not reached by either world, no gold moves).

### closing_checklist (revision_10)
| check | result | evidence |
|---|---|---|
| audit files | pass | 0.md and 1.md correspond one-to-one to tasks 0–1; `_difficulty.md` alongside; revisions 1–10 preserved; every revision_10 comparison is PASS |
| coverage and scopes | pass | all 7 extended policies covered; task scopes {u, r, h, g} and {q, s, n} pairwise disjoint over the whole trees |
| tools and uuid8s | pass | task tools and GT are closed; the seven uuid8s are independent and frozen |
| trees | pass | task0: 3 prerequisites, 2 value_input; task1: 2 prerequisites, 1 value_input. Each has an owner=user root, and the difficulty-wide graph is acyclic |
| factors | pass | every computation has 4–6 factors (≥ 2 parameter, ≥ 1 method), multi-source line pricing and the cross-difficulty promo factor. Every ladder has ≥ 3 reachable tiers, stated in full in its rule. Every factor moves its scored value against an honest baseline, and each fallback is definite and differs from gold |
| gates on the final form | pass | the round-10 snapshot (2026-10-25T00:09:23Z) shows all seven OK |

The difficulty passes the source-layer audit at revision_10.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

### charter_global_frozen (revision_11)
- Freeze time: 2026-10-25T04:26:25Z. Written before any round-11 GT field was read. Revisions 1–10 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 11` (round=11, 2026-10-25T04:25:19Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` 0e0d0d4e…37024 (changed); `task_tools.py` a114d891… (unchanged).
  - All seven gates are OK.
- Inputs: rework_claims_r11.md and the renderer scan STOP `audits/render_source/marketplace_orders_and_guarantee/render_r1.md`, which lists M1, M2, P1 and P2. worklog.md was not opened.
- **Disclosure:** M1 and M2 were present in the charter that revision_10 passed. My C16 sibling check covered the h/g/n set and the u/q set but not the r/s pair, so the revision_10 PASS missed them.

### verification (r11)
- **M1 (C16 sibling exclusion): closed.** Both `replaced_by` texts and their rule copies now exclude the sibling by name:
  - r: "a restocking top-up on such an order follows its own policy";
  - s: "a keep-it refund on such an order follows its own policy".
  - Each appears before "every other seller refund … still follows the return rule".
- **M2 (C16 in-force content): closed.** Both tails now restate the deadline: "the seller must refund within seller_refund_business_days business days after the return is delivered the price of the returned units less a restocking fee of at most the program's maximum percentage on an opened changed_mind return, plus the original shipping charge where the reason is a seller fault and never for changed_mind". Every part of the retired `market_returns` clause is restated.
- **P1: closed as asked.**
  - `s_engaged` and its sentence no longer read or mention the schedule.
  - The comparison is now `s_over_allowance` in `s_restock_schedule`, and the factor's sentence carries it ("a top-up is owed only where the restocking the seller's unit refunds on the returned line withheld is above that percentage …").
  - Sweep: no plain scope or engagement binding of any policy reads a factor binding.
- **P2: closed.** `r_req_date` is removed, and the r rule no longer names "the request date". Dead-binding sweep over all seven policies: none.
- **Exhaustive C16 sweep, every retired clause and every retiring policy:**

| retired clause | retiring policies | sibling naming | in-force content restated |
|---|---|---|---|
| `market_returns` refund clause | r, s | named both ways | in full |
| `market_guarantee_decision` reimbursement clause | h, g, n | each names the other two | in full: cap, rounding, original payment |
| `market_guarantee_eligibility` card-dispute clause | u, q | named both ways | in full |

  - No other member. Every replaced_by is verbatim in its rule.
- **New defect, a regression from the P1 fix: R11-1 (XF A3).** `s_withheld` ("the restocking fees they withheld", defined in the plain sentence "The refunds on the returned line are … the seller's unit refunds among them are the entries that refund units, with the units they refund and the restocking fees they withheld") is now read only by `s_over_allowance`, inside the factor `s_restock_schedule`. A quantity used by one factor only belongs to that factor and its sentence. Static sweep: this is the only A3 member in the charter.
- **No other regression:**
  - Both worlds give the same gold, all 35 factor substitutions move their figure, and the fallbacks are unchanged.
  - The revision_8 three-class probes and the revision_5/6 promo probes reproduce.
  - s owes 0.00 after its own booking.
  - O-r8a is unchanged (latent).

### post-reveal (revision_11)
- Every blind figure equals GT in both tasks.
- M1, M2, P1 and P2 are closed. My revision_10 PASS had missed M1 and M2; this is recorded above.
- The single remaining member is R11-1, A3 (`s_withheld` is now read only by `s_restock_schedule`), a by-product of the P1 fix. No other member of any class exists in the charter.

### closing_checklist (revision_11)
The difficulty is **NOT closed**.

| check | result | evidence |
|---|---|---|
| factor structure | fail | R11-1 |
| everything else | pass | as in revision_10 |

VERDICT revision_11: task0=PASS task1=RED charter=R11-1

## revision_12

### charter_global_frozen (revision_12)
- Freeze time: 2026-10-25T04:37:38Z. Written before any round-12 GT field was read. Revisions 1–11 above are untouched.
- Snapshot: executed `/tmp/erl0080_coord/snapshot.sh marketplace_orders_and_guarantee 12` (round=12, 2026-10-25T04:36:52Z).
  - Views are unchanged: task0 85298b36…, task1 f42ea4f3….
  - `market.extended.yaml` 852bd672…d320 (changed); `task_tools.py` a114d891… (unchanged).
  - All seven gates are OK.
- worklog.md was not opened.

### verification (r12)
- **R11-1: closed.**
  - `s_withheld` is now a binding of `s_restock_schedule` (bindings: s_restock_rate, s_withheld, s_over_allowance).
  - Its definition sits in that factor's sentence: "the restocking the seller withheld is the restocking fees recorded on the return refund entries on the returned line, and a top-up is owed only where that restocking is above that percentage …".
  - The plain refunds sentence no longer mentions withheld fees, and no plain binding reads them.
  - Decoys: a quantity-0 top-up carries a 0.00 fee; a keep-it refund on the same line is excluded by s's single-request line test.
- **Static sweep, all seven policies:** compute_basis and replaced_by are verbatim; A1, A3 and A9 are clean; no dead binding. The A3 sweep finds **no member**.
- **C16 re-sweep:** r/s, h/g/n and u/q still name their siblings and restate in-force content in full (deadline, cap, rounding, original payment, card dispute).
- **No regression:**
  - Both worlds give the same gold, all 35 factor substitutions move their figure, and the fallbacks are unchanged.
  - The revision_8 three-class probes and the revision_5/6 promo probes reproduce.
  - s owes 0.00 after its own booking.
  - O-r8a is unchanged (latent, not RED).
- **New defects:** none.

### post-reveal (revision_12)
- Every blind figure equals GT in both tasks.
- R11-1 is closed. No regression and no new defect.
- Observations carried, none RED: O1, O2, O3, O4, O14, O-r6 and O-r8a.

### closing_checklist (revision_12)
| check | result | evidence |
|---|---|---|
| audit files | pass | 0.md and 1.md correspond one-to-one to tasks 0–1; `_difficulty.md` alongside; revisions 1–12 preserved; every revision_12 comparison is PASS |
| coverage and scopes | pass | all 7 extended policies covered; task scopes {u, r, h, g} and {q, s, n} pairwise disjoint |
| tools and uuid8s | pass | task tools and GT are closed; the uuid8s are independent and frozen |
| trees | pass | 3 + 2 value_input and 2 + 1 value_input; owner=user roots; the difficulty-wide graph is acyclic |
| factors | pass | every computation has 4–6 factors (≥ 2 parameter, ≥ 1 method), multi-source line pricing and the cross-difficulty promo factor. Every ladder has ≥ 3 reachable tiers, stated in full. Every factor bears weight against an honest baseline, with a definite fallback that differs from gold |
| C16 sibling naming and restated in-force content | pass | complete on all three retired clauses |
| gates on the final form | pass | the round-12 snapshot (2026-10-25T04:36:52Z) shows all seven OK |

The difficulty passes the source-layer audit at revision_12.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN
