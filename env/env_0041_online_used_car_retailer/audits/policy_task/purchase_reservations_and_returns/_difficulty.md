# Policy-task audit — purchase_reservations_and_returns / charter-global

## charter_global_frozen

- Freeze time: 2026-10-06T06:32Z (written before any task's GT was revealed; nothing below is derived from a revealed GT).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Shared inputs and hashes (sha256, recomputed at freeze, equal to the brief's SHA256SUMS):
  - `tasks/purchase_reservations_and_returns/purchase.extended.yaml` 8917622880a582e26d9802d80ad47093971187a54790e15056a529f144d2745b
  - `tasks/purchase_reservations_and_returns/task_tools.py` 2142f4ed7f58c1e8d92d0a0d457f0f5a1cce9c388da7808354e72f383bcb7a33
  - `blueprint/products/purchase.yaml` 5774a2d7abe4fefa6fc717018a04f42b8d5f8ef0bf7ed4f75d7a0227ad0c900e
- Fields permitted: blueprint (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml of this scenario), the extended charter, task_tools.py, the masked views `audits/_views/policy_task/purchase_reservations_and_returns/task_{0,1}.view.json` (frozen_time, user_scenario, initial_state only), erlbench/. The restricted-expression interpreter `skills/erl-task-instantiate/scripts/check_compute.py` (functions `build_env`, `eval_compute`, `substitute`) was read and imported for its evaluation semantics only (it contains no task GT); a temporary script under /tmp used it to replay the auditor's own derivations and was deleted at the end.
- Fields masked until every task's derivation was frozen: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, the difficulty's `worklog.md`, and any prior audit. No recursive grep touched `tasks/`.
- Gate snapshot (supplied by the orchestrator, not re-run): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; check_traceability deferred until the KB is published. Entry conditions are met (gates green, masked views with hashes, snapshot present).
- Base copy check: lines 5–1464 of the extended charter vs `blueprint/products/purchase.yaml` (comment header removed) differ only by one blank-line position (`diff` shows `0a1 > ` and `1460d1460 < `); every base sentence is verbatim.

### policy_conflict_scan

Extended policies (5), their subjects and scopes as their own rules state them:

| policy | subject / target_tool (owner) | scope stated in its rule | comment marker |
| --- | --- | --- | --- |
| purchase_ext_exchange_shipping_fee | purchase_charge_posted / post_exchange_shipping_fee_0e49ee13 (agent) | "an exchange replacement order (an order whose exchange source order is set)" | task 0 |
| purchase_ext_debit_card_payment | purchase_payment_posted / pay_order_by_debit_card_8f259234 (user) | "A buyer whose order is paid in cash or through an outside lender" | task 0 |
| purchase_ext_transfer_shipping_fee | purchase_charge_posted / post_transfer_shipping_fee_29e5e50b (agent) | "a signed order that is not an exchange replacement" | task 1 |
| purchase_ext_documentation_fee | purchase_charge_posted / post_documentation_fee_307ebcc3 (agent) | "a signed order that is not an exchange replacement" | task 1 |
| purchase_ext_finance_cash_down | purchase_payment_posted / pay_finance_down_payment_by_ach_50ed840f (user) | "order is financed through Kestrel Auto Finance and whose finance contract is still only approved" | task 1 |

- Overlapping subjects: the two shipping-fee policies both post `charge_type=shipping_fee`, but their scopes partition on `exchange_source_order_id` (set vs not set), so no order is governed by both. The two payment policies partition on `payment_method` (cash/outside_lender vs kestrel_financing with an approved contract). The documentation-fee policy is the only extended governor of the documentation fee and is limited to non-exchange orders.
- Triggers/time anchors: all three charges are dated "today" by their tools; the transfer and documentation fee rules say "posted on the order on its signing date", the exchange rule "on the day the fee is booked". Base `purchase_agreement_charges` says agreement charges are "each as its own entry dated the signing date" (see override_declarations O-2).
- Eligibility/terminal states: every extended write inherits base state gates (`charges_on_open_order`: contracted; `payment_state`: contracted or cancelled); no extended rule weakens them.
- Cross-category read boundaries: reads only (delivery, finance, warranty, title, tradein, maintenance); no extended policy writes another category.
- Claimed scopes (inferred pre-reveal from the charter's `# task 0` / `# task 1` comments and from each task's world): task 0 = {exchange_shipping_fee, debit_card_payment}; task 1 = {transfer_shipping_fee, documentation_fee, finance_cash_down}. Pairwise disjoint and jointly complete over the 5 extended policies (to be confirmed against `charter_scope` after the reveal, in each task file).
- Residual gaps (observations, no task affected — see findings OBS-1, OBS-2): after both payment overwrites supersede the same base card-cap sentence, card money on a Kestrel-financed order whose contract is already active is governed by neither replacement; and the documentation-fee overwrite supersedes the base documentation-fee clause without restricting the supersession to non-exchange orders, while the extended rule only governs non-exchange orders.

### rule_compute_equivalence

Swept binding by binding against `compute_basis` and back, sentence by sentence against each `rule`.

