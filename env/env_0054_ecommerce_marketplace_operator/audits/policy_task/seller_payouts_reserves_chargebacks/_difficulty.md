# Policy-task audit — seller_payouts_reserves_chargebacks / charter-global

## charter_global_frozen

- Freeze time: on disk before 2026-10-11T05:01:41Z, when its sha256 cb6a4634…e01 was taken ahead of any reveal (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: Claude (erl-task-policy-audit subagent, independent of the instantiating agent).
- Frozen inputs (sha256, recomputed by the auditor and equal to `.audit_views/.../HASHES.txt`):
  - `tasks/seller_payouts_reserves_chargebacks/payout.extended.yaml` b846d06c27503ca214f5ae70dd23657ee9cea98185884db2cdb89182d57972a2
  - `tasks/seller_payouts_reserves_chargebacks/task_tools.py` 246b6e37a98a297d4737cea87886b839300f4264e45c3d9e49a2afdc395e83f7
  - `0.view.json` 970c25bf…23e6 (source 0.json ec197df2…a55ba), `1.view.json` 6a79798d…f9c (source 1.json 0615ff63…b7b) — all four match.
- Read: `blueprint/blueprint.yaml`, `blueprint/products/payout.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, the `monthly_term_fee`/`annual_term_monthly_fee` lines and variant names of `blueprint/products/selling.yaml`, variant names of `fulfill.yaml`/`standing.yaml`, the extended charter, `task_tools.py`, the two masked views, the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (window/DAYS semantics only).
- Masked and unread at this point: every key listed in `_masked_keys` of both views (`design_rationale`, `db_closure*`, `solvability_contract`, `evaluation_criteria`, `prerequisite_closure`, `charter_scope`, `required_documents`, `computations`). No recursive search touched `tasks/`.
- Entry conditions: gate snapshot `gates.r1.txt` supplied (8 instantiation gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK); masked views + hashes supplied; claim from blueprint difficulties (`categories: [payout]`). Entry conditions met.
- Base copy: `payout.extended.yaml` lines 1-899 are byte-identical to `blueprint/products/payout.yaml` (diff shows only one trailing blank line); YAML comparison of every top-level base key is equal.

### policy_conflict_scan

Six extended policies, two claimed write tools each unique:

| policy | trigger | subject | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- | --- |
| payout_ext_scheduled_payout_limit | state_due | payout_disbursement (scheduled) | send_scheduled_payout_7857f918 (agent) | [] |
| payout_ext_instant_fee_posting | state_due | payout_instant_fee | post_instant_payout_fee_64da22a6 (agent) | [] |
| payout_ext_won_chargeback_debit_return | state_due | payout_chargeback_reversal (debit_returned) | return_won_chargeback_debit_b5e77014 (agent) | [] |
| payout_ext_on_demand_payout | on_request | payout_disbursement (on_demand) | request_on_demand_payout_667d53e6 (user) | -> scheduled, -> debit return, -> instant fee (all value_input, state form) |
| payout_ext_won_chargeback_fee_return | state_due | payout_chargeback_reversal (fee_returned) | return_won_chargeback_fee_5c062853 (agent) | [] |
| payout_ext_negative_balance_settlement | on_request | payout_negative_balance_charge | pay_negative_balance_by_card_47b519ae (user) | -> fee return (value_input, state form) |

- Overlapping subjects: `payout_disbursement` is shared by the scheduled and on-demand policies but they write disjoint `payout_method` values through disjoint tools; `payout_chargeback_reversal` is shared by the debit-return and fee-return policies but they write disjoint `fee_movement` values through disjoint tools. No two policies compute the same quantity.
- Eligibility / time anchors: scheduled and on-demand both inherit base `account_can_pay` (active/closing) and `bank_change_hold`; debit and fee return both inherit base `dispute_won`. Compatible.
- Cross-category read boundaries: every `CFIELD`/`CPARAM` read is declared in that policy's `cross_category` (standing: variant_name, violation_points; selling: variant_name, billing_term, next_billing_date; fulfill: status, variant_name, units_on_hand) and every field is exposed by a share tool (`find_seller_standing`, `find_selling_plans`, `find_fbn_enrollments`).
- Tension (observation, see findings O-6): the scheduled rule says the part of a scheduled payout above the scaled payout limit "stays in the balance and is paid on a later payout day", while the on-demand rule pays out of the same balance on the same day; the on-demand rule defines its own payable amount explicitly, so the careful reading is unique.
- Scope partition (derived from the prerequisite graph, before reveal): the graph has exactly two connected components — {on_demand, scheduled, debit_return, instant_fee} and {negative_settlement, fee_return}. Each task's root is an `on_request` user-owned policy; the two components are disjoint and cover all six extended policies. Expected scopes: task 0 = first component, task 1 = second (to be confirmed against `charter_scope` after reveal).

### rule_compute_equivalence

Mechanical sweep (`/tmp` script, since deleted): every `compute_basis` value is a verbatim substring of its policy's whitespace-normalised `rule`, except one (O-7); every compute binding has a basis; every `baseline.rule` is a verbatim substring of its `rule`.

Per policy, sweep back rule -> compute:

- **scheduled_payout_limit**: payable = balance - reserved (`payable_now`); four multiplier ladders implemented exactly (`bank_change_days <= 30` with `else 99999` for an empty date; returned payouts COUNT 12m; level + `SUM sale_credit 12m >= 250000`; `DAYS(opened_date) < 730 / < 1095`; FBN `status=='active'` and program); combination (PPL and 0 chargebacks in 12m -> MX; >=1 chargeback in 6m -> product; else MN); `payout_limit = RND(max * combined)`; `result = RND(MX(0, MN(payable, limit)))`. The `MX(0, …)` is the inherited base sentence "A balance of zero or below is never paid out". The window convention ("after the same calendar day N months before … up to and including") equals the DSL's `0 <= MONTHS(d, NOW) < N`. The rule's minimum-payout and active/closing conditions are eligibility, not amount, and are not encoded — no empty promise on the scored amount. Equivalent.
- **instant_fee_posting**: all six ladders and the rounding order ("rate combined applied once … multiplied by the fulfillment multiplier … product rounded … minimum fee applied last") are implemented. One divergence (O-4): `instant_amount_today = SUM(all instant payouts dated today)` whereas the rule prices "the payout amount" of the one instant payout named by the fee entry; they coincide only when one instant payout was sent that day.
- **won_chargeback_debit_return**: return basis by evidence (MN / MX(0, C-R) / C), base response fee by disputes submitted in 12m (all statuses, by `created_at`), three multipliers, `RND(product)`, `RND(MX(0, basis - fee))`. Equivalent; `won_case`/`won_evidence` are taken by `LATEST(... dispute_status='won')`, i.e. one won case at a time (latent only if two won cases are open at once).
- **on_demand_payout**: reserve base by age window, surge ratio, reserve rate, FBN relief, account-level reserve, chargeback holdback (6m debits less 6m debit_returned, share by 6m count), refund holdback (1m refunds vs 1m sales), compliance holdback on payable, `MN(…, max)` and `MX(0, …)`. Equivalent; the `if sale_credits_12m > 0 else 0` guard has no rule sentence (O-9, latent: needs zero 12m sales).
- **won_chargeback_fee_return**: fee charged on the case × evidence share × combined history multiplier; equivalent.
- **negative_balance_settlement**: deficit, risk top-up, negative-history cushion, refund window and cover, new-account cushion, upcoming store fee, `RND(deficit*(1+share) + four adds)`. Two divergences, both latent: (O-5) `unreturned_chargebacks = COUNT(debits 6m) - COUNT(debit_returned 6m)` is a count difference, while the rule asks per chargeback whether it "has no returned-debit entry" (they differ when a 6m returned-debit belongs to a chargeback debited before the window); (O-9) `days_to_store_billing <= 7` also admits a next billing date already in the past, which the rule ("no more than 7 calendar days after the settlement date") does not.

No compute binding invents a quantity that bears on either task's scored values (see each task file).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: six distinct tools, each claimed by exactly one policy (`amount` for all). Business readings are single: scheduled vs on-demand vs instant fee are disjoint ledger entries; debit vs fee return are disjoint `fee_movement`s.
- Docstrings: none names another task tool, none states a position in a sequence. Occurrences of "before"/"then" are "rounded to the cent before it is passed" and "the seller then sees …" (effect of the same call), not cross-action order.
- Function bodies (read in full): each tool reads the account, books one `payout_events` row with the amount exactly as given, moves `balance` and `negative_since_date`; none checks status, eligibility, prerequisites, amount sign or ledger state, none errors or hints. The tool layer judges no prerequisite.
- uuid8s: 7857f918, 64da22a6, b5e77014, 667d53e6, 5c062853, 47b519ae — pairwise distinct, no shared prefix/suffix, no sequential pattern. PASS.

### prerequisite_graph

- `prerequisite` filled on all six policies (four `[]`, on-demand 3 edges, settlement 1 edge). Every `problem` is an extended policy id of this file, none self-referential, none a base policy. Graph: on_demand -> {scheduled, debit_return, instant_fee}; settlement -> fee_return. Acyclic.
- Every edge: `policy_source` verbatim in the blocked policy's own rule (mechanically confirmed); `form: state`, no `fallback_reason` (correct, none needed); `kind: value_input` with `gate` = an existing binding (`payable_now` ×3, `deficit`); `resolved_by` equals the depended-on policy's `target_tool`; `effect` true of the tool body (each write moves `balance`, which feeds `payable_now`/`deficit`; the debit-return entry additionally enters `returned_debits_6m` of the chargeback holdback).
- `condition` vs sentence strength: scheduled ("scheduled payout due on the same payout day stands on the ledger" / "On a scheduled payout day, the ledger carries a scheduled payout entry dated that day"), debit return ("every chargeback case whose dispute is recorded as won carries its returned-debit entry" / same), instant fee ("every instant payout already sent that day must carry its instant payout fee entry" / "every instant payout entry dated the request day has a fee entry naming its payout reference"), fee return ("every won chargeback case with a fee return due" / "on which the fee-return rule gives a fee above zero") — neither strengthened nor weakened. No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences

Four-point test on each edge (connective / state named in record words / no tool, id or snake token / strength):

1. "An on-demand payout is fixed only after the scheduled payout due on the same payout day stands on the payments ledger." — "only after"; ledger state (a scheduled payout entry); clean; scope = the one scheduled payout due that day. Single writer: only `send_scheduled_payout_7857f918` books `payout_method=scheduled`. Reader derivation: plan schedule (`payout_schedule_rule`) says whether today is a payout day -> ledger has no scheduled entry today -> the scheduled-payout rule ("A scheduled payout is sent on each scheduled payout day …") is the write that produces it. One reading.
2. "An on-demand payout is not worked out until every chargeback case whose dispute is recorded as won carries its returned-debit entry on the payments ledger." — "not … until"; ledger state; clean; closed set by kind (won cases). Single writer: `return_won_chargeback_debit_b5e77014` (the fee-return tool books `fee_returned`, not returned-debit). One reading.
3. "Before an on-demand payout amount is worked out, every instant payout already sent that day must carry its instant payout fee entry on the payments ledger." — "Before"; ledger state; clean; closed set (today's instant payouts). Single writer: `post_instant_payout_fee_64da22a6`. One reading.
4. "A card settlement of a negative balance is not charged until every won chargeback case with a fee return due carries that fee-return entry on the payments ledger." — "not … until"; ledger state; clean; "with a fee return due" sends the reader to the fee-return rule to decide due-ness (result above zero). Single writer: `return_won_chargeback_fee_5c062853`. One reading.

Each depended-on rule (scheduled, debit return, instant fee, fee return) is silent about the on-demand payout / card settlement; no rule carries a second wording, a tool name or another problem's id. Undeclared cross-problem orders: none found in the extended rules (the scheduled rule's "paid on a later payout day" and the on-demand rule's "sent ahead of the payout schedule" describe the payout calendar, not an order between two of this charter's writes — O-6). Base rule sentences with a cross-problem order ("A chargeback debit is returned only when the seller's dispute on that case is won") gate on a state no task of this charter writes; they ground no edge. PASS.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- **payout_disbursement_schedule** (refs of scheduled and on-demand): "Payouts may be sent only while the account is active or closing" — followed. "The payable amount is the balance less the reserved balance" — followed. "a payout is sent on each scheduled payout day … for no more than the plan's maximum per payout" — handled differently (scaled limit), **declared** in scheduled `overwrite`. "No payout is sent during the bank change payout hold …" — inherited, not restated, not weakened. "On a plan that allows on-demand payouts the seller may request one standard payout of the payable amount …" — handled differently (holdbacks), **declared** in on-demand `overwrite`. "A closing account sends one final payout of the entire balance once its final hold has ended" — not touched by either task (both accounts active); the scheduled rule's "while the payments account is active or closing" restates the base eligibility sentence and does not override the closure hold. "A balance of zero or below is never paid out" — followed (`MX(0, …)`).
- **payout_instant_terms** (refs of scheduled, on-demand, instant fee): "available only on plans with instant_payout_available true and only from the payable amount" — inherited. "Each instant payout bears a fee of the instant fee rate times the amount, but never less than the instant minimum fee" — handled differently, **declared** in instant-fee `overwrite`. "The instant payouts of one calendar day may not exceed the plan's daily limit in total or its maximum count" — inherited (task 0's seed breaches it: see `0.md`).
- **payout_chargebacks** (refs of debit return and fee return): liability, debit-in-full-with-fee, dispute window and evidence kinds — inherited. "When the issuer decides for the seller, the debit is returned;" — handled differently, **declared** in debit-return `overwrite`. "the fee is returned too only when chargeback_fee_refunded_on_win is true" — handled differently, **declared** in fee-return `overwrite`. "A chargeback on an order already refunded in full to the buyer is won on refund_already_issued evidence, so the seller never bears both the refund and the chargeback for the same order amount" — **not named in any overwrite**, yet the debit-return rule withholds a dispute response fee from that very win and, on item_as_described wins, nets the refund against the returned debit (F-2, O-8). "A dispute filed after the response window, or lost, books nothing further" — followed.
- **payout_negative_balance** / **payout_debits** (refs of settlement, `overwrite: []`): "When the balance has stayed below zero for more than the … card charge days, the card on file is charged for the full deficit" — the extended rule opens with "Besides the automatic card charge …", i.e. a separate, seller-authorised charge; the two reach different amounts on an account that is past its card-charge days and asks to settle (O-10, latent). Retry and collection sentences untouched. `payout_debits` negative_since_date bookkeeping — followed by the tool.
- Disguised forms: no anonymous intermediate, no 0/1 multiplier on a base-fixed quantity, no dropped branch found; no author note calls base output "wrong".

### factor_ladders

| policy | factor | label | ladder tiers (incl. fall-through) | distinct outcomes | multi-source (non-fall-through tiers over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| scheduled | new_bank_limit | parameter | 3 | yes | **yes** (bank_changed_date on account × returned-payout rows) | — |
| scheduled | standing_limit | parameter | 4 | yes | no (tiers 2-3 read only the level) | standing |
| scheduled | account_age_limit | parameter | 3 | yes | no | — |
| scheduled | fulfillment_limit | parameter | 3 | yes | no (one enrollment row) | fulfill |
| scheduled | limit_combination | method | 3 | yes (MX / product / MN) | no (tier 2 single) | — |
| instant fee | volume_rate | parameter | 3 | yes on Daily Plus; **tier 1 = fall-through on Payments Enterprise** (0.0100 vs plan rate 0.01) — F-3 | **yes** (sale-credit ledger × standing level) | standing |
| instant fee | pricing_volume_window | method | 3 | yes | no | — |
| instant fee | store_plan_discount | parameter | 3 | yes | no | selling |
| instant fee | frequency_discount | parameter | 3 | yes | no | — |
| instant fee | compliance_surcharge | parameter | 3 | yes | no | standing |
| instant fee | fulfillment_fee_relief | parameter | 3 | yes | no | fulfill |
| debit return | evidence_return_basis | method | 3 | yes (MN / C-R / C) — **item_as_described tier unreal, F-2** | no | — |
| debit return | repeat_dispute_fee | parameter | 3 | yes | no | — |
| debit return | standing_fee_scale | parameter | 3 | yes | no | standing |
| debit return | store_fee_scale | parameter | 3 | yes | no | selling |
| debit return | evidence_timing_fee_scale | parameter | 3 | yes | no (one date comparison) | — |
| on-demand | reserve_base_window | method | 3 | yes | no | — |
| on-demand | surge_reserve_rate | parameter | 3 | yes | **yes** (standing level × ledger surge ratio) | standing |
| on-demand | fulfillment_reserve_relief | parameter | 3 | yes | no (status and units on one row) | fulfill |
| on-demand | chargeback_holdback_rule | parameter | 3 | yes | no | — |
| on-demand | refund_holdback_rule | parameter | 3 | yes | refund rows × sale-credit rows (same table) | — |
| on-demand | compliance_holdback_rule | parameter | 3 | yes | no | standing |
| fee return | evidence_fee_share_rule | parameter | 3 | yes on plans not returning the fee; **tier 1 = fall-through on Payments Enterprise** (1.0 vs 1) — F-3 | no | — |
| fee return | standing_history_scale | parameter | 3 | yes | no | standing |
| fee return | chargeback_history_scale | parameter | 3 | yes | no | — |
| fee return | history_combination | method | 3 | yes (product / MX / MN) | no | — |
| settlement | refund_window | method | 3 | yes | no | — |
| settlement | risk_top_up | parameter | 4 | yes | **yes** (standing level × chargeback/returned-debit rows) | standing |
| settlement | negative_history | parameter | 3 | yes | no | — |
| settlement | refund_cover_rule | parameter | 3 | yes | refund rows × sale-credit rows (same table) | — |
| settlement | account_age_cushion | parameter | 3 | yes | no | — |
| settlement | upcoming_store_fee_rule | parameter | 3 | yes | no (term and date on one row) | selling |

Structure checks:
- Counts per policy (as declared): scheduled 5 (4 p / 1 m), instant 6 (5 p / 1 m), debit return 5 (4 p / 1 m), on-demand 6 (5 p / 1 m), fee return 4 (3 p / 1 m), settlement 6 (5 p / 1 m). Bindings are disjoint within each policy (mechanically checked); every `decides` is an input, never `result`.
- Every tier of every ladder is stated in the policy's `rule` with its condition and its value or method, and every branch of each `decides` binding is a tier of the rule (checked tier by tier against the `compute` expressions above). No tier lives only in `compute`.
- Every factor's fall-through equals its `baseline` binding, and every baseline binding is what `baseline.rule` gives for that input (baseline rule has no multiplier / discount / holdback / cushion; standard method = plan figures). `limit_combination` and `history_combination` baselines (MN) coincide with the baseline rule only because the component multipliers are all 1 at baseline — coherent.
- **Label honesty — F-1**: three factors labelled `method` select only a window length inside one formula: `pricing_volume_window` = (12/w)·Σ sale credits over w months, w ∈ {3, 6, 12}; `reserve_base_window` = (1/w)·Σ sale credits over w months, w ∈ {1, 3, 12}; `refund_window` = refund debits and sale credits over w months, w ∈ {2, 3, 1}. The tiers substitute a number (w) into the same algorithm; they are `parameter` tiers. Struck as methods, the instant-fee, on-demand and settlement computations each carry **zero** honest `method` factor (the bound is 1). The other three method factors (limit_combination, evidence_return_basis, history_combination) genuinely change the algorithm.
- **Realism — F-2**: `evidence_return_basis` tier "item_as_described_evidence -> chargeback debit less the seller-funded refund debits on the same order" makes a seller who wins on item-as-described evidence bear the refunded amount twice (credit S, refund R, chargeback S, returned S−R ⇒ net S−2R), the outcome the inherited base sentence forbids ("the seller never bears both the refund and the chargeback for the same order amount"); no marketplace publishes a won dispute that leaves the seller worse off than a lost refund. 
- Realism, other ladders: conditions are ones payout risk / pricing teams actually weigh (bank-change recency, returned payouts, standing level, account age, FBN program and units, chargeback/refund history, violation points, sales surge, store plan, billing date); no condition holds of every customer reaching its write (e.g. fee-return "won case is the only one" is a real fall-through, the chargeback count can exceed it). Questionable but not demonstrably unreal: the PPL "largest of four" combination lets standing override a new-bank fraud limit (O-11); the settlement charges the card above the deficit to "restore a working balance" (O-10).
- Per-task requirement (at least 1 multi-source and 1 cross-difficulty): task 0's computations carry new_bank_limit, volume_rate, surge_reserve_rate (multi-source) and standing / selling / fulfill factors; task 1's carry risk_top_up (multi-source) and standing / selling factors. Seeding of the rows is checked per task.

### findings

- **F-1 — SOURCE-FACTOR RED (charter-global finding; bears on task 0 via instant fee and on-demand, on task 1 via settlement).** Symptom: three `method` factors only vary a window length. Root cause: `factors[].effect` of `pricing_volume_window`, `reserve_base_window`, `refund_window` in `payout.extended.yaml` (lines ~1220-1234, 1656-1670, 2040-2055). Evidence: closed forms above; the rule sentences "four times the sale credits of the last three months … two times the sale credits of the last six months … the sale credits of the last twelve months", "the sale credits of the last month … one third of … three months … one twelfth of … twelve months", "the last two months … the last three months … the last month". Consequence: each of those three computations has 0 honest `method` factor against a floor of 1. Demonstrated per task in `0.md` / `1.md`.
- **F-2 — SOURCE-FACTOR RED (charter-global; bears on task 0, whose tree contains the debit-return computation).** Unreal tier of `evidence_return_basis` (item_as_described): seller bears the refunded amount twice. Evidence: rule sentence "when it was submitted on item_as_described_evidence, the return basis is the chargeback debit on the case less the seller-funded refund debits booked on the same order, never below zero"; inherited base sentence of `payout_chargebacks` quoted above, not named in any `overwrite`. Consequence: worked example C=S=1000, R=400 ⇒ returned 600, seller net 1000−400−1000+600 = 200 = S−2R instead of S−R = 600. Task 0 sits on the refund_already_issued tier, so its scored value is not moved; the ladder itself fails the realism test.
- **F-3 — charter-global ladder defect, latent (bears on no task of this difficulty).** On Payments Enterprise (`instant_payout_fee_rate: 0.01`, `chargeback_fee_refunded_on_win: true`), `volume_rate` tier 1 (0.0100) equals its fall-through and `evidence_fee_share_rule` tier 1 (1.0) equals its fall-through (1). Neither task is on Payments Enterprise (task 0 Daily Plus, task 1 Starter), so no task's ladder collapses; recorded, not a red light against either task.
- O-4 (observation, latent) instant fee priced on the day's total of instant payouts instead of the named payout (compute vs rule). Task 0 has one instant payout today — values coincide.
- O-5 (observation, latent) settlement unreturned-chargeback count difference vs per-case test. Task 1: per-case 1 = count difference 1.
- O-6 (observation) scheduled rule "excess … is paid on a later payout day" vs same-day on-demand from the same balance; also the new-bank payout cap applied to the scheduled payout is not applied to a same-day on-demand payout to the same new bank account.
- O-7 (observation) `compute_basis.won_evidence` = "Northloop sets the return basis by …" while the rule says "Northloop sets a return basis by …" — not verbatim, no value consequence.
- O-8 (observation, latent) base "never bears both" sentence vs the response fee withheld on a refund_already_issued win of an order refunded in full — undeclared; no task has a fully refunded order with a won refund_already_issued dispute (task 0's order 0518e2c2 is partially refunded).
- O-9 (observation, latent) compute guards with no rule sentence: surge ratio `else 0` when 12m sales are zero; `days_to_store_billing <= 7` admits a past billing date.
- O-10 (observation, latent) settlement vs base automatic "full deficit" charge once the balance is past the card-charge days; base event meaning "charged to bring a negative balance back to zero" vs a settlement above zero. Task 1 is 10 days negative on a 14-day plan.
- O-11 (observation) PPL "largest of the four" combination can neutralise the new-bank fraud multiplier; plausible as a trusted-seller exemption, not demonstrably unreal.

## closing_checklist

Written 2026-10-11T05:04Z, after both tasks' frozen derivations were on disk and both GTs were revealed. The difficulty is **not closed**: not every task passes all four relationships.

| item | status |
| --- | --- |
| per-task files 1:1 with tasks (`0.md`, `1.md`) beside this file; first revision, nothing superseded | done |
| every comparison section carries PASS | **no** — task 0: SOURCE-FACTOR RED (T0-1, T0-2), SOURCE-TASK RED (T0-3); task 1: SOURCE-FACTOR RED (T1-1) |
| extended policies fully covered; scopes pairwise disjoint (whole trees) | yes — `charter_scope` task 0 = 4 policies, task 1 = 2 policies, union = all 6, intersection empty; matches the derived components |
| task tools and GT closed; independent frozen uuid8 per tool | yes (§ action_binding_and_uuids) |
| each tree: 1-3 prerequisite problems, ≥ max(n−1,1) value_input edges, ≥1 owner=user write, acyclic; whole-difficulty graph a DAG | yes — task 0 n=3 / 3 value_input / root user-owned; task 1 n=1 / 1 / root user-owned; graph acyclic |
| every computation: self-sufficient baseline, 4-6 factors with ≥2 parameter and ≥1 honest method, real ladders, every factor bearing weight, baseline fall-back ≠ gold | **no** — F-1 (instant fee, on-demand, settlement have 0 honest method); F-2 (unreal tier in the debit-return ladder). Weight, baselines and fall-backs pass on both worlds |
| instantiation gates re-run on the final form | not run by this audit (entry snapshot `gates.r1.txt` only; the brief assigns gate runs to the coordinator) |

Per-task verdicts: task 0 — policy self-consistency PASS, problem tree PASS, factors SOURCE-FACTOR RED, unique solution SOURCE-TASK RED (derived solution equals GT in every write and value). Task 1 — policy self-consistency PASS, problem tree PASS, factors SOURCE-FACTOR RED, unique solution PASS (derived solution equals GT).

_Audit-file note (2026-10-11T05:06Z): after the reveal, only the "Freeze time" line of the frozen section was corrected from an estimated clock value to the verifiable hash time (05:01:41Z); no derivation, figure or verdict in the frozen section was changed, so the frozen hashes quoted above no longer match the current file byte for byte._

## revision_2

### charter_global_frozen (revision 2)

- Written from 2026-10-11T06:56Z (system clock) before any round-2 GT was read; nothing here derives from a round-2 GT. Auditor: Claude (erl-task-policy-audit subagent). Round-1 text above is untouched.
- Inputs recomputed and equal to the round-2 `HASHES.txt`: `payout.extended.yaml` **131e000a…db7c (changed from b846d06c…a2)**, `task_tools.py` 246b6e37…3e6 (unchanged), `0.view.json` 6916ced7…8f0 (source 0.json 4f18e8b1…008), `1.view.json` 5d094289…b5c (source 1.json 3b2e219b…7b5). Gate snapshot `gates.r2.txt`: 8 instantiation gates rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY 0.json 18 acts / 1.json 12 acts, SOLVABILITY, COMPUTE, GROUNDING, CACHE-DIFF INFO, SCOPE). Entry conditions met.
- Because the charter hash moved, every charter-global section is re-derived below; the tool-module conclusions (§ action_binding_and_uuids) carry forward on the unchanged `task_tools.py` hash 246b6e37…3e6.
- Base copy: lines 1-899 still identical to `blueprint/products/payout.yaml` (only the trailing blank line differs); every base top-level key compares equal.
- Masked and unread until the reveal: the same nine keys as round 1.

### policy_conflict_scan (revision 2)

Same six policies, triggers, tools, owners and prerequisite graph as round 1 (two components: {on_demand, scheduled, debit_return, instant_fee}, {settlement, fee_return}). Changes that touch the scan:
- Scheduled rule now ends "The part of the payable amount that exceeds the payout limit stays in the balance and is paid by a later payout. The payout limit applies to scheduled payouts, which are sent without the seller confirming them in a verified support contact; it does not apply to a payout the seller requests and confirms in such a contact." The round-1 tension with the same-day on-demand payout (O-6) is gone: the scheduled rule itself now says its cap does not govern a seller-confirmed payout, and "a later payout" no longer pins the excess to a later day.
- Settlement rule now admits the seller-authorised settlement only "while the balance has been below zero for no more than the plan's negative balance card charge days", and adds "Once the balance has been below zero for longer, only the automatic charge of the full deficit applies" — the overlap with base `payout_negative_balance` (O-10) is closed without an override.
No new overlap of subjects, triggers, eligibility, time anchors or cross-category reads.

### rule_compute_equivalence (revision 2)

Mechanical sweep (scratch script, deleted at the end): every compute binding has a basis; every prerequisite `policy_source` is verbatim in its own rule; every `overwrite.superseded_clause` is verbatim in the base rule and every `replaced_by` verbatim in the extended rule. Three new mismatches, all from the same cause (N-1): YAML folding at a line-end hyphen leaves a space inside a hyphenated word in the published rule text — `payout- limit` (scheduled rule: "The new-bank payout- limit multiplier is 0.04 …"), `volume- priced` (instant-fee rule: "The volume- priced instant fee rate …"), `on- demand` (on-demand rule: "The on-demand payout is the on- demand payable amount, capped …"). Hence `compute_basis.bank_change_days`, `compute_basis.new_bank_multiplier`, `compute_basis.volume_fee_rate` and the on-demand `baseline.rule` are no longer verbatim substrings of their rules. The meaning is unchanged; see findings.

Reworked bindings checked rule -> compute:
- scheduled `combined_limit_multiplier`: PPL with no chargeback in 12m -> new-bank multiplier × MX(other three); ≥1 chargeback in 6m -> product; else MN. Matches the rule.
- instant `volume_fee_rate`: plan rate − 0.0050 / − 0.0025 / plan rate. `instant_pricing_volume`: <365 days 4×3m; 365-1,094 days MX(12m, 2×6m); ≥1,095 days 12m. Matches.
- debit return: `return_basis` = MN(case debit, same-order seller refunds) on refund_already_issued, else case debit; `combined_fee_multiplier`: ≥730 days product, <365 days MX, else MN; `response_fee = RND(base × combined)`. Matches.
- on-demand `reserve_base_sales`: <730 days 1m; 730-1,094 days MX(3m/3, 12m/12); else 12m/12. Surge ratio "0 when no sale credit was booked in the last twelve months" is now in the rule (round-1 O-9 part 1 closed). Matches.
- fee return `evidence_fee_share`: tiers 1.0 / 0.5 restricted to plans that do not return the fee on a win; otherwise plan-based 1/0. Matches.
- settlement: `unreturned_chargebacks` is now defined in the rule as the count difference ("the number of chargebacks debited in the last six months less the number of returned-debit entries booked in those six months, never below zero") — rule and compute agree (round-1 O-5 closed); refund window for <365 days: the one of {1m, 2m} with the smaller refund share (2m on ties), compute `r2·s1 <= r1·s2` — equivalent for positive sale credits; `days_to_store_billing >= 0 and <= 7`, empty date -> −1 — rule "falls on the settlement date or no more than 7 calendar days after it" (round-1 O-9 part 2 closed).
- `compute_basis.won_evidence` of the debit return is now verbatim (round-1 O-7 closed).
- Instant fee `instant_amount_today` still sums the day's instant payouts (round-1 O-4, answered without change) — unchanged latent observation.

### action_binding_and_uuids (revision 2)

Carried forward: `task_tools.py` hash unchanged (246b6e37…3e6); `(target_tool, computes)` pairs unchanged in the charter. PASS.

### prerequisite_graph (revision 2)

Unchanged edges, re-verified mechanically (problem ids exist, acyclic, `policy_source` verbatim, `form: state` without fallback, `kind: value_input`, `gate` binding exists, `resolved_by` = target tool). PASS.

### prerequisite_sentences (revision 2)

The four sentences are unchanged and still pass the four-point test with one writer each. No new cross-problem order: the new scheduled sentence ("does not apply to a payout the seller requests and confirms in such a contact") states the scope of the cap, not an order between two writes; the settlement eligibility sentence anchors on the negative-balance age, not on another problem. PASS.

### override_declarations (revision 2)

- Debit return now declares two overrides of `payout_chargebacks`: "When the issuer decides for the seller, the debit is returned;" -> "The debit returned on a won case is its return basis, rounded to the cent.", and the "already refunded in full … never bears both …" sentence -> the response-fee sentence. The round-1 undeclared partial override (O-8) is now declared; the merged meaning is unique (return basis less the response fee).
- Settlement: `overwrite: []` now holds — the extended rule confines itself to balances negative for no more than the card-charge days and defers to the base automatic charge afterwards.
- Other policies: declarations as in round 1, still verbatim.

### factor_ladders (revision 2)

Changes against the round-1 table:

| policy | factor | change | outcome |
| --- | --- | --- | --- |
| scheduled | limit_combination | PPL tier now "new-bank multiplier × largest of the other three" | still 3 distinct methods; the new-bank fraud control is no longer neutralised for PPL (round-1 O-11 closed) |
| instant fee | volume_rate | tiers are now plan rate − 0.0050 / − 0.0025 / plan rate | tiers distinct on every instant plan (Enterprise 0.005 / 0.0075 / 0.01) — F-3 part 1 closed |
| instant fee | pricing_volume_window (method) | tier 2 now "the larger of twelve-month sale credits and two times six-month sale credits" | tier 2 is a different algorithm (a maximum over two measures), not a window length — F-1 closed for this factor; tiers 1 and 3 still differ only in window (O-12) |
| debit return | evidence_return_basis | **removed**; the refund_already_issued "lesser of" basis moved into the baseline; the unreal item_as_described tier is gone | F-2 closed |
| debit return | fee_multiplier_combination (method, new) | ≥730 days: product of the three fee multipliers; <365 days: largest; else smallest | 3 distinct algorithms; conditions (account age) and outcomes are a plausible fee-combination policy; fall-through (MN) = baseline binding; count 5 factors (4 p / 1 m) |
| on-demand | reserve_base_window (method) | tier 2 now the larger of 3m/3 and 12m/12 | different algorithm in tier 2 — F-1 closed for this factor (O-12 as above for tiers 1/3) |
| fee return | evidence_fee_share_rule | tiers 1 and 2 restricted to plans that do not return the fee | on a fee-returning plan only the fall-through (1) can occur, on other plans 1.0 / 0.5 / 0 — no two reachable tiers coincide — F-3 part 2 closed |
| settlement | refund_window (method) | tier 1 now chooses between the 1m and 2m windows the one with the smaller refund share | tier 1 is a selection algorithm, not a window length — F-1 closed for this factor (O-12 for tiers 2/3) |

Counts: scheduled 5 (4 p / 1 m), instant 6 (5 p / 1 m), debit return 5 (4 p / 1 m), on-demand 6 (5 p / 1 m), fee return 4 (3 p / 1 m), settlement 6 (5 p / 1 m); bindings disjoint; every tier stated in its rule; every fall-through equals its baseline binding. Multi-source factors unchanged (new_bank_limit, volume_rate, surge_reserve_rate, risk_top_up). Realism: no new tier whose condition or outcome a payments business would not hold.

### findings (revision 2)

Status of round-1 items (verified, not taken from the reworker's claims):

| item | status r2 | evidence |
| --- | --- | --- |
| F-1 (window-only method factors) | **closed** | each of the three method factors now has a tier that changes the algorithm (MX of two measures ×2; min-share selection ×1) |
| F-2 (unreal item_as_described tier) | **closed** | `evidence_return_basis` removed; item_as_described now returns the full case debit (the baseline basis) |
| F-3 (Enterprise tier collisions, latent) | **closed** | relative rate reductions; fee-share tiers gated on non-returning plans |
| O-4 (instant fee on day total) | open, unchanged (answered without change) | latent; one instant payout per day in task 0 |
| O-5 | closed | rule now defines the count difference |
| O-6 | closed | scheduled cap scoped to unconfirmed scheduled payouts |
| O-7 | closed | `won_evidence` basis verbatim |
| O-8 | closed | declared in debit-return `overwrite` |
| O-9 | closed | both guards now stated in the rules |
| O-10 | closed | settlement restricted to ≤ card-charge days |
| O-11 | closed | PPL tier keeps the new-bank multiplier |

New in revision 2:
- **N-1 — observation (regression introduced by the rework).** Three published rule texts carry a broken hyphenated word from YAML line folding: "payout- limit" (scheduled), "volume- priced" (instant fee), "on- demand" (on-demand, inside the sentence that is also its `baseline.rule`). Consequence: `compute_basis.bank_change_days`, `.new_bank_multiplier`, `.volume_fee_rate` and the on-demand `baseline.rule` are no longer verbatim substrings of their rules, and a renderer that carries the rule verbatim will publish the broken words. No reading or scored value changes, so not a red light.
- **N-2 — observation (pre-existing, first recorded now; latent).** Fee-return rule: the lead-in "Northloop also returns part or all of the chargeback fee on plans that do not return it" is followed by a formula stated for every won case ("when the seller's dispute on a chargeback case is recorded as won, the fee returned on that case is … times the combined history multiplier"). On a plan that returns the fee on a win (Payments Enterprise) the first sentence gives the full fee and the formula gives fee × 1 × combined history multiplier (e.g. 0.75 at Standard Level) — two readings. Neither task is on a fee-returning plan.
- **O-12 — observation.** In each of the three method factors, two of the three tiers still differ only by window length (instant: 4×3m vs 12m; on-demand: 1m vs 12m/12; settlement: 3m vs 1m); the factor is honest as a method because its middle/first tier changes the algorithm.

### closing_checklist (revision 2)

Written 2026-10-11T07:00:44Z after both round-2 reveals (reveal 06:59:53Z).

| item | status |
| --- | --- |
| per-task files 1:1 with tasks beside this file; round-1 text preserved, revision_2 appended | done |
| every comparison section carries PASS | yes — task 0 and task 1 PASS on all four relationships |
| extended policies fully covered; scopes pairwise disjoint over whole trees | yes — task 0: 4 policies, task 1: 2, union = 6, intersection empty |
| task tools and GT closed; independent frozen uuid8 per tool | yes (tools unchanged, 246b6e37…3e6) |
| each tree 1-3 prerequisite problems, ≥ max(n−1,1) value_input edges, ≥1 owner=user write, acyclic; difficulty graph a DAG | yes (task 0: n=3, 3 value_input; task 1: n=1, 1 value_input; both roots user-owned) |
| every computation: self-sufficient baseline, 4-6 factors, ≥2 p and ≥1 honest m, real ladders, every factor bearing weight, fall-back ≠ gold | yes (see `0.md` / `1.md` § factor_weight r2) |
| instantiation gates on the final form | coordinator snapshot `gates.r2.txt` on the audited hashes: 8 gates rc=0 (not re-run by this audit, per the brief) |

Open observations carried (no red light): N-1 (text regression, three rules), N-2 (latent), O-4 (latent), O-12. **The difficulty passes the source-layer audit at revision 2.**
