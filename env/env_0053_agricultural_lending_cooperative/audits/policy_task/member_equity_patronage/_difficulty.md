# Policy-task audit — member_equity_patronage / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11T08:11Z. Auditor: independent policy-task auditor (not the instantiating agent), revision 1.
- Inputs and hashes (re-checked with sha256sum, all matching the coordinator's HASHES.txt):
  - `tasks/member_equity_patronage/equity.extended.yaml` sha256=2d13c1e82288b40d08c58488f9e221c61be4b3a6db456d0f534a652bc2c60607
  - `tasks/member_equity_patronage/task_tools.py` sha256=239ab061bb0d11393e7ce25b6d5c3c60186dea1b8cf11178a6e35660862dc5b0
  - masked views `.audit_views/policy_task/member_equity_patronage/0.view.json` sha256=46a4f8e1…1cb843, `1.view.json` sha256=1831a9c0…53414c
- Also read: `blueprint/blueprint.yaml`, `blueprint/products/equity.yaml` (and the other products only as cross-category charters for the compute sandbox), `blueprint/db_schema.json`, `blueprint/share_tools.py`, and the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: SUM/COUNT/LATEST scoped to the target holding; `within_months=N` means `0 <= MONTHS(date, today) < N`; `MONTHS` counts whole calendar months).
- Permitted: the charter, the tool module, the schema, the share tools, and each task's `frozen_time`, `user_scenario`, `initial_state` (from the masked views only).
- Masked and not read before every task's derivation was frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, `worklog.md`, and other difficulties' audits. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred because KB docs are not published yet). The masked views and their hashes came with it too. The entry conditions are complete. The deferred traceability gate is outside this skill's scope.
- Base copy: the first 1046 lines of the extended charter are byte-identical to `blueprint/products/equity.yaml` (`diff` gave no output). The base copy is verbatim.

### policy_conflict_scan

The charter has seven extended policies, all on the Class H Preferred Stock holding:

| id | target_tool (owner) | computes | subject | prerequisite |
|---|---|---|---|---|
| A `equity_ext_preferred_dividend_reinvestment` | book_preferred_dividend_reinvestment_5d71129c (agent) | amount | equity_dividend_reinvested | D |
| B `equity_ext_preferred_redemption_payment` | pay_preferred_redemption_7befd982 (agent) | amount | equity_retirement_deferred | A |
| C `equity_ext_preferred_redemption_request` | submit_preferred_redemption_request_9710f0b7 (user) | requested_amount | equity_retirement_request | B |
| D `equity_ext_preferred_holding_excess_refund` | refund_preferred_holding_excess_154bc05b (agent) | amount | equity_purchase | [] |
| E `equity_ext_preferred_quarter_limit_refund` | refund_preferred_quarter_excess_3d5c0453 (agent) | amount | equity_purchase | [] |
| F `equity_ext_preferred_dividend_reversal` | reverse_preferred_dividend_68f89242 (agent) | amount | equity_dividend_reinvested | E |
| G `equity_ext_preferred_purchase_room` | submit_preferred_purchase_895be76e (user) | amount | equity_purchase | E, F |

Where subjects overlap:
- **A and F (equity_dividend_reinvested).** A books a quarter's reinvested dividend. F books a partial cancellation of a dividend already booked. Their triggers are disjoint: A acts only when no reinvested entry exists for the declared payment date ("a holding already carrying a reinvested dividend entry for the declared payment date has nothing further booked"). F acts only on a dividend "figured on shares later cancelled as above a quarter's purchase allowance". No conflict.
- **D, E and G (equity_purchase).** Each handles a different quantity: D the holding-ceiling excess, E the quarter-limit excess, G the size of a new purchase. Two overlaps of meaning are not conflicts in any task world, so they are recorded as observations O-G1 and O-G2 below:
  - O-G1: the holding maximum is restated twice, as D's "holding ceiling" (max_holding_usd plus four tolerances) and G's "holding room" (max_holding_usd less present shares, cushion and reserve).
  - O-G2: the quarter limit is restated twice, as E's "quarter's purchase allowance" (with tolerances; reinvested dividends "use the quarter's room as purchases do") and G's "quarter room" (preferred_max_purchase_per_quarter_usd less the latest purchase inside the quarter; the reinvested dividend in the quarter does not count).
