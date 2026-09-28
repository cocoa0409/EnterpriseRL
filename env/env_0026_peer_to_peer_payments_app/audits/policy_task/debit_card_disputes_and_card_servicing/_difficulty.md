# Policy-task audit — debit_card_disputes_and_card_servicing / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T23:40Z (round r1). Auditor: independent erl-task-policy-audit subagent (Claude Opus 5.5). I did not write any artifact under audit.
- Frozen inputs (sha256):
  - `tasks/debit_card_disputes_and_card_servicing/card.extended.yaml` = `b2bbbfe15f1def79b051e1ec5a5c956062950483e109305499a5716ecd730c0d`
  - `tasks/debit_card_disputes_and_card_servicing/task_tools.py` = `2bb93a2f0400b5ec11bde301637192beab09b51e9f11eb1b2feea3995d2d19da`
  - masked views `0.view.json` = `53ba191c…3bc` and `1.view.json` = `021012c8…ba3` (coordinator-built; each keeps only task_index, frozen_time, user_scenario, initial_state). I re-hashed both and they match the brief.
- Fields I read before the freeze: `blueprint/blueprint.yaml` (the difficulty entry), `blueprint/products/card.yaml`, `blueprint/products/wallet.yaml` (event and field meanings for restriction/recovery, plan ranks, cooling-off hours), `blueprint/share_tools.py` (read-tool contracts), the extended charter, `task_tools.py`, the two masked views, the gate snapshot `snap/d2_r1.txt`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (function bodies of MONTHS/DAYS/SUM/LATEST/XSUM/CFIELD/RND only, with no task data).
- Fields I masked and did not read before the freeze: every `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure) and `tasks/debit_card_disputes_and_card_servicing/worklog.md`. I ran no recursive search over `tasks/` or the scenario root.
- Nothing in this charter-global section comes from a revealed GT.

### entry_conditions (Step 0)

The brief supplied the gate snapshot. Every gate is green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 11 acts 22/22, 1.json 11 acts 24/24), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. check_traceability.py is deferred to step 3, which the coordinator states. The masked views and their hashes were also supplied. The input is complete.

Base copy: `diff` of lines 1–1085 of the extended charter against `blueprint/products/card.yaml` differs only by one trailing blank line, so the base section is verbatim.

### policy_conflict_scan

The extended charter has four policies. All four have `trigger: on_request`, and both cross-category blocks read only `wallet`:

| id | subject | computes | target_tool (owner) |
| --- | --- | --- | --- |
| A `card_ext_takeover_card_liability` | card_dispute_filed | customer_liability | `file_unauthorized_card_dispute_b9450be9` (user) |
| B `card_ext_takeover_card_final_credit` | card_dispute_resolved, card_dispute_credit | credit_amount | `post_takeover_dispute_credit_edfadedb` (agent) |
| C `card_ext_single_use_incorrect_amount` | card_dispute_filed | dispute_amount | `file_incorrect_amount_card_dispute_a0bf950b` (user) |
| D `card_ext_single_use_filing_credit` | card_dispute_credit | credit_amount | `post_on_filing_dispute_credit_86bd6080` (agent) |

- Overlapping subjects:
  - A and C both write card_dispute_filed, but A covers reason `unauthorized` on a takeover card and C covers reason `incorrect_amount` on a single-use card. Base `one_dispute_per_transaction` keeps them exclusive on any one transaction.
  - B and D both book card_dispute_credit, but on disjoint dispute reasons, and each reads only its own reason (`dispute_reason='unauthorized'` / `'incorrect_amount'`).
  - No two policies reach different conclusions on the same object.
- Time anchors: A counts notice days from a selected start date to the filing date (NOW). B and D read tenure "on the filing date" (NOW). All three agree on one clock.
- Terminal states:
  - B writes a resolved/approved record plus a final credit.
  - D writes only a credit and leaves the dispute open.
  - Neither conflicts with the other.
- Cross-category reads: A reads wallet restriction_reason, restricted_at, recovered_date and wallet_direct_deposit. B reads wallet variant_name, restricted_at, recovered_date and opened_date. D reads wallet opened_date, variant_name, restriction_reason, restriction_lifted_date and wallet_direct_deposit. Each matches its `cross_category` declaration.
- Scope exclusivity: the worlds imply two trees. Tree 0 is {B root, A prerequisite} and tree 1 is {D root, C prerequisite}. They are pairwise disjoint and together cover all four extended policies. The gate's SCOPE/EXTENDED lines say the same. I confirm the per-task claim only after the reveal, in the task files.
- Base conflicts: see `override_declarations`, finding F1.

### rule_compute_equivalence

I swept each binding against its `compute_basis` quote and each rule sentence back against compute.

- A:
  - `settled_purchases` SUM card_purchase on the card ↔ "every settled purchase on such a card is the activity in dispute"
  - `latest_purchase_date` ↔ the notice start sentence
  - `notice_start` three-branch expression ↔ the three-branch sentence. `0 <= lock_after_issue_days <= K(1)` renders "issued no more than takeover_issue_window_days calendar days before the day that lock was placed", and "before" supplies the lower bound 0. `block_reason=='compromised' and DAYS(latest, blocked)>=0` ↔ "blocked as compromised and the block date is on or after the settlement date"
  - `notice_days` = DAYS(start, NOW) ↔ "calendar days from the notice start date to the filing date"
  - `notice_cap` three tiers, with RND on the 50% tier ↔ the sentence
  - `deposits_two_months` XSUM within_months=2 (MONTHS(d,NOW) in [0,2)) ↔ "over the two months up to the filing date"
  - `deposit_relief` and `block_relief` three tiers each ↔ their sentences
  - `liability_ceiling` RND(cap×dr×br) ↔ "multiplied … then …, rounded"
  - `result` RND(MN(settled, ceiling)) ↔ the result sentence
  - Every sentence of the rule has a binding. Compute invents no basis.
- B:
  - `disputed_open` and `liability_open` (filed − resolved, reason unauthorized, on the card) ↔ the "open disputed amount … the open liability is worked out the same way" sentence
  - `liability_kept` three branches ↔ the absorption sentence, with `0 <= DAYS(issued, restricted_at) <= 1` ↔ "placed no more than fast_lock_days calendar days after the takeover card's issue date"
  - `lock_length_days` and `lock_courtesy` ↔ "from the day it was placed to the recovered date"
  - `foreign_fees` and `fee_return` (tier names verbatim) ↔ the fee-return sentence
  - `tenure_months` MONTHS(opened, NOW) and `tenure_courtesy` ↔ the tenure sentence
  - `result` RND(MX(0, open − kept) + courtesies) ↔ "never below zero, plus …"
  - The rule's first two sentences (definition, approval on filing) and the prerequisite sentence carry no quantity.
- C:
  - `linked_authorization` (hold whose id is the purchase's source_txn_id) ↔ "the authorization the purchase settled against"
  - `authorization_count` and `same_day_authorizations` (count of holds dated on the latest hold date) ↔ "two or more … all of them were placed on the same day"
  - `authorized_reference`, `gratuity_pct` (the dining_any≥1 conjunct is redundant but harmless), `exchange_pct` (lag = DAYS(latest hold date, latest purchase date)), `credits_counted` ↔ their tier sentences
  - `result` MN(settled, MX(0, …)) ↔ "never below zero and never more than the settled purchase amount"
  - The sweep back is clean.
- D:
  - `overcharge_on_record` (filed − resolved, reason incorrect_amount, on the card) ↔ its sentence
  - `tenure_multiplier`, `scaled_threshold`, `deposit_uplift` (within_months=3), `plan_uplift`, `standing_uplift`, `merchant_ack_uplift`, `on_filing_ceiling`, `on_filing_credit` ↔ their sentences
  - The sweep back is clean.
- Factor ladders against the rule: every tier named in each `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch of each binding is a tier the rule states. No tier appears in only one face.
- Rounding convention: the DSL's `RND` is Python `round(float, 2)`, while every rule says "half up". The two differ only on an exact half-cent float. Observation O1 records this; the task files check whether either world hits such a value.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are (b9450be9, customer_liability), (edfadedb, credit_amount), (a0bf950b, dispute_amount) and (86bd6080, credit_amount). Each tool is claimed by exactly one policy.
- Docstrings: none names another tool, a policy id or a position in a sequence.
  - b9450be9 and a0bf950b say "The cardholder then sees the dispute as open (pending)". This describes the result of the same call, not an order among calls (observation O2).
  - edfadedb says "Records the outcome approved on an open unauthorized dispute", and 86bd6080 says "for an open merchant dispute … stays open". Each identifies its object by state. Neither is a runtime hint and neither is a refusal (observation O2).