- purchase_ext_exchange_shipping_fee: every binding (`exchange_carry_funds` ... `result`) carries a verbatim `compute_basis` quotation found in the rule. Carry share = internal-transfer down payments / vehicle price net of price reversals, rounded to 2 dp; band distance tiers (≥ high: D − 2·free; ≥ low: D − free; else D); base band from the 500/1000/1500 limits; lead time = DAYS(contract_signed_date, delivery.scheduled_date); shift 2/1/0 at ≤ 2 / ≤ 5 / > 5; band capped at 4; discount ladder with XCOUNT(finance_payment_returned, within_months=12) == 0; plan credit 150/75/0; interstate 120/60/0; discounted fee rounded, then + surcharge − credit, floor 0; zero when waived or distance ≤ free. Ordering sentence ("first the band distance ... then ... the result is never below zero") matches the binding order. Sweep back: no rule sentence without a binding. Note (observation OBS-3): `CFIELD('delivery','scheduled_date', purchase_order_id=HID)` reads the first appointment row for the order whatever its status, while the rule says "the handover appointment currently scheduled for it"; equivalent whenever an order has one appointment row (true in both worlds).
- purchase_ext_debit_card_payment: balance due (charges − reversals − payments + refunds), card money (card-channel deposits + card-channel payments − card-channel refunds of payments and deposits), ticket size, allowance basis (22.5% at ≥ 40000, 19.5% at ≥ 25000, else cap; max with cap; share rounded), standing uplift (paid_off ∧ returned_ever = 0 → 1000; paid_off ∧ returned_ever > 0 ∧ returned_12m = 0 → 500; else 0), collection adjustment (+400 Hub Pickup, −500 Vending Tower, else 0), reschedule reduction (≥ 2 → 500, = 1 → 250, else 0), allowance = basis + uplift + adjustment − reduction, room = max(0, allowance − card money), result = max(0, min(balance, room)). All quoted, all bound. Observation OBS-4: the sentence "Card money already on the order is every reservation deposit and every payment received on the order by debit card or credit card" admits a reading in which "by debit card or credit card" qualifies only payments; compute restricts deposits to card channels. No order in either world has a non-card deposit on the paying order, so no consequence.
- purchase_ext_transfer_shipping_fee: base band, lead shift (≤ 3 → 2, ≤ 7 → 1, else 0), enclosed shift (Premium/Factory Certified: White-Glove → 2, any other appointment → 1; other programs or no appointment → 0), cap 4, discounted fee, cargo surcharge (≥ 50000 → 95, ≥ 35000 → 57.50, else 0), interstate (70/45/0), financing credit (A/A+ → 90, B/C → 50, else 0), back-haul (accepted trade ∧ Local Home/Extended-Zone → 125, accepted trade ∧ Hub/Vending → 40, else 0), floor 0, zero at or below free distance. All quoted, all bound; sweep back clean.
- purchase_ext_documentation_fee: selling and registration table fees (the K table equals the base `documentation_fee_by_dealer_state`; the trailing `else CO` default is unreachable because `registration_state`/`selling_dealer_state` are enums of exactly the eight table states in db_schema.json), fee base by title service (With Inspection → max; Out-of-State → registration; else selling), financing charge (C/D/E ∧ stips false → 95; any KAF → 45; none → 0), trade charge (accepted ∧ lienholder → 60; accepted ∧ none → 25; else 0), product forms (both → 35; one → 20; none → 0), courier (Extended-Zone/White-Glove → 49.50; Local Home → 24.50; else 0), sum rounded. All quoted, all bound.
- purchase_ext_finance_cash_down: required down = max(tier floor, round(price × (tier pct + premium points − repeat points)/100, 2)); deposit credit (C/D/E ∧ card deposit → 0; B ∧ card deposit → half; else full); trade equity = max(0, offer − latest payoff quote) at 75% (Rough/Inoperable), 90% (Fair), else full; required cash floor 0; stipulation cushion (C/D/E ∧ not verified → 250; B ∧ not verified → 125; else 0); unfinanced charges (D/E: doc + shipping + tax; B/C: doc + shipping; else 0), each net of reversal; result rounded. All quoted, all bound. Observation OBS-5: `XLATEST('tradein','tradein_transactions', ... event_type='tradein_payoff_quote_recorded')` reads the customer's latest payoff quote across all trade-ins, while the rule says "the latest payoff quote recorded on it" (the linked accepted trade-in); equivalent when the customer has one trade-in (true in task 1).
- Rounding convention: the rules say "rounded half up"; the interpreter's `RND` is Python `round` on floats (not strictly half-up). No intermediate in either world lands on a half-cent tie (checked in each task's factor_weight), so this is observation OBS-6 only.
- Ladder ↔ rule ↔ binding: every tier named in each `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states. No tier lives only in compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (post_exchange_shipping_fee_0e49ee13, amount), (pay_order_by_debit_card_8f259234, amount), (post_transfer_shipping_fee_29e5e50b, amount), (post_documentation_fee_307ebcc3, amount), (pay_finance_down_payment_by_ach_50ed840f, amount) — each claimed by exactly one policy.
- uuid8 tails 0e49ee13, 8f259234, 29e5e50b, 307ebcc3, 50ed840f: all distinct, no shared prefix, no sequence or adjacency pattern, none reused.
- Docstrings: each describes one atomic booking/payment; none names another tool, states a position in a sequence, or carries before/after/first/then/until (grep of task_tools.py finds "before" only in the module docstring: "settled by the policy before the call", which concerns the policy, not another write). No tool body validates any prerequisite, status, amount or eligibility: each body only rounds the amount, creates one `purchase_transactions` row and adjusts `order_balance`.
- Business reading of each tool is unique (exchange vs transfer shipping fee tools are distinguished by their docstrings' object: "exchange replacement vehicle" vs "a signed order's vehicle").

### prerequisite_graph

| blocked policy | problem | kind | gate (binding) | form | resolved_by | policy_source locatable verbatim in own rule |
| --- | --- | --- | --- | --- | --- | --- |
| purchase_ext_debit_card_payment | purchase_ext_exchange_shipping_fee | value_input | card_balance_due (exists) | state | post_exchange_shipping_fee_0e49ee13 (= target_tool of the problem) | yes, last sentence of the rule |
| purchase_ext_finance_cash_down | purchase_ext_documentation_fee | value_input | down_unfinanced_charges (exists) | state | post_documentation_fee_307ebcc3 (= target_tool) | yes, penultimate sentence |
| purchase_ext_finance_cash_down | purchase_ext_transfer_shipping_fee | value_input | down_unfinanced_charges (exists) | state | post_transfer_shipping_fee_29e5e50b (= target_tool) | yes, last sentence |

- `prerequisite` is filled on all five policies (`[]` on exchange, transfer, documentation fee). Every `problem` is an extended policy id of this file, none is a base policy, none is self-referential; the graph is two disjoint stars and is acyclic; no cross-task reference.
- `form: state` on all three edges, no `fallback_reason` — consistent.
- `condition` texts restate the sentences at the same strength ("Whenever ... owed" / "the ... entry owed ...") — neither strengthened nor weakened. `effect` texts are true of the compute: posting the fee raises `card_balance_due` (the debit edge) or `down_doc_fee`/`down_shipping_fee` inside `down_unfinanced_charges` (Tier B–E). No authoring-viewpoint phrasing ("this task", "at the opening", "current world") anywhere in the charter (grep empty).

### prerequisite_sentences

1. Debit edge — "On an exchange replacement order, the debit-card payment toward the balance is fixed only after the order's money history carries the shipping fee entry owed for transporting the replacement vehicle." Ordering connective "only after"; waited-on state is record-visible (a `purchase_transactions` charge entry of type shipping fee, which `find_purchase_transactions` shows); no tool, policy id, snake_case token or row id; scope "exchange replacement order" matches the condition. Writes able to create a shipping-fee charge entry: post_exchange_shipping_fee and post_transfer_shipping_fee, but only the exchange policy's own rule makes a fee "owed for transporting the replacement vehicle" (the transfer rule excludes exchange replacements), so the hop resolves to one write. Derivation: sentence → records show no shipping-fee entry on the replacement order → the policy whose rule describes the charge for transporting an exchange replacement vehicle is purchase_ext_exchange_shipping_fee → its target tool. Single reading.
2. Cash-down documentation edge — "On a Kestrel Auto Finance order that is not an exchange replacement, the cash down is not fixed until the order's money history carries the documentation fee entry owed on its signing date." Connective "not ... until"; record-visible state; no tool/id/token; only purchase_ext_documentation_fee's rule describes a documentation fee owed on the signing date of a non-exchange order (base clause superseded). Single reading.
3. Cash-down shipping edge — "... carries the transfer shipping fee entry owed for transporting its vehicle." Connective "not ... until"; record-visible; only purchase_ext_transfer_shipping_fee covers non-exchange orders. Single reading.
- No rule carries a second wording of any dependency; the depended-on rules (exchange, transfer, documentation fee) do not restate the sentences; no extended rule states a cross-problem order that grounds no declared edge (the "worked out in this order" sentences order intermediates of one computation). The only base cross-problem order sentence of note ("Before refunds are released, the caller must have passed identity verification", purchase_cancellation) grounds no edge and governs no write in this difficulty's trees.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry.

- purchase_ext_exchange_shipping_fee vs purchase_agreement_charges: hold-signing sentences (1–3) not touched; "At signing the following charges post ... each as its own entry dated the signing date" — the shipping-fee amount clause including the exchange-waiver parenthetical is superseded and declared; the dating phrase is not superseded while the extended rule says "posted on that replacement order on the day the fee is booked" (O-2: undeclared deviation of the posting date; the date is not a scored parameter and booking day = signing day in task 0, so observation only); "Agreement charges post only on an order whose status is contracted" followed; deposit-application sentences not touched; "Prices and fees are those of the signing date" followed (lead time counted from the signing date). vs purchase_return_settlement: the exchange-transfer sentence ("refundable funds leave the returned order as an exchange_transfer refund entry and are moved to the replacement order as a down payment by internal transfer") is what `exchange_carry_funds` reads — followed, not altered; shipping-fee reversal on return not touched. Declared: yes. Merged semantics unique: yes.
- purchase_ext_debit_card_payment vs purchase_payment_funding: money sources followed; "A payment is posted only on an order whose status is contracted or cancelled" inherited; card-cap sentence superseded and declared ("Card money on an order paid in cash or through an outside lender may not exceed the order's card allowance"); ACH limit, down-payment lead time, outside-lender and finance-proceeds sentences untouched. Declared: yes. Base `purchase_reservation_deposit` "Deposit money counts toward the order's card payment cap when paid by card" is consistent with the replacement (card deposits count in card money).
- purchase_ext_transfer_shipping_fee vs purchase_agreement_charges: shipping-fee amount clause (without the exchange parenthetical) superseded and declared; posting on the signing date followed. vs purchase_return_settlement: untouched. Declared: yes.
- purchase_ext_documentation_fee vs purchase_agreement_charges: documentation-fee clause superseded and declared. The supersession carries no scope, while the extended rule governs only non-exchange orders (OBS-2: exchange replacement orders keep no stated documentation-fee rule after the merge; in task 0 the replacement's documentation fee is already posted at the TX table fee 225.00 and no write concerns it, so no consequence). vs purchase_return_settlement: refundable-on-return switch untouched. Declared: yes.
- purchase_ext_finance_cash_down vs purchase_payment_funding: card-cap sentence superseded and declared by "A buyer whose order is financed through Kestrel Auto Finance and whose finance contract is still only approved pays the cash down ... by ACH; card money does not pay the cash down." The same base sentence is also superseded by the debit-card policy for cash/outside-lender orders (OBS-1: for a KAF order whose contract is active, neither replacement states a card limit). ACH single-payment limit inherited (task 1's figure is far below 25,000.00); down-payment lead time inherited.
- Anonymous intermediates / 0-1 multipliers / dropped branches: none found. The exchange `result` keeps base's waiver branch; the transfer `result` keeps base's free-distance branch; no extended selector drops a base branch.
- Cross-category charter note (OBS-7): blueprint/products/finance.yaml `finance_underwriting` states the approval carries "a down payment of at least the larger of the tier's minimum down payment percentage of the vehicle price and its minimum down payment dollars"; the cash-down repeat-borrower tier lowers the percentage below the tier minimum whenever no premium points apply (e.g. Tier C 10 − 2.5 = 7.5%). Not a base_policy_ref of this charter; in task 1 premium points apply (10 + 5 − 2.5 = 12.5% ≥ 10%), so no consequence.

### factor_ladders

| policy | factor | label | ladder tiers | multi-source | cross_difficulty | label honest? |
| --- | --- | --- | --- | --- | --- | --- |
| exchange_shipping_fee | carry_over_band_distance | method | 3 (D−2F / D−F / D) | no | — | **no**: every tier evaluates band distance = D − k·F with k = 2, 1, 0 — one formula, a different number |
| exchange_shipping_fee | handover_lead_time_band | method | 3 (shift 2 / 1 / 0) | no | delivery (category, not a difficulty) | **no**: band = base band + s, s = 2, 1, 0 — one formula, a different number |
| exchange_shipping_fee | borrower_shipping_discount | parameter | 3 | yes (finance_contracts status/autopay ∧ finance_transactions returned within 12 months) | finance | yes |
| exchange_shipping_fee | protection_plan_shipping_credit | parameter | 3 | no | warranty | yes |
| exchange_shipping_fee | interstate_shipping_surcharge | parameter | 3 | no | title | yes |
| debit_card_payment | ticket_size_card_allowance | method | 3 | no | — | yes (fall-through drops the max-with-share algorithm; tiers 1–2 differ only in the share, see OBS-8) |
| debit_card_payment | finance_standing_card_uplift | parameter | 3 | yes (paid-off contract ∧ returned-payment history) | finance | yes |
| debit_card_payment | collection_method_card_adjustment | parameter | 3 | no | delivery | yes |
| debit_card_payment | appointment_reschedule_card_reduction | parameter | 3 | no | delivery | yes |
| transfer_shipping_fee | transport_lead_time_band | method | 3 (shift 2 / 1 / 0) | no | delivery | **no**: same shape as handover_lead_time_band |
| transfer_shipping_fee | enclosed_carrier_band | method | 3 (shift 2 / 1 / 0) | yes (program ∧ appointment) | delivery | **no**: band = base + lead shift + e, e = 2, 1, 0 |
| transfer_shipping_fee | cargo_value_surcharge | parameter | 3 | no | — | yes |
| transfer_shipping_fee | interstate_transport_surcharge | parameter | 3 | no | title | yes |
| transfer_shipping_fee | financing_transport_credit | parameter | 3 | no | finance | yes |
| transfer_shipping_fee | trade_backhaul_credit | parameter | 3 | yes (tradein ∧ delivery) | tradein | yes |
| documentation_fee | title_service_fee_base | method | 3 | no | title | yes (max of two table fees vs single lookup; OBS-8) |
| documentation_fee | financing_documentation_charge | parameter | 3 | tier 1 combines tier ∧ stips of one row | finance | yes |
| documentation_fee | trade_documentation_charge | parameter | 3 | no (one row) | tradein | yes |
| documentation_fee | protection_product_forms_charge | parameter | 3 | yes (warranty ∧ maintenance) | warranty | yes |
| documentation_fee | courier_charge | parameter | 3 | no | delivery | yes |
| finance_cash_down | premium_vehicle_down_points | parameter | 3 | yes (purchase program ∧ finance tier) | finance | yes |
| finance_cash_down | repeat_borrower_down_points | parameter | 3 | yes (paid-off contract ∧ installments ∧ returns) | finance | yes |
| finance_cash_down | credit_card_deposit_credit | method | 3 (0 / half / full of the applied deposit) | yes (finance tier ∧ deposit channel) | — | **no**: credit = s · applied deposit, s = 0, 0.5, 1 — exactly the structure of trade_grade_equity_share (credit = s · equity, s = 0.75, 0.90, 1), which the same policy labels `parameter` |
| finance_cash_down | trade_grade_equity_share | parameter | 3 | no | tradein | yes |
| finance_cash_down | stipulation_cushion | parameter | 3 as written, **2 reachable** | tier ∧ stips (one row) | finance | label yes; ladder **unreal**, see F-4 |
| finance_cash_down | unfinanced_agreement_charges | method | 3 (doc+ship+tax / doc+ship / none) | no | — | yes (tiers select different summand sets) |

- Every `decides` is an intermediate binding, never `result`; binding sets are disjoint within each policy; every factor's fall-through tier equals its `baseline` (checked per factor) and each policy's `baseline.rule` is a verbatim excerpt of its rule from which a definite number follows with no factor applied.
- Counts after striking the factors that fail (mislabels counted as non-method; unreal ladder struck):
  - exchange_shipping_fee: 5 declared; honest parameter 3; honest method **0** (< 1 required).
  - debit_card_payment: 4 declared; parameter 3; method 1. Passes the bounds.
  - transfer_shipping_fee: 6 declared; parameter 4; honest method **0** (< 1 required).
  - documentation_fee: 5 declared; parameter 4; method 1. Passes.
  - finance_cash_down: 6 declared; stipulation_cushion struck → 5; parameter 3 (premium, repeat, trade); honest method 1 (unfinanced); credit_card_deposit_credit mislabelled.
- Per task (by comment markers): task 0 has multi-source (borrower_shipping_discount, finance_standing_card_uplift) and cross-difficulty (finance, warranty, title); task 1 has multi-source (trade_backhaul_credit, protection_product_forms_charge, repeat_borrower_down_points, premium_vehicle_down_points) and cross-difficulty (title, finance, tradein, warranty).
- Same-value collapses (OBS-9): borrower_shipping_discount's tiers are "the larger of the program's discount and 25 / 10", so for Kestrel Certified Plus (25%) the autopay tier equals the fall-through and for Premium/Factory Certified (50%) all three tiers equal the fall-through; ticket_size_card_allowance's tiers collapse to the cap whenever the share falls below the cap. Neither collapse occurs in this difficulty's worlds (task 0 is Kestrel Certified, 0% discount, share 5,165.55 > cap 5,000.00), so observation.
- Business-realism (OBS-10): several conditions are unusual for an online used-car retailer though not demonstrably unreal — the carry-over share of exchanged money shortening the charged shipping distance, autopay status of an unrelated loan discounting a shipping fee, and the financing tier crediting a transport fee. Recorded as observations; no consequence is demonstrable from the artifacts.

### findings

- **F-1 SOURCE-FACTOR RED (bears on task 0)** — symptom: purchase_ext_exchange_shipping_fee has no honest `method` factor. Root cause: both factors labelled `method` only substitute a number into one formula: carry_over_band_distance → `exchange_band_distance = F('transfer_distance_miles') − k·P('free_transfer_distance_miles')` with k ∈ {2, 1, 0}; handover_lead_time_band → `exchange_band = MN(4, exchange_base_band + s)` with s ∈ {2, 1, 0}. Evidence: purchase.extended.yaml compute bindings `exchange_band_distance`, `exchange_band_shift`, `exchange_band`; ladders at factors `carry_over_band_distance`, `handover_lead_time_band`. Consequence: counting honestly, the computation has 0 method factors against the floor of 1. Affected: extended charter, policy purchase_ext_exchange_shipping_fee, `factors`.
- **F-2 SOURCE-FACTOR RED (bears on task 1)** — symptom: purchase_ext_transfer_shipping_fee has no honest `method` factor. Root cause: transport_lead_time_band (`transfer_lead_shift` ∈ {2, 1, 0}) and enclosed_carrier_band (`transfer_enclosed_shift` ∈ {2, 1, 0}) both add an integer into `transfer_band = MN(4, base + lead + enclosed)`. Consequence: 0 method factors against the floor of 1. Affected: policy purchase_ext_transfer_shipping_fee, `factors`.
- **F-3 SOURCE-FACTOR RED (bears on task 1)** — symptom: credit_card_deposit_credit is labelled `method` but its tiers choose a share (0, ½, 1) of the applied deposit — the same structure that trade_grade_equity_share, in the same policy, labels `parameter`. Consequence: mislabelled effect; the policy still keeps one honest method (unfinanced_agreement_charges). Affected: policy purchase_ext_finance_cash_down, factor credit_card_deposit_credit.
- **F-4 SOURCE-FACTOR RED (bears on task 1)** — symptom: the stipulation_cushion ladder's second tier ("the required verifications are not yet completed and the contract is at Tier B" → 125.00) can never hold. Evidence: blueprint/products/finance.yaml Kestrel Finance Tier B parameters `proof_of_income_required: false`, `proof_of_residence_required: false`, `references_required: 0`, and the approval event field `stips_verified: "false when the tier requires verifications, true otherwise"`. A Tier B approval therefore always carries `stips_verified = true`. Consequence: the ladder has two reachable tiers (C/D/E unverified → 250.00; otherwise → 0), below the three-tier floor, so the factor does not count. Affected: policy purchase_ext_finance_cash_down, factor stipulation_cushion and the corresponding rule sentence.
- Observations OBS-1 … OBS-10 as listed in the sections above (no demonstrable consequence on either task).

## closing_checklist

Written after both reveals (2026-10-06T09:06Z); the charter-global sections above were frozen before any reveal and are unchanged.

- Per-task files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; this is revision 1 (no older revision exists). Both comparison sections are on disk; **neither carries a full PASS** — task 0 SOURCE-FACTOR RED (F-1), task 1 SOURCE-FACTOR RED (F-2, F-3, F-4). The difficulty therefore **does not close** at the source layer.
- Coverage and scopes: the 5 extended policies are fully covered; charter_scope task 0 = {exchange_shipping_fee, debit_card_payment}, task 1 = {documentation_fee, transfer_shipping_fee, finance_cash_down} — pairwise disjoint across whole trees, jointly complete. Task tools and GT are closed (each task's GT calls exactly its own scope's tools); the five uuid8s are independent and frozen.
- Trees: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 2 prerequisite problems and 2 value_input edges; each tree has one owner=user root write; the whole difficulty's prerequisite graph is acyclic with no cross-task reference. PASS.
- Factors: every computation declares a self-sufficient baseline and its fall-back differs from gold (1,099.00 vs 809.25; 5,000.00 vs 5,815.55; 499.00 vs 938.50; 399.50 vs 672.50; 0.00 vs 3,460.91), and every declared factor bears weight on its task's world. **Fails** on structure: the exchange shipping fee and the transfer shipping fee have no honest `method` factor (F-1, F-2), credit_card_deposit_credit is mislabelled (F-3), and stipulation_cushion has two reachable tiers (F-4).
- Unique solution: the auditor's blind derivations equal GT on every scored value, owner and order in both tasks. PASS.
- Instantiation-stage gates: not re-run by the auditor (the skill assigns the run to the orchestrator); the orchestrator's final-form snapshot in the brief is all green (check_traceability deferred until the KB is published). The red findings are ones those gates do not test (effect-label honesty, reachability of a tier under another category's charter).

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-06T10:20Z, before any round-2 GT was revealed. Auditor: same independent auditor as round 1.
- Shared-input hashes: `purchase.extended.yaml` 283f477583c260a23d03d95964b4b3a9fbe0329dad8811023304f4f5b2826926 (changed from 8917622880…), `task_tools.py` 2142f4ed7f58c1e8d92d0a0d457f0f5a1cce9c388da7808354e72f383bcb7a33 (unchanged), `blueprint/products/purchase.yaml` 5774a2d7… (unchanged). Masked views: task_0 f31a7160… (unchanged), task_1 ac9162aa648bcb7887ed7a7747802e6b514ccfb18eefd5f783cdbf0000a1b252 (changed). All equal to the brief's SHA256SUMS.
- Because the charter hash changed, every charter-global section below is re-derived in full; § action_binding_and_uuids is the only one whose inputs (tool module + target_tool fields) are unchanged, and it is re-checked rather than carried forward.
- Gate snapshot (orchestrator, after rework): all seven gates green; check_traceability deferred.
- Base copy: lines 5–1464 still verbatim against `blueprint/products/purchase.yaml` (same one blank-line `diff` as round 1).
- contamination_disclosure: in round 1 the auditor read tasks/0.json and tasks/1.json GT (amounts 809.25, 5,815.55, 938.50, 672.50, 3,460.91). Round-2 derivations are recomputed from the reworked charter and views; where a round-2 value equals a round-1 GT value (5,815.55, 938.50) it was recomputed, not carried. Round-2 task JSON files were not opened before the per-task revision_2 freezes. The worklog was never read.

### what changed in the charter (from a full re-read of extended_policies)

- purchase_ext_exchange_shipping_fee: rule now "posted on that replacement order dated its signing date"; carry-over factor rewritten as `carry_over_courtesy_miles` (`parameter`: courtesy miles 2·free / free / 0 taken off the distance → `exchange_pricing_distance`); the lead-time factor replaced by `expedited_exchange_transport_pricing` (`method`: ≤ 2 days → pricing distance × 1.45 per mile, no band fee; ≤ 5 days → max(band fee, distance × 1.15); else band fee); borrower discount is now additive points (program + 25 / + 10, capped at 100) instead of max(program, 25 / 10).
- purchase_ext_debit_card_payment: overwrite and rule now also state "card money on an order paid through Kestrel Auto Finance may not exceed the program's card payment cap, deposit included"; card-money sentence now reads "every reservation deposit paid on the order by debit card or credit card and every payment received on the order by debit card or credit card, less every refund of such deposit or payment money ...". Factors and compute unchanged.
- purchase_ext_transfer_shipping_fee: carrier price ladder `enclosed_carrier_pricing` (`method`: Premium/Factory + White-Glove → distance × 1.95, no band fee; Premium/Factory + other appointment → max(band fee, distance × 1.65); else band fee); lead time is now `transport_lead_time_surcharge` (`parameter`: + 120 / + 65 / 0). Overwrite replaced_by updated accordingly.
- purchase_ext_documentation_fee: rule adds "An exchange replacement order is outside this rule: its documentation fee stays the table fee for the state of its selling Kestrel dealer license, with none of the charges below." Compute and factors unchanged.
- purchase_ext_finance_cash_down: `down_pct = MX(tier pct, tier pct + premium − repeat)` with the rule sentence "never below the tier's minimum percentage"; `credit_card_deposit_credit` relabelled `parameter`; `stipulation_cushion` now D/E unverified → 400.00, C unverified → 250.00, else 0 ("no cushion once the verifications are completed or at a tier whose approval requires no verification"); the payoff quote is read through `trade_in_id = down_trade_id` (the linked accepted trade-in).

### policy_conflict_scan (revision 2)

- Scopes unchanged (exchange vs non-exchange shipping; cash/outside-lender vs KAF-approved payments; documentation fee now explicitly scoped and the exchange-replacement fee stated). Pairwise disjoint, jointly complete over the 5 policies.
- The two payment overwrites of the base card-cap sentence now together cover cash/outside-lender (card allowance) and KAF orders (program cap; cash down not payable by card). For a KAF-approved order both apply and are compatible: card money is capped and does not pay the cash down. OBS-1 closed.
- New observation OBS-11: the three fee rules say the charge is posted/dated on the order's signing date, while all three tools date the entry `ctx.now()` ("dated today"). They coincide whenever the fee is booked on the signing day, as in both worlds (2026-10-06 and 2026-10-08 are the respective signing days and frozen dates). Not a scored parameter; observation only. The transfer and documentation-fee rules carried the same wording in round 1; this is a late catch, not a regression.

### rule_compute_equivalence (revision 2)

- Exchange: each new binding (`exchange_courtesy_miles`, `exchange_pricing_distance`, `exchange_band`, `exchange_band_fee`, `exchange_transport_price`, `exchange_discount_pct` with MN(100, …), `exchange_fee_discounted`) carries a verbatim compute_basis quotation from the rule; the "worked out in this order" sentence matches the binding order (courtesy miles → pricing distance → transport price → discount → surcharge/credit → floor). No rule sentence lacks a binding.
- Debit: compute unchanged; the reworded card-money sentence now matches `card_money_in`/`card_money_out` exactly (OBS-4 closed). The new KAF cap sentence states a limit and has no binding; it governs no write of this policy, whose first sentence limits it to cash/outside-lender orders, so this is not an empty promise of the computation.
- Transfer: `transfer_carrier_price` and `transfer_lead_surcharge` match the new sentences; the order sentence ("first the carrier price ..., then ... discount ...; the lead-time surcharge, the cargo value surcharge and the interstate transport surcharge are then added ...") matches `transfer_fee_adjusted`.
- Documentation fee: unchanged compute; the new exclusion sentence matches the policy scope (exchange orders get the base table fee). OBS-2 closed.
- Cash down: `down_pct` floor matches "never below the tier's minimum percentage" (OBS-7 closed); `down_trade_payoff` now filters `trade_in_id` of the linked accepted trade-in, matching "the latest payoff quote recorded on it" (OBS-5 closed); `down_stipulation_cushion` matches the new sentence.
- Ladder ↔ rule ↔ binding: every tier of every `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and conversely.
- Still open by choice: OBS-3 (CFIELD of the first appointment row) and OBS-6 (RND not strictly half-up); no tie occurs in either world (checked in the task files).

