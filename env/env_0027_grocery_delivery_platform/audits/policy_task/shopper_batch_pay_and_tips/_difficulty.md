# Policy-task audit — shopper_batch_pay_and_tips / charter-global

## charter_global_frozen

- Scenario: env/env_0027_grocery_delivery_platform; difficulty shopper_batch_pay_and_tips; category batch; M=2 (tasks 0, 1).
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Freeze time 2026-09-24T23:46Z, before any task's GT was revealed.
- Freeze hashes (sha256, verified on disk before reading):
  - `tasks/shopper_batch_pay_and_tips/batch.extended.yaml` = 4af8c03b4d1045f762308bec165b0a3895ff4c32efad88444f8a69d5a7e40530
  - `tasks/shopper_batch_pay_and_tips/task_tools.py` = 847ff23a809d64ec0d0b2c65b061c9752b767b2246f2fc659992dc56afb3a358
  - masked view task_0 = 325c5e1b4ee883a8b49181c6dde2b1347eb2b5672a43681438aed84e4cbc763d; task_1 = f9b5009fd81fb8f35ddbf23d46f11971839a17d03318cee1e711396a459ef604
- Sources this section uses: `blueprint/products/batch.yaml`, `blueprint/products/shopper.yaml` and `payout.yaml` (for the variant parameters that level and card-plan tiers read: `level_min_batches_30d`, `cashback_fuel_pct`, `card_tier_follows_level`), `blueprint/blueprint.yaml` (difficulties), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and `erlbench/scoring.py` plus `erlbench/determinism.py` (for how writes are scored).
- Masked and not read when this section was written: every field of `tasks/*.json` other than `frozen_time`, `user_scenario` and `initial_state` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), and the instantiator's `tasks/shopper_batch_pay_and_tips/worklog.md`. This section contains nothing derived from any revealed GT.
- Entry conditions (Step 0): the brief supplied the gate snapshot. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire are all rc=0. check_traceability is deferred until the KB is published. It also supplied the masked views with their hashes. The entry conditions are complete. The auditor cites the gates and did not re-run them.

### policy_conflict_scan

The base section of the extended file is identical to `blueprint/products/batch.yaml`. A key-by-key comparison of the parsed YAML shows all ten top-level keys equal, and `extended_policies` is the only addition. The charter has seven extended policies:

| id | subject / trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| batch_ext_long_distance_bonus (LD) | batch_pay_posted / state_due | post_pay_component_6b97a1a8 (agent) | amount_usd | [] |
| batch_ext_duplicate_recovery (DR) | batch_pay_reversed / state_due | reverse_duplicate_pay_33b66c45 (agent) | amount_usd | [] |
| batch_ext_shown_pay_claim (SC) | batch_completed / on_request | submit_pay_dispute_0c2b2ed2 (user) | claimed_amount_usd | LD, DR |
| batch_ext_shown_pay_adjustment (SA) | batch_pay_adjusted / on_request | book_pay_adjustment_e97659e1 (agent) | amount_usd | SC |
| batch_ext_undelivered_recovery (UR) | batch_pay_reversed / state_due | reverse_undelivered_pay_ec14645c (agent) | amount_usd | [] |
| batch_ext_mileage_claim (MC) | batch_completed / on_request | submit_mileage_claim_29030431 (user) | claimed_amount_usd | UR |
| batch_ext_mileage_adjustment (MA) | batch_pay_adjusted / on_request | book_mileage_adjustment_6fe9f3bb (agent) | amount_usd | MC |

The policies were checked against one another in the following overlaps:

- **Subjects.** DR and UR both write `batch_pay_reversed` against a mileage posting. Their grounds differ (duplicate_pay against order_not_delivered_verified), and so do their triggers (the mileage component standing twice, against a wrong-address violation recorded against the batch). SA and MA both write `batch_pay_adjusted`, with different `adjustment_reason` values (shown_pay_shortfall against mileage_underpaid). Base `one_per_reason` allows one of each. Neither task's world contains a batch that meets both triggers of a pair (see observation O4).
- **Eligibility and time anchors.** Every extended policy inherits the base windows, which are counted from `completed_date`: the dispute window is 7 days (10 for Stock-Up) and the clawback window is 30 days, both inclusive. The adjustments also inherit the base agent limits from `batch_agg_adjustment_limits`, per-type caps and 3 adjustments per 30 days, with anything beyond them escalated. No extended rule weakens these.
- **Terminal states.** On adjustment, SA and MA mark the dispute `approved` through the tool. SC and MC leave the dispute `submitted`. The reversals and the posting only move `batches.earnings_usd`. No two policies drive one field to different terminal values.
- **Cross-category reads.** Every policy reads `shopper` (level through `level_min_batches_30d`, tenure through `activated_date`, `violation_points_balance`, violations and ratings in `shopper_events` by `batch_id`). LD, DR, SA and MA also read `payout` (plan through `cashback_fuel_pct` / `card_tier_follows_level`, and `payout_events`). All are read-only, and all are reachable through `find_shopper_accounts`, `find_shopper_events(batch_id=…)`, `find_payout_accounts` and `find_payout_events`.
- **Scope.** The tree {SA → SC → {LD, DR}} and the tree {MA → MC → UR} share no policy and together cover all seven, so the two trees are exclusive and complete. Which tree each task claims is confirmed from the worlds in the task files: task 0 has a shown-pay complaint, a duplicate mileage posting and a missing long-distance bonus; task 1 has a mileage complaint and a wrong-address violation.
- **Claimed event types.** The claimed event types include `batch_tip_adjusted_up/down`, but no extended policy writes a tip event (observation O7).

Conclusion: the scan finds no conflict that yields two readings in either task's world. The latent interactions it did find are observations O4 and O8.

### rule_compute_equivalence

Check 2 was swept both ways for every policy.