- UUID8s are b9450be9, edfadedb, a0bf950b and 86bd6080. No two share a prefix or suffix, none is sequential or adjacent to another, and none is a copy with a changed tail. I find no evidence of batch derivation.
- Tool bodies: none checks status, eligibility, ownership or a prerequisite. `post_takeover_dispute_credit_edfadedb` looks up the filed record only to copy its reason, amount and liability, and falls back to defaults when there is none; it never refuses. The other three perform one create each (plus one credit row in edfadedb). The tool layer judges no prerequisite.

### prerequisite_graph

- `prerequisite` is filled in on all four: A `[]`, C `[]`, B → A, D → C. Every `problem` names an extended policy of this file, never a base policy and never itself. The graph has two disjoint edges and no cycle.
- B → A:
  - `policy_source` "The final credit is booked only after the takeover card's purchase stands on the records with an open unauthorized dispute carrying its recorded customer liability." appears verbatim as sentence 3 of B's rule.
  - form state, no fallback_reason, which is correct.
  - kind value_input, gate `disputed_open`, which is a real binding of B's compute.
  - `resolved_by` = A's target_tool. `condition` (filed unauthorized record with dispute_amount and customer_liability, no resolved record) is neither stronger nor weaker than the sentence.
  - `effect` is correct: filing raises disputed_open and liability_open from 0.
