# Policy-task audit — damage_claims_and_protection / charter-global

## charter_global_frozen

- Round: 1 (no earlier revision exists; this directory did not exist before this round).
- Freeze time: written after 2026-10-07T19:03:44Z (directory creation) and hashed at 2026-10-07T19:07:05Z, before any reveal. Auditor: independent policy-task auditor (Claude agent); not the instantiating agent.
- Frozen inputs (sha256, re-checked from the repo root before writing):
  - `tasks/damage_claims_and_protection/protect.extended.yaml` e56da7e0e2a613dad1671b3dc21d424cc696df9c69638082419a19697e5e363c
  - `tasks/damage_claims_and_protection/task_tools.py` 9109faa63b15fbf3d117634f5696e0fe8cf378359da550338abe67bf6cddb8a0
  - blind views `/tmp/erl45_views/r1/damage_claims_and_protection/task_0.view.json` 8b009a6d…63f4a7, `task_1.view.json` 4b4f04d9…5e363c (`sha256sum -c SHA256SUMS`: both OK).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/protect.yaml`, the host/listing charter passages the cross-category factors read (`products/host.yaml` host_evt_service_fee, host_evt_cancellation_penalty, tier params; `products/listing.yaml` listing_evt_quality_assessment, listing_evt_calendar_block), the extended charter and the tool module.
- Masked and not read when this section was written: every `tasks/*.json` field outside the three view fields (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `tasks/damage_claims_and_protection/worklog.md`, the scenario `worklog.md`. Nothing here derives from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire green; check_cache_diff INFO; check_traceability NOT OK, expected before KB rendering). The masked views and their hashes were supplied. Entry conditions met; the gates were not re-run by the auditor.

### policy_conflict_scan

- Base copy: lines 1-860 of the extended charter are byte-identical to `blueprint/products/protect.yaml` (`diff` differs only by one trailing blank line at line 861).
- Extended policies (5), all with subject `[protect_reimbursement_paid]`, `computes: amount`:

| policy | target_tool | owner | trigger | prerequisite |
| --- | --- | --- | --- | --- |
| protect_ext_theft_settlement | pay_theft_reimbursement_c380c173 | agent | state_due | [] |
| protect_ext_valuables_settlement | accept_valuables_settlement_01cb0de3 | user | on_request | theft (value_input, state) |
| protect_ext_property_settlement | pay_property_damage_reimbursement_941cbbf5 | agent | state_due | [] |
| protect_ext_pet_damage_settlement | pay_pet_damage_reimbursement_a5391300 | agent | state_due | [] |
| protect_ext_income_loss_settlement | accept_income_loss_settlement_ab094655 | user | on_request | property, pet (value_input, state) |

- Overlapping subject: all five write `protect_reimbursement_paid`, but each is scoped by `damage_category` (theft / valuables / property_damage / pet_damage / income_loss) of the approved claim; the categories are an enum of `protection_claims.damage_category`, so no claim falls under two extended policies. deep_cleaning remains under base `protect_evt_reimbursement` only.
- Shared quantities across policies: (a) the stay's deductible — theft/property/pet take an order-independent equal share `deductible_usd / approved claims on the stay`, valuables/income take `deductible_usd × (approved − reimbursed)/approved`, which depends on order; that order is fixed by the declared prerequisite sentences (theft before valuables; property and pet before income). Since property and pet use the order-free equal share and neither reads the other's reimbursement except through the plan-year aggregate and the "claim from another stay" counts (both exclude or are insensitive to same-stay claims while the aggregate is far from binding), the parallel property/pet edges do not conflict in the abstract; per-world check in task 1. (b) the remaining plan-year aggregate and paid-claim count (base `protect_agg_plan_year_limits`) — every extended policy reads the aggregate, none modifies the count rule.
- Eligibility, time anchors and terminal states: every extended rule states "every base condition on paying a claim (approval, escalation in time, coverage of the stay, one reimbursement per claim) continues to apply"; no extended policy restates or weakens a base gate. Terminal state of each tool: one `protect_reimbursement_paid` row; consistent with base event definition.
- Cross-category read boundaries: listing (space type, photo_count, pet_fee, quality_outcome, calendar block), host (tier, superhost_since, host_service_fee_assessed date, host_cancellation_recorded band/initiator). All are reads; no extended policy writes outside protection_events.
- Scope of the M=2 tasks against the charter (from the views' worlds and personas only, pending reveal): task 0 = valuables (root, user tool) + theft (prerequisite); task 1 = income loss (root, user tool) + property + pet (prerequisites). The two scopes are disjoint and jointly cover all five extended policies.
- Observation (not one of the four relationships): the blueprint claim for this difficulty lists six event types (`protect_guest_payment_requested, protect_reimbursement_paid, protect_claim_denied, protect_premium_refunded, protect_plan_tier_changed, protect_plan_cancelled`); the extended charter extends only `protect_reimbursement_paid`. The other five claimed event types are exercised by no extended policy and no task.

### rule_compute_equivalence

Swept every `compute` binding of the five policies against its `compute_basis` quotation and back against the `rule` sentences.

- Quantities, filters and branches: every binding has a verbatim quotation in its own `rule`; every ladder tier named in `factors[].ladder` appears both as a rule sentence and as a branch of the `decides` binding (theft: th_dep_pct, th_access_pct, th_ded_factor, th_offset, th_documentation_pct, th_escalation_pct; valuables: va_dep_pct, va_access_pct, va_new_cover_pct, va_escalation_pct, va_ded_factor, va_offset; property: pr_dep_pct, pr_condition_pct, pr_escalation_pct, pr_ded_factor, pr_offset; pet: pe_dep_pct, pe_fee_pct, pe_condition_pct, pe_escalation_pct, pe_offset; income: in_valued_loss, in_timing_pct, in_escalation_pct, in_new_cover_pct, in_offset). No tier lives only in compute; no rule tier is missing from compute.
- Order of operations / rounding: each rule's closing sentence ("first reduced by … then multiplied … with no rounding between these steps … only that figure is rounded") matches `*_covered → *_net = MX(0, covered − offset) → RND(MN(net, cap), 2)`.
- Caps: theft/valuables/pet cut to sublimit, per-claim limit and remaining aggregate; property/income to per-claim limit and remaining aggregate ("carries no category sublimit"), matching base.
- Observation O-RC1 (window drift, no consequence demonstrated): rule "the reimbursements, net of recoveries, posted on the plan in the current plan year" is implemented as `within_months=MONTHS(F('plan_year_start'), NOW) + 1` counted back from NOW, not as `posted_date >= plan_year_start`; the two can disagree when a reimbursement is posted in the extra part-month before plan_year_start. Neither task world has any prior `protect_reimbursement_paid`/`recovered` row, so no scored value is affected; recorded as an observation only.
- Observation O-RC2: "the 12 months before the settlement date … claim from another stay" is implemented as COUNT of reimbursement rows in 12 months minus COUNT of reimbursement rows on the same stay (the second unwindowed). Equivalent whenever the same stay has no reimbursement older than 12 months, which a single stay cannot have in practice. No consequence.
- Observation O-RC3: the "stay's check-in date" in theft/property deductible factors and the new-cover shares is read from the host_service_fee_assessed event date rather than `stays.check_in_date`; the rule states it so ("the date the host service fee was assessed on the stay"), and the host charter assesses the fee at check-in. Equivalent in both worlds (task 0: 2026-08-24 = check_in_date; task 1: 2026-08-14 = check_in_date).

### action_binding_and_uuids

- Each `(target_tool, computes=amount)` is claimed by exactly one extended policy (table above); no base policy names a target tool.
- Tool bodies (`task_tools.py`): each of the five tools only reads the claim row for linkage and creates one `protect_reimbursement_paid` row with the passed amount; none computes, validates approval, checks prerequisites, refuses, or hints. Docstrings carry no sequencing word that names another tool or problem ("from then on", "at once" describe the write's own visibility).
- uuid8s: c380c173, 01cb0de3, 941cbbf5, a5391300, ab094655 — no shared prefix or suffix, no sequential pattern, no reuse; consistent with independent generation.
- Business reading of each docstring is unique (agent books a reimbursement on one approved claim of the named category; user accepts an agreed-value / lost-income settlement in person). PASS.

### prerequisite_graph

- `prerequisite` filled on all five policies (`[]` on theft, property, pet).
- Edges: valuables → theft; income → property; income → pet. All `problem` ids are extended policies of this file; no self-reference; no base target; graph acyclic (depth 1).
- `policy_source` verbatim in the blocked policy's own rule: valuables "Where the same stay also carries an approved theft claim, the valuables settlement is fixed only after the plan's HostCover ledger shows a reimbursement on that theft claim." (rule line 1182-1184) ✓; income "The income-loss settlement is not fixed until the plan's HostCover ledger shows a reimbursement on every approved property-damage claim of the same stay." ✓ and "The income-loss settlement is likewise not fixed until the ledger shows a reimbursement on every approved pet-damage claim of the same stay." ✓
- `form: state` on all three, no `fallback_reason` (correctly absent).
- `condition` matches the sentence's strength (single theft claim of that stay; every approved property/pet claim of the stay); not strengthened or weakened.
- `resolved_by` equals the depended-on policy's `target_tool` in all three; the write creates exactly the `protect_reimbursement_paid` row the condition names.
- `kind: value_input`, `gate` va_stay_settled / in_stay_settled — both bindings exist and enter `va_ded_share` / `in_deductible`; `effect` text agrees with the formula (valuables: 250×(2−0)/2 → 250×(2−1)/2 on a two-claim stay; income: one equal share less per settled claim).
- No authoring-viewpoint phrasing in `prerequisite`. PASS.

### prerequisite_sentences

- Four-point test, all three sentences: ordering connective present ("only after", "not until", "likewise not until"); waited-on object is a record-visible state named in finder words ("the plan's HostCover ledger shows a reimbursement on …" — the `find_protection_events` docstring calls protection_events "the HostCover ledger" and lists reimbursements); no tool name, policy id, snake_case token or row id; scope matches condition (one theft claim / every approved claim of the category on the same stay).
- One write per state: a reimbursement on an approved theft claim is booked only under protect_ext_theft_settlement (the valuables tool books on valuables claims); on property claims only under protect_ext_property_settlement; on pet claims only under protect_ext_pet_damage_settlement. Single reading.
- Derivation the reader performs: valuables rule → "ledger shows a reimbursement on that theft claim" → find_protection_claims on the stay shows an approved theft claim → find_protection_events shows no reimbursement on it → the theft rule is the rule that "settles a theft claim … the figure it produces is the theft reimbursement Roamhaven books on that claim" → book it, then settle valuables. Same pattern for income → property, pet.
- The depended-on rules (theft, property, pet) do not restate the sentence and name no dependent; each blocked rule states the dependency once.
- No other cross-problem order stated in any extended rule. Base rule sentences carrying an order ("Roamhaven pays a claim only after the guest has not paid it in full", "A claim is escalated … only after the guest's response deadline has passed") concern user/guest acts already complete in both worlds and ground no edge. PASS.

### override_declarations

Sentence-by-sentence against base `protect_evt_reimbursement` (and `protect_agg_plan_year_limits`) for each extended policy:

| base sentence | theft | valuables | property | pet | income |
| --- | --- | --- | --- | --- | --- |
| "Roamhaven pays a claim only after the guest has not paid it in full"; approval; escalation window; coverage of stay | inherited ("continues to apply") | inherited | inherited | inherited | inherited |
| "start from the verified loss;" | overwritten, declared | declared | declared | declared | declared |
| depreciation_schedule for property/pet/theft/valuables | follows base (20/40/60 on 13-36/37-60/61+, 0 on 0-12; same values via theft_dep_pct_*) | **differs** (10/20/30 on 13-60/61-120/121+), declared | follows base (property_dep_pct_* = 20/40/60) | follows base (pet_dep_pct_*) | n/a ("no depreciation", inherited) |
| deep-cleaning offset | n/a | n/a | n/a | n/a | n/a |
| "subtract every guest payment recorded on the claim (net of reversals)" | declared | declared | declared | declared | declared |
| "subtract deductible_usd" | declared (equal share) | declared (unborne remainder) | declared (equal share) | declared (equal share) | declared (unborne remainder) |
| "floor at 0.00; then cut to the category's sublimit, per-claim limit, remaining aggregate" | follows | follows | follows (no sublimit) | follows | follows (no sublimit) |
| income_loss "its verified loss is the nightly subtotal … for at most income_loss_max_nights nights" | n/a | n/a | n/a | n/a | declared (lost-nights method) |
| "A payable amount of 0.00 is recorded as a denial, not a payment"; "A claim is reimbursed once"; credited to default payout method | inherited | inherited | inherited | inherited | inherited |
| protect_agg_plan_year_limits (aggregate, paid-claim count, claim_limit_reached) | inherited | inherited | inherited | inherited | inherited |

- The multiplicative shares (access, documentation, condition, pet-fee, new-cover, escalation, timing) are inserted between "start from the verified loss" and the subtractions; they are covered by the declared replacement of "start from the verified loss;" whose `replaced_by` names each share. No anonymous intermediate factor, no 0/1 multiplier on a base-fixed amount (income tier "not covered → nothing payable" restates the base coverage condition), no dropped base branch found.
- Finding: no undeclared override. Merged semantics unique per category.

### factor_ladders

Per policy (label / decides / tiers incl. fall-through / multi-source / cross_difficulty):

- theft (6): depreciation P / th_dep_pct / 4 / (plan level param × claim age: two records) / – ; access P / th_access_pct / 3 / – / listing; deductible factor P / th_ded_factor / 3 / yes (host tier + Superhost run × plan reimbursement history) / host; guest-payment M / th_offset / 3 / – / –; documentation P / th_documentation_pct / 3 / – / listing; escalation P / th_escalation_pct / 3 / – / –.
- valuables (6): depreciation P 4; access P 3 listing; new-cover P 3 host; escalation P 3; deductible factor P 3 multi-source host; guest-payment M 3.
- property (5): depreciation P 4; condition P 3 listing; escalation P 3; deductible factor P 3 multi-source (host tier × listing space type; Superhost run × reimbursement history) host; guest-payment M 3.
- pet (5): depreciation P 4; pet-fee P 3 listing; condition P 3 listing; escalation P 3; guest-payment M 3.
- income (5): lost-nights M / in_valued_loss / 3 / yes (plan level coverage × listing calendar block) / listing; cancellation timing P 3 host; escalation P 3; new-cover P 3 host; guest-payment M 3.
- Bindings within each policy are pairwise disjoint; every `decides` is an input, never `result`. Every tier is stated in the rule with its condition and value/method; every value is a K()/charter param or the stated fall-through. Fall-through of each factor = the factor's `baseline`, and each `baseline` agrees with `baseline.rule` (which states no depreciation, no share, factor 1, and "every guest payment … is subtracted together with the deductible").
- Labels: depreciation/access/documentation/condition/pet-fee/new-cover/escalation/timing/deductible-factor tiers substitute a number → `parameter` honest. Lost-nights tiers change the valuation (nothing / proration by max-nights over blocked nights / whole) → `method` honest.

**F-G1 (SOURCE-FACTOR RED, charter-global, bears on tasks 0 and 1): the guest-payment method ladder has only two distinct outcomes; tiers 2 and 3 select the same subtraction.** In all five policies the ladder is: T1 "net guest payments above 0.00 and at least the deductible → subtract the payments alone"; T2 "above 0.00 but below that deductible → subtract the deductible alone"; T3 fall-through "no net guest payment stands → subtract the guest payments and the deductible both" (compute e.g. `th_offset: th_guest_paid if (th_guest_paid > 0 and th_guest_paid >= th_deductible) else (th_deductible if (th_guest_paid > 0 and th_guest_paid < th_deductible) else th_guest_paid + th_deductible)`). T3's domain is "no net guest payment stands", i.e. net payments = 0.00 (a reversal only reverses a recorded payment; the base event `protect_guest_payment_reversed` is "A guest payment on a claim is reversed", so net payments below zero do not occur). On that domain T3's "payments + deductible" = 0.00 + deductible = T2's "deductible alone". Extensionally the ladder is the single rule "subtract the larger of net payments and deductible", with two outcomes (payments vs deductible), not three; one tier has been written as two. Under the factor tests this ladder has fewer than three distinct tiers, so the factor is struck out, and theft, valuables, property and pet are each left with **zero** surviving `method` factors (income keeps the lost-nights method). The per-task demonstration is in each task file.

**F-G2 (SOURCE-FACTOR RED, charter-global, bears on task 0): the theft documentation share rests on a condition the line of business does not weigh for that quantity.** Rule: "The theft documentation share follows how fully the listing's own photos document the space the items were taken from, counted as the number of photos on the listing the plan covers: a listing with fewer than 10 photos settles the theft at theft_photos_under_10_share_pct percent, one with 10 to 19 photos at theft_photos_10_19_share_pct percent, and one with 20 or more photos in full." The listing's photo_count is the count of marketing photos shown to guests (`listings.photo_count` "photos on the listing"; `find_listings` lists it among the listing's display settings). A theft settlement turns on proof that the stolen items existed and were taken; the charter itself handles that as a gate — `evidence_required` "dated photos or video of the damage and a repair estimate, invoice or receipt", with the claims team's `evidence_status` and the `insufficient_evidence` denial reason. No host-protection programme or property insurer scales a theft payout by how many marketing photos the listing carries: listing photos do not document portable stolen items (a watch, earrings, a laptop), and evidence sufficiency is already decided (`evidence_status: complete`) before the settlement. The tier conditions therefore divide customers on a ground the business does not weigh for the theft payable, and the 90 % / 80 % outcomes are treatments no such business publishes. This is fabricated against the stated realism requirement of this run.

Observations on ladder realism (no RED; recorded because realism is a stated priority):
- O-L1 escalation shares (all five policies): a percentage haircut for escalating later *within* the escalation window that the base declares sufficient ("an escalation on the last day standing"). Timeliness of notice is something the line weighs (benefit reductions for late notification exist in other insurance lines), so not recorded as RED, but no vacation-rental host-protection programme publishes a graded payout by escalation day.
- O-L2 theft/valuables access share (Shared Room 50 %/25 %, Private Room 75 %/50 %): has an insurance analogue (theft by persons with lawful access to shared quarters is limited or excluded in homeowner forms); acceptable.
- O-L3 property/pet condition share by the listing's most recent quality review outcome: ties to the pre-existing-damage and wear exclusions the charter states; but "most recent" can be a review dated after the damaging stay (task 1: 2026-10-01). Borderline realism.
- O-L4 pet-fee share: a 10-20 % cut on pet damage because the listing charges a pet fee, justified as "priced in the ordinary wear pets bring", while ordinary wear is already excluded outright (`wear_and_tear_excluded`); double-counts a charter exclusion. Borderline realism.
- O-L5 valuables: the rule calls the settlement "an agreed value that the host accepts in person" and then depreciates it by item age; agreed-value cover in practice does not depreciate. Wording tension, values declared.

Counts (before striking): theft 5P+1M, valuables 5P+1M, property 4P+1M, pet 4P+1M, income 3P+2M; all within 4-6. After F-G1 and F-G2: theft 4P+0M (documentation and guest-payment struck), valuables 5P+0M, property 4P+0M, pet 4P+0M, income 3P+1M.

### findings

| id | verdict | tasks it bears on |
| --- | --- | --- |
| F-G1 guest-payment method ladder has two outcomes, not three; theft/valuables/property/pet keep no method factor | SOURCE-FACTOR RED | task 0 (theft, valuables), task 1 (property, pet) |
| F-G2 theft documentation share keyed to listing marketing-photo count | SOURCE-FACTOR RED | task 0 (theft) |
| O-RC1 plan-year window implemented as months-back-from-now | observation | none demonstrated |
| O-RC2, O-RC3 | observation | none |
| O-L1..O-L5 ladder realism | observation | 0 and 1 |
| claim lists six event types, charter extends one | observation | — |

Policy self-consistency (charter half): no undeclared override, rule/compute equivalent, action binding unique, prerequisite graph and sentences pass. The charter-global REDs are both under the factors relationship.

## closing_checklist

Written after both reveals (reveal at 2026-10-07T19:07:05Z); nothing above this heading was edited after any reveal.

- Per-task files: `task_0.md`, `task_1.md` correspond one-to-one with tasks 0 and 1; round 1, no older revisions. Comparison sections carry **SOURCE-FACTOR RED** for both tasks, so the difficulty is **not closed**.
- Coverage and scopes: charter_scope task 0 = {theft, valuables}, task 1 = {property, pet, income}; pairwise disjoint, jointly complete over the five extended policies; each tool has an independent uuid8 — PASS.
- Problem trees: task 0 one prerequisite (1 value_input), task 1 two prerequisites (2 value_input); each root an owner=user write; whole-difficulty graph acyclic — PASS.
- Factors: every factor bears weight against an honest baseline and every whole-baseline fall-back is definite and differs from gold (task 0: 1,705.00 / 2,500.00; task 1: 2,456.67 / 1,331.67 / 1,786.67) — but F-G1 leaves theft, valuables, property and pet with no surviving `method` factor, and F-G2 strikes the theft documentation share as an unreal ladder — **FAIL**.
- Gates: not re-run by the auditor (the auditor runs no gates; the coordinator's snapshot is cited in § charter_global_frozen; check_traceability is to be re-run after KB rendering).

Difficulty verdict: source-layer audit **not passed** — task 0 SOURCE-FACTOR RED, task 1 SOURCE-FACTOR RED; policy self-consistency, problem tree and unique solution PASS on both.

## edit_disclosure

After the reveal, the only edit made above the comparison sections was to the freeze-time and reveal-time metadata lines. The first-written times (19:05Z / 19:12Z / 19:16Z / 19:20Z) were made up and did not match the clock; they were replaced with the recorded times (19:03:44Z directory creation, 19:07:05Z hash and reveal). No derivation, figure or finding was changed. Because of this edit, the freeze hashes quoted above no longer match the current file bytes.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit started 2026-10-07T21:34:22Z (clock read at the start of the round); this section written 2026-10-07T21:36Z or later, before any round-2 task JSON was opened.
- Inputs (sha256, re-checked from the repo root): `protect.extended.yaml` 0d96e6d619c0580a20215e27ade9fbc8d02104727c6b6db9223bdf2b16b706bf (round 1: e56da7e0…e363c, **changed**); `task_tools.py` db30bac4723e69a515b4700415de52a132acbbc86fce2f4617b4112d502558df (round 1: 9109faa6…cddb8a0, **changed**); views r2 `task_0.view.json` 63319161…312693 (changed), `task_1.view.json` 4b4f04d9…5e363c (byte-identical to round 1; JSON compared equal). Both shared inputs moved, so every charter-global section is re-derived in full below, not carried forward.
- Gate snapshot r2 (coordinator, `/tmp/erl45_views/r2/damage_claims_and_protection/gate_snapshot.txt`): same as round 1 — all green except CACHE-DIFF INFO and TRACEABILITY NOT OK (expected before rendering).
- Masked until all round-2 derivations are frozen: round-2 `tasks/0.json`, `tasks/1.json` beyond the views; `tasks/damage_claims_and_protection/worklog.md`.
- Disclosure: the auditor knows round-1 GT (read in round 1 after the freeze). No round-2 GT has been seen. The brief names only the item ids the reworker claims to have changed, no values.

### policy_conflict_scan (r2)

- Base copy lines 1-860 still byte-identical to `blueprint/products/protect.yaml` (`diff` empty).
- Same five extended policies, ids, target tools, owners, triggers and prerequisite edges as round 1. Category scoping unchanged; no claim falls under two policies.
- Structural changes found by reading every extended policy in full:
  1. In all five, the guest-payment factor `*_guest_payment_method` is replaced by `*_recovery_sharing_method` (method), tiered by **plan level**: HostCover Premier/Elite/Estate subtract max(guest payments, deductible) ("made whole first"); HostCover Standard/Plus subtract deductible + payments × max(0, adjusted loss − deductible) / adjusted loss ("shared in proportion"); any other level (Essential) subtracts payments + deductible ("Roamhaven credited first"). The overwrite of "subtract every guest payment recorded on the claim (net of reversals)" is re-declared in every policy to name this method.
  2. Theft: `theft_documentation_share` (listing photo count) and its params are removed; `theft_repeat_loss_share` is added (parameter): approved theft claims on the same plan in the 24 months before settlement, leaving out claims on the same stay — ≥2 → theft_repeat_two_share_pct 75 %, exactly 1 → theft_repeat_one_share_pct 90 %, none → in full. The theft overwrite of "start from the verified loss;" now names the repeat-loss share in place of the documentation share. Theft cross_category no longer reads photo_count.
  3. All five rules say "rounded half up to the nearest cent" (rule, compute_basis.result and baseline.rule).
  4. Property and pet condition shares add: "a quality review rates the guest reviews of the year before it, so the most recent review reflects the condition guests reported over the months around the stay."
  5. Pet-fee share's reason now reads "the pet fee the guest paid is charged for the extra cleaning and upkeep a pet brings, in the way the base settlement reduces a deep-cleaning claim by the cleaning fee collected".
  6. Valuables rule (and tool docstring) drop "agreed value": "because the value of such items rests on the host's own appraisals, provenance and receipts, a valuables settlement is booked only when the host accepts it in person".
- Shared quantities: the recovery-sharing method reads only the claim's own payments, its own adjusted loss and its own deductible, so it adds no cross-policy dependence. The order-dependence of the valuables/income deductible and the order-independence of property/pet (round 1) still hold. The theft repeat-loss count reads approved theft claims only, which no write of this difficulty creates, so no write order affects it. No new conflict. Scopes of tasks 0/1 still disjoint and jointly complete (pending reveal).
- The claimed-event-types observation stands unchanged (no change claimed or found).

### rule_compute_equivalence (r2)

- `*_offset` (all five): compute `MX(P, D) if level in {Premier, Elite, Estate} else (D + P × MX(0, A − D) / A if level in {Standard, Plus} and A > 0 else P + D)` matches the rule's three sentences word for word. The `A > 0` guard sends A = 0 on Standard/Plus to P + D, where the rule's division is undefined; the net is floored at 0.00 anyway (0 − anything ≤ 0), so no scored consequence. Observation O-R2-2.
- `th_repeat_count = COUNT(approved theft, decided_at within 24 months) − COUNT(approved theft on the same stay)`; rule: "the theft claims on the same plan that the claims team approved in the 24 months before the settlement date, leaving out claims on the same stay". Equivalent whenever no same-stay approved theft claim is older than 24 months (impossible for a stay being settled now). `th_repeat_pct` branches = the rule's three tiers.
- Rounding: `RND(…, 2)` against "rounded half up"; the task worlds give no exact half-cent scored figure (checked per task).
- `compute_basis.*_guest_paid` now quotes the recovery-sharing sentence ("how the guest payments … are shared …") rather than the sentence defining the net-of-reversals sum; the rule still states "every guest payment recorded on the … claim, net of reversals". Wording only; no empty promise.
- O-RC1, O-RC2, O-RC3: compute unchanged; carried forward as observations, still without consequence in either world (task 0's prior reimbursement, 2025-04-22, is before plan_year_start 2026-05-10 and outside the months-back window too; checked in task_0 r2).
- Every ladder tier of every factor is in the rule and in its `decides` branch; no orphan tier either way. PASS.

### action_binding_and_uuids (r2)

- Same five tools, same uuid8s (c380c173, 01cb0de3, 941cbbf5, a5391300, ab094655), one policy each. Module change: the valuables docstring now says "settled only once the host accepts the settlement in person, because their value rests on the host's own appraisals, provenance and receipts"; every body is still `ctx.find` claim → `ctx.create` one `protect_reimbursement_paid` row → receipt. No validation, refusal, hint or sequence wording. PASS.

### prerequisite_graph and prerequisite_sentences (r2)

- `prerequisite` blocks of valuables and income are textually unchanged; theft/property/pet `[]`. The three policy_source sentences are still verbatim in their own rules; form state; condition, resolved_by, gate (va_stay_settled, in_stay_settled still in compute), effect all as in round 1. Acyclic. Four-point test and one-write-per-state unchanged. No new cross-problem order sentence in any rule: the repeat-loss sentence counts past approved claims, not writes of this difficulty. PASS.

### override_declarations (r2)

- Sentence sweep repeated against base `protect_evt_reimbursement` and `protect_agg_plan_year_limits`: same results as round 1. The overwrite on "subtract every guest payment …" names the recovery-sharing method in all five; the theft "start from the verified loss;" overwrite names the repeat-loss share. No undeclared override.
- Observation O-R2-1 (already present in round 1, newly recorded; not a regression): each base variant carries `guest_payment_offset: guest payments recorded on the claim are subtracted from the depreciated loss before the deductible`, a parameter string, not a rule sentence. The extended overwrites name the rule clause it parameterises but not the variant parameter. Rendered next to each other, the parameter describes only the Essential (fall-through) treatment. The extended rule states the level-specific method in full, and the base rule sentence itself is declared superseded, so no second defensible scored answer follows.

### factor_ladders (r2)

- theft (6): depreciation P 4 tiers; access P 3 (listing); deductible factor P 3 multi-source (host); **recovery-sharing M 3**; **repeat-loss P 3**; escalation P 3. Counts 5P + 1M.
- valuables (6): depreciation P; access P (listing); new-cover P (host); escalation P; deductible factor P multi-source (host); **recovery-sharing M**. 5P + 1M.
- property (5): depreciation, condition (listing), escalation, deductible factor (multi-source, host) — 4P; **recovery-sharing M**.
- pet (5): depreciation, pet-fee (listing), condition (listing), escalation — 4P; **recovery-sharing M**.
- income (5): lost-nights M (multi-source, listing); timing P (host); escalation P; new-cover P (host); **recovery-sharing M**. 3P + 2M.
- Recovery-sharing ladder, F-G1 re-test: three tiers partitioned by plan level (pairwise disjoint; Essential is the fall-through). For any net payment P > 0 and deductible D > 0 with adjusted loss A > D, the three outcomes differ: max(P, D) < D + P(A−D)/A < P + D when P ≤ D, and max(P, D) = P vs D + P(A−D)/A = P + D(A−P)/A ≠ P when P > D and A > P. No two tiers select the same method on their domains. Tiers differ in how the recovery is allocated (insured made whole first / pro-rata / insurer first), not in a substituted number, so the `method` label is honest. These are the three standard recovery-allocation rules of insurance (made-whole doctrine, pro-rata sharing, insurer-first subrogation), so the conditions and outcomes are ones the line actually holds. Fall-through = factor baseline (`P + D`) = what `baseline.rule` states ("every guest payment … is subtracted together with the … deductible"). **F-G1 closed.**
- Theft repeat-loss ladder, realism: prior theft losses on the same plan are loss history, which the line genuinely weighs (and the theft deductible factor already weighs reimbursed-claim history); a reduced settlement after earlier thefts, tied to the stated expectation that portable valuables be secured, is a recognisable protective-safeguard treatment. Three distinct values (75 / 90 / 100). Not unreal. **F-G2 closed** (the photo-count tier is gone from rule, compute, params, factors and cross_category; `grep -i photo` finds only the base `evidence_required` strings).
- O-L3: the added sentence ties the most recent review to the trailing year of guest reviews, which makes reading a post-stay review a stated convention. Borderline realism remains (the review window includes the damaging stay's own guest review), but it is now explicit. Observation kept, softened.
- O-L4: the pet-fee reduction is now anchored to existing charter logic (the base deep-cleaning offset by the collected cleaning fee). Observation closed.
- O-L5: "agreed value" removed; depreciation of valuables at gentler rates is now consistent with the rule's own wording. Observation closed.
- O-L1 (escalation shares) and O-L2 (access shares): unchanged, kept as observations.
- Counts after the tests: no factor is struck in round 2. Theft 5P+1M, valuables 5P+1M, property 4P+1M, pet 4P+1M, income 3P+2M — all within bounds.

### findings (r2)

| id | round-1 verdict | round-2 status |
| --- | --- | --- |
| F-G1 | SOURCE-FACTOR RED | closed (recovery-sharing ladder: three distinct methods) |
| F-G2 | SOURCE-FACTOR RED | closed (documentation share removed; repeat-loss share real) |
| O-L3 | observation | kept, softened |
| O-L4, O-L5 | observation | closed |
| O-L1, O-L2, O-RC1, O-RC2, O-RC3, claimed-event-types | observation | unchanged (no change claimed or found) |
| O-R2-1 base variant `guest_payment_offset` string not named in overwrites | — | new observation (pre-existing text) |
| O-R2-2 `A > 0` guard on the proportional tier | — | new observation, no consequence |

No new RED at charter level. Per-task demonstrations are in each task file's revision_2.

### closing_checklist (r2)

Written after both round-2 reveals (2026-10-07T21:37:59Z). Nothing in this revision above this heading was edited after the reveal.

- Per-task files `task_0.md`, `task_1.md` sit next to this file, one per task. Round-1 text is preserved unchanged above each `## revision_2`. Both round-2 comparison sections carry **PASS**.
- Coverage and scopes: charter_scope task 0 = {theft, valuables}, task 1 = {property, pet, income}. Pairwise disjoint and jointly complete over the five extended policies. Task tools are closed against GT; uuid8s are unchanged and independent — PASS.
- Problem trees: task 0 has n = 1 with 1 value_input edge; task 1 has n = 2 with 2. Each root is an owner=user write. The difficulty graph is acyclic — PASS.
- Factors: every computation has a self-sufficient baseline and 5-6 factors with ≥ 2 parameter and ≥ 1 method. Each task has multi-source and cross-difficulty factors. Every ladder has ≥ 3 distinct tiers, all stated in the rule. Every factor bears weight against an honest baseline. Whole-baseline fall-backs are definite and differ from gold (1,705.00 / 2,500.00; 2,456.67 / 1,331.67 / 1,786.67) — PASS.
- Gates: re-run by the coordinator on the final form (snapshot r2 cited above: all green except the optional CACHE-DIFF INFO and TRACEABILITY NOT OK, which is expected until docs/ is rendered). The auditor ran no gates.

Difficulty verdict, revision 2: source-layer audit **passed** — task 0 PASS, task 1 PASS. Remaining items are observations only: O-L1 escalation shares, O-L2 access shares, O-L3 post-stay quality review (softened), O-RC1-3, O-R2-1, O-R2-2, and the claimed-event-types note.