- **LD.** The level/tenure threshold ladder uses `ld_level >= 80` for Gold and `>= 40` for Silver. These match `shopper.yaml`, where Silver has `level_min_batches_30d` 40, Gold 80, Platinum 150 and Diamond 250, so "Gold or above" is ≥ 80. `ld_due` against the threshold that applies matches "exceeds that threshold". The "batch type whose own threshold is zero carries no bonus" clause becomes `P('long_distance_threshold_miles') > 0`. `ld_route_excess` is measured against the type's own threshold, and the extension is measured beyond the threshold that applies, rounded separately; each of these is stated in the rule. The order count is "posted per-order pay ÷ per-additional-order pay, rounded to a whole number", matching `RND(…,0)`. The uplift uses fuel cashback ≥ 3 → 1.10, (0, 3) → 1.05, else 1.00, and matches `payout.yaml` (Blue 2.0, Gold 3.0, Platinum 4.0, Diamond 5.0, and 0.0 for the other plans). The result is "sum × uplift, rounded once", matching `RND((…)*ld_uplift*ld_due,2)`. Equivalent both ways.
- **DR.** The later of the two mileage postings is `LATEST(… mileage)` when there are 2 or more postings. The three allowances, the floor at 0, the same-day count on `event_date == completed_date`, "instant cashout less than one whole calendar month before the handling date" (`within_months=1`) and "Everyday Pay Card plan" (`card_tier_follows_level == True`, true exactly for the four EPC plans in `payout.yaml`) all have a rule sentence and a compute branch each. Halving rounds down (`int(RND(x*50,6))/100`) and the ×0.75 branch rounds up (ceiling), as the rule states. Equivalent.
- **SC.** Each of the guarantee method, standing share, claim tolerance, waiting-pay offset share and five-star supplement has one tier sentence per branch. The stated order of operations, "(guaranteed × share + supplement) − (standing − wait × (1 − share)) − tolerance, rounded once, floored at 0", is implemented literally in `result`/`sc_counted`. Equivalent.
- **SA.** The rating approval share uses "three stars or fewer", which becomes `sa_low` over ratings 1–3, and "none below four", which becomes `sa_low == 0`. The make-good credit and the prompt credit (completion date to dispute `created_at`) each have a sentence and a branch. The card method is ceiling ×1.05 when fuel ≥ 3 and floor ×1.02 on Blue. The minimum-claim gate uses `pay_dispute_min_usd`. Equivalent.
- **UR.** The delivery-distance method, standing share, loyalty allowance and verification timing all appear in both the rule and the compute. `MN(ur_mileage, …)` implements "never exceeds the mileage posting". Note O9: `ur_mileage` is the SUM of all mileage postings, while the rule speaks of "the mileage posting it is booked against"; the two are equal whenever a single posting stands. Equivalent in both tasks' worlds.
- **MC.** The claim tolerance replaces the type tolerance in both `mc_beyond` and `mc_qualifies`. The rule's "claimed only when … by more than the mileage dispute tolerance" together with "The claim tolerance replaces the batch type's mileage dispute tolerance" gives the claim tolerance. The detour method, the claim rate, the rated supplement (low = ratings 1–2, from "two stars or fewer") and the mileage standing (posted mileage minus reversals on the order_not_delivered_verified ground) each have a sentence. The order is "paid route × rate + supplement − standing, rounded once". Equivalent.
- **MA.** The approval share and the cashout-fee credit (`XSUM` of `payout_cashout_fee_charged` within one month) each have a sentence. The prompt credit uses 0–1, 2–4 and else. The long-route credit uses posted mileage ≥ 3.00 together with driven miles against 1.5× the estimate and against the type tolerance. The tenure method is ceiling ×1.08 or floor ×1.04. Equivalent.

Every ladder named in `factors[].ladder` is a sentence of its policy's rule and a branch of its `decides` binding, and no binding branch lacks a rule tier. **Check 2 PASS for all seven policies.**

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (seven distinct tools, see the table above).
- The uuid8 tails are 6b97a1a8, 33b66c45, 0c2b2ed2, e97659e1, ec14645c, 29030431 and 6fe9f3bb. They share no common prefix, form no sequence and are not adjacent values, and none is reused or derived from another by changing the tail. PASS.
- Docstrings: none names another tool or states a position in a sequence. The words "after" and "before" appear only inside enum meanings ("canceled after shopping started", "less before tips"), never as an ordering instruction. PASS.
- No tool checks eligibility, refuses a call or computes a pay figure: every body only rounds the argument, creates a row and moves `earnings_usd`. The module docstring states this explicitly. PASS (no tool judges a prerequisite).
- **Observation O1 (duplicate tool surfaces).** `book_mileage_adjustment_6fe9f3bb` and `book_pay_adjustment_e97659e1` have identical signatures, identical `adjustment_reason` enums (all seven reasons) and identical bodies, including the `make_id("bev_", batch_id, shopper_account_id, batch_pay_dispute_id, adjustment_reason, amount)` key. Likewise, `submit_pay_dispute_0c2b2ed2(dispute_reason="mileage_underpaid")` builds exactly the row `submit_mileage_claim_29030431` builds, with the same `make_id("bpd_", batch_id, "mileage_underpaid", amount)` key. So the docstrings of the generic tools admit the sibling tree's business. Scoring is a DB-hash comparison (`erlbench/scoring.py`: "any agent path that performs the same writes with the same arguments reaches the same hash"), so either tool of a pair produces the same end state. This yields no second scored answer and is recorded as an observation only.

### prerequisite_graph

Check 7 found the following edges:

| edge | kind | gate (binding exists?) | form | resolved_by = depended-on target_tool? |
| --- | --- | --- | --- | --- |
| SC ← LD | value_input | sc_posted (yes) | state | post_pay_component_6b97a1a8 = LD target (yes) |
| SC ← DR | value_input | sc_reversed (yes) | state | reverse_duplicate_pay_33b66c45 = DR target (yes) |
| SA ← SC | value_input | sa_claim (yes) | state | submit_pay_dispute_0c2b2ed2 = SC target (yes) |
| MC ← UR | value_input | mc_standing (yes) | state | reverse_undelivered_pay_ec14645c = UR target (yes) |
| MA ← MC | value_input | ma_claim (yes) | state | submit_mileage_claim_29030431 = MC target (yes) |

- Every policy fills in `prerequisite`: LD, DR and UR have `[]`. Every `problem` names an extended policy in this file, none names itself or a base policy, and the graph is two disjoint in-trees with no cycle.
- Every `policy_source` was found verbatim in its own blocked rule (string search over the folded rule text).
- `form` is `state` on all five edges and no edge carries a `fallback_reason`, which is consistent.
- Each `condition` restates the sentence at the same strength: for example, "whenever estimated_miles exceeds the long-distance threshold that applies", and "When two … mileage stand …, a batch_pay_reversed row names the later one".
- Each `effect` direction checks out against compute. The LD posting raises `sc_posted`, which lowers the claim. The DR reversal raises `sc_reversed`, which raises the claim. The UR reversal raises `mc_reversed` (UR writes reason order_not_delivered_verified), which raises the claim. The two disputes supply `sa_claim` and `ma_claim`.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

**Check 7 PASS.**

### prerequisite_sentences

Each edge was put through the four-point test of check 6:

1. **SC ← LD.** "The claimed shortfall is fixed only after the batch's earnings entries carry a long-distance bonus whenever the estimated route exceeds the long-distance threshold that applies to the shopper."
   - Connective: "only after".
   - Waited-on state: a long-distance entry among the batch's earnings entries, which is visible through `find_batch_events` as `pay_component long_distance`. It names no action and no performer.
   - It names no tool, id or snake_case token.
   - Strength and scope: conditional on the threshold that applies, exactly as `condition` states.
   - Single write: only LD's rule describes posting a long-distance component, so the only resolving write is `post_pay_component_6b97a1a8`. The generic tool can post other components, but only a `long_distance` posting brings this state about.
   - Derivation: sentence → "does the batch carry a long-distance entry?" → no → which rule posts one → LD, whose rule says a due-but-absent bonus "is posted by the desk as one long-distance pay component" → LD's own ladder decides whether it is due and how much.
   - PASS.