- D → C:
  - `policy_source` "The credit on filing is not booked until the single-use card's purchase stands on the records with an open incorrect-amount dispute." appears verbatim as sentence 2 of D's rule.
  - form state. kind value_input, gate `overcharge_on_record`, which is a real binding.
  - `resolved_by` = C's target_tool. `condition` matches. `effect` is correct.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

- B's sentence:
  - The connective is "only after". The waited-on state is "the takeover card's purchase stands on the records with an open unauthorized dispute carrying its recorded customer liability". That is record-visible: find_card_disputes shows event_type, dispute_reason, customer_liability and resolution.
  - It names no tool, policy id, snake_case token or row id, and its scope is exactly the condition.
  - Exactly one write of this difficulty creates an unauthorized card_dispute_filed row: A's `file_unauthorized_card_dispute_b9450be9`. No shared tool writes card_disputes.
  - Derivation: the sentence plus the records (no unauthorized dispute on the takeover purchase) plus A's own rule ("This rule settles the customer liability recorded when the cardholder disputes, as unauthorized, a purchase on a virtual card they say they never created") lead to A's filing, and to no other action.
  - A's rule does not restate the sentence. B's rule carries no second wording.
- D's sentence:
  - The connective is "not … until". The waited-on state is "an open incorrect-amount dispute" on the single-use card's purchase, which is record-visible.
  - Exactly one write creates it: C's `file_incorrect_amount_card_dispute_a0bf950b`. C's rule ("This rule settles the amount the cardholder disputes as an incorrect amount on the purchase made with a single-use virtual card") identifies it uniquely.
  - C's rule does not restate the sentence.
- Other cross-problem orders in the rules:
  - No extended rule states an order that grounds no edge.
  - Base `card_disputes_unauthorized` says "a card still active or locked must be blocked as compromised first". That is a base cross-problem order, not an extended edge. It grounds no edge here and is observation O3; each task file checks whether its tree rests on it.

### override_declarations

Findings only. Each task file demonstrates the consequence against its own world.

- A vs `card_disputes_unauthorized`:
  - s1 (coverage) followed. A's "takeover card" is a subset of unauthorized activity.
  - s2 (blocked or closed only) inherited.
  - s3/s4 (report window) inherited.
  - s5 (one dispute per transaction) inherited.
  - s6 (liability = lower of dispute amount and timely/late cap by business-day notice) replaced and **declared**.
  - **s7 ("A dispute amount at or below small_dispute_auto_credit_threshold is credited in full as final on filing … without liability or investigation.") — A handles the same quantity differently and does not declare it**: A's liability applies to every takeover purchase whatever its amount. This is finding F1.
  - s8–s11 (provisional credit, rolling cap, investigation, approval) govern credits, not liability, and B handles them.
