# Policy-task audit — driver_earnings_bonuses_and_payouts / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-11T11:50Z (written before any task's GT field was read).
- Frozen inputs (hashes re-computed by the auditor, equal to the brief and to `.audit_views/policy_task/driver_earnings_bonuses_and_payouts/HASHES.txt`):
  - `tasks/driver_earnings_bonuses_and_payouts/earnings.extended.yaml` sha256 `eabe19a915c26f432257ec9e752029a5fc7c3a41f4c84c30f442869ee674d521`
  - `tasks/driver_earnings_bonuses_and_payouts/task_tools.py` sha256 `c6e2124d0017b7274f40963182431ab9a832caee98093a3a25e0bfd6998518c7`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/earnings.yaml` (plus the lifecycle/parameter parts of `rental.yaml` and `driver.yaml` that the cross-category reads name), the extended charter, `task_tools.py`, and the compute evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `RND`).
- Masked and not read: every task file `tasks/*.json`; in the views only `frozen_time`, `user_scenario`, `initial_state` exist, and `design_rationale`, `db_closure*`, `solvability_contract`, `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents` were masked by the coordinator.
- Entry conditions (Step 0): gate snapshot supplied with the brief — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their OK lines; check_traceability deferred to the render stage (needs the published KB). Masked views supplied with hashes, re-hashed by the auditor and equal (`0.view.json` 1263d603…2f185, `1.view.json` c4160470…5b16). Entry conditions complete. Coordinator note on `share_tools.py verify_customer_identity` (loop rewritten to `sum(...)`, equivalent) accepted, not a finding.
- Base copy: lines 1-1115 of the extended charter are byte-identical to `blueprint/products/earnings.yaml` (`diff` shows only the trailing blank line before `extended_policies:`).

### policy_conflict_scan

Extended policies (4) and their trees, as the `prerequisite` graph declares them:

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| earnings_ext_hold_release_payout | lift_payout_hold_7e61ef01 (agent) | payout_amount | [] |
| earnings_ext_guarantee_optin_lock | opt_in_to_guarantee_dc9f134f (user) | guaranteed_amount | -> hold_release_payout (value_input, gate pro_boost, state form) |
| earnings_ext_quest_reward_settlement | credit_quest_reward_07fce82e (agent) | amount | [] |
| earnings_ext_max_instant_cashout | cash_out_to_debit_card_82ffed45 (user) | amount | -> quest_reward_settlement (value_input, gate bal, state form) |

- Two disjoint trees: {guarantee_optin_lock <- hold_release_payout} and {max_instant_cashout <- quest_reward_settlement}. With M=2 the expected scopes are one tree per task; the two trees are pairwise disjoint and together cover all four extended policies (jointly complete). The per-task claim (`charter_scope`) is masked and is compared after the reveal in each task file.
- Overlapping subjects: none — subjects are earnings_payout_release / earnings_bonus_optin / earnings_bonus_credit / earnings_instant_cashout, one per policy.
- Triggers / eligibility / time anchors: hold release is `state_due` and inherits the base resolution test (earnings_payout_holds S3); quest settlement is `state_due`, inherits the base claim window (earnings_evt_bonus `within_claim_window`, 14 calendar days from window_end) and the once-per-offer dedup; guarantee opt-in is `on_request`, open only before the window start (consistent with base `optin_before_window`); cashout is `on_request`, inherits base `active_account` and `new_account_wait` gates.
- Cross-policy reads of another extended policy's write (latent coupling, not a stated order):
  - hold_release reads bonus entries (reserve base, reserve rate) that quest_reward_settlement writes, and instant cashouts (cashout holdback) that max_instant_cashout writes;
  - max_instant_cashout's settling credits read "every credit posted today", which includes the bonus entry its own prerequisite (quest settlement) posts today;
  - max_instant_cashout is gated by base `active_account` ("an account on payout hold cannot cash out"), which hold_release resolves.
  None of these is stated as an order in an extended rule, so none is an undeclared dependency on the charter surface; each becomes a defect only in a world where both writes are due. Each task file checks its own world for it.
- Cross-category read boundaries: driver (current_rating, lifetime_trips, variant_name, standing events quality_warning/safety_report) and rental (status, balance_due, deposit_held, class weekly_rate) — all reads, no writes outside earnings. No conflict found.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back against the rule (all `compute_basis` texts are verbatim rule sentences; `result` bases are two rule sentences each, both verbatim).

- hold_release: `bal` (whole available balance) — ok; `bonus_count`/`bonus_net`/`bonus_latest`/`reserve_base` — counts/sums `earnings_bonus_credit` and `earnings_bonus_clawback` by `entry_date` within 3 whole months (`_within`: 0 <= MONTHS(entry_date, NOW) < 3), latest by `posted_at` across all time; the rule's "most recently posted bonus entry" is necessarily inside the lookback when >= 3 are inside it — equivalent; `disq_count` = fraudulent_trip debits + clawbacks in lookback — ok; `trust_scale` — conjunction rating band AND zero `driver_safety_report` in 6 months — ok; `months_open` = MONTHS(opened_date, NOW) — "whole months … counted from its opened date" ok; `cashout_total`/`cashout_count`/`cashout_share` — ok ("before their fees": cashout rows only); `rental_holdback` — `returned` -> MX(0, due-deposit), `return_due` -> due, else 0 — ok; `result` — MX(0, RND(bal - sum of four, 2)) — ok.
- guarantee_optin_lock: `offer_guarantee`/`offer_start` — latest `earnings_guarantee` issue by `window_start` — "the earnings guarantee offer with the latest window start" ok; `level_scale` — ok; `warnings` — `driver_quality_warning` in 6 months — ok; `quarter_points` — SUM of `earnings_points_credit.points` with `points_period_start = tier_period_start` — the rule says "the Pro points the account has earned in the current quarter"; the account also carries `pro_points_balance` ("Pro points earned in the current quarter", earnings.yaml accounts). Two sources for one rule input; equal by construction in a consistent seed — each task file checks its world. `pro_boost` — compute tests `F('status') == 'active'`; the rule says "on an account whose payouts are not on hold" / "an account on payout hold earns no boost". The two faces differ on accounts in `pending_setup` or `closed` (rule: not on hold -> boost tier; compute: not active -> 0). See finding G-1 (observation: no task of this difficulty reaches those statuses at the opt-in — confirmed per task). `paid_trips`, `activity_scale`, `career_supplement`, `days_ahead` = DAYS(NOW, window_start) ("from the opt-in date to the window's start date"), `early_credit`, `result` (product of four scales on the stated amount, then + supplement + credit, one rounding) — ok.
- quest_reward_settlement: `reward`/`quest_end` — latest `quest` issue by `window_end`; the rule names "the account's most recently ended quest, which is the quest offer with the latest window end on the account". `LATEST` does not filter on window_end <= now; if a world carries a quest whose window has not ended, "most recently ended" and "latest window end" diverge — checked per task. `boost_rate` (account status AND agreement rating) — ok; `standing_scale` (0 / 0.5 / 1.0) — ok; `peak_trips` = count of `earnings_points_credit` rows with `points_basis = peak_trip` in the current quarter — "how many trips earned peak-trip Pro points … in the current quarter" ok; `days_late` = DAYS(window_end, NOW) - bonus_payout_days — "counted from the payout date … to the settlement date" ok; `late_credit` — ok; `result` = RND(reward*(1+boost*standing) + supplement + late, 2) — ok.
- max_instant_cashout: `cashed_today` (all instant cashouts dated today, any channel) — "the instant cashouts already made today" ok; `daily_cap` — ok; `ext_today`/`fee` — free while ext_today < P(free_external_cashouts_per_day); then card_holder_fee if `payout_method == wayfare_debit_card`, else P(instant_cashout_fee_external) — ok; `settling` — every credit type posted today (trip, tip, cancellation, cleaning, bonus, adjustment) / tips only / nothing — ok; `risk_adjusted` — fraud -> ×0.8; else route clawback in 3 months -> minus latest route clawback; else as is — ok; `rental_setaside` — active & due>0 -> due; active -> class weekly_rate; else 0 — ok; `result` = MX(0, MN(cap - cashed_today, RND(risk - setaside - fee, 2))) — the rule's order ("settling … risk … set-aside and fee … compared with the daily limit less today's cashouts") — ok.
- Evaluator note (not a finding against the artifacts): `RND` is Python `round` on a float, which is not half-up at exact half-cent ties; each task file checks whether any scored value lands on a tie.
- Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and every branch of each binding is a tier the rule states. No tier lives only in `compute`.

### action_binding_and_uuids

- `(target_tool, computes)`: (lift_payout_hold_7e61ef01, payout_amount), (opt_in_to_guarantee_dc9f134f, guaranteed_amount), (credit_quest_reward_07fce82e, amount), (cash_out_to_debit_card_82ffed45, amount) — each claimed by exactly one policy.
- uuid8s `7e61ef01`, `dc9f134f`, `07fce82e`, `82ffed45`: no common prefix/suffix, no sequence, no reuse — independently generated on their face.
- Docstrings: none names another tool, none carries a sequencing word (before/after/first) relative to another action ("after the call" in `lift_payout_hold` Returns describes its own receipt). `lift_payout_hold` says "so scheduled payouts and instant cashouts work again" — a state effect of its own write, not an order (observation G-4).
- Function bodies: none of the four reads a prerequisite state or refuses: `lift_payout_hold` sets active and writes a `hold_release` payout row of the given amount (none for 0.00); `opt_in_to_guarantee` creates an `earnings_bonus_optin` row with the given amount; `credit_quest_reward` posts an `earnings_bonus_credit` and raises the balance; `cash_out_to_debit_card` posts the cashout and its fee row and lowers the balance. No tool validates eligibility, status or the prerequisite.

### prerequisite_graph

- `prerequisite` present on every extended policy (`[]` on hold_release and quest_settlement).
- Edges: guarantee_optin_lock -> earnings_ext_hold_release_payout; max_instant_cashout -> earnings_ext_quest_reward_settlement. Both point at extended ids in this file, neither at a base policy or itself; graph acyclic.
- Both `policy_source` strings are verbatim in the blocked policy's own `rule` (checked programmatically) and absent from the depended-on rule.
- Both `form: state`, no `fallback_reason` — consistent.
- `condition` vs sentence: guarantee edge — "status active and payout_hold_reason none whenever the hold reason on record has been resolved (for negative_balance, available_balance above negative_balance_hold_threshold)" equals the sentence's scope ("no longer shows a payout hold whose reason has been resolved"; an unresolved hold does not block). Cashout edge — "an earnings_bonus_credit entry whose bonus_offer_id is the quest offer with the latest window_end, whenever that quest's target was reached and its payout date has passed" equals the sentence's scope. Neither strengthened nor weakened.
- `resolved_by` = the depended-on policy's `target_tool` in both edges; `kind: value_input` with `gate` naming real bindings (`pro_boost` in guarantee compute; `bal` in cashout compute). Whether each `effect` holds is a world fact, checked per task.
- No authoring-viewpoint phrasing in the `prerequisite` fields.

### prerequisite_sentences

1. Guarantee edge — "A locked guarantee is not worked out until the earnings account no longer shows a payout hold whose reason has been resolved."
   - ordering connective "not … until" joining this policy's own result (the locked guarantee) to a state — pass;
   - state form: the waited-on state is record-visible (`earnings_accounts.status`/`payout_hold_reason` and the balance/review facts that decide resolution under base earnings_payout_holds S3) with no action, performer or tool — pass;
   - names no tool, policy id, snake_case token or row id — pass;
   - strength equals `condition` — pass.
   - Single write: within this difficulty only `lift_payout_hold_7e61ef01` moves an account out of payout hold. Derivation: the reader finds `status = payout_hold` with a reason whose base resolution test holds -> the sentence blocks the guarantee -> the only rule that lifts a hold is hold_release ("A payout hold is lifted only when its recorded reason is resolved, and the agent who lifts it sends the hold-release payout at the same moment") -> lift with the hold-release payout. One reading.
2. Cashout edge — "The largest instant cashout is worked out only after the earnings statement carries a bonus entry for the most recently ended quest whose trip target was reached and whose payout date has passed."
   - "only after" — pass; state: a bonus entry on the statement for a named offer — record-visible — pass; no tool/id/token — pass; strength equals `condition` — pass.
   - Single write: only `credit_quest_reward_07fce82e` posts a bonus entry in this difficulty. Derivation: the reader finds the quest with the latest window end, target reached, payout date passed, no bonus entry -> the sentence blocks the cashout -> the rule that posts an unpaid quest reward is quest_settlement ("Support settles an unpaid quest reward for the account's most recently ended quest … once the records show that its trip target was reached … and that its payout date … has passed with no bonus entry") -> credit it. One reading.
- Neither rule carries a second wording, a tool name or another problem's id for its dependency; neither depended-on rule restates the sentence.
- Undeclared orders: no extended rule states a cross-problem order beyond the two sentences. The base sentence "Instant cashout is available only on an active account; an account on payout hold cannot cash out." (earnings_evt_instant_cashout) states a cross-problem gate that hold_release would resolve; it grounds no edge here (observation G-3; a task whose cashout account is on hold would turn it into a RED — checked in task files).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

- hold_release_payout vs earnings_payout_holds: S1 (activation) n/a; S2 (four hold reasons) followed; S3 (lift only when resolved, with the per-reason tests) followed — extended S1 restates "lifted only when its recorded reason is resolved" and inherits the tests; S4 (earnings keep posting) followed; S5 (payout method) n/a; S6 (closing) n/a. vs earnings_evt_weekly_payout: S1 (payable states) compatible (the tool sets active in the same call); S2 (weekly, min amount, carry-forward) compatible ("any amount kept back … is paid with the next scheduled weekly payout"); S3 first clause — handled differently (whole held balance -> balance less four holdbacks) and **declared** in `overwrite`; S4 (no payouts on hold, no other off-cycle payouts) compatible. Merged semantics unique.
- guarantee_optin_lock vs earnings_evt_bonus: S1 followed; S2 n/a; S3 (guarantee pays guaranteed_amount less window earnings) — handled differently (locked guarantee) — **declared**; S4 (opt-in before window_start, driver's own action) followed and narrowed to the upcoming guarantee; S5-S7 n/a/compatible. vs earnings_pro_tier_evaluation S4 (status benefits = instant cashout fees and free cashouts) — "superseded" by "The Pro boost follows the Wayfare Pro status …" although the boost does not conflict with that sentence (see G-2).
- quest_reward_settlement vs earnings_evt_bonus: S2 quest clause (pays reward_amount once) — handled differently — **declared**; S5 (post within bonus_payout_days, once per offer) followed; S6 (claim window) not restated, inherited — whether it bites is a world fact (checked per task); S7 (near misses never paid) followed (target must be reached). vs earnings_pro_tier_evaluation S4 — same over-declaration as above (G-2).
- max_instant_cashout vs earnings_evt_instant_cashout: S1 (active only) inherited; S2 (waiting period) inherited; S3 (daily max 500) — handled differently (daily cashout limit ladder) — **declared**; S4 (fee schedule) — handled differently (card-holder fee tier) — **declared**; S5 ("never waived outside these rules") compatible with the new rules; S6 (driver's own act) followed. The extended rule's further reductions (settling credits, risk method, rental set-aside) add limits beneath base's "no more than the available balance" without contradicting it; the extended rule fixes the "as much as possible" amount explicitly, so base yields no competing value for that request. vs earnings_pro_tier_evaluation S4 — replaced by "The daily cashout limit follows …", while the extended rule itself keeps the fee/free-cashout dependence on status ("under the driver's Pro status") — no loss of content in the merged surface.
- Disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch): none found. `standing_scale` 0 tier multiplies only the boost (declared in the rule: "so no boost is paid"), not the stated reward.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| hold_release | reserve_base_selection | method | reserve_base | 3 (latest / net total / nothing) | no (ledger only) | — |
| hold_release | reserve_rate | parameter | reserve_rate | 3 (1.0 / 0.5 / 0) | no (ledger only; two event types) | — |
| hold_release | trust_scale | parameter | trust_scale | 3 (0.5 / 0.75 / 1.0) | yes (agreement rating AND standing record) | driver |
| hold_release | new_account_holdback | parameter | tenure_holdback | 3 (60 / 30 / 0) | no | — |
| hold_release | cashout_holdback_share | parameter | cashout_share | 3 (0.2 / 0.1 / 0) | no | — |
| hold_release | ended_rental_holdback | method | rental_holdback | 3 (due-deposit floored / whole due / nothing) | no (rental row) | rental |
| guarantee | level_scale | parameter | level_scale | 3 (1.25 / 1.1 / 1.0) | no | driver |
| guarantee | quality_scale | parameter | quality_scale | 3 (0.85 / 0.93 / 1.0) | no | driver |
| guarantee | pro_boost | parameter | pro_boost | 3 (0.08 / 0.04 / 0) | yes (account status/tier AND ledger points) | — |
| guarantee | activity_scale | parameter | activity_scale | 3 (0.8 / 0.9 / 1.0) | no | — |
| guarantee | early_career_supplement | parameter | career_supplement | 3 (20 / 10 / 0) | no | driver |
| guarantee | early_optin_credit | method | early_credit | 3 (flat 15 / 4 per day / nothing) | no | — |
| quest | pro_boost_rate | parameter | boost_rate | 3 (0.10 / 0.05 / 0) | yes (account tier AND agreement rating) | driver |
| quest | standing_scale | parameter | standing_scale | 3 (0 / 0.5 / 1.0) | no | driver |
| quest | peak_driver_supplement | parameter | peak_supplement | 3 (12 / 6 / 0) | no | — |
| quest | late_settlement_credit | method | late_credit | 3 (2 per day / flat 5 / nothing) | no | — |
| cashout | daily_cashout_limit | parameter | daily_cap | 3 (1000 / 750 / 500) | yes (account tier AND agreement lifetime trips) | driver |
| cashout | cashout_fee | parameter | fee | 3 (0 / 0.40 / P(instant_cashout_fee_external)) | no (ledger count; payout method on account) | — |
| cashout | settling_credits | method | settling | 3 (all credits today / tips today / nothing) | no | — |
| cashout | risk_method | method | risk_adjusted | 3 (×0.8 / minus latest route clawback / as is) | no | — |
| cashout | rental_setaside | parameter | rental_setaside | 3 (balance due / class weekly_rate / 0) | no | rental |

- Counts: hold_release 6 (4 parameter, 2 method); guarantee 6 (5 parameter, 1 method); quest 4 (3 parameter, 1 method); cashout 5 (3 parameter, 2 method) — all within 4-6, each >= 2 parameter and >= 1 method.
- Per tree: tree {hold_release, guarantee} has multi-source factors trust_scale and pro_boost and driver cross-difficulty factors (trust_scale, level_scale, quality_scale, early_career_supplement); tree {quest, cashout} has multi-source pro_boost_rate and daily_cashout_limit and driver cross-difficulty factors (pro_boost_rate, standing_scale, daily_cashout_limit). `rental` is not a difficulty of this scenario (blueprint claims trip, pass, damage, earnings, driver), so the two `cross_difficulty: rental` labels read another category, not another difficulty (observation G-5); each tree has driver factors regardless.
- Bindings disjoint within each policy; every `decides` is an input, never `result`.
- Every fall-through tier equals that factor's `baseline` binding, and every baseline equals what `baseline.rule` implies for the input (hold release: nothing kept back -> every holdback 0, reserve base 0, rate 0, trust 1.0; guarantee and quest: stated amount unchanged -> every scale 1.0, boost 0, supplements/credits 0; cashout: balance less fee capped at max-minus-today with standard limit and fee -> cap P(500), fee P(fee_external), settling 0, risk as is, set-aside 0).
- Labels honest: method factors change what is computed (latest vs net sum; floored difference vs whole due; flat vs per-day×days; all credits vs tips; ×share vs minus latest clawback); parameter factors substitute a number.
- Distinct outcomes: every ladder's three outcomes are pairwise distinct as stated, except `cashout_fee` whose fall-through value `P('instant_cashout_fee_external')` is 0.00 for Wayfare Pro Diamond Elite (earnings.yaml line 390), coinciding with the "free" tier, and whose first tier is unreachable for Blue/Silver (free_external_cashouts_per_day 0). Status-dependent collapse — observation G-6, a defect only on a world at those statuses (checked in task 1).
- Real-ladder judgement: every condition is one a driver-earnings business weighs for that quantity (fraud/clawback history, rating and safety reports, tenure, cashout velocity, rental exposure, service level, warnings, Pro tier and points, activity, career length, timing of opt-in/settlement, payout method). Two ladders are unusual but not demonstrably unreal: `reserve_base_selection` gives a smaller base (latest bonus alone) to a driver with more bonuses, and `cashout_holdback_share` holds back a share of cashouts that have already left the account (observation G-7). No condition holds of every customer who reaches the write.

### findings

- G-1 (observation; bears on task 0 only if its opt-in account is `pending_setup`/`closed` — checked there). Symptom: rule/compute faces of `pro_boost` differ outside {active, payout_hold}. Evidence: rule "on an account whose payouts are not on hold earns boost_top … or an account on payout hold earns no boost"; compute `… and F('status') == 'active'`. Consequence: on a `pending_setup` Silver account with >= 30 points the rule gives 0.04, compute 0. No task of this difficulty reaches that state (see task files), so no scored value is demonstrated to move. Affected: earnings.extended.yaml, earnings_ext_guarantee_optin_lock rule / compute `pro_boost`.
- G-2 (observation). Symptom: three extended policies each declare `earnings_pro_tier_evaluation` S4 ("Status benefits (instant cashout fees and free cashouts) follow the status recorded on the account for the current quarter.") superseded, each with a different replacement (Pro boost / Pro boost rate / daily cashout limit), although none of the three contradicts S4. Consequence: none demonstrable — the cashout rule restates the status dependence of fees and free cashouts in its own words. Affected: `overwrite` entries of guarantee_optin_lock, quest_reward_settlement, max_instant_cashout.
- G-3 (observation; checked in task 1). Base sentence of earnings_evt_instant_cashout states a cross-problem gate (account on payout hold cannot cash out) that would make hold_release a prerequisite of cashout with no extended prerequisite sentence.
- G-4 (observation). `lift_payout_hold_7e61ef01` docstring "so scheduled payouts and instant cashouts work again" describes a downstream availability; not a sequence word, no other tool named.
- G-5 (observation). `cross_difficulty: rental` on `ended_rental_holdback` and `rental_setaside` names a category no difficulty claims.
- G-6 (observation; checked in task 1). `cashout_fee` ladder collapses at Diamond Elite (fall-through 0.00 = free tier) and loses its first tier at Blue/Silver.
- G-7 (observation). `reserve_base_selection` inverts magnitude with bonus count; `cashout_holdback_share` holds back a share of past cashouts — unusual but not shown to be unreal.
- Latent couplings to check per world (from policy_conflict_scan): quest settlement due in task 0's world (would move the reserve base); hold due in task 1's world (would gate the cashout); task 1's quest bonus posting today vs the settling-credits tier; quest "most recently ended" vs a not-yet-ended quest in task 1's world; account `pro_points_balance` vs ledger points sum in task 0's world.

## closing_checklist

Written after both tasks' derivations were frozen (mtimes 0.md 11:49:49Z, 1.md 11:51:39Z) and revealed (from 11:51:42Z). The "Freeze time" stated in `charter_global_frozen` above (11:50Z) was an estimate; this file's charter-global section was written at 11:47:34Z (file mtime), before any reveal, and contains nothing derived from GT.

- Audit files: `_difficulty.md`, `0.md`, `1.md` — one per task plus this charter file; first revision, no older revisions. Both comparison sections carry PASS.
- Coverage and scope: task 0 = {earnings_ext_hold_release_payout, earnings_ext_guarantee_optin_lock} with tools {lift_payout_hold_7e61ef01, opt_in_to_guarantee_dc9f134f}; task 1 = {earnings_ext_quest_reward_settlement, earnings_ext_max_instant_cashout} with tools {credit_quest_reward_07fce82e, cash_out_to_debit_card_82ffed45}. Pairwise disjoint, union = all four extended policies and all four task tools. GT write steps use only these tools. uuid8s independently generated (see `action_binding_and_uuids`).
- Trees: each has 1 prerequisite problem, 1 value_input edge (>= max(n-1,1) = 1), one owner=user write (opt-in; cashout), no cycle; the difficulty-wide graph (two disjoint edges) is acyclic.
- Factors: hold release 6 / guarantee 6 / quest 4 / cashout 5, each >= 2 parameter and >= 1 method; per task >= 1 multi-source (task 0: trust_scale, pro_boost; task 1: pro_boost_rate, daily_cashout_limit) and >= 1 driver cross-difficulty factor; every ladder 3 distinct tiers on the task worlds, stated in full in the rule; all 21 factors bear weight against honest baselines; whole-baseline numbers (160.67, 240.00, 80.00, 440.00) differ from gold (62.17, 232.27, 93.00, 667.27).
- Gates on the final form: the audited artifacts are unchanged since the coordinator's gate snapshot (extended charter `eabe19a9…d521`, task_tools `c6e2124d…18c7` re-hashed after the reveal and equal; the task files hashed at reveal `5143ed1e…` / `cfed8415…`). Per Step 0 the auditor does not run the gates; the supplied snapshot (all rc=0; traceability deferred to render) stands for the final form.
- Difficulty verdict: policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS for both tasks — the difficulty passes the source-layer audit. Open items are observations only: G-1 … G-7 (above) and T1-O1 (`1.md`).