2. **SC ← DR.** "The claimed shortfall is not worked out until every mileage posting that stands twice on the batch carries a reversal against its later posting."
   - Connective: "not … until".
   - State: a reversal entry whose `source_event_id` is the later mileage posting, which is record-visible.
   - No tool, id or snake_case token.
   - Strength: conditioned on a mileage posting standing twice, as `condition` states.
   - Single write: DR's rule ("When the mileage component stands twice …, the second posting is a duplicate and the desk takes it back with one reversal … against that later posting") is the only rule describing a reversal against the later of two mileage postings. See observation O2 on the tool layer.
   - PASS.
3. **SA ← SC.** "A shown-pay adjustment is booked only after the batch carries a submitted shown-pay shortfall dispute from the shopper stating a claimed amount."
   - Connective: "only after".
   - State: a dispute row with reason shown-pay shortfall, status submitted and a claimed amount. "From the shopper" describes the row's owner, not an action to perform.
   - No tool or id.
   - Single write: SC is the only policy whose rule files a shown-pay shortfall dispute. `submit_mileage_claim` cannot write that reason.
   - PASS.
4. **MC ← UR.** "The mileage claim is not fixed until the batch's earnings entries carry a reversal on the verified not-delivered ground for the orders that wrong-address violations recorded against the batch show as not delivered."
   - Connective: "not … until".
   - State: a reversal entry with the verified not-delivered ground, which is record-visible.
   - Single write: only `reverse_undelivered_pay_ec14645c` writes that ground, and only UR's rule describes it.
   - PASS.
5. **MA ← MC.** "A mileage adjustment is not booked until the batch carries a submitted mileage dispute from the shopper stating a claimed amount."
   - Connective: "not … until".
   - State: a submitted mileage-underpaid dispute row.
   - Single write: at the rule layer, MC is the only policy whose rule has the shopper file a mileage dispute. At the tool layer, `submit_pay_dispute_0c2b2ed2` can write the same reason and produces a byte-identical row (O1), so there is no scoring consequence.
   - PASS.

The rest of check 6:

- No blocked rule carries a second wording of its dependency, a tool name or another policy's id.
- No depended-on rule (LD, DR, UR, SC, MC) restates the sentence of the rule that waits on it.
- No rule states a cross-problem order that grounds no declared edge. The ordering words inside the SC, SA, UR and MA rules ("first … then", "then", "finally") order steps within one computation.
- No base rule sentence grounds an edge.
- The docstrings are silent about sequence (see action_binding_and_uuids).

**Check 6 PASS.**

- **Observation O2.** `reverse_undelivered_pay_ec14645c` takes any `source_event_id`, so mechanically it can also book a reversal against the later of two mileage postings. The resolution at the rule level is still unique (the undelivered ground needs a wrong-address violation, and the sentence names the posting "that stands twice"), and neither world has both a wrong-address violation and a duplicate. Observation only.

### override_declarations

Check 1 findings, taken sentence by sentence over each policy's `base_policy_refs`:

- **LD → batch_evt_pay_calculation.**
  - The only sentence governing the long-distance quantity is "long_distance is long_distance_bonus_usd when long_distance_threshold_miles is above 0 and estimated_miles exceeds it." The `overwrite` names it as superseded. Its replacement ("… that sum multiplied by the long-distance card uplift and only then rounded once") and the rule's ladder sentences, which set the threshold that applies, the amount, the extension, the supplement and the uplift, fix one merged value.
  - The other sentences are followed: the cent half-up rounding, "posted once per batch" and "Components are posted only on a batch that is completed or canceled", which the rule repeats verbatim.
  - Declared. No undeclared override.
- **DR → batch_evt_clawback.**
  - Followed: "Posted pay is reversed only on a ground listed …", which duplicate_pay satisfies for every type; the clawback window; "A reversal targets one posted or adjusted pay row … never more than that row's amount, and each row is reversed at most once"; and "Tips are never reversed".
  - The base sets no amount for a reversal beyond "never more than", so taking back less (goodwill allowances, the cash-out method) does not conflict. `overwrite: []` is correct.
  - Observation: the base pay calculation's "each posted once per batch" is left partly unrestored by the goodwill. That is a remedy choice, not a clause about the reversal amount.
- **SC → batch_evt_pay_calculation, batch_evt_lifecycle, batch_evt_pay_disputes.**
  - The claimed amount is a quantity no base sentence governs. Base only says the shopper "disputes pay … by submitting a dispute naming a reason".
  - The pay-calculation shown-pay clause governs the owed adjustment, not the claim, and SA declares its replacement. The lifecycle sentences (the agent never advances status, and so on) are followed.
  - `overwrite: []` is correct.
- **SA → batch_agg_adjustment_limits, batch_evt_pay_disputes, batch_evt_pay_calculation.**
  - Two supersessions are declared: the pay-calculation clause "and when shown_pay_is_floor is true and the sum is below shown_pay_usd while the orders did not change after acceptance, the gap is owed as a shown_pay_shortfall adjustment", and the disputes clause "The owed amount is what the component should have been … minus what was posted for it, rounded to the cent;".
  - Inherited unweakened: the agent cap and 30-day count with escalation, the dispute window, `pay_dispute_min_usd` (restated), one adjustment per reason, and approved/denied marking.
  - Declared.
- **UR → batch_evt_clawback.**
  - The same sentences are followed as for DR: the order_not_delivered_verified ground is listed for every delivery type, the window, one row, never more than that row, at most once.
  - `overwrite: []` is correct.
- **MC → batch_evt_pay_calculation, batch_evt_lifecycle, batch_evt_pay_disputes.**
  - The `overwrite` names the supersession of "mileage_underpaid is owed only when actual_miles exceed estimated_miles by more than mileage_dispute_tolerance_pct and then pays mileage_rate_usd_per_mile on the miles above that tolerance."
  - Pay calculation's "mileage … always computed on the estimated route …, never on actual miles" governs the posted mileage component, not the claim, and it is followed: the claim nets out posted mileage computed on the estimated route.
  - Declared.
