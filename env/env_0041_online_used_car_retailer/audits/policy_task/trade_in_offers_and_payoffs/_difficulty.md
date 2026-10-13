# Policy-task audit — trade_in_offers_and_payoffs / charter-global

## charter_global_frozen

- Scenario: `env/env_0041_online_used_car_retailer`; difficulty `trade_in_offers_and_payoffs` (claim: categories [tradein]); M = 2.
- Freeze hashes (sha256, verified against the orchestrator's `SHA256SUMS` before reading):
  - `tasks/trade_in_offers_and_payoffs/tradein.extended.yaml` = `dcbad53ead82283f734c63c57c8bba430a52db7b290730772c944943e5a82cfc`
  - `tasks/trade_in_offers_and_payoffs/task_tools.py` = `9328a0fda8882cd445a02abda3bc6fa22441e5c595a3807c8424fb7359862f09`
- Freeze time: 2026-10-06T06:31Z (written before any task's GT was opened). Auditor: independent policy-task auditor (Claude agent), not the instantiating agent.
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/tradein.yaml` (whole), `blueprint/products/finance.yaml` (tier `min_credit_score` / `max_negative_equity_usd` lines only), the whole extended charter, the whole tool module, and the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, lines 240-390: customer-scoped `EXISTS`/`CFIELD`/`CPARAM`/`X*`, holding-scoped `SUM`/`LATEST`/`MAX`, `RND` = Python `round`).
- Fields masked and not read for this section: every `tasks/*.json` field other than the orchestrator's views; `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; `worklog.md`; any earlier audit.
- Entry conditions (Step 0): gate snapshot supplied with the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; `check_traceability` deferred until the KB is published — recorded, not a defect of this audit's input); masked views supplied with hashes, both `task_*.view.json` verified `OK` by `sha256sum -c`. Input complete.
- Base copy: `diff blueprint/products/tradein.yaml <(sed -n 1,1077p tradein.extended.yaml)` is empty — the base section of the extended charter is a verbatim copy.

Policy abbreviations used below and in the task files:
M = `tradein_ext_mileage_overage_deduction` (post_mileage_deduction_140e91ac, agent);
R = `tradein_ext_negative_equity_rollin` (record_negative_equity_rollin_4688789d, agent);
S = `tradein_ext_payoff_shortfall_payment` (pay_trade_shortfall_d2aa4d28, **user**);
L = `tradein_ext_lien_payoff_charge` (send_lien_payoff_9460d1ba, agent);
T = `tradein_ext_towing_fee_deduction` (post_towing_fee_7cb58a13, agent);
C = `tradein_ext_title_delay_chargeback` (post_title_delay_chargeback_a143df45, agent);
I = `tradein_ext_chargeback_shortfall_installment` (pay_chargeback_shortfall_4672c84f, **user**).

### policy_conflict_scan

Subjects and writes. The seven extended policies write three ledger families:
- `tradein_value_deducted` — M (`adjustment_type` mileage_overage), T (towing_fee), C (title_delay_chargeback). Distinct reasons, distinct tools; no two of them price the same quantity.
- `tradein_negative_equity_settled` — R (`rolled_into_financing`), S (`customer_payment`, payoff shortfall), I (`customer_payment`, chargeback shortfall). S and I share the ledger kind but are separated by their trigger sentences ("When the payoff the old lienholder is owed exceeds the undistributed trade equity…" vs "When a title-delay chargeback leaves the undistributed trade equity … below zero") and by tool; no situation in which both are the one applicable policy was found.
- `tradein_lien_payoff_sent` — L only.

Base provisions inherited without overwrite and that bear on the extended writes (each must hold at the write; checked per task):
- `tradein_pickup_inspection`: "Value is credited or deducted only on an agreement whose status is picked_up." (M, T, C).
- `tradein_lien_payoff`: `payoff_on_picked_up`; `quote_age` ("…no more than the payoff quote max age on the send date", 10 days in every grade); `one_payoff`; "When negative equity must be cleared first, the payoff is sent only after the shortfall has been covered under tradein_negative_equity." (same direction as L's own prerequisite sentence — compatible).
- `tradein_negative_equity`: "…or by the customer's own payment on one of the accepted shortfall channels within the negative equity payment days after pickup" (5 days in every grade) and "Card payments are not accepted for a shortfall." — inherited by S; S's rule is silent on timing and says "by bank transfer" (compatible with ach/wire). Whether the 5-day window is open at S's write is a per-task fact.
- `tradein_negative_equity`: "…by rolling it into the Kestrel Auto Finance contract of the linked purchase, when the grade allows roll-in and the finance contract is signed with the shortfall included in the amount financed" — the clause "signed with the shortfall included in the amount financed" is not named in R's `overwrite` and is not restated by R's rule, whose trigger is only "paid through a Kestrel Auto Finance contract and the grade allows roll-in"; R's own value-figure ladder explicitly prices contracts signed before pickup ("the figure the contract was written on"). No record (`finance_contracts.amount_financed` is not itemised) can show whether a shortfall was included, so the clause can be neither satisfied nor refuted from the world → observation O-1 (not demonstrable as a second answer).
- `tradein_title_receipt` `chargeback_timing` (applies_to `tradein_value_deducted` in the base eligibility list): M declares an overwrite releasing mileage deductions from it; T does not, but the base sentence speaks only of "A title-delay chargeback", so it does not govern a towing deduction → observation O-2 (inconsistent declaration practice, no second reading).
- `tradein_pickup_inspection` reacceptance: "When the inspection reduction, counted by tradein_msr_inspection_reduction, exceeds the reacceptance threshold … the customer must re-accept the adjusted offer before pickup completes". The measure counts deductions "dated the pickup date"; M and T book their entries "dated the day it is booked". A post-pickup mileage/towing deduction therefore never enters the measure, by letter. No conflict by letter; observation O-3 (the extended booking date silently removes post-pickup deductions from the reacceptance test).

Scope exclusivity and completeness. The `prerequisite` graph splits the seven policies into two disjoint trees: {L ← S, L ← M, S ← M, S ← R} rooted at L, and {I ← C, I ← T} rooted at I. Two tasks, one tree each, would cover all seven policies with no overlap; confirmed per task from `user_scenario` (task 0 asks for the lien payoff; task 1 asks to spread a chargeback shortfall) and re-checked against `charter_scope` only after the reveal.

### rule_compute_equivalence

Every compute binding of all seven policies was matched to its `compute_basis` quotation and the quotation located verbatim in that policy's `rule`; every rule sentence was swept back to a binding. Results:

- M: all 16 bindings quoted and implemented. `record_lead_days` uses `if record_odometer_reading else -1` (a zero reading is treated as no record) — non-claim entries carry 0 but are filtered by `event_type`, so no divergence. `kestrel_history_rate_share` reads `EXISTS('warranty', vin=…)` of any status — the rule says "a KestrelCare service contract on that VIN", any status. Equivalent.
- R: all 17 bindings quoted. Value-figure ladder thresholds (`>= 7`, `>= 1`, else) match "at least the early-signing days before pickup / at least one day but fewer … / on the pickup date or later". Accrual ladder matches. Ceiling via `CPARAM('finance','max_negative_equity_usd')`. Equivalent.
- S: all 15 bindings quoted. **One divergence (finding F-4):** tier 1 of the accrual convention, rule "a quote good for no more than the short-validity days accrues per diem for each calendar day from its quote date through the day of payment", compute `MX(0, DAYS(cover_quote_date, NOW))` (excludes the quote date), while the very next tier writes out "from its good-through date itself through the day of payment, both days counted" and computes `DAYS(...)+1`. "Each calendar day from X through Y" read plainly counts both ends (DAYS+1); the compute counts one end. Consequence arises only in a world whose latest quote is good for ≤ 2 days (checked per task).
- L: all 18 bindings quoted. `send_weekday == 4` is Friday (2024-01-01 is a Monday). The rule's ladder names "a Friday send date" and "a send date on any other weekday"; a Saturday/Sunday send falls into compute's "non-Friday" branch while the rule is silent → observation O-4 (only for weekend send dates). `deadline_offset_days` reproduces "payoff send business days after the pickup date, counting Monday to Friday only and starting with the first weekday after the pickup date" for every pickup weekday when n ≤ 5 (n is 2 or 3 in every grade). Equivalent.
- T: all 12 bindings quoted and implemented. Equivalent.
- C: all 14 bindings quoted. `autopay_installments_last_year` = `XCOUNT('finance','finance_transactions', within_months=12, …)` counts autopay postings on **all** of the customer's finance ledgers, while the rule says "posted on it [the Kestrel Auto Finance contract of that purchase] by autopay in the last twelve months" → observation O-5 (diverges only for a customer with a second finance contract carrying autopay postings; checked per task). "Last twelve months" is implemented as `0 <= MONTHS(d, NOW) < 12`.
- I: all 13 bindings quoted. `kestrel_purchase_count` counts every `purchase_charge_posted / vehicle_price` row of the customer, matching "counted as the vehicle-price charges posted on the customer's Kestrel purchase orders". Equivalent.
- All policies: `RND` is Python `round` on a binary float; the rule says "rounded to the nearest cent". Diverges only on an exact half-cent; checked per task.

Each factor's ladder is present in both faces: every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and every branch of each `decides` binding is a stated tier (checked for all 35 factors: M 6, R 6, S 5, L 4, T 5, C 5, I 4). No tier lives only in compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (post_mileage_deduction_140e91ac, deduction_amount), (record_negative_equity_rollin_4688789d, rollin_amount), (pay_trade_shortfall_d2aa4d28, payment_amount), (send_lien_payoff_9460d1ba, payoff_amount), (post_towing_fee_7cb58a13, towing_fee), (post_title_delay_chargeback_a143df45, chargeback_amount), (pay_chargeback_shortfall_4672c84f, payment_amount) — each claimed by exactly one policy.
- Owners: S and I tools are `owner="user"`; the other five `owner="agent"`.
- Docstrings: `grep -niE "\b(before|after|first|then|until|prior|once|only)\b" task_tools.py` → no match. No docstring names another tool, a sequence position or a policy id.
- Function bodies: every tool rounds the amount, `ctx.create`s one `tradein_transactions` row dated `ctx.now()[:10]` and moves `equity_balance` by ±amount; none reads status, quote age, prior entries or any prerequisite and none refuses or hints. The tool layer judges no prerequisite.
- uuid8 tails: 140e91ac, 4688789d, d2aa4d28, 9460d1ba, 7cb58a13, a143df45, 4672c84f — seven distinct values, no shared prefix, no sequential or adjacent pattern, no reuse. Pass.

### prerequisite_graph

- `prerequisite` is filled on all seven policies: M `[]`, R `[]`, T `[]`, C `[]`; S → {M, R}; L → {S, M}; I → {C, T}.
- Every `problem` is an extended policy id of this file; none is a base policy or the policy itself.
- Edges: L→S (state_gate, action form), L→M (value_input, state), S→M (value_input, state), S→R (value_input, state), I→C (value_input, state), I→T (value_input, state). Acyclic (M, R, C, T are sinks). Two components: {L,S,M,R} and {I,C,T}.
- `policy_source` located verbatim in the blocked policy's own `rule` for all six edges (string-matched against the rule text).
- `form`/`fallback_reason`: the single action-form edge (L→S) carries `fallback_reason`; the five state-form edges carry none. Consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all six edges.
- `kind`/`gate`: value_input gates name real bindings — `cover_trade_equity` (S, both edges), `kestrel_absorbed_days` (L), `shortfall_owed` (I, both edges). The state_gate L→S names `tradein_agreements.equity_balance`, a field rather than an eligibility id; the gate it refers to is L's own rule sentence (no base eligibility entry gates on equity) → observation O-6.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any `prerequisite` text.
- `condition` vs sentence strength: see `prerequisite_sentences` — S→R's sentence is broader than its condition (finding F-1).

### prerequisite_sentences

Four-point test per edge (connective / form / no tool-id-token / strength):

1. **S→M** — "The shortfall payment is not figured until the agreement's ledger carries the mileage deduction owed on an inspected mileage above the stated mileage." Connective "not … until"; state form (a ledger entry of a named kind, in record words); no tool or id; strength matches the condition ("whenever its inspected mileage exceeds its stated mileage and the mileage rule charges any miles" — "owed"). The only write of this difficulty that leaves a mileage-overage deduction entry is M's. Derivation: sentence → reader looks for the policy that books "one value deduction entry for mileage overage" → M's rule → post the mileage deduction. Single reading. Pass.
2. **S→R** — "Where the purchase the trade is applied to is financed through Kestrel Auto Finance, the shortfall payment is fixed only after the agreement's ledger carries the entry for the negative equity rolled into that financing." Connective "only after"; state form; no tool or id; the one write that leaves a rolled-into-financing entry is R's. **Strength fails**: the condition is "whenever that purchase is paid through Kestrel Auto Finance **and the grade allows roll-in**"; the sentence omits the grade clause. R's rule applies only "Where the purchase order … is paid through a Kestrel Auto Finance contract **and the grade allows roll-in**", and `negative_equity_roll_in_allowed` is false for Inoperable Condition Offer. Finding F-1.
3. **L→S** (action form) — "Where the payoff charge exceeds the undistributed trade equity, the lien payoff is not sent until the customer has paid in the part of the shortfall that no financing roll-in covers." Connective "not … until"; action named in business words; no tool or id. Fallback test: the state the write leaves (a `customer_payment` covering entry) is also left by I's write, and the equity level it restores is also raised by R's write; no record-visible state singles out S's write — fallback justified. Derivation: the reader finds the policy in which "the customer pays the shortfall from their own funds … booked as one covering entry for a customer payment" whose trigger is "the payoff the old lienholder is owed exceeds the undistributed trade equity" → S (I's trigger is a title-delay chargeback, excluded). Single reading of *which* action. **Strength note**: the condition is "the undistributed trade equity is at least the payoff charge"; the sentence is satisfied by "the customer has paid in the part of the shortfall that no financing roll-in covers", whose amount S prices by its own formula (coverage payoff figure, cushion, loyalty and protection credits) rather than as payoff charge − equity. Whether the two coincide after S's write is a per-task number (observation O-7; demonstrated per task where it matters).
4. **L→M** — "The payoff charge is fixed only after the agreement's ledger carries the mileage deduction due on an inspected mileage above the stated mileage." Connective "only after"; state form; one writer (M). Pass.
5. **I→C** — "Today's installment is fixed only after the agreement's ledger carries the title-delay chargeback owed once the title delay chargeback days have passed with no title received date." Connective "only after"; state form; one writer (C). Strength matches condition. Pass.
6. **I→T** — "Today's installment is not worked out until the agreement's ledger carries the towing fee deduction owed for a vehicle Kestrel collected by tow truck." Connective "not … until"; state form; one writer (T). Strength matches condition. Pass.

Other checks: no blocked rule carries a second wording of its dependency, a tool name or another problem's id; no depended-on rule restates the sentence (M, R, C, T rules mention no downstream write; R's "whatever part of the negative equity it leaves uncovered is the customer's to pay" states no order). Undeclared cross-problem orders in extended rules: none stated. Base sentences stating a cross-problem order: `tradein_lien_payoff` "When negative equity must be cleared first, the payoff is sent only after the shortfall has been covered under tradein_negative_equity" — L carries its own extended sentence for that edge, so no tree rests on the base sentence alone → observation O-8. Order-dependent values with no declared order: R's value-figure fall-through ("a contract signed on the pickup date or later is measured against the undistributed trade equity") reads `equity_balance`, which M's write lowers, and there is no edge between M and R — two orders give two roll-in values in a world on that tier (observation O-9; the swap test is run per task).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only):

- M ⟂ `tradein_pickup_inspection`: the mileage clause ("the mileage deduction when … charged on every mile above the stated mileage;") is handled differently and is named in `overwrite` ✓. "Then each remaining finding is deducted at the rates of the grade in force after any regrade" — followed (`P('mileage_overage_deduction_per_mile')` of the current grade). Picked-up state gate followed. Reacceptance sentence — O-3. M ⟂ `tradein_title_receipt`: chargeback-timing sentence named ✓.
- R ⟂ `tradein_negative_equity`: the definition sentence and the "limited by the finance tier's negative equity limit …" sentence both named ✓; "signed with the shortfall included in the amount financed" — not named, not demonstrable (O-1); state gate (accepted or picked_up) followed. R ⟂ `tradein_agg_purchase_link`: roll-in only into the linked purchase's KAF contract — followed.
- S ⟂ `tradein_negative_equity`: definition sentence named ✓; "within the negative equity payment days after pickup" — not named, therefore inherited in full (per-task timing check); channels/no-card — followed ("bank transfer"). S ⟂ `tradein_lien_payoff`: S prices no payoff amount; nothing handled differently.
- L ⟂ `tradein_lien_payoff`: "The amount sent is the quote amount when sent on or before …" named ✓ (the whole quantity is replaced; the refresh-relief and program-share tiers modify that same named quantity); late-per-diem sentence named ✓; picked-up gate, quote-age gate, one-payoff dedup, negative-equity-first sentence followed. Dropped-branch check: "quote amount when sent on or before the good-through date" is still produced (window `MX(0, …)` = 0). L ⟂ `tradein_negative_equity`: nothing priced.
- T ⟂ `tradein_pickup_inspection`: towing clause named ✓. T ⟂ `tradein_title_receipt`: not named; O-2.
- C ⟂ `tradein_title_receipt`: amount sentence named ✓; timing sentence restated verbatim in C's rule; "reversed by nothing" followed. C ⟂ `tradein_pickup_inspection`: picked-up gate followed.
- I ⟂ `tradein_title_receipt` and ⟂ `tradein_negative_equity`: both "within the chargeback payment days" sentences named ✓; no-card followed.
- Disguised forms: L's upper-program customer share is 0 (a 0 multiplier on the per diem) — but the per diem is the quantity named in L's first overwrite, so declared. No anonymous intermediate or dropped base branch found elsewhere.
- Every extended rule states its baseline sentence unhedged and then the factor sentences that refine it (e.g. I: "The amount paid today is the whole shortfall …" followed by "Today's installment is the installment basis divided by the installment count …"). This is the baseline-in-rule shape the method requires; the merged reading (specific tier sentence governs) is unique → observation O-10, not a conflict.

Override result: no undeclared override with a demonstrable second answer.

### factor_ladders

Classification standard used throughout: a tier set is `parameter` when there is one formula f(x; θ) and the tier only changes a scalar θ (a rate, fee, threshold, multiplier or fixed day offset); it is `method` when the tiers select different input quantities or records, or different functional forms.

| Policy | Factor | Label | Tiers (≥3, disjoint, distinct outcome) | Multi-source (every non-fall-through tier ≥2 conditions over distinct records) | cross_difficulty | Label honest? |
|---|---|---|---|---|---|---|
| M | tolerance_by_wait | parameter | 2000 / 1500 / grade 1000 ✓ | no (dates of one agreement) | — | ✓ |
| M | kestrel_odometer_record | method | excess-only / all miles no test / all miles if > tolerance ✓ | **yes** (warranty claim + agreement) | warranty | ✓ |
| M | delivery_delay_credit | parameter | 60 / 40 / 0 ✓ | no (one delivery row) | (delivery, not a difficulty) | ✓ |
| M | value_band_share | parameter | 0.5 / 0.75 / 1 ✓ | no | — | ✓ |
| M | kestrel_history_share | parameter | 0.85 / 0.92 / 1 ✓ | **yes** (purchase + warranty) | — (reads purchase, warranty) | ✓ |
| M | program_share | parameter | 0.8 / 0.9 / 1 ✓ | no | purchase | ✓ |
| R | payoff_accrual_window | method | per-diem×days / per-diem×cap / none ✓ | no | — | narrow: a capped day count (O-11) |
| R | signing_value_figure | method | credited total / original offer / equity ✓ | **yes** (finance contract date + agreement) | finance | ✓ |
| R | term_share | parameter | 0.7 / 0.85 / 1 ✓ | no | finance | ✓ |
| R | standing_share | parameter | 0.8 / 0.9 / 1 ✓ | tier variant + contract flag (same contract) | finance | ✓ |
| R | addon_share | parameter | 0.9 / 0.95 / 1 ✓ | **yes** (warranty + maintenance) | — | ✓ |
| R | gap_share | parameter | 0.9 / 0.95 / 1 ✓ | no | — | ✓ |
| S | coverage_quote_choice | method | highest / average / latest ✓ | no (one ledger) | — | ✓ |
| S | coverage_accrual_convention | method | from quote date / from good-through inclusive / after good-through ✓ | no | — | narrow: tier 1 reads a different field (O-11) |
| S | coverage_cushion | parameter | 5 / 3 / 0 ✓ | no | — | ✓ |
| S | loyalty_credit_tier | parameter | 60 / 30 / 0 ✓ | **yes** (purchase + finance) | finance | ✓ |
| S | protection_credit_tier | parameter | 50 / 25 / 0 ✓ | no | warranty | ✓ |
| L | payoff_channel_window | method | +3 / +1 / +0 days ✓ | yes (quote amount + send weekday) | — | **✗ — F-5** |
| L | kestrel_backlog_absorption | method | cutoff pickup / pickup+2 / business-day deadline ✓ | no | — | narrow: tier 3 uses a business-day calendar (O-11) |
| L | quote_refresh_relief | parameter | 2 / 1 / 0 ✓ | no | — | ✓ |
| L | program_per_diem | parameter | 0 / 0.5 / 1 ✓ | no | purchase | ✓ |
| T | tow_trip_pattern | method | 2× / 0× / 1× one-way ✓ | **yes** (delivery + agreement pickup date) | — | **✗ — F-2** |
| T | tow_included_by_method | parameter | 60 / 40 / 25 ✓ | no | — | ✓ |
| T | tow_weekend_hook | parameter | 75 / 50 / 0 ✓ | no | — | ✓ |
| T | tow_distance_rate | parameter | 1.50 / 1.75 / 2.00 ✓ | no | — | ✓ |
| T | tow_carry_share | parameter | 0.8 / 0.9 / 1 ✓ | **yes** (finance + warranty) | finance | ✓ |
| C | chargeback_clock_anchor | method | payoff date / customer-payment date / pickup ✓ | tier 1 single-condition → no | — | ✓ |
| C | staged_percentage | parameter | 40 / 70 / grade 100 ✓ | no | — | ✓ |
| C | lien_outlay_basis | method | payoff − payments / min(payoff, credited) / credited ✓ | **yes** (payoff entries + payment entries) | — | ✓ |
| C | title_collateral | parameter | 0.9 / 0.95 / 1 ✓ | lienholder + status of one title order → no | title | ✓ |
| C | finance_standing | parameter | 0.85 / 0.95 / 1 ✓ | **yes** (contract flag + finance ledger) | finance | ✓ |
| I | installment_count_by_size | parameter | 3 / 2 / 1 ✓ | no | — | ✓ |
| I | late_towing_deferral | method | basis − 1×tow / − ½×tow / − 0×tow ✓ | no | — | **✗ — F-3** |
| I | repeat_buyer | parameter | 0.8 / 0.9 / 1 ✓ | no | purchase | ✓ |
| I | finance_tier_installment | parameter | 0.85 / 0.92 / 1 ✓ | no | finance | ✓ |

Counts per policy (declared → surviving the label test): M 6 (5 param, 1 method) → 6/1 ✓; R 6 (4 param, 2 method) → ✓; S 5 (3 param, 2 method) → ✓; L 4 (2 param, 2 method) → 1 honest method (backlog, narrowly) ✓ count, but F-5 mislabel; T 5 (4 param, 1 method) → **0 honest method** (F-2); C 5 (3 param, 2 method) → ✓; I 4 (3 param, 1 method) → **0 honest method** (F-3).

Other structural checks, all policies:
- `decides` is an input binding, never `result`; binding sets of one policy's factors are pairwise disjoint.
- Every fall-through tier equals that factor's `baseline`, and every factor `baseline` is what the policy's `baseline.rule` states for that input (M: grade tolerance, threshold rule, no credit, shares 1; R: quote amount, equity, shares 1; S: latest quote, days after good-through, no cushion/credits; L: window through send date, deadline-based absorption, no relief, share 1; T: one-way miles, 25 included, no surcharge, $2.00, share 1; C: pickup anchor, grade %, value credited, shares 1; I: one installment, whole shortfall, shares 1). `baseline.params` keys match.
- Each `baseline.rule` is a complete standard method whose sentences are in the `rule` verbatim.
- Every tier (condition and value/method) is stated in the `rule` prose; no tier only in compute.
- Realism (conditions that line of business weighs; outcomes it would publish): wait-dependent mileage tolerance, Kestrel's own odometer record, delivery-delay credit, tapered tow rates, weekend hook surcharge, staged chargeback percentage, capped per-diem accrual, term/tier/GAP-dependent negative-equity absorption, installment counts by size — all recognisable practice. Marketing-style incentives (program shares, loyalty/protection credits, tow carry share, autopay standing shares, repeat-buyer share) are unusual in their placement but not demonstrably unpublishable → observation O-12. Two outcomes are doubtful as customer treatment: S's top tier collects the shortfall on a superseded higher quote, and S's tier-1 accrual charges per diem from the quote date (days the quote amount already covers) → observation O-12 (no demonstration that no business would publish them).
- No tier condition holds of every customer who reaches the write, by charter. Structural note: I's `late_towing_deferral` and L's `kestrel_backlog_absorption` are tiered on the posting date of the latest towing/value deduction, and when T or M is a live prerequisite that posting date is the prerequisite write itself, made today; the tier is then fixed by `frozen_time − pickup_date` → observation O-13 (examined per task under "stamp/universal condition").

### findings

- **F-1 — SOURCE-POLICY RED (prerequisite sentence broader than its condition).** Symptom: S→R's sentence blocks S for every KAF-financed purchase. Root cause: the `policy_source` omits the condition's "and the grade allows roll-in". Evidence: S `prerequisite[1].policy_source` "Where the purchase the trade is applied to is financed through Kestrel Auto Finance, the shortfall payment is fixed only after the agreement's ledger carries the entry for the negative equity rolled into that financing." vs `condition` "…whenever that purchase is paid through Kestrel Auto Finance and the grade allows roll-in"; R `rule` "Where the purchase order a trade is applied to is paid through a Kestrel Auto Finance contract and the grade allows roll-in, …"; base variant Inoperable Condition Offer `negative_equity_roll_in_allowed: false`. Demonstrated consequence (same situation, two conclusions): Inoperable-grade trade, KAF-financed purchase, payoff above equity — by S's sentence the shortfall payment can never be fixed (no rolled-into-financing entry can ever exist, since R does not apply), so S and therefore L are blocked indefinitely; by the condition the gate is vacuous and S is payable now. Affected: `tradein.extended.yaml` → S `prerequisite[1]` / S rule. Bears on: task 0 (edge in its tree); its world's consequence is assessed in `0.md`.
- **F-2 — SOURCE-FACTOR RED (mislabelled method; T has no honest method factor).** `tow_trip_pattern` tiers are `tow_miles_counted = k × tow_one_way_miles` with k ∈ {2, 0, 1} (compute: `2 * tow_one_way_miles if … else (0 if … else tow_one_way_miles)`): one formula, a number substituted. T's other four factors are `parameter`. Affected: T `factors[0]`. Bears on: task 1.
- **F-3 — SOURCE-FACTOR RED (mislabelled method; I has no honest method factor).** `late_towing_deferral` tiers are `installment_basis = MX(0, shortfall_owed − k × towing_fee_total)` with k ∈ {1, ½ (rounded to the cent), 0} (compute line `installment_basis`; the fall-through omits `MX` but `shortfall_owed ≥ 0`). One formula, a number substituted. I's other three factors are `parameter`. Affected: I `factors[1]`. Bears on: task 1.
- **F-4 — rule/compute divergence (S tier-1 accrual count).** Rule "for each calendar day from its quote date through the day of payment" vs compute `DAYS(cover_quote_date, NOW)`; the neighbouring tier states the inclusive count explicitly ("both days counted") and computes `+1`. Red only in a world on tier 1 (latest quote good ≤ 2 days). Bears on: task 0 (assessed there).
- **F-5 — SOURCE-FACTOR RED (mislabelled method).** `payoff_channel_window` tiers are `per_diem_window_days = MX(0, days_from_good_through_to_send + t)` with t ∈ {3, 1, 0} (compute line `per_diem_window_days`): a fixed day offset substituted into one formula. L keeps one method factor (`kestrel_backlog_absorption`, narrowly — O-11), so the count bound survives; the mislabel itself is the defect. Affected: L `factors[0]`. Bears on: task 0.
- Observations (no demonstrated second answer at charter level): O-1 R's unnamed base clause "signed with the shortfall included in the amount financed"; O-2 T's undeclared (inapplicable) title_receipt timing; O-3 post-pickup deductions fall outside the reacceptance measure; O-4 weekend send date not covered by L's channel ladder; O-5 C counts autopay postings across all finance ledgers; O-6 L→S `gate` names a field; O-7 S's figure vs L's gate condition (per task); O-8 base cross-problem sentence in `tradein_lien_payoff`; O-9 R's equity fall-through vs M with no edge (per task); O-10 baseline-then-refinement shape of every rule; O-11 narrowly-method factors (R accrual cap, S accrual anchor, L backlog cutoff); O-12 incentive-style and doubtful tiers; O-13 tiers fixed by today's prerequisite posting.

## closing_checklist

Written 2026-10-06 after both tasks' derivations were frozen and revealed. **The difficulty does not pass the source-layer audit**; the checklist records the state of each item.

- Per-task files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; round 1, no earlier revision exists. Comparison sections: task 0 — SOURCE-POLICY RED, SOURCE-CHAIN RED (minor), SOURCE-FACTOR RED, SOURCE-TASK RED; task 1 — SOURCE-FACTOR RED. Not all PASS.
- Coverage and scopes: task 0 claims {M, R, S, L}, task 1 claims {T, C, I} (`charter_scope` of each, compared after reveal) — pairwise disjoint, jointly all seven extended policies; task tools and GT closed (each task's gold writes are exactly its scope's tools); every uuid8 independently generated and unreused (§ action_binding_and_uuids). ✓
- Trees: task 0 — 3 prerequisite problems, 3 value_input edges (≥2), customer write S, acyclic; task 1 — 2 prerequisite problems, 2 value_input edges (≥1), customer write I, acyclic; the difficulty's combined graph is a DAG with no cross-task edge. ✓ (task 0's closure carries one false figure, F-T0-4.)
- Factors: every computation declares a self-sufficient baseline and 4–6 factors, every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome; per task ≥1 multi-source and ≥1 cross-difficulty factor ✓. Failing: T and I have no honest `method` factor (F-2, F-3 → task 1); L's `payoff_channel_window` is mislabelled (F-5 → task 0); R's `signing_value_figure` does not bear weight on R's handling-time world in a valid order (F-T0-2 → task 0).
- Policy self-consistency: F-1 (S→R prerequisite sentence broader than its condition) charter-global RED; F-4 (S tier-1 accrual count) realised in task 0.
- Instantiation-stage gates on the final form: the snapshot supplied with the brief (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred) is the run on the audited form — the charter and tool hashes are unchanged from those in the brief. No artifact was changed by this audit, so no re-run was needed or performed by the auditor.

## revision_2

### charter_global_frozen (revision 2)
- Re-audit round 2, 2026-10-06, same auditor. Hashes: `tradein.extended.yaml` = `736a99d13c8159cdcb8b1ec334b136fd3d23fb30e6b02f4cda87c0ea4134017e` (**changed** from `dcbad53e…`); `task_tools.py` = `9328a0fd…` (unchanged). Views re-verified with `sha256sum -c` (task_0 `dfbc5e6c…`, task_1 `28d88035…` OK). Gate snapshot supplied with the brief: all seven gates OK, traceability deferred.
- Because the charter changed, every charter-global section was re-derived from the new file. Because the tool module did not change, § action_binding_and_uuids is carried forward by reference on the hash `9328a0fd…`.
- Written before any round-2 task GT was opened. The round-1 text above is left untouched.
- Base copy: still verbatim (`diff` over the base length is empty).

### What changed in the charter (verified against the file, not the claims)
- S: prerequisite sentence and rule now read "Where the purchase the trade is applied to is financed through Kestrel Auto Finance **and the grade allows roll-in**, the shortfall payment is fixed only after…"; tier-1 accrual now reads "for each calendar day **after** its quote date through the day of payment" (rule, `compute_basis` and ladder).
- R: a third `overwrite` names the base clause "when the grade allows roll-in and the finance contract is signed with the shortfall included in the amount financed," and the rule gains "A Kestrel Auto Finance contract signed before the pickup inspection cannot show the shortfall the inspection settles, so the roll-in is recorded without waiting for the contract to itemise it." The superseded span also contains "when the grade allows roll-in", which R's rule keeps stating, so the merged reading is unchanged on that point (observation R2-O1).
- L: `payoff_channel_window` is relabelled `parameter` and now decides a new binding, `check_transit_days_added` (3 / 1 / 0); `per_diem_window_days = MX(0, days_from_good_through_to_send + check_transit_days_added)`. The weekday wording is now "any other day of the week" in the rule, the overwrite and the ladder (closes O-4).
- T: a second `overwrite` releases towing from the title-delay waiting sentence, restated in the rule (closes O-2). `tow_trip_pattern` now decides `towing_charge`, with three functional forms: max(towing fee, rate × max(0, 2 × one-way − included)) for a trip of its own / towing fee alone when the tow rode with the delivery / towing fee + rate × max(0, one-way − included), which is also the fall-through and baseline. The result is now (towing_charge + hook) × share.
- C: the autopay count is now filtered by `finance_contract_id = CFIELD('finance','finance_contract_id', purchase_order_id=…)`, matching "posted on it" (closes O-5).
- I: `late_towing_deferral` is replaced by `towing_installment_placement` (method), which decides `todays_installment_figure`. Tier 1 (lag > 30): max(0, s − t) / n. Tier 2 (lag ≤ 7): max(0, s − t) / n + min(t, s). Fall-through (8–30, or no towing): s / n, which is also the baseline. The result is today's figure × the repeat-buyer and tier shares.
- M and the C formula are unchanged (compute lists re-read line by line).

### Re-derived sections (results only, rest as round 1)
- policy_conflict_scan: unchanged except O-1 (now declared) and O-2 (now declared). No new overlap.
- rule_compute_equivalence: a script checked every `compute_basis` quotation, every `overwrite.replaced_by` and every `baseline.rule`, and found each verbatim in its policy's rule; every new binding is implemented as quoted. F-4 is closed: the "after its quote date" wording now matches `DAYS(cover_quote_date, NOW)`. O-4 and O-5 are closed. The `RND` half-cent observation still stands.
- action_binding_and_uuids: carried forward (tool hash unchanged). The `(target_tool, computes)` pairs are unchanged.
- prerequisite_graph: same six edges, same kinds and forms, all `policy_source` verbatim in their own rules (script-checked); acyclic.
- prerequisite_sentences: **F-1 closed.** The S→R sentence now carries "and the grade allows roll-in", which equals its condition. The other five edges are unchanged and still pass.
- override_declarations: the new R overwrite and T overwrite are declared. No undeclared override found.
- factor_ladders: counts are unchanged (M 6/1 method, R 6/2, S 5/2, L 4/1, T 5/1, C 5/2, I 4/1).
  - **F-5 closed.** The label is now `parameter`, matching the +3/+1/0 day offsets. L keeps `kestrel_backlog_absorption` as its method; it remains a narrow method (O-11).
  - **F-2 closed.** The `tow_trip_pattern` tiers now differ in form (a maximum against a floor, a flat fee, a fee plus mileage), not in one substituted number. Minimum-or-mileage pricing for a separate trip is ordinary towing practice.
  - **F-3 closed.** The tiers of `towing_installment_placement` place the towing fee in the last installment, in today's installment, or not at all (even split). These are three different allocation structures. They can be written as a two-coefficient family, but they are not one scalar substituted into one formula, so the label passes; this is noted as a narrow method under O-11.
  - Each new fall-through equals its `baseline`, and every tier is stated in the rule.
  - Structural note O-13 still stands: with T a live prerequisite, the towing entry is posted today, so the lag is frozen_time − pickup.
- New charter-global defects: none found.

### closing_checklist (revision 2)
Written 2026-10-06 after both round-2 derivations were frozen and revealed.
- Per-task files `0.md` and `1.md` each carry an appended `## revision_2` (frozen derivation, then comparison). The round-1 text is untouched. Both revision-2 comparisons are **PASS**.
- Every round-1 red light was verified closed against the artifacts:

  | Item | Status | Evidence |
  |---|---|---|
  | F-1 | closed | sentence = condition |
  | F-2 / F-T1-1 | closed | `tow_trip_pattern` tiers are distinct functional forms |
  | F-3 / F-T1-2 | closed | `towing_installment_placement` |
  | F-4 / F-T0-1 | closed | wording "after its quote date" |
  | F-5 / F-T0-3 | closed | relabelled `parameter` |
  | F-T0-2 | closed | seeded missing-key deduction |
  | F-T0-4 | closed | closure figure 10,622.99 |

- Observations acted on: O-1, O-2, O-4 and O-5 are closed. Still open as observations: O-3, O-6–O-13, the `RND` half-cent convention (sensitivity 144.58 vs 144.59), R2-O1 (R's superseded span includes the grade clause the rule keeps) and R2-T1-O1.
- Coverage and scope: {M, R, S, L} and {T, C, I} are disjoint and together cover the charter.
  - Tools and GT are closed.
  - uuid8s are unchanged and independent.
- Problem trees: 3 and 2 prerequisite problems, with 3 and 2 value_input edges.
  - Each tree has a customer write (S and I).
  - The combined graph is a DAG.
- Factors: every computation has 4–6 factors with ≥2 `parameter` and ≥1 honest `method`. Each task has a multi-source and a cross-difficulty factor. Every factor bears weight against an honest baseline, and every whole baseline ≠ gold.
- Gates: the orchestrator's re-run on the final form gave all seven gates OK (traceability deferred). This audit changed no artifact.
- **The difficulty passes the source-layer audit in revision 2.**
