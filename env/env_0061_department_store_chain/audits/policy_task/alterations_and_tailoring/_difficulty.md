# Policy-task audit — alterations_and_tailoring / charter-global

## charter_global_frozen

- Scenario: env/env_0061_department_store_chain; difficulty alterations_and_tailoring; M = 2 (tasks 0, 1).
- Auditor: erl-task-policy-audit agent (independent of the instantiating agent). Freeze time: 2026-10-13 14:15 UTC (before any task GT was revealed).
- Frozen inputs (sha256[:16], recomputed by the auditor and equal to the brief):
  - tasks/alterations_and_tailoring/alteration.extended.yaml d59625a6fe3b025e
  - tasks/alterations_and_tailoring/task_tools.py 68f498099840b3c9
  - masked views .audit_views/policy/alterations_and_tailoring/0.json d132117908743baa, 1.json a980a1e164987de1
- Read: blueprint/blueprint.yaml, blueprint/db_schema.json, blueprint/share_tools.py, blueprint/products/alteration.yaml (and the variant tables of loyalty.yaml, card.yaml, registry.yaml, order.yaml for cross-category parameters), the extended charter, task_tools.py, the two masked views, and the compute DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/within_months/CFIELD/XLATEST/RND).
- Masked / not read before the freeze: every key listed in `_masked_keys` of the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), tasks/*/tasks/*.json, env/.../worklog.md, every other audit directory.
- Entry conditions: gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK); check_traceability NOT OK and validate_scenario missing-document errors, both explained as pre-render (KB not yet published). Recorded as observation O-11; not treated as incomplete input.
- Base copy: lines 1-838 of the extended charter are byte-identical to blueprint/products/alteration.yaml (diff shows only the appended comment/blank line); every top-level key of the base parses equal.

### policy_conflict_scan

Seven extended policies, seven distinct target tools:

| policy | target_tool (owner) | computes | prerequisite edges |
| --- | --- | --- | --- |
| alteration_ext_rush_fee | book_rush_fee_44a954b1 (agent) | amount | [] |
| alteration_ext_rush_fee_waiver | waive_rush_fee_f377d7ac (agent) | amount | -> rush_fee (value_input, rush_standing) |
| alteration_ext_pre_work_deposit | pay_ticket_deposit_a1dd4c80 (user) | amount | -> rush_fee, -> rush_fee_waiver (value_input, standing_charges) |
| alteration_ext_added_work_lining | book_lined_surcharge_bf0414f9 (agent) | amount | [] |
| alteration_ext_quote_overrun | waive_quote_overrun_938dcea5 (agent) | amount | -> added_work_lining (value_input, overrun_charges) |
| alteration_ext_complimentary_work | waive_complimentary_work_96f02105 (agent) | amount | [] |
| alteration_ext_extra_fitting_fee | book_extra_fitting_87db3b08 (user) | amount | -> complimentary_work, -> quote_overrun (value_input, chargeable_work) |

- Subjects: two policies write alteration_charge (rush fee row vs lined_surcharge row vs extra_fitting_fee row — distinct charge_type, so no overlap), three write alteration_charge_waiver with distinct waiver_reason (loyalty_rush_waiver / quote_overrun / complimentary_basic), one writes alteration_payment (deposit). No two policies conclude differently on the same quantity.
- Scopes observed in the two worlds (pre-reveal, from the trees the auditor derives): task 0 = {pre_work_deposit (root), rush_fee, rush_fee_waiver}; task 1 = {extra_fitting_fee (root), complimentary_work, quote_overrun, added_work_lining}. Pairwise disjoint and jointly complete over the seven policies. Final confirmation against charter_scope is in each task's source_gt_comparison.
- Cross-category read boundaries: card (accounts, transactions, statements), order (purchases, order_events), loyalty (memberships, points ledger), registry (registries); every read is scoped to the customer (DSL `_cross`/`_xrows` filter on customer_id). No write touches another category.
- Latent cross-problem couplings that no declared edge carries (no task world contains both ends; see O-7): rush_fee operation base reads lined_surcharge rows (added_work_lining writes them); quote_overrun tier 2 reads the standing rush fee; pre_work_deposit standing charges read every charge and waiver (lined surcharges, overrun/complimentary waivers, extra fittings); extra_fitting_fee chargeable work subtracts every waiver including loyalty_rush_waiver.

### rule_compute_equivalence

Mechanical sweep (auditor script): every compute_basis value is a verbatim substring of its policy's rule; every compute binding has a compute_basis entry except `operation_base` in alteration_ext_rush_fee (O-5; its sentence is the one quoted for op_charges/lined_charges). Every sentence of each `baseline.rule` is a sentence of the policy's `rule`. Every factor ladder tier is stated in the rule prose and implemented as a branch of its `decides` binding.

Manual sweep, sentence by sentence, findings only:
- rush_fee: lead-time tiers, lining premium, cardmember discount, new-purchase discount, occasion discount, additive rate/discount and the single final rounding are each implemented. The late-fee lookback tier "a customer whose active card account opened less than 12 whole months before today has counted every late fee since the account opened" is implemented as `XCOUNT(... event_type='card_fee', fee_type='late_fee')` with no date bound over all of the customer's card accounts, i.e. it also counts late fees dated before the active account opened (O-1, latent: neither world reaches this tier).
- rush_fee_waiver: same divergence for returned payments, tier 2 (O-1).
- pre_work_deposit: `XLATEST('card','card_statements','statement_balance')` takes the latest statement across all the customer's card accounts while the rule says "the statement_balance of the latest statement" of "the active Marlowe & Finch card" (latent; both worlds hold one card). The class gate "A ticket in a class whose deposit_pct is above 0 owes a deposit" has no compute counterpart (the result is undefined when deposit_min_usd is not_applicable) — scope sentence, latent.
- complimentary_work: the rule sentence "A lined surcharge on an operation that receives the full complimentary share is complimentary too" has no compute counterpart (`qualifying_gross` sums operation rows only) — an empty promise (O-2, latent: task 1 is on a partial share).
- All policies: `RND` is Python `round` on binary floats (half-to-even on exactly representable halves) while every rule says "rounded half up". Divergence appears only on exact half-cents; on the worlds audited it touches only the rush-fee all-baseline figure (216.25 x 50% = 108.125 -> compute 108.12, rule 108.13) (O-4).

### action_binding_and_uuids

- Each (target_tool, computes) pair is claimed by exactly one policy (seven tools, seven policies).
- uuid8 tails: 44a954b1, f377d7ac, a1dd4c80, bf0414f9, 938dcea5, 96f02105, 87db3b08 — pairwise distinct, no shared prefix, no sequence or adjacency pattern.
- Tool bodies (task_tools.py lines 10-190): each creates one alteration_charges row and moves balance_due; none reads another row to refuse, validate a prerequisite, or compute an amount. No tool judges eligibility or order.
- Docstrings: none names another tool, none states a position in a sequence; the only ordering word is "then" inside "the customer then sees ..." describing the call's own effect. No docstring or parameter description carries a concrete example value (amounts, ids, dates); `fitting_number` says "an integer counted from 1" (a counting convention, not an example value). Enum lists (operation codes, tenders) are domain enumerations. pay_ticket_deposit's tender enum omits alteration_credit, matching the declared overwrite.

### prerequisite_graph

- Every policy fills `prerequisite` ([] for rush_fee, added_work_lining, complimentary_work).
- Every `problem` is an extended policy id of this file, none self-referencing; graph edges: waiver->rush_fee, deposit->rush_fee, deposit->waiver, overrun->lining, fitting->complimentary, fitting->overrun. Acyclic (two components).
- Every `policy_source` is a verbatim substring of the blocked policy's own rule (script check) and is absent from the depended-on policy's rule.
- All six edges: form `state`, no fallback_reason (none required).
- `resolved_by` equals the depended-on policy's target_tool on all six edges; each `gate` (rush_standing, standing_charges, overrun_charges, chargeable_work) is a binding of the blocked policy's compute; `kind` value_input on all six, and each gate binding genuinely reads the rows the resolving tool writes (rush_fee row; loyalty_rush_waiver row; lined_surcharge row; complimentary_basic / quote_overrun waiver rows).
- No authoring-viewpoint wording ("this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test per edge (ordering connective / state named in record words / no tool, id, snake_case or row id / strength equals condition), the one write that brings the state about, and the reader's derivation.

1. waiver -> rush_fee: "A rush fee waiver is booked only after the ticket carries the rush fee it waives." Connective "only after"; state = the ticket carries a rush fee (alteration_charges row, charge_type rush_fee); no tool/id. Strength equals condition. Only book_rush_fee_44a954b1 writes a rush_fee row. Derivation: the waiver rule acts on "the rush fee standing on a ticket"; the records show rush_service true and no rush_fee row; the rush-fee rule says "A ticket accepted with rush service owes one rush fee" -> book it first. Single reading. PASS.
2. deposit -> rush_fee: "The deposit on a ticket accepted with rush service is worked out only after that ticket carries its rush fee." Connective "only after"; state named; scope "ticket accepted with rush service" = condition "On a ticket with rush_service true". One write (book_rush_fee). PASS.
3. deposit -> waiver: "A deposit is not taken until every rush fee waiver the customer's Finch Circle standing earns stands on the ticket." Connective "not until"; state = a rush fee waiver stands; open set stated open ("every ... earns"). One write (waive_rush_fee_f377d7ac is the only loyalty_rush_waiver writer). Wording note: the condition reads "Where the customer's Finch Circle tier and card standing earn a rush fee waiver"; the sentence says "Finch Circle standing". Every rush fee waiver this charter books is the Finch Circle rush fee waiver (waiver_reason loyalty_rush_waiver), so the sentence covers the same set; a narrower reading ("tier alone") is possible but weak (O-10). PASS with observation.
4. overrun -> lining: "The quote overrun waiver is worked out only after every operation on a lined garment carries its lined surcharge." Connective "only after"; state named. One write (book_lined_surcharge_bf0414f9; the base pricing rule has no tool in this difficulty). Scope: sentence says "every operation on a lined garment", condition says "every operation charge booked after the dropoff_date". Under base alteration_pricing ("when the garment is lined, a lined_surcharge row adds ...") operations booked at drop-off already carry surcharges, so the two coincide on every charter-consistent world; in a class with lined_garment_surcharge_pct 0 neither the sentence nor the condition can ever be satisfied for an added operation (the lining policy's result is 0 and the tool books positive amounts) — latent deadlock (O-6). PASS with observation.
5. fitting -> complimentary: "The fee for an extra fitting is fixed only after the ticket carries the complimentary waiver owed on its qualifying operations." Connective "only after"; state named; one write (waive_complimentary_work_96f02105). PASS.
6. fitting -> overrun: "An extra fitting fee is not booked until any operation charges running past the honored quote stand waived on the ticket." Connective "not until"; state named ("honored" matches the overrun rule's "honored amount"); one write (waive_quote_overrun_938dcea5). PASS.

No rule carries a second wording of any edge, a tool name or another problem's id. No rule states a cross-problem order that grounds no declared edge (the deposit rule's "after drop-off and before the tailor starts the work" orders against a shop event, not a problem). No base rule sentence is used to ground an edge.

### override_declarations

Sentence-by-sentence over each policy's base_policy_refs; only sentences that touch the policy's scored quantity are listed as "handled differently".

- alteration_ext_rush_fee (alteration_pricing, alteration_rush_service): pricing "A rush fee row charges rush_fee_pct of alteration_msr_operation_charges ..." — replaced, declared. All other pricing sentences (operation prices, lined surcharge, extra fittings, overrun, pressing, tax) are not this quantity. rush_service sentences (availability, open-ticket state, promised date, loyalty waiver, refund/waive on missed date) are inherited; "books the rush fee under alteration_pricing" now resolves to the declared replacement. No undeclared override.
- alteration_ext_rush_fee_waiver (agg_complimentary, complimentary_basic, rush_service, cancellation, remake): rush_service "A Finch Circle member whose tier held on the ticket's dropoff_date ..." — replaced, declared (tier at booking; partial shares extend). Missed-date full waiver inherited. Other refs do not govern the rush fee waiver. No undeclared override.
- alteration_ext_pre_work_deposit (payment_rules, intake_rules): intake deposit sentence and payment "deposit is paid at drop-off" — both replaced, declared (base: deposit_pct of quoted_total at drop-off; extended: rate on standing charges after drop-off, alteration credit excluded). Intake rush-only acceptance, promised date, price list inherited. No undeclared override.
- alteration_ext_added_work_lining (pricing, rush_service): pricing lined surcharge sentence — replaced for operations added after drop-off, declared. "Operations beyond the quote are added only after the customer approves them" inherited. No undeclared override.
- alteration_ext_quote_overrun (..., pricing): pricing overrun sentence — replaced, declared. The rule's bridge "Work the customer approves is reflected in the ticket's quoted_total" reads base approval through the record; no conflict.
- alteration_ext_complimentary_work (agg_complimentary, complimentary_basic, ...): three declared replacements (window; price types/sale share; lined surcharge treatment). Handled differently but NOT declared: complimentary_basic "At most complimentary_max_operations operations are complimentary (see alteration_agg_complimentary_per_purchase), taken from the qualifying operations with the highest price first." and alteration_agg_complimentary_per_purchase "the complimentary operations granted on every ticket that names the same purchase_id ... never exceed the class's complimentary_max_operations in total". The extended rule waives "the qualifying operation charges ... less any complimentary waiver already booked against them" on the ticket alone, with no count cap and no cross-ticket count. Finding F-5 (undeclared override; consequence only where qualifying operations exceed the cap or a second ticket names the same purchase — demonstrated per task).
- alteration_ext_extra_fitting_fee (pricing, rush_service): pricing "Each fitting beyond fittings_included is charged extra_fitting_fee_usd." — replaced, declared. No undeclared override.

### factor_ladders

Structure only (weight lives in each task file). "MS" = every non-fall-through tier is a conjunction/disjunction over distinct records. "XD" = cross_difficulty category. Every ladder below has 3 or 4 tiers, each tier stated in the rule prose and implemented as a branch of its `decides` binding; no two tiers of any ladder select the same value; bindings are disjoint within each policy; no `decides` is `result`.

| policy | factor | label | XD | MS | structural verdict |
| --- | --- | --- | --- | --- | --- |
| rush_fee | rush_lead_time_rate | parameter | - | no | ok |
| rush_fee | lined_work_rush_premium | parameter | - | yes (lined rows + op rows) | ok |
| rush_fee | late_fee_lookback_by_card | method | card | yes | **struck (F-1)** |
| rush_fee | cardmember_rush_discount | parameter | card | yes (card + late fees + spend) | ok |
| rush_fee | new_purchase_rush_discount | parameter | order | no | ok |
| rush_fee | registry_occasion_discount | parameter | registry | no | ok |
| rush_fee_waiver | member_waiver_share (4 tiers) | parameter | loyalty | yes (tier + card standing) | ok (realism note O-8) |
| rush_fee_waiver | returned_payment_lookback_by_card | method | card | yes | **struck (F-1)** |
| rush_fee_waiver | membership_tenure_addition | parameter | loyalty | no | ok |
| rush_fee_waiver | points_earning_addition | parameter | loyalty | no | ok |
| pre_work_deposit | card_deposit_rate | parameter | card | yes (card + statements) | ok |
| pre_work_deposit | utilization_balance_by_card | method | card | yes | **struck (F-2)** |
| pre_work_deposit | uncollected_order_addition | parameter | order | no | ok |
| pre_work_deposit | finch_circle_deposit_reduction | parameter | loyalty | no | ok |
| pre_work_deposit | garment_tender_reduction | parameter | order | no | ok |
| pre_work_deposit | card_tenure_deposit_reduction | parameter | card | no | ok |
| added_work_lining | own_purchase_lining_rate | parameter | loyalty | yes (purchase + tier) | ok |
| added_work_lining | lining_opening_priced_amount | method | - | yes | **struck (F-3)** |
| added_work_lining | multi_operation_reduction | parameter | - | no | **struck (F-4)** |
| added_work_lining | lining_tenure_reduction | parameter | loyalty | no | ok |
| quote_overrun | standing_quote_tolerance | parameter | loyalty | yes (tier + card) | ok |
| quote_overrun | card_tenure_tolerance_reduction | parameter | card | no | ok |
| quote_overrun | points_tolerance_reduction | parameter | loyalty | no | ok |
| quote_overrun | extra_fitting_allowance | parameter | - | no | ok |
| quote_overrun | tolerance_application_base | method | - | yes (op date + tier) | ok (O-9) |
| complimentary_work | sale_price_complimentary_share (4 tiers) | parameter | order | yes (price type + tier) | ok |
| complimentary_work | premium_garment_addition | parameter | order | no | ok |
| complimentary_work | finch_circle_window_extension | parameter | loyalty | no | ok |
| complimentary_work | card_charged_window_extension | parameter | card | yes (card + purchase) | ok |
| complimentary_work | complimentary_window_anchor | method | loyalty | yes (tier change + purchase) | ok (realism O-8) |
| extra_fitting_fee | member_fitting_rate | parameter | loyalty | no | ok |
| extra_fitting_fee | fitting_number_basis | method | - | yes (needed_by + count) | ok (realism O-8) |
| extra_fitting_fee | event_proximity_surcharge | parameter | registry | no | ok |
| extra_fitting_fee | small_job_fitting_surcharge | parameter | - | no | ok |
| extra_fitting_fee | wedding_party_credit | parameter | registry | yes (type + date) | ok |
| extra_fitting_fee | cardmember_fitting_credit | parameter | card | no | ok |

Counts after striking (declared -> surviving; parameter / method):
- rush_fee 6 -> 5 (5 / 0) — **no honest method factor**.
- rush_fee_waiver 4 -> 3 (3 / 0) — **below 4 factors, no method factor**.
- pre_work_deposit 6 -> 5 (5 / 0) — **no surviving method factor**.
- added_work_lining 4 -> 2 (2 / 0) — **below 4 factors, no method factor**.
- quote_overrun 5 (4 / 1), complimentary_work 5 (4 / 1), extra_fitting_fee 6 (5 / 1) — within bounds.
- Per tree: task 0's computations carry multi-source (cardmember_rush_discount, member_waiver_share, card_deposit_rate) and cross-difficulty factors (card, order, registry, loyalty); task 1's carry multi-source (own_purchase_lining_rate, standing_quote_tolerance, sale_price_complimentary_share) and cross-difficulty factors (loyalty, card, order, registry).

### findings

**F-1 — SOURCE-FACTOR RED (structural): the two card-lookback "method" factors are a lookback-length parameter, and their first two tiers overlap as stated.** Bears on task 0 (rush fee and rush fee waiver).
- Symptom: late_fee_lookback_by_card (rush_fee) and returned_payment_lookback_by_card (rush_fee_waiver) are each the only `method` factor of their policy.
- Evidence (rule, rush_fee): "a customer whose active card is the Marlowe & Finch Store Card Elite or the Marlowe & Finch World Elite Mastercard has counted the late fees dated less than 6 whole months before today; a customer whose active card account opened less than 12 whole months before today has counted every late fee since the account opened; any other customer has counted the late fees dated less than 12 whole months before today." Compute: three `XCOUNT('card','card_transactions', ..., fee_type='late_fee')` calls differing only in `within_months=6` / none / `within_months=12`. The waiver's returned-payment ladder is the same with event_type card_payment_returned.
- Root cause / demonstration: (a) every tier is the same count of the same rows with a different window bound (6 months, account opening, 12 months) — a number substituted into one formula, i.e. a `parameter`; no tier changes how the count is computed. (b) As stated, tiers 1 and 2 are not disjoint: a Store Card Elite account opened 10 months ago satisfies both "active card is the ... Store Card Elite" and "active card account opened less than 12 whole months before today", and the prose states no precedence. With one late fee dated 8 months ago, tier 1 counts 0 late fees (cardmember discount 5 or 10 percent) while tier 2 counts 1 (no cardmember discount) — two rush fees for one world. The returned-payment ladder has the identical overlap (clear vs not-clear card standing). Compute silently applies tier 1 first; in compute tier 2 also has no date bound at all (O-1). Struck, the rush_fee computation keeps 0 `method` factors and the waiver computation keeps 3 factors and 0 `method`.
- Affected: alteration.extended.yaml, alteration_ext_rush_fee.factors[late_fee_lookback_by_card] and rule; alteration_ext_rush_fee_waiver.factors[returned_payment_lookback_by_card] and rule.

**F-2 — SOURCE-FACTOR RED (structural): utilization_balance_by_card tiers 1 and 2 overlap as stated.** Bears on task 0 (deposit).
- Evidence (rule): "for the Marlowe & Finch Store Card Elite or the Marlowe & Finch World Elite Mastercard it is the lower of the card's current_balance and the statement_balance of the latest statement; for a card account opened less than 12 whole months before today it is the higher of those two balances; for any other card it is the current_balance."
- Demonstration: a World Elite account opened 4 months ago, credit_limit 6,000, current_balance 1,900, latest statement_balance 900: tier 1 gives 900/6000 = 15.0% (deposit rate 30%), tier 2 gives 1900/6000 = 31.7% (deposit rate 40%). No precedence is stated in the rule; compute silently applies tier 1 first. Struck, the deposit computation keeps no `method` factor.
- Affected: alteration_ext_pre_work_deposit rule and factors[utilization_balance_by_card].

**F-3 — SOURCE-FACTOR RED: lining_opening_priced_amount divides no customer who reaches the write, and it is labelled `method` while it adds an amount.** Bears on task 1.
- Evidence: scope sentence "a lined surcharge is owed for an operation added to a lined garment's ticket after its dropoff_date that does not yet carry one, and the lined surcharge for added work is priced on the most recently booked operation charge on the ticket"; ladder "when a lined surcharge already stands on the ticket and the operation was booked after the dropoff_date ... the operation charge less a lining-opening allowance of 8.00 USD, never below zero; when no lined surcharge stands on the ticket yet and the operation was booked after the dropoff_date ... the operation charge plus a lining reopening amount of 6.00 USD; otherwise the priced amount is the operation charge."
- Demonstration: (a) the conjunct "the operation was booked after the dropoff_date" holds of every customer who reaches this write (the policy is owed only for an operation added after drop-off, and the most recently booked operation is then that operation), so the fall-through tier — the baseline "price on the operation charge" — is reachable by no customer of this policy. (b) Base alteration_pricing books a lined_surcharge row for every operation of a lined garment at drop-off ("when the garment is lined, a lined_surcharge row adds lined_garment_surcharge_pct of that operation's price") and the policy is scoped to classes with lined_garment_surcharge_pct above 0, so "a lined surcharge already stands" also holds of every such customer on a charter-consistent ticket; tier 2 needs a ticket whose drop-off operations were never surcharged. The ladder therefore selects tier 1 for every customer reaching the write. (c) The three tiers are operation charge + {−8.00 floored at 0, +6.00, 0}: one formula with a substituted amount — a `parameter`, not a `method`.
- Affected: alteration_ext_added_work_lining rule, compute `priced_amount`, factors[lining_opening_priced_amount].

**F-4 — SOURCE-FACTOR RED: multi_operation_reduction's fall-through is out of scope.** Bears on task 1.
- Evidence: "3 percentage points when the ticket carries three or more operation charges, 1 percentage point when it carries two, and none for a single operation charge"; scope as in F-3.
- Demonstration: a customer reaching this write has the operation(s) agreed at drop-off (alteration_dropoff: "an alteration ticket is opened with the agreed operations and quote") plus the operation added after drop-off, so at least two operation charges; the "single operation charge" tier (the factor's baseline 0) is a treatment applied to no customer of this policy, leaving a two-tier ladder.
- Affected: alteration_ext_added_work_lining factors[multi_operation_reduction]. With F-3, the lining computation keeps 2 factors, 0 `method`.

**F-5 — undeclared override of the complimentary cap (finding; consequence per task).** See override_declarations. Task 1 has one qualifying operation (cap 3) and one ticket on its purchase, so no second answer arises there (demonstrated in 1.md); recorded as observation for the difficulty, not a RED.

Observations (no demonstrated consequence on tasks 0/1):
- O-1 Lookback tier 2 (late fees / returned payments) compute counts every fee on every card account with no date bound; rule says "since the account opened".
- O-2 complimentary_work rule promises "A lined surcharge on an operation that receives the full complimentary share is complimentary too"; compute never waives lined surcharges.
- O-4 RND half-even vs "rounded half up" (exact half-cents only).
- O-5 rush_fee `operation_base` has no compute_basis entry.
- O-6 overrun->lining sentence scope ("every operation on a lined garment") wider than its condition (after-drop-off operations); unsatisfiable for lined garments in 0%-surcharge classes.
- O-7 Latent undeclared couplings (listed under policy_conflict_scan); no world contains both ends.
- O-8 Realism: card utilization, card returned payments and card late fees set alteration deposits, loyalty rush-waiver shares and rush discounts; the complimentary window restarts at a tier upgrade; extra-fitting fees escalate by ordinal only on tickets with no needed-by date. Each is a defensible retail practice taken alone; none is recorded as RED.
- O-9 quote_overrun tolerance_application_base tier 1 conjunct "most recent operation charge was booked after its dropoff_date" holds for practically every customer owed an overrun waiver (overruns arise from operations added after the quote); the ladder still divides customers by tier and rush, so it is not struck.
- O-10 deposit->waiver sentence wording "Finch Circle standing" vs condition "Finch Circle tier and card standing" (weak second reading; see task 0).
- O-11 Gate snapshot: traceability and validate_scenario not green, explained as pre-render.

## closing_checklist

Written after both tasks' GT was revealed (task 0 at 14:18:51 UTC, task 1 at 14:19:43 UTC, both after every derivation and this file's charter-global section were frozen). The difficulty does **not** close: not all four relationships PASS.

| item | status |
| --- | --- |
| per-task files 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; _difficulty.md alongside; first revision | met |
| every comparison section carries a PASS | **not met** — task 0 SOURCE-FACTOR RED (T0-1, T0-2), task 1 SOURCE-FACTOR RED (T1-1) |
| extended policies fully covered; scopes pairwise disjoint (task 0: rush_fee, rush_fee_waiver, pre_work_deposit; task 1: added_work_lining, quote_overrun, complimentary_work, extra_fitting_fee) | met |
| task tools and GT closed; uuid8s independent and frozen | met |
| each tree 1-3 prerequisite problems, ≥ max(n−1,1) value_input edges, a user-owned write, acyclic; whole-difficulty graph acyclic | met (task 0: n=2, 3 value_input, root user-owned; task 1: n=3, 3 value_input, root user-owned) |
| every computation 4-6 factors with ≥2 parameter and ≥1 honest method, ladders ≥3 disjoint tiers that divide the customers reaching the write | **not met** — rush_fee (0 method), rush_fee_waiver (3 factors, 0 method), pre_work_deposit (0 surviving method), added_work_lining (2 factors, 0 method) |
| every factor bears weight against an honest baseline; baseline alone definite and ≠ gold | met on both worlds (every substitution moves the scored value; fall-backs 108.13 [recorded 108.12, T0-3] / 0.00 / 144.62 / 6.40 / 26.48 / 0.00 / 15.00, all ≠ gold) |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | met |
| instantiation gates re-run on the final form | not run by this audit (artifacts unchanged since the coordinator's 14:06 snapshot; traceability/validate_scenario pending KB render) |

Per-task verdicts: task 0 — SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-TASK PASS, **SOURCE-FACTOR RED**; task 1 — SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-TASK PASS, **SOURCE-FACTOR RED**.

## revision_2

### charter_global_frozen (r2)

- Re-audit round 2. Freeze time 2026-10-13 16:27 UTC (written before any round-2 task GT was revealed); auditor: erl-task-policy-audit agent.
- Inputs: alteration.extended.yaml **6484e71d7fbbc913 (changed from d59625a6fe3b025e)**; task_tools.py 68f498099840b3c9 (unchanged); views 0.json b7bf41b69b1a702d, 1.json 09ac6b5744119b95; gate snapshot .audit_views/policy/alterations_and_tailoring/snapshot_r2.txt (all OK except traceability unlock-tool_name misses and validate_scenario missing documents, both pre-render — O-11 carried).
- Masked/unread before the freeze: as round 1. Round-1 sections above are left untouched.
- Base copy: still byte-identical to blueprint/products/alteration.yaml (only the appended comment differs); all base keys parse equal.
- Carried forward by reference (task_tools.py hash unchanged): § action_binding_and_uuids of round 1 — tool bodies, uuid8s, docstrings unchanged; each (target_tool, computes) still claimed by exactly one policy (seven tools, same seven policy ids). Docstrings still carry no example value.
- Re-derived in full (charter hash changed): policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders.

### policy_conflict_scan (r2)

Same seven policies, tools, owners and edge set as round 1 (waiver→rush_fee, deposit→rush_fee, deposit→waiver, overrun→lining, fitting→complimentary, fitting→overrun). Distinct subjects / charge types / waiver reasons; no two policies conclude differently on one quantity. Latent couplings without an edge (no world holds both ends): rush fee's lined-work premium counts lined_surcharge rows (lining policy writes them); deposit standing charges and fitting chargeable work read every waiver.

### rule_compute_equivalence (r2)

- Script sweep: every compute binding has a verbatim compute_basis quotation (O-5 closed); every baseline.rule sentence is in its rule; every ladder tier is in the rule and in its `decides` branch.
- Manual sweep: rush fee (basis form, multiplier, premium, three discounts, single final rounding), waiver (four forms, co-pay, reliefs, cap at standing), deposit (three forms, rate, addition, three reductions, floor 0, class gate now in compute), lining (three basis forms, three discounts), overrun (three tolerance forms, dollar tolerance, allowance, two credits), complimentary (three forms, allowance, premium, two window extensions, first-waiver-on-ticket), fitting fee (unchanged except small-job thresholds 100/125) — each rule sentence has its compute and vice versa, except:
  - complimentary_work: "complimentary operations are taken highest price first and stay within complimentary_max_operations across every ticket naming the purchase as the base allowance rule provides" — compute checks only `first_on_ticket` on this ticket; no cross-ticket count (latent: one ticket per purchase in both worlds). O-R2-1.
  - complimentary_work: "the lined surcharge of an operation waived in full is waived on its own row as complimentary basic work" — no policy of the charter computes or books that row (this policy books the operation charge only, and `first_on_ticket` would zero this policy's own waiver if the surcharge row stood first). Latent (no world has a full-share lined operation). O-R2-1.
- Rounding: every result now adds `half_up_offset` 1e-6 before RND, giving half up on exact half-cents (O-4 closed); the deposit two-part form adds deposit_min_usd after rounding (whole-cent addend, equivalent).

### prerequisite_graph (r2)

All seven `prerequisite` fields present; six edges, all `state`, `value_input`; problems are extended ids; acyclic; each policy_source verbatim in its own rule and absent from the depended-on rule; resolved_by = depended-on target_tool; gates rush_standing / standing_charges / overrun_charges / chargeable_work are compute bindings reading the rows the resolving tool writes. No authoring-viewpoint wording.

### prerequisite_sentences (r2)

Unchanged sentences 1, 2, 5, 6 pass as in round 1. Changed:
- deposit → waiver: "A deposit is not taken until any Finch Circle rush fee waiver the ticket is owed stands on it." — "not until", state named, open set stated open, scope equals condition ("Where the rush fee waiver policy gives the ticket a waiver above zero ..."); one write (waive_rush_fee_f377d7ac). O-10 closed.
- overrun → lining: "The quote overrun waiver is worked out only after every operation added to a lined garment's ticket after its drop-off carries its lined surcharge, in a class that charges one." — scope now equals the condition (after-drop-off operations, class surcharge above 0); one write (book_lined_surcharge_bf0414f9). O-6 closed.

### override_declarations (r2)

- rush_fee, rush_fee_waiver, pre_work_deposit, added_work_lining, quote_overrun, extra_fitting_fee: each base sentence on the scored quantity is replaced and named in `overwrite` (texts above); all other sentences inherited. No undeclared override.
- complimentary_work: three declared replacements (window extensions; price types / sale-work allowance; lined-surcharge treatment). The base cap sentence of complimentary_basic and alteration_agg_complimentary_per_purchase are now expressly kept ("stay within complimentary_max_operations across every ticket naming the purchase as the base allowance rule provides") and the policy books only the highest-priced qualifying operation of a ticket with no complimentary waiver yet. F-5 closed as an undeclared override; the residual compute gap is O-R2-1.

### factor_ladders (r2)

| policy | factor | label | XD | MS | structural verdict |
| --- | --- | --- | --- | --- | --- |
| rush_fee | rush_charge_basis_form | method | - | yes (op count + op base) | ok: per-operation count × 30.00 / flat 25.00 / rush_fee_pct of base — three formula shapes, "exactly one of three", fall-through reachable |
| rush_fee | rush_lead_time_multiplier | parameter | - | no | ok |
| rush_fee | lined_work_rush_premium | parameter | - | no | ok |
| rush_fee | cardmember_rush_discount | parameter | card | no | ok |
| rush_fee | new_purchase_rush_discount | parameter | order | no | ok |
| rush_fee | registry_occasion_discount | parameter | registry | no | ok |
| rush_fee_waiver | member_waiver_form (4 tiers) | method | loyalty | yes (tier + own purchase) | ok: whole / standing less co-pay / 25% share / nothing |
| rush_fee_waiver | member_rush_copay | parameter | order | yes (tier + price type) | ok (nested: exists only under the co-pay form; O-R2-3) |
| rush_fee_waiver | membership_tenure_relief | parameter | loyalty | no | ok (nested, O-R2-3) |
| rush_fee_waiver | points_earning_relief | parameter | loyalty | no | ok (nested, O-R2-3) |
| pre_work_deposit | deposit_form_by_record | method | - (order rows) | no | ok: whole prepay / two-part / percentage with floor and cap |
| pre_work_deposit | finch_circle_deposit_rate | parameter | loyalty | no | ok |
| pre_work_deposit | uncollected_order_addition | parameter | order | no | ok |
| pre_work_deposit | garment_tender_reduction | parameter | order | no | ok |
| pre_work_deposit | frequent_shopper_reduction | parameter | order | no | ok |
| pre_work_deposit | cardmember_deposit_reduction | parameter | card | no | ok |
| added_work_lining | lined_work_basis_form | method | - | no | **struck (R2-2)** |
| added_work_lining | member_lining_discount | parameter | loyalty | yes (own purchase + tier) | ok |
| added_work_lining | recent_purchase_lining_discount | parameter | order | no | ok |
| added_work_lining | ticket_size_lining_discount | parameter | - | no | ok (fall-through < 60.00 reachable within scope) |
| quote_overrun | quote_tolerance_form | method | - | no | **struck (R2-1)** |
| quote_overrun | standing_dollar_tolerance | parameter | loyalty | yes (tier + card) | ok |
| quote_overrun | extra_fitting_allowance | parameter | - | no | ok |
| quote_overrun | own_purchase_quote_credit | parameter | order | no | ok |
| quote_overrun | membership_tenure_quote_credit | parameter | loyalty | no | ok |
| complimentary_work | complimentary_waiver_form | method | order | yes (price type + tier) | ok: whole charge / lesser of charge and allowance / nothing |
| complimentary_work | member_sale_work_allowance | parameter | loyalty | no | ok (nested, O-R2-3) |
| complimentary_work | premium_garment_addition | parameter | order | no | ok |
| complimentary_work | finch_circle_window_extension | parameter | loyalty | no | ok |
| complimentary_work | card_charged_window_extension | parameter | card | yes (card + purchase) | ok |
| extra_fitting_fee | (six factors unchanged from round 1) | 5 param / 1 method | loyalty, registry, card | yes | ok |

Counts after striking (parameter / method): rush_fee 6 (5/1); rush_fee_waiver 4 (3/1); pre_work_deposit 6 (5/1); **added_work_lining 3 (3/0)**; **quote_overrun 4 (4/0)**; complimentary_work 5 (4/1); extra_fitting_fee 6 (5/1).

### round-1 item closure (charter-level)

| item | claim | verdict |
| --- | --- | --- |
| F-1 lookback "method" factors / overlap | closed | **closed** — both lookback factors removed; rush fee and waiver now carry honest, disjoint method factors (rush_charge_basis_form, member_waiver_form) |
| F-2 utilization overlap | closed | **closed** — factor removed; deposit_form_by_record is an honest method |
| F-3 lining_opening_priced_amount | closed | closed as such (factor removed) — but its replacement lined_work_basis_form fails (R2-2), so the lining computation still has no honest method |
| F-4 multi_operation_reduction fall-through | closed | **closed** — removed; ticket_size_lining_discount fall-through is reachable |
| F-5 undeclared complimentary cap | closed | **closed** as an override (cap expressly kept); residual compute gap O-R2-1 |
| O-1 lookback tier-2 compute | closed | closed (factors removed) |
| O-2 lined surcharge on full-share op | closed | **partly** — the rule now says the surcharge row is waived "on its own row", but no policy books it (O-R2-1) |
| O-4 half-even rounding | closed | closed (half_up_offset) |
| O-5 missing compute_basis | closed | closed |
| O-6 overrun→lining sentence scope | closed | closed |
| O-8 realism | closed | closed for the card-based factors (removed); the fitting-fee ordinal escalation without a needed-by date is unchanged (observation stands, low) |
| O-9 after-drop-off conjunct | closed | closed as such (factor replaced); see O-R2-2 for the replacement's fall-through |
| O-10 deposit→waiver wording | closed | closed |

### findings (r2)

**R2-1 — SOURCE-FACTOR RED: quote_tolerance_form writes one tier as two.** Bears on task 1.
- Evidence (rule): "two or more such operations give a per-operation tolerance, the dollar tolerance times the number of those operations; exactly one such operation gives the dollar tolerance once; no such operation gives the class's quote_overrun_tolerance_pct of the quoted_total." Compute: `dollar_tolerance * added_ops if added_ops >= 2 else (dollar_tolerance if added_ops == 1 else quoted * pct / 100)`.
- Demonstration: the single expression `dollar_tolerance × added_ops` reproduces tier 1 on its whole domain (n ≥ 2) and tier 2 on its whole domain (n = 1: d × 1 = d). Tiers 1 and 2 select the same method; the ladder has two distinct methods (per-operation dollar tolerance / percentage of the quote), below three. Struck, the overrun computation has 4 parameter factors and no `method`.
- Affected: alteration_ext_quote_overrun rule, compute `tolerance_amount`, factors[quote_tolerance_form]. New in round 2 (round 1's tolerance_application_base passed).

**R2-2 — SOURCE-FACTOR RED: lined_work_basis_form writes one tier as two.** Bears on task 1 (T1-1 not closed).
- Evidence (rule): "an operation charged under 40.00 USD carries a flat lining charge of 5.00 USD; an operation charged 100.00 USD or more carries lined_garment_surcharge_pct of the first 100.00 USD of its charge; an operation charged 40.00 to 99.99 USD carries lined_garment_surcharge_pct of its whole charge."
- Demonstration: `lined_garment_surcharge_pct × min(charge, 100.00)` reproduces tier 2 on its domain (charge ≥ 100) and tier 3 on its domain (40.00-99.99, where min(charge, 100) = charge): one capped-percentage rule written as two tiers whose boundary is exactly where the cap starts to bind. The ladder has two distinct methods (flat 5.00 / capped percentage). Struck, the lining computation has 3 factors (3 parameter / 0 method).
- Affected: alteration_ext_added_work_lining rule, compute `lining_basis`, factors[lined_work_basis_form].

Observations (r2):
- O-R2-1 complimentary_work: cross-ticket cap stated but not computed; full-share lined-surcharge waiver row promised but owned by no policy (latent).
- O-R2-2 quote_overrun fall-through ("no such operation" → percentage of the quote) is reached by a customer owed a waiver only when the purchase and tenure credits exceed the percentage tolerance (quotes under about 50.00 at 10%), and then the waiver falls on quoted, approved work — against the rule's own opening sentence "the overrun charges that run past the honored amount are unapproved work". Latent; no world reaches it.
- O-R2-3 Nested factors (member_rush_copay, tenure/points reliefs, member_sale_work_allowance) exist only inside a non-baseline form; their `baseline` is their fall-through tier, which baseline.rule does not state (it states no co-pay/allowance at all). Each still bears weight on its world (see task files).
- O-R2-4 Structural, carried from round-1 T1-3: whenever a quote overrun waiver is owed, chargeable work after it equals the honored amount less the other waivers, so the lining write can never reach the extra-fitting fee; the overrun→lining edge bears weight only on the overrun's own scored value.

### closing_checklist (r2)

Written after the round-2 reveal (16:27:22 UTC). The difficulty does **not** close.

| item | status |
| --- | --- |
| files 0.md / 1.md ↔ tasks; revision_2 appended without editing round 1 | met |
| every comparison PASS | **not met** — task 0 PASS; task 1 SOURCE-FACTOR RED (R2-1, R2-2) |
| scopes disjoint and complete; tools/GT closed; uuid8s (carried forward, task_tools.py unchanged) | met |
| trees: 1-3 prerequisites, ≥ max(n−1,1) value_input, user write, acyclic | met (task 0 n=2; task 1 n=3; all edges value_input; roots user-owned) |
| 4-6 factors, ≥2 parameter, ≥1 honest method per computation | **not met** — added_work_lining 3 (3/0), quote_overrun 4 (4/0); the other five computations meet it |
| every factor bears weight, honest baseline, fall-back definite ≠ gold | met on both worlds |
| ≥1 multi-source and ≥1 cross-difficulty factor per task | met |
| gates re-run on the final form | coordinator snapshot_r2 (16:21Z) on the audited hashes; not re-run by this audit |

Round-1 items: F-1, F-2, F-4, F-5, O-1, O-4, O-5, O-6, O-9, O-10, T0-3, T1-4 closed; F-3 closed as a factor but T1-1 still RED through its replacement (R2-2); O-2 partly closed (O-R2-1); O-8 closed except the unchanged fitting-fee escalation (low); T1-3 not closed (structural observation O-R2-4). New: R2-1 (RED, regression in quote_overrun), O-R2-1..O-R2-4 (observations).

Per-task verdicts (r2): **task 0 — PASS** (all four relationships); **task 1 — SOURCE-FACTOR RED** (policy, chain and unique solution PASS).

## revision_3

### charter_global_frozen (r3)

- Re-audit round 3. Freeze time 2026-10-13 16:55 UTC, before any round-3 GT was revealed; auditor: erl-task-policy-audit agent.
- Entry: ran /tmp/erl0061_coord/snapshot.sh alterations_and_tailoring 3 (2026-10-13T16:52:20Z) → .audit_views/policy/alterations_and_tailoring/snapshot_r3.txt: EXTENDED / TASK TOOL CONTRACT / REPLAY(--check) / SOLVABILITY / COMPUTE (branches=73.00 steps=18.00; history_rows_max=24 branches_max=79) / GROUNDING / SCOPE OK; traceability: only unlock tool_name misses, 0 non-tool_name misses; validate_scenario: only "required document … not found" errors. tasks/alterations_and_tailoring/rework_r3_claims.md present (read: item ids and prose, no figures). Rework landed.
- Inputs: alteration.extended.yaml **1ad84f08fffc7a5c (changed)**; task_tools.py 68f498099840b3c9 (unchanged); views 0.json b7bf41b69b1a702d (**unchanged world**), 1.json 304412958a397d7f (changed).
- Carried forward by reference (task_tools.py unchanged): action_binding_and_uuids (round 1). Re-derived in full: everything else. Base copy still verbatim.

### charter sweep (r3)

- Conflict scan, prerequisite graph and prerequisite sentences: same seven policies, tools and six state-form value_input edges; every policy_source verbatim in its own rule and absent from the depended-on rule; resolved_by / gates valid; acyclic. Unchanged from round 2 (§ revision_2), re-checked.
- Rule/compute: script sweep clean (every binding has a verbatim basis; every baseline.rule sentence in its rule; every tier in rule and compute). Manual sweep: waiver (four forms; co-pay ladder with fall-through "the whole rush fee standing"; reliefs now multiply the co-pay-form amount), deposit (per-operation / two-part / percentage), lining (flat / per-lined-operation count / percentage), overrun (count / percentage of the excess for one added operation at Platinum+ / percentage of the quote; honored amount floored at quoted_total), complimentary (one waiver per ticket; lined surcharge always stays chargeable; allowance falls through to 0), fitting fee (step basis; chargeable work = operation charges less every waiver; small-job lines 75/100) — each rule sentence has its compute and vice versa.
- Overrides: complimentary_work now declares five overwrites, including complimentary_basic's highest-price-first cap sentence and alteration_agg_complimentary_per_purchase (scoped "for a complimentary waiver this policy books, and only for such a waiver"); the lined-surcharge overwrite is scoped "This waiver covers the operation charge only". Other policies' declarations as round 2. No undeclared override.

### factor_ladders (r3) — method factors, same-formula test

Test applied to every method factor: does one tier's own formula, read on another tier's whole domain, reproduce that tier's value (one tier written as two)?

| policy | method factor | tiers | verdict |
| --- | --- | --- | --- |
| rush_fee | rush_charge_basis_form | count × 30.00 / flat 25.00 / rush_fee_pct of base | distinct — ok (unchanged) |
| rush_fee_waiver | member_waiver_form | whole / standing − co-pay (× reliefs) / 8.00 × operations capped at standing / nothing | distinct — ok |
| pre_work_deposit | deposit_form_by_record | 40.00 × operations capped at standing / minimum + rate × (standing − 250) / rate × standing floored and capped | distinct (two-part read below 250 gives the minimum, not max(minimum, rate × standing)) — ok |
| added_work_lining | lined_work_basis_form | flat 5.00 / 2.00 × (lined surcharges + 1) / rate × charge | distinct; fall-through reachable (one drop-off operation, first added operation) — **ok, R2-2 closed** |
| quote_overrun | quote_tolerance_form | 5.00 × added ops (≥2) / pct × excess (1 op, Platinum+) / pct × quoted | distinct — **ok, R2-1 closed** |
| complimentary_work | complimentary_waiver_form | whole / lesser of charge and allowance / nothing | distinct — ok |
| extra_fitting_fee | fitting_number_basis | fee × number (no needed-by) / fee + 5.00 for each extra fitting beyond the second (needed-by, n ≥ 3) / fee (needed-by, n ≤ 2) | **fails (R3-1)** |

Parameter factors: all ladders distinct and reachable for customers whose computation uses them; member_rush_copay and member_sale_work_allowance now fall through to the standard treatment (whole fee / 0) with three distinct reachable tiers inside their form (O-R2-3 closed). Counts after striking: rush_fee 6 (5/1), rush_fee_waiver 4 (3/1), pre_work_deposit 6 (5/1), added_work_lining 4 (3/1), quote_overrun 5 (4/1), complimentary_work 5 (4/1), **extra_fitting_fee 5 (5/0)**.

### findings (r3)

**R3-1 — SOURCE-FACTOR RED (new, introduced by the round-3 class sweep): fitting_number_basis writes one tier as two.** Bears on task 1.
- Evidence (rule): "on a ticket with a needed_by_date, an extra fitting numbered 3 or higher has a fee basis of extra_fitting_fee_usd plus 5.00 USD for each extra fitting beyond the second; on a ticket with a needed_by_date, an extra fitting numbered 1 or 2 has a fee basis of extra_fitting_fee_usd." Compute: `base_fee + K('late_fitting_step') * (fitting_number - 2) if fitting_number >= 3 else base_fee`.
- Demonstration: the tier-2 rule itself, read on fittings 1 and 2, finds no extra fitting beyond the second and gives extra_fitting_fee_usd + 0 = the tier-3 value; `extra_fitting_fee_usd + 5.00 × max(0, n − 2)` reproduces both tiers on their whole domains — the same pattern as R2-2's "first 100.00 USD of its charge". Round 2's version (twice the fee from the third fitting) passed this test; the replacement does not. The ladder has two distinct methods (fee × number / fee plus a step beyond the second); struck, the fitting-fee computation has 5 parameter factors and no `method`.
- Affected: alteration_ext_extra_fitting_fee rule, compute `fee_basis`, factors[fitting_number_basis]; tasks/1.json computations (fitting fee).

Observations (r3):
- O-R3-1 pre_work_deposit: the per-operation form ("40.00 USD for each operation charge on the ticket, never more than the standing charges") has no deposit_min_usd floor, while the policy's own overwrite text says the deposit is taken "at least deposit_min_usd and never more than the standing charges". On a hypothetical Bridal ticket (minimum 100.00) with two operations for a customer with three uncollected-pickup refunds the two passages give 80.00 and 100.00. Neither world reaches the per-operation form (latent).
- O-R3-2 complimentary_work: "one complimentary waiver is booked per ticket" for this policy while "every other complimentary waiver remains under the base allowance rule": a regular-price ticket with two qualifying operations leaves the second operation's treatment (base complimentary vs charged) to the base rule, which has no tool here. Latent (task 1 has one qualifying operation).
- Closed in r3: O-R2-1 (lined surcharge row promise dropped; cross-ticket count retired by declared overwrites), O-R2-2 (honored amount floored at quoted_total), O-R2-3 (nested fall-throughs are the standard treatment), O-R2-4/T1-3 (see task 1). O-8: escalation without a needed-by date unchanged (low).

### closing_checklist (r3)

Written after the round-3 reveal (16:55:50 UTC). The difficulty does **not** close.

| item | status |
| --- | --- |
| files ↔ tasks; revision_3 appended, earlier revisions untouched | met |
| every comparison PASS | **not met** — task 0 PASS; task 1 SOURCE-FACTOR RED (R3-1) |
| scopes, tools, GT closure, uuid8s | met |
| trees (n = 2 and 3, all value_input, user-owned roots, acyclic) | met |
| 4-6 factors, ≥2 parameter, ≥1 honest method per computation | **not met** — extra_fitting_fee 5 (5/0); the other six computations meet it |
| every factor bears weight; fall-backs definite ≠ gold | met on both worlds |
| ≥1 multi-source and ≥1 cross-difficulty factor per task | met |
| gates on the final form | snapshot_r3 (16:52:20Z, run by this auditor via the coordinator script) on the audited hashes |

Round-2 items: R2-1 closed, R2-2/T1-1 closed, O-R2-1..O-R2-4 closed (T1-3 closed). New: R3-1 (RED, regression introduced by the class sweep in fitting_number_basis), O-R3-1 and O-R3-2 (latent observations).

Per-task verdicts (r3): **task 0 — PASS**; **task 1 — SOURCE-FACTOR RED (R3-1)**, with policy, chain and unique solution PASS.

## revision_4

### charter_global_frozen (r4)

- Re-audit round 4; freeze 2026-10-13 19:30 UTC, before the round-4 GT was opened; auditor: erl-task-policy-audit agent.
- Entry: ran /tmp/erl0061_coord/snapshot.sh alterations_and_tailoring 4 (2026-10-13T19:28:48Z) → snapshot_r4.txt: EXTENDED / TASK TOOL CONTRACT / REPLAY(--check) / SOLVABILITY / COMPUTE (branches=80.00 steps=18.00; history_rows_max=24 branches_max=87) / GROUNDING / SCOPE OK; traceability: only unlock tool_name misses, 0 non-tool_name misses; validate_scenario: only "required document … not found". rework_r4_claims.md present (no figures). Rework landed.
- Inputs: alteration.extended.yaml **a590eb09cdb1a94c (changed)**; task_tools.py 68f498099840b3c9 (unchanged → action_binding_and_uuids carried by reference); views 0.json b7bf41b69b1a702d and 1.json 304412958a397d7f (both **unchanged** since round 3). Base copy still verbatim. The worklog (which the claims cite for a pairwise table) was not read.

### charter sweep (r4)

- Graph and sentences: seven policies, six state-form value_input edges; each policy_source verbatim in its own rule, absent from the depended-on rule; resolved_by and gates valid; acyclic.
- Rule/compute: script sweep clean (bases verbatim, baseline sentences in rules, tiers in rule and compute). Manual sweep of the round-4 changes: card tiers now read "holding an active Elite / World Elite account" vs "active accounts none of which is one of those" vs none (EXISTS reads — no first-match dependence); complimentary card window tests whether the purchase's card account is an active account of the customer; occasion discount prefers a Wedding Registry among active registries on the needed-by date; fitting-fee proximity and wedding credit read the active Wedding Registry, with Anniversary/Celebration as the second credit tier; lining prices the higher operation on a shared latest date and owes nothing with no operation; per-operation deposit now floored at deposit_min_usd and capped at standing charges in rule and compute (O-R3-1 closed); complimentary override now says "any further qualifying operation on that ticket stays chargeable" (O-R3-2 closed). Each change has its rule sentence and its compute.
- Overrides: as round 3, with the extended complimentary replaced_by; no undeclared override.

### method factors — coinciding-tier check on reachable domains (all seven policies)

For each pair of tiers: does one tier's formula reproduce the other tier's value on the other tier's whole reachable domain?

| policy | tiers (domain → formula) | pairwise result |
| --- | --- | --- |
| rush_fee / rush_charge_basis_form | n≥3 → 30n; n≤2, base<80 → 25; n≤2, base≥80 → pct × base | 30n ∈ {30, 60} ≠ 25; pct × base = 25 only at one base value; no whole-domain coincidence |
| rush_fee_waiver / member_waiver_form | Gold/Plat + own purchase → s − co-pay (× reliefs); Gold/Plat, no own purchase → min(s, 8n); else → standard (s for a flag tier, 0 otherwise) | co-pay formula gives 0 on non-flag customers of the standard tier but not s on Diamond/Icon; min(s, 8n) ≠ s − co-pay in general; none coincides on a whole domain |
| pre_work_deposit / deposit_form_by_record | ≥3 uncollected refunds → clamp(40n, min, S); S≥250 → min + p(S−250); else → clamp(pS, min, S) | two-part = percentage only where min = 250p (a single rate); per-operation independent of p; distinct |
| added_work_lining / lined_work_basis_form | charge<40 → 5.00; charge≥40, k≥2 → 2(k+1); charge≥40, k<2 → pct × charge | 2(k+1) ≤ 4 < pct × charge (≥ 8 at 20%); pct × charge = 5 only at one charge; distinct |
| quote_overrun / quote_tolerance_form | added≥2 → 5n; added=1, Platinum+ → pct × excess; else → pct × quoted | 5 × 1 ≠ pct × excess in general; pct × excess = pct × quoted only where excess = quoted; distinct |
| complimentary_work / complimentary_waiver_form | regular → charge; sale, Gold+ → min(charge, allowance); else → 0 | min(charge, allowance) gives 0 on the sale-below-Gold part of the third tier but not on clearance/final-sale Gold+ purchases; not charge for regular non-members; distinct |
| extra_fitting_fee / fitting_number_basis | no needed-by → fee × n; needed-by 0-14 days → fee + 10% × operations; later or passed → fee | fee × n = fee only at n = 1; fee + 10% × operations > fee whenever an operation is booked; distinct — **R3-1 closed** |

Every tier of every method factor is reachable; the fall-through of each is the policy's standard treatment. Parameter ladders re-checked: distinct values, conditions reachable within the computation that uses them. Counts: rush_fee 6 (5/1), rush_fee_waiver 4 (3/1), pre_work_deposit 6 (5/1), added_work_lining 4 (3/1), quote_overrun 5 (4/1), complimentary_work 5 (4/1), extra_fitting_fee 6 (5/1).

### findings (r4)

- R3-1: **closed**. O-R3-1, O-R3-2: closed. O-8: the rule now states the business reason for each fitting-fee form (observation retired).
- No new SOURCE-* RED in the charter.
- Observation O-R4-1 (latent, not reached by either task): pre_work_deposit's compute evaluates `deposit_by_form` (which reads `P('deposit_min_usd')`) before the `class_owes` gate, so on a ticket in a class with deposit_pct 0 (deposit_min_usd not_applicable) the evaluation raises a type error instead of returning the out-of-scope 0. Probe: task 1's Standard Alterations ticket with the card, loyalty, registry and purchase records stripped → `'>' not supported between 'float' and 'str'`. The rule itself is unambiguous ("A ticket in a class whose deposit_pct is above 0 owes a deposit"), so no second reading arises; the reworker's claim "every policy takes its fall-through tier without error" does not hold for this policy outside its scope.

### closing_checklist (r4)

Written after the round-4 GT was opened (19:30:53 UTC).

| item | status |
| --- | --- |
| files ↔ tasks; revision_4 appended, earlier revisions untouched | met |
| every comparison PASS | met — task 0 PASS, task 1 PASS |
| extended policies covered; scopes disjoint (task 0: rush_fee, rush_fee_waiver, pre_work_deposit; task 1: added_work_lining, quote_overrun, complimentary_work, extra_fitting_fee); tools/GT closed; uuid8s independent (task_tools.py unchanged since round 1) | met |
| trees: task 0 n=2, task 1 n=3; all edges value_input; roots user-owned; difficulty graph acyclic | met |
| every computation 4-6 factors, ≥2 parameter, ≥1 method with no coinciding tiers, ladders reachable, rule states every tier | met — 6 (5/1), 4 (3/1), 6 (5/1), 4 (3/1), 5 (4/1), 5 (4/1), 6 (5/1) |
| every factor bears weight against an honest baseline; fall-backs definite and ≠ gold | met (task 0: 155.00 / 0.00 / 170.41; task 1: 6.40 / 24.70 / 0.00 / 15.00) |
| per task ≥1 multi-source and ≥1 cross-difficulty factor, other-product rows seeded | met |
| instantiation gates on the final form | snapshot_r4 (2026-10-13T19:28:48Z) on charter a590eb09cdb1a94c / task_tools 68f498099840b3c9 / views b7bf41b69b1a702d, 304412958a397d7f: all OK; traceability and validate_scenario pending only the KB render |

Open items: none at RED. Observations carried: O-R4-1 (deposit compute raises a type error out of scope, on deposit_pct-0 classes); O-11 (traceability/validate_scenario await the KB render).

Per-task verdicts (r4): **task 0 — PASS; task 1 — PASS.** The difficulty passes the source-layer audit.

## revision_5

### charter_global_frozen (r5)

- Re-audit round 5 (2026-10-14); freeze 2026-10-14 19:51 UTC, before the round-5 GT was opened; auditor: erl-task-policy-audit agent. Scope: the alteration renderer's source items (audits/render_source/alterations_and_tailoring/render_r1_alteration.md, read in full; item 6 is base text, logged by the coordinator, no action) and O-R4-1.
- Entry: ran /tmp/erl0061_coord/snapshot.sh alterations_and_tailoring 5 (2026-10-14T19:49:55Z) → snapshot_r5.txt: EXTENDED / TASK TOOL CONTRACT / REPLAY(--check) / SOLVABILITY / COMPUTE (branches=86.00 steps=18.00; history_rows_max=24 branches_max=94) / GROUNDING / SCOPE OK; **TRACEABILITY OK** (0.json 22/0, 1.json 24/0); validate_scenario: only "required document … not found" errors. rework_r5_claims.md present (no figures). Rework landed.
- Inputs: alteration.extended.yaml **b7b4163e17873ec2 (changed)**; task_tools.py **2ff38c739313e218 (changed)**; views 0.json b7bf41b69b1a702d (unchanged), 1.json 96f122c47ff891a8 (persona changed; initial_state identical to round 3-4). Base copy still verbatim. Every charter-global section re-derived (both shared inputs changed).

### charter sweep (r5)

- Tools: seven functions, same names, owners, signatures and uuid8s; every body still creates one alteration_charges row and moves balance_due, with no condition, error or refusal. book_extra_fitting_87db3b08's docstring, Returns text and confirmation now say the call records the extra fitting fee with the fitting's number and "does not set a date or time for the fitting" — matching the body (render item 5 closed). No docstring names another tool or a sequence; no concrete example value in any docstring.
- Graph and sentences: seven policies, six state-form value_input edges; each policy_source verbatim in its own rule, absent from the depended-on rule; resolved_by and gates valid; acyclic. Unchanged.
- Rule/compute: script sweep clean (bases verbatim, baseline sentences in rules, tiers in rule and compute). Four method factors now decide a form label (waiver co_pay / per_operation / standard; deposit per_operation / two_part / percentage; overrun per_operation / excess / quote; complimentary whole_charge / allowance / no_waiver) and the result binding assembles the amount; each assembly is quoted from a combining sentence of the rule ("The rush fee waiver is assembled from its form: …", "The deposit is assembled from its form: …", "The quote tolerance is assembled from its form: …", "The complimentary waiver is assembled from its form: …") (render item 3 closed). Scope guards: rush fee result only when rush_service is true ("A ticket accepted with rush service owes one rush fee"); lining result only when the latest operation is after drop-off and lined surcharges are fewer than operations; deposit result only when deposit_pct > 0 (O-R4-1 closed — probe below).
- Factor ownership: mechanical listing over all seven policies (every factor binding, followed through non-factor plumbing bindings) — no factor binding reads a binding owned by another factor (render items 1 and 2 closed: premium_garment_addition reads only regular_price; complimentary_waiver_form and quote_tolerance_form read the tier through their own CPARAM; wedding_party_credit reads the Wedding Registry date through its own `wedding_event`).
- Overrides: every replaced_by opens with its scope ("For a … this policy books/works out/prices, and only for such …") and ends by leaving everything else under the base rule, including the lined-surcharge overwrite of complimentary_basic (render item 4 closed). No undeclared override.
- Uncollected-order addition now states "none for none or for three or more, since three or more such refunds put the deposit in the per-operation form" (render item 7 closed).
- Probe (auditor's script, both views with card, loyalty, registry, purchase and order rows removed, needed_by and purchase link blanked, and again with no charges): all seven policies evaluate without error; the Standard Alterations deposit returns 0 (round 4 raised a type error).

### method factors — coinciding-tier check (r5)

The assembled formulas per form are those of round 4 (§ revision_4 table): rush basis 30n / 25.00 / pct × base; waiver min(s, (s − co-pay)⁺ × (1 + reliefs)) / min(s, 8n) / standard; deposit clamp(40n) / min + p(S − 250) / clamp(pS); lining 5.00 / 2(k + 1) / pct × charge; overrun tolerance 5n / pct × excess / pct × quoted; complimentary charge / min(charge, allowance + premium) / 0; fitting basis fee × n / fee + 10% × operations / fee. No pair coincides on a whole reachable domain; every tier reachable; every fall-through is the standard treatment. Counts unchanged: 6 (5/1), 4 (3/1), 6 (5/1), 4 (3/1), 5 (4/1), 5 (4/1), 6 (5/1).

### findings (r5)

- Render items 1, 2, 3, 4, 5, 7 and O-R4-1: **closed**. Render item 6: base text, no action (not a finding of this audit).
- No SOURCE-* RED in the charter.
- Observation O-R5-1 (latent, pre-existing, not a regression): the lining policy's rule applies to "a lined garment's ticket", but the schema carries no lined flag and the new `surcharge_owed` guard (latest operation after drop-off, fewer lined surcharges than operations) is also true for an unlined garment with an added operation, where the rule owes nothing. The rule is unambiguous, so no second reading arises; neither world reaches it (task 0 has no added operation; task 1's garment is described "lined" and carries lined surcharges).

### closing_checklist (r5)

Written after the round-5 GT was opened (2026-10-14 19:51:52 UTC).

| item | status |
| --- | --- |
| files ↔ tasks; revision_5 appended, earlier revisions untouched | met |
| every comparison PASS | met — task 0 PASS, task 1 PASS |
| policies covered; scopes disjoint; tools/GT closed; uuid8s unchanged and independent; tool effects match docstrings | met |
| trees (n = 2 and 3, all value_input, user-owned roots, acyclic) | met |
| 4-6 factors, ≥2 parameter, ≥1 method with no coinciding tiers; no factor reads another factor's binding | met |
| every factor bears weight against an honest baseline; fall-backs definite ≠ gold | met (155.00 / 0.00 / 170.41; 6.40 / 24.70 / 0.00 / 15.00) |
| ≥1 multi-source and ≥1 cross-difficulty factor per task | met |
| gates on the final form | snapshot_r5 (2026-10-14T19:49:55Z) on charter b7b4163e17873ec2 / task_tools 2ff38c739313e218 / views b7bf41b69b1a702d, 96f122c47ff891a8: all OK including traceability; validate_scenario only missing-document errors |

Renderer items 1-5, 7 and O-R4-1 closed; item 6 base text (coordinator-logged). Open REDs: none. Observations carried: O-R5-1 (lining guard does not see "lined"; latent).

Per-task verdicts (r5): **task 0 — PASS; task 1 — PASS.**