### action_binding_and_uuids (revision 2)

Tool module unchanged (hash 2142f4ed…); target_tool and computes fields unchanged. Same five unique (tool, amount) claims; uuid8s 0e49ee13, 8f259234, 29e5e50b, 307ebcc3, 50ed840f still independent; no docstring states order; no body validates anything. PASS.

### prerequisite_graph and prerequisite_sentences (revision 2)

Prerequisite blocks and the three prerequisite sentences are byte-identical to round 1 (debit → exchange fee; cash down → documentation fee; cash down → transfer fee; all value_input, state form, gates `card_balance_due` and `down_unfinanced_charges` still exist). The round-1 conclusions stand (acyclic, verbatim, four-point test passed, single resolving write per state-form edge). The new documentation-fee exclusion sentence strengthens the uniqueness of the documentation hop for non-exchange orders. PASS.

### override_declarations (revision 2)

- Exchange: same superseded clause; the posting-date deviation O-2 is closed (the rule now says "dated its signing date", matching base "each as its own entry dated the signing date").
- Debit: replaced_by extended to KAF orders; declared. Transfer: replaced_by rewritten to the carrier-price order; declared. Documentation fee: same clause; the rule now states what applies to exchange replacements (the base table fee), so the merge leaves no ungoverned order. Cash down: unchanged declaration.
- Cross-category: the down-payment percentage can no longer fall below the finance charter's tier minimum (`finance_underwriting`). OBS-7 closed.
- No anonymous intermediate, 0/1 multiplier or dropped branch found in the reworked compute.