- **B and C (redemption).** B pays an approved request. C registers a new one, and its own rule blocks registration while an approved, run-notice redemption remains unpaid. The two overwrite different base sentences. B's whole-holding test still uses min_balance_after_partial_usd, and C replaces that minimum only for sizing a new request (O-G3).
- **Cross-category reads.** All are read-only: CFIELD on farmland (status/principal_balance/next_due_date/installment_amount), operating (status/commitment_amount/outstanding_principal) and equipment (status/next_due_date/installment_amount). None writes to another category.
- **Terminal states.** Every write leaves the holding active, except C (retirement_requested) and B (active, or retired when the balance reaches zero). They do not collide.
- **Scope partition.** Derived from the charter's prerequisite graph alone, it has two connected components: {E, F, G} with root G, and {D, A, B, C} with root C. Together they cover all seven extended policies with no overlap. Each task's own scope claim is compared at reveal in its file.
- **Event-type scope (observation O-G4).** B's `subject: [equity_retirement_deferred]` is not in the blueprint claim's event_types for this difficulty (the claim lists equity_retirement but not equity_retirement_deferred). The write B performs books an equity_retirement row, which is claimed, and check_cross_fire reported SCOPE OK. No consequence was shown.

Conclusion: no conflict on any overlapping subject reaches different conclusions in the same situation.

### rule_compute_equivalence

I swept each policy sentence by sentence, rule to compute and compute back to rule. All seven: every `compute_basis` quotation is verbatim in its own `rule`; every factor's ladder tiers are rule sentences and branches of the `decides` binding; no compute branch lacks a rule sentence.