- A vs `card_disputes_merchant`:
  - A declares the merchant-contact sentence overwritten. That sentence applies only to goods-not-received, not-as-described and credit-not-processed merchant disputes, never to an unauthorized dispute, so the declaration replaces a sentence that did not conflict (observation O4).
  - The remaining merchant sentences do not govern unauthorized disputes.
- B vs `card_disputes_unauthorized`:
  - s8 ("Otherwise provisional credit …") declared.
  - s11 ("The disputes team records approved or denied") declared.
  - s10 (rolling-cap withholding and new-card timings) governs provisional-credit and investigation timing only, which B eliminates. Its conclusion "credited only on approval" is compatible with approval on filing.
  - **s7 is not declared by B.** B's overwrite of s8 names the "Otherwise …" sentence, which covers only disputes above the threshold. For a takeover purchase at or below the threshold, s7 credits in full with no liability, while B credits the open amount less the liability kept plus courtesies. This is F1.
  - B vs `card_disputes_merchant`: no merchant sentence governs an unauthorized dispute.
- C vs `card_disputes_merchant`:
  - m1 (coverage: charged at the wrong amount) followed.
  - m2/m3 (window) inherited.
  - m4 declared, with the same meaning restated ("need no merchant contact").
  - m5 (no liability, no provisional credit, one dispute per transaction) followed; C's rule says "A merchant dispute records no customer liability". m5's small-dispute auto-credit clause governs the credit, not dispute_amount, and D handles it.
  - m6 (documents and team decision) inherited.
  - The base defines no dispute amount for merchant disputes, so C sets a new quantity rather than overriding one.
- C vs `card_disputes_unauthorized`: no sentence governs an incorrect-amount dispute_amount.
- D vs both refs: s7 and m5's auto-credit clause are **declared** by D for "an open incorrect-amount dispute of a single-use card purchase". No other base sentence governs the credit on filing.
- Disguised forms:
  - No anonymous intermediate override was found.
  - No 0/1 multiplier was found: B's `liability_kept = 0` is a declared factor tier, not an existence gate on a base quantity.
  - No dropped branch was found.

### factor_ladders

Structure only. Whether a factor bears weight is decided in each task file's `factor_weight`.

| policy | factor | label | decides | tiers | multi-source (non-fall-through tiers) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| A | notice_start_date | method | notice_start | 3 | yes (wallet lock reason and time vs card issue date; card block reason and date vs purchase date) | wallet |
| A | notice_cap_tier | parameter | notice_cap | 3 | no (notice days only) | — |
| A | deposit_relief_tier | parameter | deposit_relief | 3 | no | wallet |
| A | block_relief_tier | parameter | block_relief | 3 | no | — |
| B | liability_absorption | method | liability_kept | 3 | yes (wallet plan and wallet lock time vs card issue date) | wallet |
| B | lock_courtesy_tier | parameter | lock_courtesy | 3 | no | wallet |
| B | fee_return_tier | parameter | fee_return | 3 | yes (fee rows and card tier) | — |
| B | tenure_courtesy_tier | parameter | tenure_courtesy | 3 | no | wallet |
| C | authorized_reference_rule | method | authorized_reference | 3 | yes (several authorization rows and their dates) | — |
| C | gratuity_rate_tier | parameter | gratuity_pct | 3 | no (two fields of one purchase row) | — |
| C | exchange_tolerance_tier | parameter | exchange_pct | 3 | yes (purchase row and authorization row date) | — |
| C | merchant_credit_rule | method | credits_counted | 3 | yes (credit rows and the purchase link) | — |
| D | tenure_multiplier_tier | **method (mislabelled; see F2)** | tenure_multiplier | 3 | no | wallet |
| D | deposit_uplift_tier | parameter | deposit_uplift | 3 | no | wallet |
| D | plan_uplift_tier | parameter | plan_uplift | 3 | no | wallet |
| D | standing_uplift_tier | parameter | standing_uplift | 3 | no (one wallet row) | wallet |
| D | merchant_ack_tier | parameter | merchant_ack_uplift | 3 | no | — |
| D | near_ceiling_release | method | on_filing_credit | 3 | no (one derived comparison) | — |

- Counts:
  - A: 4 factors (3 parameter, 1 method).
  - B: 4 (3 parameter, 1 method).
  - C: 4 (2 parameter, 2 method). C has no cross-difficulty factor; its tree partner D supplies one.
  - D: 6 factors. As labelled that is 4 parameter and 2 method. Counted honestly it is 5 parameter and 1 method (near_ceiling_release), which still meets the method floor.