### factor_ladders (revision 2)

| policy | factor | label | honest? | tiers reachable | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| exchange | carry_over_courtesy_miles | parameter | yes (a mileage figure) | 3 | no | — |
| exchange | expedited_exchange_transport_pricing | method | yes: per-mile product without band fee / max(band fee, per-mile product) / band fee — three different pricing algorithms | 3 | no | delivery (category) |
| exchange | borrower_shipping_discount | parameter | yes | 3; values program+25 / program+10 / program, capped at 100 — distinct for every program (0→25/10/0, 25→50/35/25, 50→75/60/50) | yes | finance |
| exchange | protection_plan_shipping_credit | parameter | yes | 3 | no | warranty |
| exchange | interstate_shipping_surcharge | parameter | yes | 3 | no | title |
| debit | (unchanged: ticket_size_card_allowance method; standing uplift, collection, reschedule parameter) | — | as round 1 | 3 each | uplift yes | finance, delivery |
| transfer | enclosed_carrier_pricing | method | yes: white-glove per-mile only / max(band, per-mile) / band fee | 3 | yes (program ∧ appointment) | delivery |
| transfer | transport_lead_time_surcharge | parameter | yes | 3 | no | delivery |
| transfer | cargo_value_surcharge, interstate_transport_surcharge, financing_transport_credit, trade_backhaul_credit | parameter | yes | 3 each | backhaul yes | title, finance, tradein |
| documentation fee | (unchanged: title_service_fee_base method; 4 parameter) | — | as round 1 | 3 each | forms yes | title, finance, tradein, warranty, delivery |
| cash down | premium_vehicle_down_points, repeat_borrower_down_points | parameter | yes | 3 each | yes | finance |
| cash down | credit_card_deposit_credit | parameter | yes (now consistent with trade_grade_equity_share) | 3 | yes | — |
| cash down | trade_grade_equity_share | parameter | yes | 3 | no | tradein |
| cash down | stipulation_cushion | parameter | yes | **3 reachable**: Tier D/E (finance.yaml: proof of income true, residence true, references 2/4) and Tier C (proof of income true) approvals open with `stips_verified` false; otherwise 0 | tier ∧ stips (one row) | finance |
| cash down | unfinanced_agreement_charges | method | yes | 3 | no | — |

