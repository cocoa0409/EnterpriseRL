# Policy-task audit — patient_balance_and_coverage_resolution / charter-global

## charter_global_frozen

- Revision: r1 (first audit of this difficulty; no earlier revision exists under this directory).
- Freeze time: 2026-09-25T00:08:53Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (Claude), not the instantiating agent.
- Frozen inputs and their hashes (re-computed by the auditor and equal to the coordinator's brief):
  - `tasks/patient_balance_and_coverage_resolution/billing.extended.yaml` sha256 `232ba8856c83255fd13c5fe78cb9da9b75950c2bab4f55f97a231cf27c82a33a`
  - `tasks/patient_balance_and_coverage_resolution/task_tools.py` sha256 `2d96271957c7e53dcc6c3e47d9f1e7904a2f1fe5a61635bfde18bc32658794e9`
  - masked view `audits/_coordinator/views/policy_task/patient_balance_and_coverage_resolution/r1/0.view.json` sha256 `2adde76d…4010e1d`; `1.view.json` sha256 `eafc0690…4612e75` (only `frozen_time`, `user_scenario`, `initial_state`).
- Fields permitted: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml` (billing base; appointment, payplan, membership parameters for the cross-category reads), the extended charter, `task_tools.py`, the two masked views.
- Fields masked and not opened before the freeze: `tasks/*.json` (all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), `tasks/patient_balance_and_coverage_resolution/worklog.md`, the scenario-level `worklog.md`, every other `audits/` subdirectory, `audits/_coordinator/` apart from the two view files. No recursive search was run over `tasks/` or `audits/`.
- Entry conditions (Step 0): the brief supplies the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred until the KB is published), the masked views with hashes, and the charter hashes. Input complete. The deferred traceability gate is noted, not re-run.
- Base-copy check: `billing.extended.yaml` lines 4–1489 are byte-identical to `blueprint/products/billing.yaml` lines 4–1488 (the only diff is one trailing blank line before `extended_policies:`). The base copy is verbatim.

### policy_conflict_scan

Five extended policies, all with `base_policy_refs` inside the billing charter:

| id | trigger | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- | --- |
| billing_ext_card_on_file_charge | state_due | billing_payment_posted | charge_amount_usd | charge_card_on_file_381e2993 (agent) | [] |
| billing_ext_pre_placement_statement | state_due | billing_statement_issued | statement_amount_usd | issue_account_statement_de3ca581 (agent) | card_on_file_charge (value_input, gate `owed`, state form) |
| billing_ext_final_notice_paydown | on_request | billing_payment_posted | payment_amount_usd | pay_final_notice_balance_8381dcc2 (user) | pre_placement_statement (value_input, gate `statement_balance`, state form) |
| billing_ext_returned_payment_replacement | on_request | billing_payment_posted | replacement_amount_usd | pay_returned_payment_replacement_5bda38e8 (user) | [] |
| billing_ext_credit_refund | on_request | billing_refund_issued | refund_amount_usd | issue_credit_refund_942b7f9f (agent) | returned_payment_replacement (value_input, gate `net_credit`, state form) |

- Overlapping subject `billing_payment_posted` (three policies): the three differ in trigger, in account state (card-on-file charge: a tier whose `card_on_file_required` is true; paydown: status precollection, on the patient's request; replacement: a returned check/ACH payment, on the patient's request), in the posting target (largest deductible/coinsurance line of the most recent encounter; open charge with the earliest date of service; charge the most recently returned payment had paid) and in `payment_method` (card_on_file vs card vs card). No situation was found in which two of them govern the same payment with different amounts.
- Eligibility, time anchors and terminal states: every base eligibility of the cited base policies not hit by an `overwrite` is inherited (see override_declarations); the extended rules add no eligibility that contradicts an inherited one. Terminal states: the paydown returns the account to active and clears `final_notice_date` (consistent with base billing_collections_recall "Recall and return to active clear the placement and final-notice dates"); the other four leave the status untouched.
- Cross-category reads: every compute read of another category (appointment `variant_name`/`waiver_documentation_days`/`first_no_show_waived`/booked status; payplan status, `defaulted_date`, `installment_amount`, `remaining_balance`, released/missed/paid ledger rows and tier `reinstatement_*`; membership status, `variant_name`, `imaging_discount_pct`, `activated_date`, `billing_cycle`, `dues_amount_usd`, `current_period_start`; telehealth status/type) is declared in that policy's `cross_category`, and the replacement declares none and reads none.
- Scope of the M = 2 tasks (from the masked views only, before any reveal): task 0 (precollection HDHP account asking what to pay to stop collections) reaches billing_ext_final_notice_paydown ← billing_ext_pre_placement_statement ← billing_ext_card_on_file_charge; task 1 (PPO account asking for a duplicate-payment refund) reaches billing_ext_credit_refund ← billing_ext_returned_payment_replacement. The two trees are disjoint and together cover all five extended policies (to be compared with `charter_scope` after the reveal).
- Claim note: the blueprint claim of this difficulty lists `[billing_coverage_updated, billing_adjustment_posted, billing_payment_posted, billing_refund_issued, billing_hold_placed, billing_hold_released, billing_charge_posted]`; `billing_statement_issued`, the subject of billing_ext_pre_placement_statement, is not in it (observation O-5).

### rule_compute_equivalence

A mechanical sweep (auditor's temporary script, since removed) confirmed for every policy: every compute binding has a `compute_basis` entry and vice versa; every `compute_basis` sentence is a verbatim sentence of the policy's `rule`; every `overwrite.replaced_by` is verbatim in the `rule`; every `baseline.rule` sentence is verbatim in the `rule`; every factor binding is a compute binding. The rule sentences not quoted by any basis are the scope sentence ("This policy settles…"), the posting-target sentence, the prerequisite sentence and, for the paydown, "Under the standard method no part of a released plan balance is left out of the paydown base" (its content is the `reinstatable_plan_release` baseline `plan_left_out: '0'`) — none of them names a quantity the compute omits.

Manual sentence-by-sentence sweep of each ladder, window and filter:

- card_on_file_charge: most-recent-encounter selector (`enc` = encounter of the last-posted deductible/coinsurance line) = rule; notice rule (`DAYS(date, NOW) >= notice`), mail rule (`>= 2*notice`), precollection rule (all lines) = rule; deductible ceiling three tiers = rule; cap three tiers = rule; share three tiers with six-month windows (`within_months=6`, `MONTHS(default, NOW) < 6`) = rule; hold three tiers = rule; order "chargeable → cap → share → hold, floor 0, round once" = `result`. Equivalent.
- pre_placement_statement: owed = charges + reversed + refunds − payments − collections − adjustments = rule; plan balance of active or delinquent plan = rule; lead-time ladder = rule; deductible ladder applied only when the deductible line is not in lead (`ded_left_off: 0 if ded_in_lead`) = rule ("that is not inside the statement lead time"); no-show and late-fee ladders = rule. One wording gap without consequence on either world: the rule defines "a line's open part is its amount less the payments posted against that line" for the encounter's lines, and `fee_open` additionally subtracts adjustments (observation O-9).
- final_notice_paydown: statement balance, plan left-out ladder, method ladder, tenure / card-on-file / membership / late-fee ladders and the combination "tenure − card-on-file − membership + late-fee" = rule.
- returned_payment_replacement, credit_refund: ladders = rule, **except the returned-payment filter (finding F-1).**

**F-1 (SOURCE-POLICY RED, charter-global, check 2 and check 6).** The rules restrict the returned payments they count to check or ACH payments; the compute counts every `billing_payment_reversed` row, and the charter's own event makes card chargebacks `billing_payment_reversed` rows too.

- Evidence, rule side: paydown "an account with a check or ACH payment returned in the 12 calendar months before the handling date pays the whole paydown base"; replacement "when the account has at least the tier's returned_payments_before_restriction returned check or ACH payments in the 12 calendar months…"; refund "for an account with at least the tier's returned_payments_before_restriction returned check or ACH payments in the 12 calendar months before the handling date, the tier's returned_payment_fee_usd times that number of returns is kept"; refund prerequisite sentence "the charge whose check or ACH payment was most recently returned".
- Evidence, compute side: paydown `returned_12m: COUNT('billing_transactions', within_months=12, …, event_type='billing_payment_reversed')`; replacement `returns_12m`, `returns_24m`, `returned_12m`, `returned_24m`, `returned_last`, `returned_payment_id` all filter only `event_type='billing_payment_reversed'`; refund `returns_12m` likewise; refund prerequisite `condition` "The billing charge referenced by the payment of the latest billing_payment_reversed entry…".
- Evidence that chargebacks are such rows: base event `billing_payment_reversed` "A posted payment is reversed because the check or ACH debit was returned unpaid or the card payment was charged back."; base billing_returned_payment "or a card payment is charged back, the payment row is reversed in full". The base measure `billing_msr_returned_payments` filters "whose payment_method is check or ach", so the charter itself distinguishes the two.
- Demonstrated consequence (same situation, two conclusions): on a world with one ACH return and one card chargeback in the last 12 months, the paydown rule gives the whole-base tier only through the ACH return in both readings, but the replacement rule reads one check/ACH return (tier 2 or 3: only the most recent return covered, one fee) while the compute reads `returns_12m = 2` (tier 1: every reversal of 12 months covered, and every late fee included); the refund rule keeps one `returned_payment_fee_usd` while the compute keeps two; and where the chargeback is the latest reversal, the refund prerequisite sentence points at the charge of the ACH return while the `condition` points at the charge of the chargeback.
- Affected: billing_ext_final_notice_paydown (`returned_12m`), billing_ext_returned_payment_replacement (six bindings), billing_ext_credit_refund (`returns_12m`, prerequisite `condition`). Bears on task 0 (paydown) and task 1 (replacement, refund); each task file states whether its world carries a chargeback.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct: (charge_card_on_file_381e2993, charge_amount_usd), (issue_account_statement_de3ca581, statement_amount_usd), (pay_final_notice_balance_8381dcc2, payment_amount_usd), (pay_returned_payment_replacement_5bda38e8, replacement_amount_usd), (issue_credit_refund_942b7f9f, refund_amount_usd). Each tool is the target of exactly one policy.
- Function bodies (task_tools.py): each tool looks up the account and (where named) the ledger row, creates exactly one `billing_transactions` row and updates `patient_balance` (statement: `last_statement_date`; paydown: also `status="active"`, `final_notice_date=""`). No tool checks eligibility, status, amount, prerequisite or ownership, returns an error or gives a hint.
- Docstrings: no docstring names another tool, states a position in a sequence, or uses before/after/first/then/until as an ordering between actions (the hits are "once the charge is posted" for the call's own effect and "1 for the first statement of a series"). No confirmation, review or wait is added.
- uuid8s: 381e2993, de3ca581, 8381dcc2, 942b7f9f, 5bda38e8 — five distinct values with no common prefix, no sequence and no copy-with-changed-tail; none appears in `blueprint/`. (381e2993 and 8381dcc2 share the trigram "381" at different offsets, which is within chance for five random 8-hex strings; observation only, no evidence of derivation.)
- Tool/charter mismatch (observation O-4): `issue_credit_refund_942b7f9f` refunds a cash payment by check (docstring "a cash payment is refunded by check"; body `method = "check" if method == "cash"`), while billing_ext_credit_refund declares the base sentence carrying that exception superseded and says only "it goes to that payment's own method". The refund method is set by the tool and is not a scored argument; neither task refunds a cash payment.

### prerequisite_graph

- `prerequisite` is filled on every policy (`[]` on card_on_file_charge and returned_payment_replacement).
- Edges: pre_placement_statement → card_on_file_charge; final_notice_paydown → pre_placement_statement; credit_refund → returned_payment_replacement. Every `problem` is another extended policy id of this file; none points at a base policy or at itself. The graph is acyclic (two chains, depth 2 and 1).
- `policy_source` verbatim in the blocked policy's own `rule`: all three (mechanical check True).
- `form: state` on all three; no `fallback_reason` present, none required.
- `resolved_by` equals the depended-on policy's `target_tool` on all three.
- `kind: value_input` and `gate` names a real binding of the blocked policy's compute: `owed` (statement), `statement_balance` (paydown), `net_credit` (refund). Each resolving write changes that binding: a card-on-file payment raises `paid` and so lowers `owed`; a new statement becomes `LATEST(... billing_statement_issued)`; a replacement card payment raises `paid` and so `net_credit`.
- `condition` vs sentence: statement and paydown match in strength and scope. The refund `condition` ("the latest billing_payment_reversed entry") is broader than its sentence ("the charge whose check or ACH payment was most recently returned") — recorded under F-1.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge:

1. pre_placement_statement ← card_on_file_charge: "On an account whose tier requires a card on file, the pre-placement statement balance is fixed only after the most recent encounter carries a card-on-file payment." Connective "only after"; waited-on thing is a record-visible state (a payment row of method card_on_file carrying the encounter number of the most recent encounter), no action, performer or tool; no tool name, policy id, snake_case token or row id; scope "an account whose tier requires a card on file" = `condition` "card_on_file_required true". The only write of this difficulty that posts `payment_method="card_on_file"` is `charge_card_on_file_381e2993` (the other two payment tools post `card`), so exactly one write brings the state about. Derivation: sentence → the reader looks for the policy whose write leaves a card-on-file payment on the most recent encounter → billing_ext_card_on_file_charge, whose rule posts "one entry against the largest deductible or coinsurance line of the most recent encounter", with the same definition of "most recent encounter". One reading.
2. final_notice_paydown ← pre_placement_statement: "The final-notice paydown is not fixed until the account's most recent statement is dated no earlier than its most recent charge posting." Connective "not … until"; state (statement date vs charge posting date); clean wording; scope = `condition`. The only statement-issuing write is `issue_account_statement_de3ca581`; no write of this difficulty posts a charge. Derivation: the reader looks for the rule that issues a statement to a precollection account whose most recent charge post-dates its last statement → billing_ext_pre_placement_statement's first sentence names exactly that situation. One reading.
3. credit_refund ← returned_payment_replacement: "A credit is refunded only after the charge whose check or ACH payment was most recently returned carries a card, HSA/FSA card or cash payment posted after that return." Connective "only after"; state; clean wording. Writes posting a card payment: `pay_returned_payment_replacement_5bda38e8` (against "the charge the most recently returned payment had paid" — exactly the waited-on charge) and `pay_final_notice_balance_8381dcc2` (against "the open charge with the earliest date of service", and only during the final-notice period). The second brings the state about only where the account is in precollection and its earliest open charge is the returned charge; not reachable on either task's world (observation O-3). Derivation: sentence → the reader looks for a rule that posts a card payment against the charge whose check/ACH payment was returned → billing_ext_returned_payment_replacement. Scope mismatch with `condition`: F-1.

Other checks: no rule of the charter carries a second wording of any of the three dependencies, a tool name or another policy id; no depended-on rule restates the sentence; no base rule sentence grounds any of the three trees. One cross-problem coupling not declared as an edge: the paydown's card-on-file reduction ("lowered by card_on_file_paid_reduction_pct points when a card-on-file payment was posted to the account within the one calendar month before the handling date") is moved by the card-on-file charge. It states no order, and the order card → statement → paydown is already pinned by the two declared edges, so no second terminal state follows (observation O-8).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- billing_payment_application (cited by card_on_file_charge, final_notice_paydown, returned_payment_replacement, credit_refund): "applied to open charges in the tier's payment_allocation_order … never exceeding that charge's remaining balance" — superseded by each of the three payment policies (declared); "applied to a specific encounter only when the patient names that encounter's encounter number" — superseded by each (declared); "Any part of a payment exceeding everything owed stays on the account as a credit…" — followed; accepted methods and the check/ACH refusal under the restriction — followed; HDHP card-on-file sentence (cap, notice, excess statemented) — superseded by card_on_file_charge (declared; covers the precollection tier ignoring notice, the deductible ceiling, the visit-type cap, the share and the hold); installment sentence — not touched.
- billing_coverage_verification (cited by card_on_file_charge, pre_placement_statement, credit_refund): tier, activation, coverage-update and re-verification sentences — followed (the re-verification duty is tied to "a new charge is about to be billed to the payer", which none of the five writes does).
- billing_statement_escalation (pre_placement_statement, final_notice_paydown): cycle/numbering sentence — superseded (declared; the numbering is restated in the rule); pending-claim and plan-enrolled sentence — superseded (declared; the rule keeps the active/delinquent plan balance off); "Statements are issued only while the account status is active or precollection" — followed; final-notice and placement sentences — not touched; "An account on billing hold is never statemented" — followed; "Enrolling … or paying it below collections_min_balance_usd … returns the account to active" — superseded by the paydown (declared).
- billing_itemized_statement (pre_placement_statement): informational statement sentences — not touched; "Statements go by the account's statement_delivery channel; a patient whose portal is not active receives mail regardless of the recorded preference" — followed for delivery, but the statement and card-on-file mail tiers key on the recorded `statement_delivery` only (observation O-6; both task worlds have `portal_status: active`).
- billing_collections_recall (final_notice_paydown): the precollection-return sentence — superseded (declared); "Recall and return to active clear the placement and final-notice dates, and the statement series restarts at 1" — followed (the paydown clears `final_notice_date`).
- billing_returned_payment (returned_payment_replacement, credit_refund): every sentence followed; `overwrite` lists none for it and none is needed.
- billing_credit_balance_refund (credit_refund): "Before any refund the credit is applied to any other open charge…" — superseded (declared); credit-hold sentence ("held for at least the tier's credit hold period counted from the posting date of the payment that created the credit") — inherited, not restated; threshold/method sentence — superseded (declared); "refunded at most once", refundable status (active, billing_hold, closed) and collections sentence — inherited.

Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch was found outside a declared `overwrite`. The card-on-file "deductible lines count as 0.00" tier and the refund holds sit inside quantities whose base sentences are declared superseded. No undeclared override.

### factor_ladders

| policy | factor | label | tiers | multi-source (every non-fall-through tier a conjunction over distinct records) | cross_difficulty | label honest |
| --- | --- | --- | --- | --- | --- | --- |
| card_on_file_charge | covered_lines | method | 3 | no (account status / account field) | – | **no (F-2)** |
| | deductible_ceiling | parameter | 3 | no (two fields of the account row) | – | yes |
| | visit_type_cap | parameter | 3 | no (one appointment field) | appointment | yes |
| | plan_history_share | parameter | 3 | yes (plan row + plan ledger rows) | payplan | yes |
| | membership_hold | parameter | 3 | yes (membership row + appointment row) | membership | yes |
| pre_placement_statement | statement_lead_time | method | 3 | no (tier param + account field; account field) | – | yes, narrowly (O-7) |
| | deductible_above_remaining | parameter | 3 | no | – | yes |
| | no_show_documentation_window | parameter | 3 | yes (fee ledger row + appointment tier) | appointment | yes |
| | post_notice_late_fee | parameter | 3 | yes (late-fee ledger rows + account `opened_date`) | – | yes |
| final_notice_paydown | paydown_method | method | 3 | no (tier 1 is the single condition "a check or ACH payment returned") | – | yes |
| | tenure_percentage | parameter | 3 | no | – | yes |
| | card_on_file_reduction | parameter | 3 | no (tier 1 single condition) | – | yes |
| | membership_reduction | parameter | 3 | no (one membership row) | membership | yes |
| | late_fee_addition | parameter | 3 | no | – | yes |
| | reinstatable_plan_release | method | 3 | yes (plan row + plan tier + ledger) | payplan | yes |
| returned_payment_replacement | returned_scope | method | 3 | no (tier 1 single condition) | – | yes (tier 3 changes the aggregate) |
| | charge_reduction | parameter | 3 | no (tier 1 single) | – | yes |
| | returned_fee_inclusion | parameter | 3 | no (tier 1 single) | – | yes |
| | late_fee_inclusion | parameter | 3 | yes (reversal rows + late-fee rows) | – | yes |
| credit_refund | plan_offset | method | 3 | yes (plan row + plan ledger) | payplan | yes |
| | booked_visit_hold | parameter | 3 | no | appointment | yes |
| | returned_payment_reserve | parameter | 3 | no | – | yes |
| | membership_dues_hold | parameter | 3 | no (tier 2: one membership row) | membership | yes |
| | deductible_reserve | parameter | 3 | no | – | yes |
| | virtual_visit_hold | parameter | 3 | no | telehealth | yes |

Structural checks passed on every policy: four to six factors; `decides` is a binding of its own factor and never `result`; binding sets pairwise disjoint (mechanical check); each ladder has three tiers, pairwise disjoint as stated; every tier's condition and value/method is a sentence of the `rule` and a branch of its `decides` binding (no tier lives only in `compute`); every factor's fall-through equals its declared `baseline`; every `baseline.rule` sentence is in the `rule`.

Counts per policy (before label tests): card_on_file 1 method / 4 parameter; statement 1 / 3; paydown 2 / 4; replacement 1 / 3; refund 1 / 5. Categories read by cross-difficulty factors: appointment, payplan, membership, telehealth.

**F-2 (SOURCE-FACTOR RED, charter-global structure; bears on task 0).** `covered_lines`, the only `method` factor of billing_ext_card_on_file_charge, only substitutes a threshold into one formula. Its three tiers are "every deductible and coinsurance line of the encounter is covered whether or not its notice has run" / "only lines posted at least twice the tier's card_on_file_notice_days calendar days before the handling date are covered" / "lines posted at least the tier's card_on_file_notice_days calendar days before the handling date are covered". The compute is the same selector with a different age threshold: `ded_ready`/`coi_ready` (`DAYS(date, NOW) >= notice`), `ded_mail`/`coi_mail` (`>= 2 * notice`), and the precollection branch taking every line (threshold 0). The factor is a `parameter` under the charter's own test ("a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)"). Without it, the card-on-file computation has 0 `method` factors against a floor of 1.

Charter-global observations on the ladders (no demonstrated consequence on either world; the task files say where one bears):

- O-1 `membership_hold` realism: the rule holds back "the membership tier's imaging_discount_pct" of an insured patient's card-on-file charge "for the membership desk". The membership charter says members receive imaging_discount_pct "only on self-paid in-house services" and that "a membership never waives an insurer's cost share". A hold-back is not a discount, so no contradiction can be demonstrated, but the tier's outcome has no counterpart in the membership rules. Tier 1 also gives 0 for a Linden Connect Virtual Membership (imaging_discount_pct 0), the same value as the fall-through.
- O-2 `plan_history_share` tier 1: "a payment plan … defaulted less than six calendar months before the handling date and a plan balance was released within the six calendar months" — payplan_release_and_reinstatement releases the balance on default, so the second conjunct holds whenever the first does (except for a zero balance). The conjunction is close to one condition; `membership_hold` still gives the policy a genuine multi-source factor.
- O-7 `statement_lead_time` label: tiers 1 and 2 are both "leave off lines younger than T" (T = card_on_file_notice_days vs mail_lead_days). Only the card-on-file exemption in tier 1 ("that carries no card-on-file payment") makes the selection rule differ, so the `method` label holds narrowly.
- O-10 paydown nested factors: `tenure_percentage`, `card_on_file_reduction`, `membership_reduction` and `late_fee_addition` feed only the good-faith tier of `paydown_method`. `baseline.rule` (the standard below-minimum paydown) never uses a good-faith percentage, so "what the baseline states for that input" is empty. Their declared baselines are their fall-through tiers, and they can bear weight only on a world where `paydown_method` takes its good-faith tier.
- O-11 `no_show_documentation_window` condition "that visit type waives a first no-show (first_no_show_waived)": a fee that was charged was, by appointment_no_show_fee, not a waived first offense. The visit type's first-offense policy is therefore a property of the visit type, not of this missed visit. It divides customers, but its weight for "how much of a fee awaiting documentation to leave off" is weak.
- O-12 `membership_dues_hold` tier 2 keeps one twelfth of an annual member's dues when the renewal (a full annual bill) is under a month away, which does not match the next dues bill.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | rule counts returned check/ACH payments; compute and refund `condition` count every `billing_payment_reversed` row incl. card chargebacks | task 0 (paydown), task 1 (replacement, refund) |
| F-2 | SOURCE-FACTOR RED | card_on_file_charge's only `method` factor is a threshold substitution → 0 honest method factors | task 0 |
| F-3 | charter wording, demonstrated per task | credit_refund target "the payment that created the credit, which is the later of the payments posted to a charge whose payments exceed its amount" has no unique referent once more than one charge is overpaid, and the inherited credit-hold anchor ("the posting date of the payment that created the credit") hangs on the same referent | task 1 (see 1.md) |
| O-1, O-2, O-7, O-10, O-11, O-12 | observation | ladder realism / labels / nested baselines (above) | as stated |
| O-3 | observation | second card-payment write (paydown) can satisfy the refund prerequisite state on a precollection account | none on these worlds |
| O-4 | observation | refund tool keeps base cash→check exception superseded in the charter | none (no cash payment refunded) |
| O-5 | observation | `billing_statement_issued` outside the blueprint claim of this difficulty | task 0 |
| O-6 | observation | mail tiers key on recorded `statement_delivery`, not on base "portal not active receives mail" | none (both portals active) |
| O-8 | observation | card-on-file charge also moves paydown's card-on-file reduction tier; order pinned by declared edges | task 0 |
| O-9 | observation | `fee_open` subtracts adjustments; rule's "open part" definition names payments only | none (no adjustment on the fee) |

## closing_checklist

Written after both reveals (2026-09-25T00:13:29Z onward). It sits below the pre-reveal charter-global section, which was not edited after the reveal (hash at reveal `88b5e175c493670cb78002bdf7928f414f77fbe34185ce4c2dc2bcf76b7a5a30`).

**The difficulty does not close: not every relationship passes.**

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-1, no consequence on its world) | PASS | SOURCE-FACTOR RED (F-2) | PASS |
| 1 | SOURCE-POLICY RED (F-1, no consequence on its world) | PASS | SOURCE-FACTOR RED (no near-miss in the replacement computation) | SOURCE-TASK RED (F-3: refund object / credit-hold anchor) |

Checklist status:

- Per-task files correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` sits alongside. First revision, so no older revisions exist. Comparison sections are present, and both carry RED verdicts.
- Coverage and scope: the revealed `charter_scope` of task 0 is {card_on_file_charge, pre_placement_statement, final_notice_paydown}, and of task 1 {returned_payment_replacement, credit_refund}. They are pairwise disjoint and jointly cover all five extended policies, matching the pre-reveal scan. Task tools are closed (each task's `charter_scope.task_tools` equals its targets). uuid8s are distinct and independent (action_binding_and_uuids).
- Trees: task 0 has two prerequisite problems and two value_input edges; task 1 has one and one. Each has an owner=user write (paydown; replacement). No cycle, and the difficulty-wide graph is acyclic.
- Factors: every computation declares a self-sufficient baseline, 4–6 factors and three-tier ladders stated in the rule. Every factor bears weight on its task's world, and every whole-baseline number differs from gold. The difficulty still fails on F-2 (card-on-file computation has no honest method factor) and on the replacement computation's missing near-miss.
- Gates: not re-run. The difficulty does not close, and the charter, tool and task hashes equal those of the coordinator's snapshot (`billing.extended.yaml` 232ba885…, `task_tools.py` 2d962719…; task files hashed at reveal as recorded in each task file). The gate snapshot in the brief stands as the latest run on this form.

## revision_2

### charter_global_frozen (r2)

- Re-audit round 2, frozen 2026-09-25T04:05:55Z, before either revised task JSON was opened. Auditor: the same independent erl-task-policy-audit agent. Revision 1 above is left untouched.
- Hashes re-computed by the auditor: `billing.extended.yaml` sha256 `6f17b379f1631000794bf19033a3178cf3901faf752612393e2f78490e12c3fa` (**changed** from r1 `232ba885…`); `task_tools.py` `2d96271957c7e53dcc6c3e47d9f1e7904a2f1fe5a61635bfde18bc32658794e9` (unchanged); views r2/0 `2adde76d…` (unchanged), r2/1 `3d145bbf…` (changed).
- Re-audit rule: the charter changed, so every charter-global section is re-derived in full below from the r2 charter, the unchanged tool module and the blueprint. Nothing in this section rests on the revised task JSONs.
- Entry conditions: the brief supplies the r2 gate snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, SCOPE OK; traceability deferred), the masked r2 views with hashes, and the charter hashes. Input complete.
- Base copy: lines 4–1489 are still byte-identical to `blueprint/products/billing.yaml` 4–1488 (one trailing blank line of difference).
- Masked and unread at freeze: revised `tasks/0.json`, `tasks/1.json`, both worklogs, other audit directories.

### policy_conflict_scan (r2)

Same five policies, triggers, subjects, `computes`, target tools, owners and prerequisite edges as r1. The changes are confined to rule/compute text:

- card_on_file_charge: the old `covered_lines` ladder is replaced by `notice_anchor`, which sets the day each line's notice is counted from.
- final_notice_paydown, returned_payment_replacement, credit_refund: returned-payment counts are now filtered to check/ACH.
- credit_refund: gains a definition of "the payment that created the credit" and the cash→check clause.
- pre_placement_statement: the no-show fee's open part is now defined.

The overlap analysis on `billing_payment_posted` is unchanged: no situation gives two policies the same payment. Scope from the masked views: task 0 still reaches {card_on_file_charge, pre_placement_statement, final_notice_paydown} and task 1 {returned_payment_replacement, credit_refund}. The two trees are disjoint and jointly complete. Cross-category reads are all declared (replacement reads none).

### rule_compute_equivalence (r2)

Mechanical sweep repeated on the r2 charter (auditor's temporary script, since removed). It found every binding with a basis and every basis with a binding; every basis sentence, `replaced_by` and `baseline.rule` sentence verbatim in its rule; and every factor binding present. Unquoted rule sentences are only the scope, posting-target and prerequisite sentences, the paydown's "no part of a released plan balance" baseline sentence, and the refund's new posting-object definition, which is a target sentence and not a quantity.

- **F-1 re-check — closed.** The check/ACH filter now sits in every place where it matters:
  - paydown `returned_12m` = COUNT(check) + COUNT(ach);
  - replacement `returns_12m`, `returns_24m`, `returned_12m`, `returned_24m` are check+ach sums or counts, and `returned_last` / `returned_payment_id` take the later of the latest check and the latest ACH reversal;
  - refund `returns_12m` = check+ach;
  - refund prerequisite `condition` now reads "the latest billing_payment_reversed entry whose payment_method is check or ach".
  - The rule texts say "check or ACH" at each of those places. The `billing_payment_reversed` sums inside balance figures (`owed`, `net_credit`) rightly stay unfiltered: a chargeback moves the balance too.
  - Residual wording (observation O-13): the factor-ladder `when`/`method` strings of `returned_scope`, `late_fee_inclusion` and `returned_payment_reserve` still say "returns" / "every payment returned" without the qualifier. The rule sentences, which are what the KB renders and what compute_basis quotes, carry it. No consequence.
  - Same-day tie (observation O-14): `returned_last` prefers the check reversal when a check and an ACH reversal share the latest date. The rule's "most recently returned check or ACH payment" does not break that tie. No such tie exists on either world.
- card_on_file_charge `notice_anchor`: rule "while the account is in precollection …, the notice of every line of the encounter is counted from the encounter's date of service; for an account not in precollection whose statement_delivery is paperless, … from the posting date of the encounter's first-posted deductible or coinsurance line; for any other account each line's notice is counted from that line's own posting date". Compute: `enc_dos`, `enc_first_post = MN(ded_date, coi_date)`, `ded_anchor` / `coi_anchor` by the same branches, and `*_covered` if `DAYS(anchor, NOW) >= notice`. Equivalent.
- pre_placement_statement: the no-show open part is now defined in the rule ("whose open part is its amount less the payments and adjustments posted against it"), which matches `fee_open`. **O-9 closed.**
- credit_refund posting sentence: "The payment that created the credit is the most recently posted payment that brought the unreversed payments applied to a charge above that charge's amount, counting only charges to which no returned check or ACH payment was ever applied; the credit refund is issued as one refund entry against that payment and goes to that payment's own method, a cash payment being refunded by check." This is not a compute binding (it is the `applies_to_txn_id` and method), so it has no compute face.

### action_binding_and_uuids (r2)

`task_tools.py` is unchanged (same hash), so the r1 function-body and docstring conclusions carry forward on that hash. The `(target_tool, computes)` pairs re-read from the r2 charter are the same five distinct pairs, and the uuid8s are the same five independent values. **O-4 closed:** the charter now says "goes to that payment's own method, a cash payment being refunded by check", which agrees with `issue_credit_refund_942b7f9f`'s body and docstring. The overwrite still lists the base sentence as superseded, and the extended sentence restates the exception explicitly, so the merged reading is unique.

### prerequisite_graph (r2)

Unchanged topology: statement → card_on_file_charge, paydown → statement, refund → replacement. All edges are `value_input`, state form, with no fallback. Each `policy_source` is verbatim in its blocked rule (mechanical True), `resolved_by` equals the depended-on target tool, and each gate is a real binding (`owed`, `statement_balance`, `net_credit`). The refund `condition` now matches its sentence's scope ("check or ach"), which closes F-1's prerequisite half. There is no authoring-viewpoint phrasing.

### prerequisite_sentences (r2)

The three sentences are textually unchanged and pass the four-point test as in r1. Exactly one write produces each state:
- card_on_file payment → `charge_card_on_file_381e2993`;
- statement → `issue_account_statement_de3ca581`;
- card payment on the latest check/ACH-returned charge → `pay_returned_payment_replacement_5bda38e8`.

O-3 is unchanged: `pay_final_notice_balance_8381dcc2` could post a card payment on that charge only on a precollection account, which neither world is. The paydown's card-on-file reduction coupling is also unchanged (O-8). No new cross-problem order was found in the r2 rule texts. The new refund posting sentence refers to "returned check or ACH payment" only as a filter on charges, not as an ordering.

### override_declarations (r2)

The `overwrite` lists are textually the same as r1, and every `replaced_by` is verbatim in its rule. The sentence-by-sentence conclusions of r1 hold for the r2 texts:
- The card-on-file notice-anchor ladder sits inside the declared supersession of base's HDHP sentence ("only once card_on_file_notice_days have passed since the charge was posted").
- The refund's new object definition sits inside the declared supersession of base's "refunded … to the method of that payment" sentence.
- The inherited credit-hold eligibility now has a defined anchor: "the payment that created the credit" is defined by the new sentence.

No undeclared override.

### factor_ladders (r2)

| policy | factor | label | honest? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| card_on_file_charge | notice_anchor | method | **yes (narrowly)** — see F-2 re-check | no | – |
| | deductible_ceiling | parameter | yes | no | – |
| | visit_type_cap | parameter | yes | no | appointment |
| | plan_history_share | parameter | yes | yes | payplan |
| | membership_hold | parameter | yes | yes | membership |
| pre_placement_statement | (unchanged four) | 1 method / 3 parameter | as r1 | no_show, post_notice_late_fee | appointment |
| final_notice_paydown | (unchanged six) | 2 / 4 | as r1 | reinstatable_plan_release | membership, payplan |
| returned_payment_replacement | (unchanged four, check/ACH filtered) | 1 / 3 | as r1 | late_fee_inclusion | – |
| credit_refund | (unchanged six) | 1 / 5 | as r1 | plan_offset | payplan, appointment, membership, telehealth |

Structural checks re-run: 4–6 factors per policy; `decides` inside its own bindings and never `result`; binding sets disjoint; three tiers each, stated in the rule and implemented in compute; each fall-through equals its declared baseline (`notice_anchor` baseline `ded_anchor: ded_date`, `coi_anchor: coi_date` equals tier 3, "each line's own posting date", which is the standard method's "lines posted at least … card_on_file_notice_days … before the handling date").

**F-2 re-check — closed, narrowly.** The r1 defect was a pure constant-threshold swap (all lines / ≥ 2×notice / ≥ notice). `notice_anchor` keeps the threshold fixed and changes the reference event whose age is measured, and with it the unit of judgement:
- tier 1 measures from the encounter's date of service, one anchor shared by all lines;
- tier 2 measures from the encounter's first posting (an aggregate `MN` over the encounter's lines), all lines judged together;
- tier 3 measures each line from its own posting.

Tiers 1–2 judge the encounter as a unit and tier 3 judges line by line, so the selection rule differs, not only a constant. Physician-group billing does vary on whether a patient notice runs from the visit, the first statement of the encounter, or each posting. The label passes. It is narrower than the paydown's or the refund's method factors (the formula shape `DAYS(anchor, NOW) >= notice` is shared), and that is recorded here so a later round can weigh it again. The card-on-file computation now has 1 method and 4 parameter factors.

Carried-forward observations, re-checked against the r2 text and unchanged in substance: O-1 (membership hold realism; Connect tier 0 equals fall-through), O-2 (default ⇒ release conjuncts), O-7 (statement_lead_time narrow method), O-10 (paydown nested sub-factor baselines not stated by baseline.rule), O-11 (visit-type first-no-show condition), O-12 (annual dues one-twelfth).

**O-6 re-check — not closed (observation stands).** The card-on-file tier 2 now keys on "statement_delivery is paperless" (it keyed on mail in r1), and the statement's lead-time tier 2 still keys on "statement_delivery is mail". Neither rule mentions base billing_itemized_statement's "a patient whose portal is not active receives mail regardless of the recorded preference". A recorded-paperless patient with an inactive portal therefore still has two readings in both policies. Both task worlds have `portal_status: active`, so there is no consequence.

O-5 (the `billing_statement_issued` claim) is unchanged: the blueprint was not edited.

### findings (r2)

| id | r1 verdict | r2 status | evidence |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | **closed** | check+ach filters in paydown, replacement (six bindings) and refund `returns_12m`; refund `condition` scoped to check/ACH |
| F-2 | SOURCE-FACTOR RED | **closed (narrowly)** | `notice_anchor` changes the reference event and per-line vs per-encounter judgement |
| F-3 | charter wording (SOURCE-TASK in task 1) | **closed at the charter level** | new definition of "the payment that created the credit" excludes charges that ever carried a returned check/ACH payment and anchors the credit hold; per-task confirmation in 1.md revision_2 |
| O-4 | observation | closed | cash→check restated in the rule, matching the tool |
| O-9 | observation | closed | no-show open part defined with adjustments |
| O-6 | observation | still open (moved from mail to paperless tier wording, portal clause still absent) | see above |
| O-1, O-2, O-3, O-5, O-7, O-8, O-10, O-11, O-12 | observation | unchanged, re-checked | as r1 |
| O-13 (new) | observation | factor-ladder strings omit the check/ACH qualifier the rules carry | returned_scope, late_fee_inclusion, returned_payment_reserve |
| O-14 (new) | observation | same-day check/ACH tie in `returned_last` / `returned_payment_id` resolved to check with no rule text | replacement compute |

No new charter-global RED.

### closing_checklist (r2)

Written after the r2 reveals (2026-09-25T04:06Z). The r2 charter-global section above was frozen before them.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Files: `_difficulty.md`, `0.md`, `1.md`, each with revision 1 untouched and `## revision_2` appended. Both comparison sections carry PASS.
- Coverage and scope: `charter_scope` is {card_on_file_charge, pre_placement_statement, final_notice_paydown} for task 0 and {returned_payment_replacement, credit_refund} for task 1. They are disjoint and jointly complete over the five extended policies. Task tools are closed, and the uuid8s are independent and unchanged.
- Trees: task 0 has 2 prerequisite problems, 2 value_input edges and customer write = paydown. Task 1 has 1 prerequisite problem, 1 value_input edge and customer write = replacement. The difficulty graph is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors (at least 2 parameter and at least 1 honest method each; `notice_anchor` passes narrowly). Each task has at least 1 multi-source factor (task 0: plan_history_share, membership_hold, …; task 1: plan_offset, late_fee_inclusion) and at least 1 cross-difficulty factor with seeded rows. Every ladder has three tiers stated in the rule. Every factor bears weight on its world, and every whole baseline (412.75 / 2095.58 / 1567.74 / 242.40 / 355.67) is definite and differs from gold. Each computation has a near-miss.
- Gates: the coordinator's r2 snapshot on the final form (all OK, traceability deferred to KB publication) is cited. The hashes audited equal those in the brief: charter `6f17b379…`, tools `2d962719…`, views as listed.
- Open observations (no RED): O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-10, O-11, O-12, O-13, O-14, T0-O1, T1-O1, T1-O4.

**The difficulty passes the source-layer audit at revision 2.**