- Bindings are pairwise disjoint within each policy, and no factor `decides` `result`.
- Each ladder has three pairwise-disjoint tiers with the fall-through counted. No two tiers of one ladder select the same value or method: the values differ (for example 0.6/0.8/1, 10/5/0, 1.5/1.25/1, 15/20/0), and the methods differ (sum/max/linked, all/linked+latest-unlinked/linked, whole/ceiling+half/min, recovered/block/purchase date, 0/−cap/identity).
- Every tier is stated in its rule and implemented in compute. The baselines agree with each `baseline.rule`:
  - A: notice start = latest purchase, binary timely/late cap, reliefs 1.
  - B: kept = open liability, courtesies 0.
  - C: linked authorization, rates 0, linked credits.
  - D: multiplier 1, uplifts 0, min.
  - Each baseline.rule sentence is in its rule, and the `params` keys are ones the baseline uses. Each fall-through tier equals its baseline.
- Label honesty:
  - The method factors of A, B and C, and D's near_ceiling_release, change the algorithm.
  - A's notice_start_date selects which record anchors the day count. I accept that as a method of counting notice (observation O5: it is the nearest to a mere input substitution).
  - **D's tenure_multiplier_tier is labelled `method`, but its tiers substitute only a number** (1.5, 1.25 or 1) into the one formula `RND(P('small_dispute_auto_credit_threshold') * tenure_multiplier, 2)`. This is F2.
- Realism: every condition is one the line of business weighs (notice timing, account-takeover lock, deposits and plan relationship, tenure, merchant credits, incremental versus re-authorization, dining gratuity, foreign-exchange drift). None holds of every customer who reaches the write. Three ladders have outcomes I cannot prove unreal but record as observations:
  - O6: A's block_relief lowers liability the longer the takeover card stayed unblocked (0.8 at 3 or more days, 1 on the issue day). The same rule makes later notice raise the cap, so the two point in opposite directions. It can be read as issuer-detection-lag relief.
  - O7: B's fee_return returns only 50% of the foreign fee charged on a purchase that is being credited as unauthorized on lower tiers.
  - O8: D's plan_uplift fall-through (Lite or Core) and its Plus half are reachable for a single-use card holder only through a later plan downgrade. Single-use cards exist only from Platinum up, and Platinum needs Prime or higher.
- Cross-difficulty reads all go to `wallet` (the personal account row and wallet_direct_deposit rows). Whether those rows are seeded is checked per task.

### findings

- **F1 — SOURCE-POLICY RED (charter-global; bears on the policies of task 0).**
  - Symptom: base `card_disputes_unauthorized` s7 and extended A/B reach different liability and credit results for a takeover-card purchase at or below the tier's small_dispute_auto_credit_threshold.
  - Root cause: undeclared override. A's `overwrite` names only s6, and B's names only s8 and s11. Neither names s7.
  - Evidence: base s7 reads "A dispute amount at or below small_dispute_auto_credit_threshold is credited in full as final on filing as a card_dispute_credit and resolved approved the same day, without liability or investigation." A reads "The liability recorded on the dispute is the lower of the takeover card's settled purchases and the liability ceiling …". B reads "The final credit is the open disputed amount less the liability kept by the customer, never below zero, plus the lock courtesy, the fee return and the tenure courtesy …".
  - Demonstrated consequence (constructed situation):
    - The situation: a takeover virtual card on Pocketwire Visa Signature Debit (threshold 25.00, liability_cap_late 50.00), issued on day 0. One purchase of 20.00 settles on day 1.
    - The linked Pocketwire Prime account has a suspected_account_takeover lock placed on day 5, so A's tier 1 and B's fast-lock absorption both fail.
    - The card is blocked as compromised on day 6, so A's tier 2 starts the notice count on day 6. The dispute is filed on day 18, giving 12 notice days, which is over 10, so the notice cap is 50.00.
    - Direct deposits are under 300.00, so deposit relief is 1. The card was blocked 6 days after issue, so block relief is 0.8.
    - Base s7 gives liability 0.00 and credit 20.00 in full.
    - A gives ceiling 40.00 and liability min(20.00, 40.00) = 20.00. B then gives liability kept 20.00 and credit 0.00 + courtesies.
    - Two defensible answers exist for both scored quantities.
  - Affected: `card.extended.yaml` A.overwrite and B.overwrite, which omit base s7.
  - Per-task: task 0 must show whether its world falls in the conflict zone; see `0.md`.