- Counts: exchange 5 (4 parameter, 1 method); debit 4 (3, 1); transfer 6 (5, 1); documentation fee 5 (4, 1); cash down 6 (5, 1). All within 4–6 with ≥ 2 parameter and ≥ 1 honest method. Fall-through = baseline for every factor; every `baseline.rule` is a verbatim excerpt of its rule.
- Interaction note (observation OBS-12): with the new floor, the repeat-borrower ladder can lower the percentage only when premium points apply; for any other vehicle or tier the floor cancels both reduction tiers, and the factor bears no weight. In task 1 premium points apply (10 + 5 − 2.5 = 12.5 > 10), so the factor bears weight there (see 1.md revision_2).
- OBS-9: the borrower-discount collapse is closed; the ticket-size collapse (share below cap) remains as before, with no effect in task 0 (5,165.55 > 5,000.00).
- OBS-8 and OBS-10 left unchanged by choice; still observations.

### findings (revision 2)

- F-1 **closed**: the exchange computation now has one honest method factor (expedited_exchange_transport_pricing) and the carry-over factor is honestly labelled `parameter`.
- F-2 **closed**: the transfer computation now has one honest method factor (enclosed_carrier_pricing); lead time is an honestly labelled `parameter` surcharge.
- F-3 **closed**: credit_card_deposit_credit is labelled `parameter`, consistent with trade_grade_equity_share.
- F-4 **closed**: all three stipulation-cushion tiers are reachable under the finance charter.
- Observations closed: O-2, OBS-1, OBS-2, OBS-4, OBS-5, OBS-7, OBS-9 (borrower-discount half). Still open by choice: OBS-3, OBS-6, OBS-8, OBS-10, ticket-size half of OBS-9. New: OBS-11 (fee date vs tool date), OBS-12 (floor makes the repeat ladder inert without premium points). No new charter-global RED found.

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-06T10:14:54Z). Timestamp correction: this revision's "Freeze time 10:20Z" above was an estimate; the actual on-disk time of the charter-global revision_2 sections is 10:14:07Z, before any round-2 reveal.