| policy | quantity / window / tier / rounding: rule text → compute | result |
|---|---|---|
| A | share basis: purchases+reinvested−retirements → `div_end_shares`. The four-way latest-purchase/latest-retirement adjustment, with days counted from the quarter's first day inclusive to the date exclusive → `div_basis` with `DAYS(start, date)`. Bracket on the adjusted basis → `div_bracket_rate(div_basis)`. Loyalty by whole months since issue and reinvested count → `div_loyalty`. Relationship by active farm principal → `div_relationship`. The rate sum is added before it is applied → `div_rate`. Basis × rate /100 × days/365, rounded once → `result` | equivalent |
| B | start-of-quarter shares → `rp_start_shares`; the base ladder → `rp_base`; tenure, reinvest, size, installment (farm first, then equipment) and delay (`> delay_extended_days`, then `> retirement_processing_days`) → the matching bindings; allowance → `RND(base*(pct+ten+rein−size)/100 + inst + delay)`; the lesser of named amount and allowance → `MN`; the whole holding when the remainder is below min_balance_after_partial_usd → `result` | equivalent (O-G5 on the allowance sentence's grammar) |
| C | present shares; purchase window 6/9/12 by months held; dividend window 0/3/6 by reinvested count; start-of-quarter shares; keep = max(min, pct × start); the combination ladder on "reinvested dividend in last overlap_months"; pacing on redemption-reason retirements within 3 and 12 months; `MX(0,…)` to the cent | equivalent |
| D | counted-shares ladder; four tolerances; ceiling = max + sum; `MX(0, counted − ceiling)` | equivalent |
| E | counted = latest purchase (+ the reinvested dividend on review_quarter_dividend_date if no retirement in the quarter; − the latest retirement if it is in the quarter); relationship tolerance on (farm ≥ threshold) AND/OR an active operating line; reinvest and tenure tolerances | equivalent |
| F | dividend = latest reinvested; cancelled = latest subscription_cancelled; end shares = present − dividend + cancelled; fraction (days from the cancellation to quarter end, both counted, /91; or 0; or 1); three waivers; the final rounding | equivalent |
| G | quarter room; holding room; size quarters; loyalty quarters; estimate ladder (the reversal entry is the `payment_method='none'` cancellation); operating reserve by drawn ratio; the whole-increment cut-down and the min_purchase test | equivalent |

Observations (no second scored answer could be shown):
- **O-G5, grammar of B's allowance sentence.** The sentence reads "the redemption allowance base times allowance_pct plus the redemption tenure points plus the redemption reinvestment points less the redemption size reduction, divided by 100". Parsed as strict arithmetic English it gives (base×pct + points)/100, which adds a few cents of "points". Parsed as percentage points added to allowance_pct, it gives base×(pct+points)/100, which is what compute does. The ladder sentences call them "points" taken off or earned against a percentage. A's analogous sentence spells out "all in percentage points, summed into one annual rate", but B's does not. The strict reading is dimensionally incoherent (a 10-point tenure bonus worth $0.10), so I do not count it as a defensible second reading. The figure is in task 1's file.
- **O-G6, guards not in compute.** The rules' "nothing further is booked/cancelled/reversed/paid" guard sentences are trigger conditions that compute does not encode. A's compute returns a positive number on a holding that already carries the declared payment date's reinvested entry (7,996.90 on task 0's opening world). F's compute does not tell a holding-ceiling cancellation from a quarter-limit cancellation, because the two refund tools write identical rows (subscription_cancelled, paid by the holding's method), so it returns 49.44 on task 1's terminal world. In both cases the rule text alone excludes the write. The per-task files confirm that neither appears in the derived solution.
- **O-G7, rounding.** The `RND` implementation is Python `round` (banker's rounding on floats), while the rules say "rounded half up". I re-did every scored value of both tasks with Decimal ROUND_HALF_UP and they agree, so there is no divergence in these worlds.

### action_binding_and_uuids

- Each of the seven `(target_tool, computes)` pairs is claimed by exactly one policy. Seven policies map to seven distinct tools.
- The tool bodies (task_tools.py lines 11–270) only `find`, `create`, `update` and return a receipt. None refuses, errors or hints on any business condition. The module docstring says so explicitly ("It checks no business condition").
- **Docstrings.** None names another tool, a policy id, or a position in a sequence. The ordering-like words present are "Afterwards" (the visible effect of the same call) and "rounded … before it is passed" (argument formatting). Neither states a sequence among actions (observation O-G8).
- **Identical effects of the two refund tools.** `refund_preferred_quarter_excess_3d5c0453` and `refund_preferred_holding_excess_154bc05b` have identical effects (both go through `_Preferred.cancellation(..., paid=True)`) and differ only in the docstring and the make_id tag. The business reading of each is single, because the docstrings name "a calendar quarter's purchase limit" and "the largest balance a member may hold" respectively. See O-G6 for what the identical rows mean downstream.
- **uuid8s.** 5d71129c, 7befd982, 9710f0b7, 154bc05b, 3d5c0453, 68f89242, 895be76e. No two share a prefix or suffix, none is sequential or adjacent, and none looks batch-derived. PASS.

### prerequisite_graph

Edges: A→D, B→A, C→B, F→E, G→E, G→F. D and E have `prerequisite: []`.

- `prerequisite` is filled in on all seven policies. Every `problem` points at an extended policy id in this file, never at a base policy or at the policy itself. The graph is acyclic: topological orders are D, A, B, C and E, F, G.
- `policy_source` was found verbatim (after whitespace normalisation) in the blocked policy's own `rule` for all six edges, and in none of the depended-on rules (scripted check).
- All six edges have `form: state` and no `fallback_reason`, which is consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all six.
- All six edges have `kind: value_input`. Every `gate` (`div_basis`, `rp_base`, `rq_shares`, `dr_cancelled`, `pr_shares`, `pr_estimate`) is a binding in the blocked policy's compute.
- Each `effect` sentence describes what the depended-on write changes in that compute. I checked them numerically on the task worlds in the per-task files.
- None of the prerequisite text uses an authoring viewpoint ("in this task", "at the opening" and similar: none found).

PASS.

### prerequisite_sentences

Four-point test per edge:

| edge | sentence (verbatim, own rule) | connective | waited-on state (record-visible) | tool/id/snake_case | single resolving write |
|---|---|---|---|---|---|
| A→D | "The quarterly preferred dividend is fixed only after the holding carries a cancellation entry for every share it held above the largest balance a member may hold." | only after | a cancellation entry on the holding | none | D's write: the only rule that cancels shares "above the holding ceiling" (the max-holding quantity); E cancels against a quarter allowance, F reverses dividend shares |
| B→A | "The amount paid on an approved redemption is fixed only after the holding carries the reinvested dividend for every quarter whose dividend payment date has passed." | only after | reinvested dividend entries on the holding | none | A's write: the only tool that creates equity_dividend_reinvested rows |
| C→B | "A new preferred redemption request is not registered until no approved redemption on the holding whose notice period has run remains unpaid." | not … until | approved request + redemption retirement entry + holding status | none | B's write: the only one creating a redemption-reason retirement and clearing the pending request date |
| F→E | "The reversal on a reinvested dividend is worked out only after the holding carries the cancellation entry for every purchase share above its quarter's purchase allowance." | only after | a cancellation entry | none | E's write ("quarter's purchase allowance" is E's own term) |
| G→E | "The purchase room is fixed only after the holding carries the cancellation entry for every share that a purchase took above its quarter's purchase allowance." | only after | a cancellation entry | none | E's write |
| G→F | "Before the purchase room is worked out, every reinvested dividend earned by cancelled shares must stand reversed on the holding." | before | the dividend stands reversed | none | F's write: the only "reversed" dividend booking |

Derivations (sentence + records + the depended-on rule → resolving action):
- A→D: "a cancellation entry for every share above the largest balance a member may hold" plus D's rule "When a purchase has been accepted that takes a … holding above the holding ceiling, the shares above it are cancelled as of the date of that purchase" gives D's refund for D's computed excess.
- B→A: "the reinvested dividend for every quarter whose payment date has passed" plus A's "the board's current declaration covers the quarter from declared_quarter_start to declared_quarter_end … paid on declared_quarter_payment_date" gives A's booking for the declared quarter.
- C→B: "no approved redemption whose notice period has run remains unpaid" plus B's "An approved … redemption whose notice period has run is paid …" gives B's payment.
- F→E and G→E: "cancellation entry for every (purchase) share above its quarter's purchase allowance" plus E's "the part above it is cancelled as of that purchase's date" gives E's refund.
- G→F: "every reinvested dividend earned by cancelled shares must stand reversed" plus F's "the reinvested shares that the cancelled shares earned are cancelled in one entry" gives F's reversal.

No rule carries a second wording of its edge, and no depended-on rule restates the sentence. I scanned every rule for ordering words (before/after/until/first/prior). Apart from the six edge sentences, the hits are intra-policy ("after the unseasoned shares and the redemption minimum have been dealt with"), date facts ("figured before the cancelled shares were bought"), or "months before today". None states a cross-problem order, so there is no undeclared dependency.

Observations on wording strength (no second answer could be shown):
- **O-G9 (A→D).** "the largest balance a member may hold" is the parameter_schema gloss of max_holding_usd (1,000,000). D's overwrite replaces "may not take the holding above max_holding_usd" with a tolerance-raised "holding ceiling", and counts shares that may exclude reinvested dividends. Read literally against max_holding_usd, the sentence demands cancelling every share above 1,000,000, which no rule produces. Read through the declared overwrite, it is D's ceiling. The condition field repeats the same phrase, so sentence and condition agree. The per-task file for task 1 shows the literal reading yields no executable alternative (D's rule alone fixes the amount).
- **O-G10 (B→A).** The sentence says "every quarter whose dividend payment date has passed", while the condition says "every declared quarter whose payment date is on or before today". The charter declares exactly one quarter (2026-04-01..06-30, paid 2026-07-15). The sentence's scope is open in time, and a world whose seeded dividend history starts later than the holding's issue date leaves earlier quarters with no entry. The natural reading ("the reinvested dividend" that fell due) resolves to the declared quarter, and no rule gives an amount for any earlier quarter.
- **O-G11 (C→B).** After a partial payment the request row stays `approved` (the tool does not change request_status). "remains unpaid" is settled by B's own sentence "The part of an approved request above the quarter's redemption allowance is not paid; the holding returns to active status … and the member may ask again in writing". Single reading.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

**`equity_preferred_stock` (base refs of A, B, C, D, E, F, G):**
1. "Class H Preferred Stock is sold only to members in good standing who acknowledge the offering circular." Inherited by G and not weakened (observation O-G12: no DB field records an acknowledgement, and no extended rule says whether an existing holder re-acknowledges on a top-up purchase).
2. "A purchase must be at least min_purchase_usd in multiples of purchase_increment_usd, may not take the holding above max_holding_usd, and purchases in one calendar quarter may not exceed preferred_max_purchase_per_quarter_usd (equity_msr_quarter_preferred_purchases); shares are issued preferred_purchase_settlement_business_days business days after the funds clear."
   - "may not take the holding above max_holding_usd": overwritten by D (holding ceiling plus tolerances) and by G (holding room less cushion and reserve). Both are declared; the same clause is superseded twice with two different replacements (O-G1).
   - "purchases in one calendar quarter may not exceed …": overwritten by E (declared). E's `replaced_by` restates only the allowance, while the change in what is counted (the latest purchase ± the in-quarter dividend/retirement, against base's measure of the sum of purchase rows in the quarter) lives in E's rule. The counting clause is inside the named superseded clause, so the override is declared (observation O-G13).
   - "at least min_purchase_usd in multiples of purchase_increment_usd": overwritten by G (cut down to a whole multiple). The variant's `rounding_rule: up_to_increment` is glossed in parameter_schema as "How required purchases are rounded", which is about required borrower-stock purchases, so it does not compete with G's cut-down (observation O-G14).
   - "shares are issued … business days after the funds clear": not overwritten. The user tool books the purchase dated today. It does not touch a scored quantity and nothing downstream depends on it.
3. "Dividends are declared quarterly at dividend_rate_pct per year on the average daily shares held in the quarter and paid on the 15th day after quarter end, in cash or reinvested according to dividend_option." Overwritten by A (declared, whole sentence). F (overwrite []) reverses part of a dividend already booked. With the base sentence superseded by A, F operates on A's figure, so no base clause is handled undeclared.
4. "A redemption is requested in writing as a preferred_redemption request for an amount or the whole holding." C follows it ("A request for a named dollar amount is written for that amount … the whole holding is written as the whole holding").
5. "A redemption takes effect no earlier than redemption_notice_days … the last notice day itself qualifying." B follows it ("whose notice period has run"). C's gate follows it.
6. "It is paid at par, subject to board approval; a partial redemption must leave at least min_balance_after_partial_usd, and a redemption that would leave less is made for the whole holding."
   - "It is paid at par, subject to board approval": overwritten by B (declared). Board approval is kept through "approved".
   - "a partial redemption must leave at least min_balance_after_partial_usd": overwritten by C (declared) for request sizing. B's whole-holding test keeps min_balance_after_partial_usd for paying (O-G3, no conflict in any world here).
   - "made for the whole holding": kept in B's result.
7. "Preferred stock is not insured and is not a deposit." Not affected.

**`equity_estate_retirement` (B, C):** concerns deceased members' estates. Only "preferred stock is redeemed at par" bears on B, and B pays at par. Nothing is handled differently.

**`equity_agg_class_combination` (D, E, G):** "new amounts are booked to the existing holding". The tools book onto the existing H holding. Followed.

**`equity_stock_requirement` (D, E, G):** "anything paid is refunded within subscription_refund_days calendar days with retirement_reason subscription_cancelled". D and E refund with the same reason and window. Followed.

Disguised forms: anonymous intermediate factor, 0/1 multiplier and dropped branch were each looked for at every intermediate. None found (the whole-holding branch is kept in B, and the min_purchase branch is kept in G). No artifact calls base's output wrong.

Findings: none rises to SOURCE-POLICY RED. Every conflict with base is named in `overwrite`.

### factor_ladders

| policy | factor | label | decides | tiers (incl. fall-through) | multi-source | cross_difficulty | in rule + compute | label honest |
|---|---|---|---|---|---|---|---|---|
| A | dividend_share_basis | method | div_basis | 4 | tier1 is a conjunction (purchase AND retirement in quarter) but tiers 2–3 are single, so not multi-source | – | yes | yes (changes the basis algorithm) |
| A | dividend_bracket_rate | parameter | div_bracket_rate | 3 (4.5 / 4.375 / 4.25) | no | – | yes | yes |
| A | dividend_loyalty_premium | parameter | div_loyalty | 3 (0.10 / 0.05 / 0) | **yes** (issue date AND reinvested count; exactly one) | – | yes | yes |
| A | dividend_relationship_premium | parameter | div_relationship | 3 (0.15 / 0.05 / 0) | no | **farmland** | yes | yes |
| B | redemption_allowance_base | method | rp_base | 3 | no | – | yes | yes |
| B | redemption_tenure_points | parameter | rp_tenure | 3 (10/5/0) | no | – | yes | yes |
| B | redemption_reinvestment_points | parameter | rp_reinvest | 3 (10/5/0) | no | – | yes | yes |
| B | redemption_installment_addition | parameter | rp_installment | 3 (farm inst / equip inst / 0) | **yes** (tier 2: no farm installment in quarter AND equipment installment in quarter) | **farmland, equipment** | yes | yes |
| B | redemption_size_reduction | parameter | rp_size_reduction | 3 (5/2/0) | no | – | yes | yes |
| B | redemption_delay_addition | parameter | rp_delay_addition | 3 (20% / 10% / 0) | no | – | yes | yes |
| C | purchase_seasoning_period | parameter | rq_purchase_window | 3 (6/9/12) | no | – | yes | yes |
| C | dividend_seasoning_period | parameter | rq_dividend_window | 3 (0/3/6) | no | – | yes | yes |
| C | redemption_minimum | parameter | rq_keep_pct | 3 (15% / 10% / min) | no | – | yes | yes |
| C | unseasoned_and_minimum_combination | method | rq_redeemable | 3 | **yes** (recent reinvested entry AND unseasoned vs minimum) | – | yes | yes |
| C | redemption_pacing_reserve | parameter | rq_pace_pct | 3 (10/5/0) | no | – | yes | yes |
| D | ceiling_counted_shares | method | hx_counted | 3 | **yes** (recent reinvested entry AND count ≥ 8) | – | yes | yes |
| D | ceiling_relationship_tolerance | parameter | hx_tol_relationship | 3 | no | **farmland** | yes | yes |
| D | ceiling_tenure_tolerance | parameter | hx_tol_tenure | 3 | no | – | yes | yes |
| D | ceiling_size_tolerance | parameter | hx_tol_size | 3 | no | – | yes | yes |
| D | ceiling_operating_tolerance | parameter | hx_tol_operating | 3 | no | **operating** | yes | yes |
| E | quarter_counted_amount | method | ql_counted | 3 | tier1 is a conjunction, tier2 single | – | yes | yes |
| E | quarter_relationship_tolerance | parameter | ql_tol_relationship | 3 | **yes** (farm loan ≥ threshold AND an active operating line; exactly one) | **farmland, operating** | yes | yes |
| E | quarter_reinvestment_tolerance | parameter | ql_tol_reinvest | 3 | no | – | yes | yes |
| E | quarter_tenure_tolerance | parameter | ql_tol_tenure | 3 | no | – | yes | yes |
| F | reversal_holding_period | method | dr_fraction | 3 | no | – | yes | yes (a days-based fraction, or 0, or 1) |
| F | reversal_farm_waiver | parameter | dr_waive_farm | 3 | no | **farmland** | yes | yes |
| F | reversal_tenure_waiver | parameter | dr_waive_tenure | 3 | no | – | yes | yes |
| F | reversal_reinvestment_waiver | parameter | dr_waive_reinvest | 3 | no | – | yes | yes |
| G | cushion_size_quarters | parameter | pr_size_quarters | 3 (6/3/0) | no | – | yes | yes |
| G | cushion_loyalty_quarters | parameter | pr_loyal_quarters | 3 (2/1/0) | **yes** (recent dividend AND issue date; exactly one) | – | yes | yes |
| G | cushion_dividend_estimate | method | pr_estimate | 3 | tier1 conjunction, tier2 single | – | yes | yes |
| G | operating_reserve | parameter | pr_reserve_pct | 3 (10% / 5% / 0) | no | **operating** | yes | yes |

Counts per policy (bounds: 4–6 factors, ≥2 parameter, ≥1 method):

| policy | factors | parameter | method | result |
|---|---|---|---|---|
| A | 4 | 3 | 1 | ok |
| B | 6 | 5 | 1 | ok |
| C | 5 | 4 | 1 | ok |
| D | 5 | 4 | 1 | ok |
| E | 4 | 3 | 1 | ok |
| F | 4 | 3 | 1 | ok |
| G | 4 | 3 | 1 | ok |

- **Per tree.** {E, F, G} has a multi-source factor (E relationship, G loyalty) and cross-difficulty factors (farmland, operating). {D, A, B, C} has multi-source factors (A loyalty, B installment, C combination, D counted) and cross-difficulty factors (farmland, operating, equipment).
- **Bindings and tiers.** Within each policy the bindings are disjoint across factors, and every `decides` is an input rather than `result`. All ladders have three or four pairwise-disjoint tiers, each stated in the rule with its condition and value or method. No two tiers of one ladder select the same value or method. Every fall-through equals the policy baseline: for the "premium/points/tolerance/waiver/reserve/addition/pacing" factors the zero fall-through is implicit in a baseline that omits them; C's redemption_minimum fall-through is min_balance_after_partial_usd, matching "The redemption minimum is min_balance_after_partial_usd".
- **Baselines.** Each `baseline.rule` is a complete standard method whose sentences are all in its rule, and its `params` name the defaults it uses.
- **Observation O-G15.** G's cushion_dividend_estimate has no counterpart in G's baseline rule (the baseline holding room has no cushion at all), so its fall-through "the latest reinvested dividend" is not something the baseline states. The factor bears weight only while the size and loyalty quarters are non-zero. Its declared baseline is its own fall-through, not a straw man.
- **Business realism.** These are judgement calls; none could be shown to be a treatment no such business would publish, so all are observations (O-G16):
  - Tiered dividend rates and relationship/loyalty premiums within one preferred class (A).
  - A "delay addition" that enlarges a board's quarterly redemption allowance by 10–20% of the named amount (B).
  - An operating reserve justified "so that … an operating paydown fit[s] under the maximum" (G). The stated rationale is incoherent (an operating paydown adds no preferred shares), but the treatment itself, limiting a stock purchase for a member whose operating line is heavily drawn, is a plausible credit-prudence rule.
  - Each tier condition divides customers. No condition holds of everyone who reaches the write: for example, "a reinvested dividend within the last 3 months" separates reinvest-option holders from cash-option ones.

### findings

No charter-global RED. Observations O-G1 to O-G16 above bear on both tasks as indicated. The demonstrations relevant to a task are in that task's file:
- O-G1, O-G2, O-G12, O-G14: task 0.
- O-G3, O-G5, O-G9, O-G10, O-G11: task 1.
- O-G6: both tasks.

## closing_checklist

Written after both reveals (2026-10-11T08:25Z). It is kept below the pre-reveal charter-global section, which was not edited after any reveal.

**Status: NOT CLOSED.** Task 1 carries two proof-text RED findings: T1-R1 (SOURCE-CHAIN) and T1-R2 (SOURCE-FACTOR). Both are false or unreproducible world assertions in `prerequisite_closure` and `design_rationale`. Neither changes the scored solution, which matches the independent derivation on every parameter. Task 0 passes all four relationships.

| item | state |
|---|---|
| Per-task files one-to-one with tasks | `0.md`, `1.md`, plus this file. Each comparison section carries a verdict: task 0 PASS on all four; task 1 PASS / RED (chain proof) / RED (factor proof) / PASS. |
| Old revisions traceable | revision 1, nothing earlier |
| Extended policies fully covered | 7/7 |
| Scopes pairwise disjoint | task 0 {quarter_limit_refund, dividend_reversal, purchase_room}; task 1 {holding_excess_refund, dividend_reinvestment, redemption_payment, redemption_request}; each spans its whole tree |
| Task tools closed | each tool is claimed by exactly one task |
| uuid8s independent | yes (§ action_binding_and_uuids) |
| Prerequisite problems per tree | task 0: 2, with 3 value_input edges (floor 1); task 1: 3, with 3 value_input edges (floor 2) |
| owner=user problem in each tree | yes: the purchase in task 0, the redemption request in task 1 |
| Acyclic | yes, per task and difficulty-wide. The two components share no node, so no cross-task cycle is possible. |
| Factors | every computation has 4–6 factors with ≥2 parameter and ≥1 method; each task has ≥1 multi-source and ≥1 cross-difficulty factor; every ladder has ≥3 tiers stated in its rule with distinct outcomes; every factor bears weight against an honest baseline; every all-baseline number is definite and differs from gold (task 0: 40,000 / 236.82 / 193,300; task 1: 105,900.83 / 11,638.53 / 274,600.21 / 179,006.67) |
| Gate re-run on the final form | I did not re-run it, following Step 0 (the coordinator runs the gates). The audited artifacts are byte-identical to the gate snapshot's inputs: equity.extended.yaml 2d13c1e8…c60607 and task_tools.py 239ab061…dc5b0, re-hashed at close. The coordinator's snapshot (all rc=0, traceability deferred) therefore applies to this form. Closing the difficulty still requires the coordinator to re-run the gates once the task 1 proof fields are corrected. |

The difficulty does not pass the source-layer audit until T1-R1 and T1-R2 are resolved. Per this skill, the auditor arranges no fix.

## revision_2

- Re-audit time: 2026-10-11T11:19Z. Same independent auditor. The round-1 text above is left untouched.
- **Charter-global sections carried forward by reference**, not re-derived. Grounds: both shared inputs are byte-identical to round 1.
  - equity.extended.yaml sha256=2d13c1e82288b40d08c58488f9e221c61be4b3a6db456d0f534a652bc2c60607
  - task_tools.py sha256=239ab061bb0d11393e7ce25b6d5c3c60186dea1b8cf11178a6e35660862dc5b0
  - Both were re-hashed by me at re-audit start.
  - The blueprint inputs read in round 1 (products/equity.yaml, share_tools.py, db_schema.json) are not under the rework; their round-2 hashes are 3534e5d1…, 06aca16d… and 44f84502….
  - Every conclusion of § policy_conflict_scan through § findings, including observations O-G1..O-G16, therefore stands unchanged. That is consistent with the reworker's "no change" claim for O-G1..O-G16, but the grounds are the hashes, not the claim.
- **Entry conditions.**
  - The coordinator's gate snapshot after rework: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK, CACHE-DIFF INFO, all rc=0, traceability deferred.
  - Masked views: unchanged (0.view.json 46a4f8e1…, 1.view.json 1831a9c0…). I confirmed that frozen_time, user_scenario and initial_state in the current tasks/0.json and tasks/1.json equal the views field for field.
- **Undeclared change (observation R2-O1).** tasks/0.json changed on disk (sha256 ffbd9ca7… at round-1 close, 70f0d6b9… now; mtime 10:50, the same as tasks/1.json). The reworker claimed only tasks/1.json was edited. Its world fields and every scored field are value-identical to round 1, and every figure in its proof fields reproduces (see `0.md` § revision_2). No defect was found in it, but the change was not declared.

### closing_checklist (revision 2)

**Status: CLOSED for the source-layer audit.** T1-R1 and T1-R2 are verified closed against the artifacts (see `1.md` § revision_2). No new defect was found and nothing regressed.

| item | state |
|---|---|
| Per-task files | `0.md` and `1.md`, each with a revision_2 comparison; both tasks PASS on all four relationships |
| Old revisions | round-1 text intact in all three files |
| Coverage | 7/7 extended policies |
| Scopes | disjoint, unchanged from round 1 (charter_scope fields re-read) |
| Task tools | closed |
| uuid8s | unchanged |
| Trees | task 0: 2 prerequisite problems, 3 value_input edges; task 1: 3 prerequisite problems, 3 value_input edges; both acyclic; both rooted in an owner=user write |
| Factors | every computation within 4–6 factors with ≥2 parameter and ≥1 method; multi-source and cross-difficulty factors in each task; every factor bears weight; all baseline-only results definite and different from gold (figures unchanged from round 1 and re-read from computations[].baseline_result / factor_sensitivity) |
| Gate re-run on the final form | the coordinator's post-rework snapshot, all rc=0, traceability deferred because the KB docs are not yet published |