- **F2 — SOURCE-FACTOR RED (charter-global structure; bears on task 1).**
  - Symptom: D's `tenure_multiplier_tier` is labelled `effect: method`.
  - Root cause: its three tiers ("multiplied by long_tenure_multiplier", "multiplied by mid_tenure_multiplier", "used as it stands") put a different number (1.5, 1.25 or 1) into the same product `RND(P('small_dispute_auto_credit_threshold') * tenure_multiplier, 2)`. A multiplier is a rate, which is exactly the case the label test excludes from `method`.
  - Evidence: D.compute `tenure_multiplier: "K('long_tenure_multiplier') if … else (K('mid_tenure_multiplier') if … else 1)"` and `scaled_threshold: "RND(P('small_dispute_auto_credit_threshold') * tenure_multiplier, 2)"`.
  - Demonstrated consequence: the label is dishonest. With it corrected, D still has one honest method (near_ceiling_release), so the method floor is not breached. The mislabel itself is the listed defect.
  - Affected: D.factors[tenure_multiplier_tier].effect.
- Observations (not grounds for rework):
  - O1: `RND` is Python float `round`, while the rules say "half up". The two diverge only on exact half-cent values.
  - O2: docstrings say "then sees", and the credit tools name their object by the state "open dispute".
  - O3: base "must be blocked as compromised first" is a base cross-problem order.
  - O4: A declares an override of the merchant-contact sentence, which never governed unauthorized disputes.
  - O5: A's notice_start_date `method` label is borderline.
  - O6: block_relief direction.
  - O7: 50% fee return on an accepted unauthorized purchase.
  - O8: plan_uplift tiers are reachable only through downgrade.
  - O9: A records liability per dispute as min(sum of all the card's settled purchases, ceiling). With several purchases on one takeover card, each dispute would carry that whole figure, and B's `liability_open` would add them together.
  - O10: D's standing ladder has no stated outcome for a recovered security lock (restriction_reason suspected_account_takeover with an empty restriction_lifted_date). Compute then falls through to 0.00. It also has no stated outcome for "restricted now" while an older restriction_lifted_date is still on the record.
  - O11: A block_relief/`blocked_date` has no value for a card that is closed but was never blocked. Such a card can take an unauthorized dispute under base s2, but `DAYS(F('issued_date'), F('blocked_date'))` would have no date to use.

## closing_checklist

Written after both reveals (2026-09-24T23:44:10Z). **Closing is not reached**, because not every task passes all four relationships:
- task 0: SOURCE-POLICY RED (F1, charter-global, with no consequence on its world); the tree, factors and unique solution PASS
- task 1: SOURCE-FACTOR RED (F2); policy, tree and unique solution PASS

State of the Step 4 items as of this round, for the next round's reference:
- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits alongside them. This is round r1, so there are no older revisions. Both comparison sections are written; neither is a full PASS.
- Coverage and scopes: `charter_scope` shows task 0 = {card_ext_takeover_card_liability, card_ext_takeover_card_final_credit} and task 1 = {card_ext_single_use_incorrect_amount, card_ext_single_use_filing_credit}. The two are pairwise disjoint and together cover all four extended policies. The task tools are closed (two per task, no sharing), and the uuid8s are independent (see `action_binding_and_uuids`).
- Trees: each task has 1 prerequisite problem, 1 value_input edge and 1 owner=user write (the filing), with no cycle. The whole difficulty graph is the two disjoint edges B → A and D → C, which is acyclic.
- Factors: every factor of every computation bears weight on its world against an honest baseline, and each whole-baseline number differs from gold (50.00 / 377.00 / 92.75 / 25.00 against 12.00 / 410.89 / 49.25 / 47.75). The label defect F2 is open.
- Gates: I did not re-run the instantiation-stage gates. No artifact was changed in this round, and the gate snapshot supplied with the brief stands.

## revision_2

### charter_global_frozen (r2)

- Written 2026-09-24T23:48Z by the same independent auditor. This is before any round-2 task JSON was opened.
- Inputs:
  - `card.extended.yaml` sha256 `169beffcf9c594cdae58988af5c447bebe5ce4bbac51b213565f5528b4398076`. This changed from r1 `b2bbbfe1…c0d`, so every charter-global section is re-derived here.
  - `task_tools.py` sha256 `2bb93a2f…9da`, unchanged.
  - r2 views `0.view.json` `53ba191c…3bc` and `1.view.json` `021012c8…ba3`, re-hashed and identical to r1.
  - gate snapshot `snap/d2_r2.txt`: all seven gates OK, traceability deferred.
- Masked until the per-task r2 freezes: `tasks/0.json`, `tasks/1.json` (as edited by the reworker) and `worklog.md`.
- contamination_disclosure (r2): I read both r1 task JSONs in round 1, so I am not blind to their r1 GT values. The r2 charter-global section rests only on the charter, the tools and the blueprint.
- What changed: I diffed the r1 file (my own r1 read, which captured the full file) against the r2 file. There are exactly four hunks:
  1. A.overwrite gains a third entry. It supersedes base `card_disputes_unauthorized` s7 ("A dispute amount at or below small_dispute_auto_credit_threshold is credited in full …") with "The liability of a takeover card's purchase is recorded by this rule whatever the amount disputed, including an amount at or below small_dispute_auto_credit_threshold, which carries no liability-free small-dispute credit."
  2. A.rule gains that same sentence as its 3rd sentence.
  3. B.overwrite gains a third entry that supersedes s7 with "Such a dispute is settled by this final credit whatever the amount disputed, including an amount at or below small_dispute_auto_credit_threshold, which is not credited in full as a small dispute.", and B.rule gains that sentence as its 3rd sentence.
  4. D.factors[tenure_multiplier_tier]: `effect: method` becomes `effect: parameter`, and the ladder `method:` strings become `value: "K('long_tenure_multiplier')"`, `"K('mid_tenure_multiplier')"` and `"1"`.
- Nothing else moved: compute, compute_basis, params, prerequisite, cross_category and baselines are unchanged. The base section (lines 1–1085) still differs from `products/card.yaml` only by one trailing blank line.

### policy_conflict_scan (r2)

- Subjects, computes, target tools, owners and cross-category reads are unchanged from r1, and so is the conclusion: no two policies conflict on one object.
- Scopes: the r1 derivation of tree 0 = {B, A} and tree 1 = {D, C} still holds, since no scope sentence moved except A/B's new "whatever the amount" sentences. Those widen nothing across policies.
- The two new sentences make A and B apply to takeover disputes of any amount. They introduce no overlap with C or D, because the reasons (unauthorized against incorrect_amount) and the card forms stay disjoint.

### rule_compute_equivalence (r2)

- A's and B's new 3rd sentences are scope sentences. They state that the policy's own formula governs every amount and that s7's full credit does not apply. They name no quantity that compute lacks: compute already has no amount floor, and a scope sentence has no binding of its own. Nothing is promised that compute does not deliver.
- D's tenure ladder values `K('long_tenure_multiplier')`, `K('mid_tenure_multiplier')` and `1` are exactly the three branches of the unchanged `tenure_multiplier` binding and the three tiers of the unchanged rule sentence.
- Every other r1 equivalence conclusion re-verifies on unchanged text. O1 (Python `round` against "half up") stays open as an observation.

### action_binding_and_uuids (r2)

- The tool module is unchanged (same sha256), and no `target_tool` or `computes` moved. The r1 conclusion carries forward on the hash: each pair has exactly one owner, the four uuid8s are independent, and no tool judges a prerequisite. O2 is unchanged.

### prerequisite_graph (r2) and prerequisite_sentences (r2)

- Both `prerequisite` blocks are byte-identical to r1, and both policy_source sentences are still verbatim in their own rules. B's is now sentence 4 of its rule; D's is still sentence 2.
- The new A and B sentences carry no ordering connective and no cross-problem order. They ground no edge and state no undeclared dependency.
- The graph is still B → A and D → C, acyclic, with state form and value_input edges. O3 is unchanged.

### override_declarations (r2)

- A vs `card_disputes_unauthorized` s7: now **declared**, and the replacement is in A's rule verbatim.
  - Merged semantics for a takeover purchase at or below the threshold: liability is computed by A's formula, and there is no liability-free full credit. That is unique for the quantity A scores (customer_liability).
- B vs s7: now **declared**, and the replacement is in B's rule verbatim.
  - Merged semantics for an open unauthorized takeover-lock dispute at or below the threshold: settled by B's final credit, not credited in full. That is unique for credit_amount.
- Re-running the r1 F1 constructed situation (a 20.00 takeover purchase on Signature, Prime, lock on day 5, 12 notice days): A gives liability 20.00 and B gives credit 0.00 + courtesies. Base s7 is superseded by both declarations, so no second answer remains.
- Residual (observation O12): a takeover-card purchase at or below the threshold where the linked account has **no** recorded takeover lock.
  - A still records liability and supersedes s7. B does not apply.
  - The credit path is then base s8 ("Otherwise provisional credit …"), whose "Otherwise" now has no preceding s7 branch in A's scope. A's wording "carries no liability-free small-dispute credit" can be read either as "no small-dispute credit" or as "a small-dispute credit less liability".
  - No extended policy of this difficulty scores that credit, and neither task's world reaches it, so there is no demonstrable consequence on a scored quantity.
- All other r1 sentence-by-sentence conclusions re-verify on unchanged text. O4 is unchanged.

### factor_ladders (r2)

- D now has 6 factors: tenure_multiplier_tier, deposit_uplift_tier, plan_uplift_tier, standing_uplift_tier and merchant_ack_tier are `parameter` (5), and near_ceiling_release is `method` (1).
- Each label is honest: tenure's tiers now declare values (numbers substituted into one product), and near_ceiling_release changes the algorithm.
- The ladders, bindings, baselines and fall-throughs are unchanged.
- A, B and C are unchanged from r1: 3 parameter + 1 method, 3 parameter + 1 method, and 2 parameter + 2 method.
- The r1 multi-source and cross-difficulty table stands, with the D tenure row relabelled `parameter`. O5–O8, O10 and O11 are unchanged.

### findings (r2)

- **F1: closed.** Both A and B declare the base s7 override, each rule carries the replacement sentence verbatim, and the r1 demonstration no longer produces two answers for a scored quantity. Residual O12 is recorded as an observation.
- **F2: closed.** tenure_multiplier_tier is labelled `parameter` with value tiers, and D keeps one honest method (near_ceiling_release).
- **New charter-global defects: none found.**
- Observations: O1–O11 carried unchanged, and O12 added.

### closing_checklist (r2)

Written after both r2 reveals (2026-09-24T23:49:16Z). **Closing is reached: all four relationships PASS for both tasks.**
- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits alongside them.
  - The r1 text of all three files is preserved above each file's `## revision_2` heading.
  - Both r2 comparison sections carry PASS: task 0 PASS, task 1 PASS.
- Coverage and scopes: task 0 = {card_ext_takeover_card_liability, card_ext_takeover_card_final_credit} and task 1 = {card_ext_single_use_incorrect_amount, card_ext_single_use_filing_credit}. They are pairwise disjoint and cover all four extended policies.
  - Each tree's scope spans its root and its prerequisite.
  - The task tools are closed (two per task, none shared), and the four uuid8s are independent and frozen. `task_tools.py` is unchanged since r1.
- Trees: each task has 1 prerequisite problem, 1 value_input edge (meeting the max(n−1, 1) = 1 floor), 1 owner=user write, and no cycle. The difficulty graph {B → A, D → C} is acyclic, and no task references another's policies.
- Factors: every computation declares a self-sufficient baseline.
  - Factor counts are 4, 4, 4 and 6.
  - Parameter/method splits are 3/1, 3/1, 2/2 and 5/1.
  - Task 0 has multi-source factors (notice_start_date, liability_absorption, fee_return) and cross-difficulty factors (wallet: notice_start_date, deposit_relief, liability_absorption, lock_courtesy, tenure).
  - Task 1 has multi-source factors (authorized_reference, exchange_tolerance, merchant_credit) and cross-difficulty factors (wallet: tenure, deposit, plan, standing).
  - Every ladder has three tiers stated in its rule, with distinct outcomes.
  - Every factor bears weight against an honest baseline. The whole-baseline numbers differ from gold: 50.00 against 12.00, 377.00 against 410.89, 92.75 against 49.25, and 25.00 against 47.75.
- Gates on the final form: the coordinator ran them after the rework (`snap/d2_r2.txt`). EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 22/22, 1.json 24/24), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. check_traceability.py is deferred to step 3 by the coordinator.
- Open observations (not grounds for rework): O1–O12 and P1.