- Per-task files `0.md` and `1.md` each carry a revision_2 frozen derivation and comparison; both are **PASS** on all four relationships. The round-1 text is preserved unchanged above each revision_2.
- Coverage: all 5 extended policies covered; scopes pairwise disjoint and jointly complete; tools and GT closed; uuid8s independent and frozen.
- Trees: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 2 and 2; each root is an owner=user write; the difficulty's graph is acyclic.
- Factors: every computation has 4–6 factors with ≥ 2 parameter and ≥ 1 honest method, a self-sufficient baseline whose fall-back differs from gold (1,099.00 vs 731.06; 5,000.00 vs 5,815.55; 499.00 vs 938.50; 399.50 vs 561.75; 0.00 vs 3,350.16), every ladder has three reachable tiers stated in the rule, and every factor bears weight on its task's world. Each task has a multi-source factor and a cross-difficulty factor.
- Unique solution: blind round-2 derivations equal GT on every scored value, owner and order.
- Gates: the orchestrator's post-rework snapshot (all seven green; traceability deferred) is the final-form re-run; the auditor did not run gates.
- **The difficulty passes the source-layer audit at revision 2.** Remaining observations (OBS-3, OBS-6, OBS-8, OBS-9 ticket-size half, OBS-10, OBS-11, OBS-12, task-0 persona note) carry no demonstrated consequence.