- **MA → batch_agg_adjustment_limits, batch_evt_pay_disputes.**
  - Declared: supersession of the owed-amount clause.
  - **Observation O3.** The disputes sentence "mileage_underpaid is owed only when … and then pays mileage_rate_usd_per_mile on the miles above that tolerance" also governs what a mileage adjustment pays. It is declared superseded only in MC's `overwrite`, not in MA's own. Because the charter as a whole does declare it superseded, the merged semantics stay unique (the adjustment is the claimed amount run through MA's ladders). Whether a reader of the base sentence would get a second value is demonstrated against task 1's world in `1.md`.
  - The inherited limits are unweakened.

None of the three disguised forms was found: no anonymous intermediate factor overrides a base quantity, no 0/1 multiplier zeroes a base-fixed amount (`ld_due` restates the base existence condition), and no base branch is dropped. No rule text calls the base output a "wrong value".

### factor_ladders

This section records the structure only; each factor's weight is judged in the task files. "MS" marks a multi-source factor (every non-fall-through tier is a conjunction or disjunction over distinct records). "X" marks a cross-difficulty factor.

**LD** (5 declared; labelled 4 parameter and 1 method):

| factor | label | tiers (outcome) | MS | X | structural verdict |
| --- | --- | --- | --- | --- | --- |
| ld_threshold_by_standing | parameter | 8.0 / 9.0 / type threshold (10, 15 or 0) | level and tenure (two fields of the account row) | shopper | distinct; holds |
| ld_amount_by_points | parameter | 3.00 / 2.50 / type bonus | no | shopper | **Stock-Up: tier 1 (3.00) = fall-through (type bonus 3.00)** — F4 |
| ld_route_extension | **method** | 0.25/mi / 0.15/mi / none | route excess (batch) and late violation (shopper_events) | shopper | **mislabelled: one formula, rate 0.25 / 0.15 / 0** — F1 |
| ld_order_supplement | parameter | 0.40×n / 0.30×n / 0 | no | — | distinct; holds |
| ld_card_uplift | parameter | 1.10 / 1.05 / 1.00 | no | payout | distinct; holds |

After the tests, LD keeps 0 honest `method` factors, below the floor of 1 (F1).

**DR** (4 declared; 3 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| dr_loyalty_allowance | parameter | 1.00 / 0.50 / 0 | level and tenure | shopper | holds |
| dr_standing_allowance | parameter | 0.50 / 0.25 / 0 | points (account) and late (events) | shopper | holds |
| dr_same_day_allowance | parameter | 0.30 / 0.15 / 0 | two postings' dates against completion | — | holds |
| dr_cashout_method | method | ×0.5 down / ×0.75 up / full | cashout (payout_events) and plan (payout account) | payout | accepted as method on the change of rounding direction (O5) |

Counts: 4 factors, 3 parameter, 1 method. PASS.

**SC** (5 declared; 4 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| sc_late_order_guarantee | method | prorate to on-time orders / shown − per-add-order pay / whole | late (events) and order count (batch) | shopper | genuine method; holds |
| sc_standing_share | parameter | 0.97 / 0.95 / 1.00 | no | shopper | holds |
| sc_offer_tolerance | parameter | 0 / 0.25 / 0.50 | level and tenure | shopper | holds |
| sc_waiting_offset | parameter | 0.50 / 0.75 / 1.00 | no | — | holds |
| sc_five_star_supplement | parameter | 1.00 / 0.50 / 0 | no | shopper | holds |

PASS.

**SA** (4 declared; 3 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| sa_rating_approval_share | parameter | 0.90 / 1.05 / 1.00 | rating rows | shopper | holds |
| sa_makegood_credit | parameter | 1.50 / 0.75 / 0 | level and tenure | shopper | holds |
| sa_prompt_credit | parameter | 0.50 / 0.25 / 0 | dispute date against completion | — | holds |
| sa_card_method | method | ×1.05 up / ×1.02 down / as is | no | payout | accepted (O5) |

PASS.

**UR** (4 declared; 3 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| ur_delivery_distance_method | method | driven-route share / posted share rounded down / posted share half-up | "≥1 wrong-address" and driven over or within tolerance | shopper | **fall-through unreachable in scope; "≥1 wrong-address" restates scope; tier-1 outcome unreal** — F2 |
| ur_standing_share | parameter | 0.80 / 0.60 / 1.00 | no | shopper | holds |
| ur_loyalty_allowance | parameter | 0.80 / 0.40 / 0 | level and tenure | shopper | holds |
| ur_verification_timing | parameter | 0.30 / 0.15 / 0 | **"a wrong-address violation is recorded" restates scope** and day span | shopper | F2 (the part is vacuous; three tiers remain reachable by day span) |

After the tests, UR keeps 3 factors and 0 method, below the floors of 4 and 1.

**MC** (4 declared; 3 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| mc_claim_tolerance | parameter | 5% / 10% / type tolerance | level and tenure | shopper | holds |
| mc_detour_exclusion | method | prorate by delivered/all orders, floored to 0.1 / none count / all count | wrong-address and order count | shopper | **tiers 1 and 2 are one method** — F3 |
| mc_claim_rate | parameter | 0.60 / 0.55 / type rate | no | shopper | **Express 30: tier 1 (0.60) = fall-through (0.60)** — F4 |
| mc_rated_supplement | parameter | 0.40 / 0.20 / 0 | five-star row and low-rating row | shopper | holds |

After the tests, MC keeps 3 factors (2 if F4 is counted) and 0 method, below the floors.

**MA** (5 declared; 4 parameter and 1 method):

| factor | label | tiers | MS | X | verdict |
| --- | --- | --- | --- | --- | --- |
| ma_approval_share | parameter | 0.95 / 0.90 / 1.00 | no | shopper | holds |
| ma_cashout_fee_credit | parameter | 1.00 / 0.50 / 0 | no | payout | holds |
| ma_prompt_credit | parameter | 0.40 / 0.20 / 0 | dispute date against completion | — | holds |
| ma_long_route_credit | parameter | 0.75 / 0.40 / 0 | posted mileage (batch_events) and driven miles (batch) | — | holds |
| ma_tenure_method | method | ×1.08 up / ×1.04 down / as is | level and tenure | shopper | accepted (O5) |

PASS.

Other structural points:

- Every factor's `baseline` equals its fall-through tier and the policy's `baseline.rule` for that input. The one exception is UR's distance method, whose fall-through is out of scope (F2).
- Every `decides` names an input, never `result`.
- Binding sets within each policy are disjoint.
- Every `baseline.rule` sentence appears verbatim in its rule.
- The cross-difficulty categories read are `shopper` (difficulty shopper_ratings_and_deactivations) and `payout` (difficulty shopper_payouts_and_cashouts).
- Per task, the multi-source and cross-difficulty minimums hold in both trees (tree 1: ld_route_extension, dr_standing_allowance, dr_cashout_method, sc_late_order_guarantee; tree 2: ma_long_route_credit, mc_rated_supplement). Whether the other product's rows are actually seeded is checked per task.

### findings

- **F1 — SOURCE-FACTOR RED (mislabelled effect), policy LD, factor `ld_route_extension`. Bears on task 0.**
  - Symptom: a factor labelled `method` whose tiers change only a number.
  - Root cause: tier 1 is `RND(0.25 × (estimated − threshold applied), 2)`, tier 2 is `RND(0.15 × (estimated − threshold applied), 2)` and tier 3 is "no per-mile extension", which is the same expression with rate 0. It is one formula with a rate chosen from {0.25, 0.15, 0}, so the tiers "only substitute a different number into the same formula (a rate)".
  - Evidence: `batch.extended.yaml`, the `ld_extension` compute line and `factors[id=ld_route_extension].ladder`, whose three `method:` strings are "flat bonus plus 0.25 per estimated mile …", "flat bonus plus 0.15 per estimated mile …" and "the flat bonus alone".
  - Consequence: counted honestly, LD has 5 parameter factors and 0 method, below the per-computation floor of 1 `method`.
  - Affected artifact: `extended_policies[id=batch_ext_long_distance_bonus].factors`.
- **F2 — SOURCE-FACTOR RED (unreal ladder), policy UR. Bears on task 1.**
  - Strand (a), `ur_delivery_distance_method`: tiers 1 and 2 both require "one or more wrong-address violations against the batch". UR's own rule opens "An order that a wrong-address violation recorded against a completed batch shows was handed to the wrong address was not delivered, and the pay … is taken back", and with `ur_wrong = 0` every branch of `ur_share` gives 0 and nothing is booked. So that part of each compound condition holds for every customer who reaches this write. The fall-through tier ("otherwise", meaning no wrong-address violation) is reached by no customer who reaches this write. The ladder that actually divides customers therefore has two tiers (driven beyond tolerance, or within it), below the floor of three, and the baseline tier (posted share rounded half up) is a treatment given to no in-scope customer.
  - Strand (b), `ur_verification_timing`: its tiers' part "a wrong-address violation is recorded" is likewise scope-restating. Its three day-span tiers remain distinct, but the factor cannot count as multi-source.
  - Strand (c), the unreal outcome of tier 1: the rule says the amount is "the pay the batch received for delivering it". The base charter says mileage pay "is always computed on the estimated route … never on actual miles". Tier 1 still recomputes that received pay from the miles driven ("mileage rate times the miles driven beyond the included miles, times the wrong-address violations, divided by the order count"), which can exceed the not-delivered order's share of what was actually posted. It recovers pay that was never paid; the task-1 figures are in `1.md`.
  - Consequence: counted honestly, UR has 3 factors (standing, loyalty, timing), all `parameter`, below the floors of 4 factors and 1 `method`.
  - Affected artifact: `extended_policies[id=batch_ext_undelivered_recovery].factors` and its rule's delivery-distance and timing sentences.
- **F3 — SOURCE-FACTOR RED (two tiers, one method), policy MC, factor `mc_detour_exclusion`. Bears on task 1.**
  - Tier 1 ("≥1 wrong-address AND two or more orders") counts beyond × (orders − wrong) / orders, rounded down to 0.1. Tier 2 ("≥1 wrong-address against a single-order batch") counts none.
  - On tier 2's whole domain (orders = 1, wrong ≥ 1), tier 1's method gives floor(beyond × 0 / 1) = 0.0, which is exactly "none of them count". The auditor's run confirms it for beyond = 3.69, 4.06 and 0.7. One tier has been written as two, and the ladder has two distinct methods (prorate, or all count).
  - Consequence: the factor is struck, leaving MC with 3 factors (tolerance, rate, supplement) and 0 `method`, below the floors.
  - Affected artifact: `extended_policies[id=batch_ext_mileage_claim].factors[id=mc_detour_exclusion]` and the rule's detour-exclusion sentence.
- **F4 — SOURCE-FACTOR RED (two tiers, one value, on one batch type), policies LD and MC.**
  - `ld_amount_by_points`: tier 1 is `amt_clean` 3.00 and the fall-through is `P('long_distance_bonus_usd')`, which is 3.0 for the Stock-Up Batch (batch.yaml, variant Stock-Up Batch). A clean shopper and a shopper with three or more points get the same amount.
  - `mc_claim_rate`: tier 1 is `rate_clean` 0.60 and the fall-through is `P('mileage_rate_usd_per_mile')`, which is 0.6 for the Express 30 Batch.
  - Neither task's world is on those batch types (task 0 is a Triple Delivery Batch, task 1 a Double Delivery Batch), so no scored value in this difficulty is affected. The ladders are still not distinct across the charter's real domain. Bears on tasks 0 and 1 structurally only, and neither task file relies on F4 for its verdict.
- **O1** (duplicate tool surfaces with identical DB effect) — observation; see action_binding_and_uuids.
- **O2** (`reverse_undelivered_pay` can mechanically target a duplicate posting) — observation; see prerequisite_sentences.
- **O3** (the base mileage_underpaid sentence is superseded only in MC's `overwrite`, not in MA's) — observation; the task-1 consequence check is in `1.md`.
- **O4 — observation.** Latent cross-tree interactions outside both worlds:
  - A batch carrying both a duplicate mileage posting and a wrong-address violation would have DR and UR competing for mileage rows under base `reverse_once`.
  - SC's `sc_reversed` counts every reversal, including undelivered ones, with no SC ← UR edge.
  - Neither task's world has such a batch.
- **O5 — observation.** `dr_cashout_method`, `sa_card_method` and `ma_tenure_method` differ between tiers by a multiplier plus the rounding direction (down, up, or none). They are accepted as `method` on the strength of the rounding-direction change, but that algorithmic content is thin.
- **O6 — observation on realism, not a demonstrated RED.**
  - The payout-card plan multiplies a pay bonus (LD) and a pay adjustment (SA).
  - Customer ratings scale a shown-pay guarantee (SC, SA) and a mileage claim (MC).
  - Half of a duplicate is forgiven after a recent instant cashout (DR).
  - Card-linked earnings boosts and rating-linked bonuses exist in gig pay (base itself has `quality_bonus`), so none of these is shown to be a treatment no such business would publish.
- **O7 — observation.** The claimed event types `batch_tip_adjusted_up` and `batch_tip_adjusted_down` are covered by no extended policy. Tip changes are not exercised by this difficulty.
- **O8 — observation.** SC, SA, MC and MA speak of a "completed batch". A batch past `pay_finalize_after_hours` has status `finalized`. The base dispute window (7 or 10 days) and clawback window (30 days) both outlast finalization (24 or 48 hours), and base limits finality to tips ("after that no tip change reaches the batch"), so "completed" reads as "has been completed". The task-1 world (status `finalized`) is examined in `1.md`.
- **O9 — observation.** In `ur_mileage`, SUM of all mileage postings stands in for "the mileage posting it is booked against"; the two are equal when only one posting stands.

## closing_checklist

**Not closed.** Step 4 closes out a difficulty only when every task passes all four relationships, and in this revision both tasks carry REDs. This section was written after both reveals at 2026-09-24T23:51Z. Nothing above it was changed after the reveal.

Status of each Step 4 item:

- **Audit files.** `0.md`, `1.md` and `_difficulty.md` are present and correspond one-to-one with tasks 0 and 1. This is revision 1, with no older revisions.
- **Comparison sections.** Each `source_gt_comparison` section records the per-relationship verdicts. Neither is all-PASS.
- **Coverage and scope.** The seven extended policies are fully covered. The scopes {LD, DR, SC, SA} and {UR, MC, MA} are pairwise disjoint: `charter_scope` of `tasks/0.json` and `tasks/1.json` equals the derived trees. Every task tool uses an independently generated uuid8.
- **Problem trees.** Task 0 has 3 prerequisite problems and 3 `value_input` edges; task 1 has 2 and 2. Each tree contains one problem the customer resolves with an `owner=user` tool. No cycle exists within either tree, and the difficulty-wide graph is also acyclic. PASS.
- **Factors.** **Fails.**
  - Task 0: the LD computation has no honest `method` factor (F1).
  - Task 1: the UR and MC computations each fall below 4 factors with 0 `method` (F2, F3); MC has no near-miss; the MC fall-back figure is misrounded.
  - Charter-wide: two ladders repeat a value on one batch type (F4).
- **Instantiation gates.** Not re-run on a final form, because no final form exists yet. The gate snapshot in the brief is all green, and the check_traceability gate is deferred.

Per-task verdicts, revision 1:

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (T0-2: stale, false `design_rationale` proof sentences) | PASS | **SOURCE-FACTOR RED** (T0-1 / F1) | PASS |
| 1 | PASS | PASS | **SOURCE-FACTOR RED** (T1-1 / F2, T1-2 / F3, T1-3, T1-4) | PASS |

In both tasks the independent blind derivation matched GT on every scored value, argument, owner, order and terminal state.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor who wrote revision 1. Frozen at 2026-09-25T00:10Z, before any revision-2 task file (`tasks/0.json`, `tasks/1.json`) or the difficulty worklog was opened.
- Hashes in force:
  - `batch.extended.yaml`: 8a153a58bbf8be8e28e077946b658d5c22136938b9dd1562c50e91b63b7c3e6b. **Changed** from 4af8c03b…, so every charter-global section below was re-derived in full.
  - `task_tools.py`: 847ff23a…a358, **unchanged**. The tool-module conclusions of revision 1's `### action_binding_and_uuids` (uuid8s, docstrings, no tool judging a prerequisite, O1) are carried forward on the strength of this hash.
- Base section of the extended file: it still equals `blueprint/products/batch.yaml` key for key. The only added key is `extended_policies`.
- Contamination disclosure: the auditor saw the revision-1 GT of both tasks during revision 1. Revision 2 re-derives from the changed charter and the revision-2 views. The reworker's worklog was not read.

### what changed in the charter

| policy | change found by reading the revision-2 text |
| --- | --- |
| LD | `amt_clean` 1.0 and `amt_fair` 0.5 are now *added to* the type bonus. The ladder is type + 1.00 / type + 0.50 / type. `ext_rate_late` was removed. Tier 2 of `ld_route_extension` now reads "the bonus amount times the estimated miles beyond the long-distance threshold that applies, divided by that threshold, rounded down to the ten cents". |
| DR, SC, SA | Rule, compute, factors and prerequisite are textually identical to revision 1. |
| UR | `ur_delivery_distance_method` was removed and `ur_settlement_method` added: ×0.75 rounded down when there was an instant cashout on a fee-charging plan, ×0.5 rounded up when there was a cashout on a no-fee plan, otherwise in full. The timing tiers no longer carry the "a wrong-address violation is recorded" conjunct. `ur_mileage` changed from SUM to LATEST, and the rule speaks of "that posting". Allowances were lowered (loyalty 0.40 / 0.20, timing 0.15 / 0.10). The result is gated on `ur_wrong >= 1`. |
| MC | Detour ladder: ≥1 wrong-address → prorate by delivered orders (never below 0), floored to 0.1 mile; no wrong-address and ≥1 late → halve, floored to a whole mile; otherwise all. The claim rate is now type + 0.10 / type + 0.05 / type. The rule adds "a batch whose pay has since been finalized still counts as completed here". |
| MA | The rule adds "finalized or not". `overwrite` now also names the base mileage_underpaid sentence. |

### policy_conflict_scan (revision 2)

- The subject overlaps are unchanged: DR and UR on `batch_pay_reversed`, SA and MA on `batch_pay_adjusted`.
- The scope trees are unchanged: {SA→SC→{LD,DR}} and {MA→MC→UR}. They are exclusive and together complete.
- One new overlap: the base sentence "mileage_underpaid is owed only when … and then pays mileage_rate_usd_per_mile on the miles above that tolerance." is now superseded twice. MC replaces it with the claim sentence, and MA with the adjustment sentence. The two replacements govern different quantities (claimed amount vs adjustment amount) and neither contradicts the other, so the merged semantics are unique. This is an observation.
- DR's cash-out method (EPC plan → halve) and UR's settlement method (fee plan → ×0.75 down; no-fee plan → halve up) both key on a recent instant cashout, with different plan partitions. They are different quantities, so there is no conflict.

**PASS.**

### rule_compute_equivalence (revision 2)

- **LD.** The new `ld_amount` branches are P(type) + K('amt_clean') / + K('amt_fair') / P(type), matching "the batch type's long-distance bonus plus 1.00 … plus 0.50 … alone". The new tier-2 `ld_extension` is `int(RND(ld_amount*(est−ld_threshold)/MX(ld_threshold,0.1)*10,6))/10`. That matches "bonus amount times the estimated miles beyond the long-distance threshold that applies, divided by that threshold, rounded down to the ten cents". The `MX(…,0.1)` guard is unreachable when the bonus is due (threshold > 0). Every `compute_basis` quotation is verbatim in the rule. PASS.
- **UR.**
  - `ur_mileage = LATEST(mileage)` matches "that posting's amount".
  - `ur_postings >= 1` matches "a batch carrying no mileage posting has nothing to take back".
  - `ur_amount = MN(ur_mileage, MX(0, …))` matches "never below zero" and "never exceeds that mileage posting".
  - `ur_fee_plan` reads `instant_cashout_fee_usd > 0`. That matches "its payout plan charges a fee for instant cashouts", and `payout.yaml` gives 0.5 for Instant Cashout and 0.0 for every other plan.
  - The three settlement branches match the rule's three clauses (×0.75 floor, ×0.5 ceiling, half-up).
  - Gating the result on `ur_wrong >= 1` is justified by the rule's opening sentence.
  - PASS.
- **MC.**
  - The new `mc_late` and the three `mc_counted` branches match the detour sentence. This includes "never below zero", implemented as `MX(order_count − wrong, 0)`, and "halved and rounded down to a whole mile", implemented as `int(RND(b/2,6))`.
  - The new `mc_rate` matches the "type's rate plus 0.10 / plus 0.05 / alone" sentence.
  - The added finalized sentence is scope text and does not appear in compute. That is correct: it is an eligibility reading, not a quantity.
  - PASS.
- **MA.** Compute is unchanged. The added "finalized or not" is scope text. PASS.
- **DR, SC, SA.** Unchanged; revision 1's conclusions stand. PASS.

**Check 2 PASS for all seven policies.**

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged, and so is each policy's `(target_tool, computes)`. Revision 1's conclusion is carried forward: PASS, with O1 still open.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The five edges, their `policy_source` sentences, `condition`, `form`, `gate`, `resolved_by` and `effect` are textually identical to revision 1. Each sentence is still verbatim in its blocked rule.
- UR's rewritten rule still describes "one reversal against the batch's mileage posting on the verified not-delivered ground". It remains the only rule whose write brings about MC's waited-on state.
- None of the new rule text (LD extension, UR settlement, MC finalized clause, MA "finalized or not") states a cross-problem order.

**Checks 6 and 7 PASS.** O2 still stands.

### override_declarations (revision 2)

- **LD.** The declared supersession is unchanged. The new amount ladder is additive to the type bonus, and the merged value is unique. Declared.
- **UR.** Every base clawback sentence is followed. The amount is at most the posting, one row, at most once. `overwrite: []` is still correct, since base fixes no amount.
- **MC.** Unchanged declaration. The finalized sentence follows base: finality in base limits only tip changes.
- **MA.** Both base sentences that govern the mileage-adjustment amount are now named in its own `overwrite`. **O3 is acted on and closed.**
- **DR, SC, SA.** Unchanged.

No undeclared override.

### factor_ladders (revision 2)

| policy | factors (label) | changes and structural verdict |
| --- | --- | --- |
| LD | threshold (p), amount (p), route_extension (m), order_supplement (p), uplift (p) | `ld_amount_by_points`: type + 1.00 / type + 0.50 / type is distinct for every batch type, so **the F4 LD half is closed**. `ld_route_extension`: tier 1 is a fixed 0.25 per mile, rounded to the cent; tier 2 is proportional to the bonus amount (amount × excess ÷ threshold), rounded down to the dime; tier 3 has none. Tier 2's per-mile yield is no longer a published constant: it depends on the bonus amount and the threshold, and the rounding direction and granularity change. **The label is honest, so F1 is closed as a labelling defect.** Tier 2 does, however, introduce **N1** (below). Counts: 4 p and 1 m. |
| DR | unchanged | PASS (O5) |
| SC | unchanged | PASS |
| SA | unchanged | PASS (O5) |
| UR | standing_share (p), loyalty (p), verification_timing (p), settlement_method (m) | The distance ladder is gone, which closes F2 strand (a). The timing tiers are now "0 days / 1–3 days / otherwise", with no scope-restating conjunct, which closes strand (b). The amount is the posted share, which closes strand (c). Settlement is ×0.75 down / ×0.5 up / in full: distinct outcomes, genuinely divided by cashout record and plan, and multi-source (payout events and payout plan). Its effect is a multiplier plus rounding direction, the same thin method as DR's (O5). Counts: 3 p and 1 m, 4 in all. **F2 closed.** |
| MC | tolerance (p), detour (m), rate (p), supplement (p) | Detour tier 1 (wrong-address → prorate by delivered orders, floor to 0.1) now also covers single-order batches, via `MX(…,0)`. The old "single-order → none" tier is gone. The new tier 2 (no wrong-address and ≥1 late → halve, floor to a whole mile) is not tier 1's formula at any input: tier 1 needs wrong ≥ 1, and its proration by delivered orders differs from a flat half. Tier 3 counts all. That gives three distinct methods, so **F3 is closed**. Rate: type + 0.10 / type + 0.05 / type is distinct for every type, so **the F4 MC half is closed**. Counts: 3 p and 1 m. |
| MA | unchanged | PASS (O5) |

### findings (revision 2)

- **N1 — SOURCE-FACTOR RED (unreal ladder: the penalty tier pays more than the good-conduct tier). Policy LD, factor `ld_route_extension`. Bears on task 0.**
  - The factor's ladder divides shoppers whose route clears the type threshold by 3.0 miles or more. Tier 1 is "no late-delivery violation recorded against this batch". Tier 2 is "one or more late-delivery violations recorded against this batch".
  - Tier 1 pays a fixed 0.25 per mile beyond the threshold that applies. Tier 2 pays the bonus amount ÷ that threshold per mile, floored to the dime.
  - The tier-2 yield exceeds 0.25 per mile whenever amount > 0.25 × threshold. On this charter that covers every clean (+1.00) or 1–2-point (+0.50) shopper at the 8.0-mile Gold threshold (2.50 or more against 2.00), and many others. For example, a clean Stock-Up shopper at the type's 15.0 threshold has 4.00 > 3.75.
  - So for those shoppers, having a late delivery recorded against the batch *raises* the bonus above what the same shopper would get for an on-time batch. No gig platform publishes a lateness violation as grounds for a larger distance bonus.
  - This is the "a tier's value or method … that no such business would publish" shape. It was introduced by the round-2 rework of F1, so it is a new defect. The demonstration on task 0's world is in `0.md` revision 2.
- F1, F2, F3 and F4: closed at the charter level (see the table above). T0-2, T1-3 and T1-4 are per-task, so they are judged in the task files.
- O3: closed. O8: acted on in MC and MA, and verified in `1.md` revision 2. O9: acted on (LATEST). O1, O2, O4, O5, O6 and O7: unchanged. O5 now also covers `ur_settlement_method`.
- **O10 (new, observation).** MC and MA both supersede the same base mileage_underpaid sentence, with different replacement texts that govern different quantities. The merged semantics remain unique.

### closing_checklist (revision 2)

This section was written after the revision-2 reveal at 2026-09-25T00:08:30Z. The freeze times printed inside this revision's frozen sections (00:10Z, 00:14Z, 00:17Z) were estimates and are wrong. The file modification times taken just before the reveal are the evidence: `_difficulty.md` 00:07:15Z, `0.md` 00:07:43Z, `1.md` 00:08:25Z, so every freeze preceded the reveal.

**Not closed.** Task 0 still carries a RED (N1).

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS (T0-2 closed) | PASS | **SOURCE-FACTOR RED** (N1, new: the late-delivery extension tier outpays the on-time tier, 5.50 against 5.17 on this world) | PASS |
| 1 | PASS | PASS | PASS | PASS |

**Round-1 items:**

| item | status |
| --- | --- |
| F1 / T0-1 | closed; replaced by N1 in the same factor |
| T0-2 | closed |
| F2 / T1-1 | closed |
| F3 / T1-2 | closed |
| F4 | closed (both halves) |
| T1-3 | closed |
| T1-4 | closed |
| O3, O8, O9 | acted on and closed |
| O1, O2, O4, O5, O6, O7 | unchanged observations, with no scoring consequence. O5 now also covers `ur_settlement_method`. |

**New in revision 2:**
- N1 is a RED.
- O10 is an observation: the base mileage_underpaid sentence is superseded in both MC and MA.

**Regressions:** none outside N1.
- Scope, tree shapes, edges, uuid8s and tool contracts are unchanged.
- All the other factor ladders still bear weight on their worlds.

**Other checklist items:**
- The instantiation gates were not re-run by this auditor. The orchestrator's post-rework snapshot is all rc=0, with check_traceability deferred.
- Coverage and scope exclusivity hold: `charter_scope` equals the derived trees in both tasks.

## revision_3

### charter_global_frozen (revision 3)

- **Auditor and timing.** Same auditor. The revision-3 GT (`tasks/*.json`) and the worklog had not been opened when this section was written. The freeze time is taken from the file modification time recorded before the reveal (see closing_checklist r3), not typed by hand.
- **Hashes and scope of re-derivation.**
  - `batch.extended.yaml` is df36fca7b376001becbf7e57015eaeda128b03d3fcab605d15e3b7d89c985bae. It **changed**, so every charter-global section was re-checked.
  - `task_tools.py` is 847ff23a…a358, **unchanged**. The action-binding and uuid conclusion is carried forward.
  - The base section still equals `products/batch.yaml`.
- **What changed.** Every policy's params and compute were dumped and compared against the revision-2 text:
  - **LD** `ld_route_extension`: the tiers are swapped and rewritten. The no-late tier is now the proportional extension (amount × excess ÷ threshold, rounded down to the dime). The late tier is "only 0.10 for each whole estimated mile beyond the long-distance threshold that applies, part miles not counted". A new param `ext_rate_late` 0.1 was added, and `ext_rate_ontime` is gone.
  - **SA** `share_high_rating`: 1.05 → **1.04**, the same in the rule, `compute_basis`, the ladder and params.
  - **DR, SC, UR, MC, MA**: params and compute are identical to revision 2.
- **Check 2 (verbatim basis).** A mechanical check confirmed that every `compute_basis` quotation, every `policy_source` and every `baseline.rule` appears verbatim in its own rule, with one exception. `ur_share`'s basis ends "…never exceeds that mileage posting." while the rule reads "…never exceeds that mileage posting; a batch carrying no mileage posting…". This is a punctuation-only difference, and the words are verbatim. It was already present in revision 2, where the auditor's check-2 PASS did not catch it. Recorded as **O11 (observation)**: no second reading, no consequence.
- **Other checks.**
  - The rule/compute equivalence for the new LD tiers holds: `K('ext_rate_late') * int(RND(est − threshold, 6))` implements "0.10 for each whole estimated mile … part miles not counted".
  - The prerequisite graph and sentences are unchanged. PASS.
  - Override declarations are unchanged. PASS.

### factor_ladders (revision 3)

**`ld_route_extension` (method).**
- The three tiers are:
  - on-time: proportional to the bonus amount, rounded down to the dime;
  - late: a flat 0.10 per whole mile;
  - otherwise: none.
- Tiers 1 and 2 are different algorithms, so the label is honest.
- **N1 check across the charter's real domain.**
  - The tier-1 per-mile yield is amount ÷ threshold that applies. The amount is at least the type bonus: 2.00 on Single, Double and Triple with a threshold of at most 10; 3.00 on Stock-Up with a threshold of at most 15. So the yield is at least 0.20 per mile.
  - The tier excess (estimated − applied threshold) is at least 3 miles, because the applied threshold is at most the type threshold.
  - Tier 1 is therefore at least 0.20e − 0.10, where e is the excess. Tier 2 is at most 0.10e. The difference is at least 0.10e − 0.10 ≥ 0.20 > 0.
  - **The late tier never pays more than the on-time tier for any in-scope customer. N1 closed at charter level.**

**`sa_rating_approval_share`.**
- The tiers 0.90 / **1.04** / 1.00 remain pairwise distinct. The ordering is unchanged: a low rating is penalised, all four-and-five-star ratings are rewarded, and no rating is neutral.
- The change was made to avoid a half-cent tie in task 0's card-method fall-back. With 1.05 that fall-back sum is 3.73-style arithmetic giving 4.10 × 1.05 + 2.00 = 6.305. With 1.04 it is 6.264.
- A published 4% uplift is as plausible as 5%, and the change introduces no tie, no equal-tier pair and no label change. **Not a defect.**
- Observation **O12**: a charter constant was tuned to one task's arithmetic. This is harmless, but the ladder's value is now chosen for the seed rather than the other way round.

**All other ladders:** unchanged from revision 2 and PASS.

### findings (revision 3)

- **N1: closed** at the charter level (see the analysis above). The task-0 demonstration is in `0.md` r3.
- **New REDs:** none at the charter level.
- **New observations:** O11 and O12.
- **Carried observations:** O1, O2, O4, O5, O6, O7 and O10 are unchanged.

### closing_checklist (revision 3)

Written after the revision-3 reveal at 2026-09-25T00:15:09Z. All three frozen sections have a recorded modification time of 00:15:04Z, which is before the reveal.

- **Audit files.** `0.md`, `1.md` and `_difficulty.md` exist for tasks 0 and 1. Revisions 1, 2 and 3 are appended, and the older text is untouched. The last revision of each `source_gt_comparison` records all four relationships as PASS.
- **Coverage.**
  - All seven extended policies are covered.
  - The scopes {LD, DR, SC, SA} and {UR, MC, MA} are pairwise disjoint and together complete, and each equals its task's `charter_scope`.
  - The task tools and the scored solution are closed.
  - The seven uuid8s are independently generated, and `task_tools.py` has not changed since revision 1.
- **Problem trees.**
  - Task 0 has 3 prerequisite problems, 3 `value_input` edges and one user write (SC).
  - Task 1 has 2 prerequisite problems, 2 `value_input` edges and one user write (MC).
  - The difficulty-wide graph is acyclic.
- **Factors.**
  - Every computation declares 4 to 6 factors, with at least 2 `parameter` and 1 `method`.
  - Each task has at least one multi-source factor and at least one cross-difficulty factor (shopper, payout), with the corresponding rows seeded.
  - Every ladder has three distinct tiers, stated in full in its rule, with no tier equal to another on any batch type.
  - Every factor bears weight against an honest baseline.
  - Every fall-back figure is definite and differs from gold: task 0 gives 2.00 / 6.30 / 7.02 / 4.10; task 1 gives 1.65 / 2.55 / 2.35.
  - Each computation has a near-miss record.
- **Gates.** The instantiation gates were re-run on the final form by the orchestrator after round 3, and all seven returned rc=0. check_traceability is deferred until the KB is published. This auditor cites that snapshot and did not run the gates itself.

**Round-2 and round-3 items:**

| item | status |
| --- | --- |
| N1 | closed |
| SA rating share 1.05 → 1.04 | verified, not a defect (O12) |
| O11 (new, punctuation-only basis slip in UR, present since r2) | observation |
| O1, O2, O4, O5, O6, O7, O10 | observations, unchanged |

**Per-task verdicts:**

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

**The difficulty passes the source-layer audit as of revision 3.**
