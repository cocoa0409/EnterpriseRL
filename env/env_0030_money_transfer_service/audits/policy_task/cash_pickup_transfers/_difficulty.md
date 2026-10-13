# Policy-task audit — cash_pickup_transfers / charter-global

## charter_global_frozen

- Freeze time: 2026-10-04T16:37Z, clock reading (written before any task's GT was revealed; nothing below derives from a revealed GT field).
- Auditor: erl-task-policy-audit (independent of the instantiating agent).
- Frozen inputs (sha256):
  - `cash.extended.yaml` 647e1c8753170ef9de0aa2191d818808b84af0b8203c18a534a27cecdbe85ed6 (masked view = source, verified by sha256sum)
  - `task_tools.py` 64510a2f8f7b38df8532fcee70977840d4bae26abcea185bc3abdb2277fa39f0 (masked view = source, verified)
  - blueprint read: `blueprint.yaml`, `db_schema.json` (structure only), `share_tools.py`, `products/cash.yaml`; for cross-difficulty consistency spot checks only: `products/bank.yaml` (Bank Deposit Standard ladder), `products/wallet.yaml` (Mobile Wallet Express ladder/providers), `products/account.yaml` (Paloma Enhanced), `products/rewards.yaml` (tier names).
- Permitted: the charter, the tool module, the blueprint, `erlbench/`, and per task `frozen_time`, `user_scenario`, `initial_state` from `/tmp/erl0030_views/policy_task/cash_pickup_transfers/tasks/*.json`.
- Masked until both tasks' derivations were frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, both `worklog.md` files.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl0030_gates/cash_pickup_transfers.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; masked views with VIEW_MANIFEST hashes supplied and re-verified. Observation E-1: the replay section of the snapshot prints a row only for `1.json` (`1.json 18 True True 0 47 47 True`); no row for `0.json` appears, though the section ends in `REPLAY OK`. Recorded as an observation on the input, not re-run (the auditor does not run gates).
- Base copy check: `diff` of extended lines 1-1393 against `blueprint/products/cash.yaml` differs only by the two trailing blank lines 1392-1393. Base section is verbatim.

### policy_conflict_scan

Six extended policies, grouped by the `prerequisite` graph into two connected components:

| Component | Policies (target tool, owner) |
| --- | --- |
| Shortfall | `cash_ext_shortfall_reissue_window` (choose_shortfall_reissue_92bb83b1, user) <- `cash_ext_shortfall_credit` (book_shortfall_credit_cb14652e, agent) |
| Expired pickup name correction | `cash_ext_reactivation_fee` (pay_reactivation_fee_6d9bfacd, user), `cash_ext_reactivation_window` (reactivate_expired_pickup_d4e94bda, agent), `cash_ext_correction_fee` (pay_name_correction_fee_e426b8ef, user), `cash_ext_correction_extension` (record_name_correction_726c5192, agent) |

Overlap scan:

- Subject `cash_fee_charged`: claimed by `cash_ext_reactivation_fee` (fee_type reactivation_fee) and `cash_ext_correction_fee` (fee_type name_correction_fee), plus base `cash_evt_pricing` (booking fees, fee_seq 1), base `cash_evt_name_correction` and base `cash_evt_expiry_and_reactivation`. The two extended fee policies govern disjoint fee types and write through different tools; each replaces exactly the base fee sentence of its own fee type (see override_declarations). No conflict.
- Subject `cash_remedy_chosen` / `cash_reissued`: extended `cash_ext_shortfall_reissue_window` + base `cash_evt_error_resolution`. Base gate "A remedy can be chosen only after a decision of error_found on that notice." is inherited unchanged; base "a re-issue made available within reissue_business_days Paloma business days of the choice" is met by the extended "makes the cash collectable again from the day of the choice" (0 days). No conflict.
- Subject `cash_paloma_credit`: extended `cash_ext_shortfall_credit` + base `cash_evt_error_resolution`; the base amount sentence is declared superseded. Base "On error_found every fee collected is refunded with fee_refund_reason paloma_error" stays in force and is a separate write not claimed by any extended policy (relevant per task: whether the seed already carries it).
- Subject `cash_pickup_reactivated`: extended `cash_ext_reactivation_window` + base `cash_evt_expiry_and_reactivation`. Inherited base gates: reactivation within reactivation_window_days of expired_date (inclusive), at most max_reactivations. Extended adds one new gate (reactivation fee charge on the ledger), which is a prerequisite sentence of its own rule, not a contradiction of a base sentence (the base fee-on-reactivation sentence is superseded by `cash_ext_reactivation_fee`).
- Subject `cash_name_corrected` / `cash_recipient_name_updated`: extended `cash_ext_correction_extension` + base `cash_evt_name_correction`. Inherited base gates: correctable status (awaiting_funds, on_hold, ready_for_pickup; expired must first be reactivated), max_name_corrections including the new one. Two base sentences declared superseded (character distance with accents ignored; window change).
- Triggers: five `on_request`, one `state_due` (credit). Time anchors: `expired_date` (reactivation fee and window), `date_available` = disclosed date (correction fee and extension), `pickup_expiry_date` (re-issue and extension days-left), notice/finding/payout dates (credit). None collides with a base time anchor.
- Cross-category read boundaries: rewards (all six), account (re-issue window, reactivation fee, reactivation window, correction extension), bank (credit), wallet (correction fee). Each is declared in `cross_category` with exactly the fields the compute reads.
- Terminal states: re-issue -> ready_for_pickup under a new Pickup Number; credit -> principal_held raised, status unchanged; reactivation -> ready_for_pickup, count +1; fees -> fees_held raised; correction -> name replaced, expiry moved. No two policies write incompatible terminal states on the same field in one tree.

Task scopes (derived from the graph before reveal; to be compared with `charter_scope` after reveal): the two components above are disjoint and together cover all six extended policies, i.e. M = 2 tasks, one per component, would be pairwise disjoint and jointly complete.

### rule_compute_equivalence

Swept every compute binding against `compute_basis` and the `rule`, and every rule sentence back to a binding.

- `cash_ext_shortfall_reissue_window`: `window_left` = DAYS(NOW, pickup_expiry_date) <- "days left counted as calendar days from the day of the re-issue to that last day, the re-issue day not counted"; `window_base` three branches <- the keep / top-up / full-window sentence ("has not passed" = window_left >= 0); `cash_out_refusals` filter `refusal_reason='location_out_of_cash'` <- "because the payout location had no cash ... refusals for any other reason do not count"; `loyalty_days`, `tenure_days` (MONTHS from opened_date to NOW) <- their sentences; `result` int sum <- "added as whole days with no rounding". Equivalent both ways.
- `cash_ext_shortfall_credit`: `disclosed_cash` RND(principal x fx_rate, 2), `shortfall_usd` RND((disclosed - handed)/fx_rate, 2) <- standard sentence; `uplift_pct` three branches incl. `counter_rate < fx_rate` <- uplift sentence; `uplifted_usd` RND once <- "applied once to that rounded value"; `finding_lag` DAYS(notice, finding) with per-day / flat / none <- delay sentence; `bank_payouts` XCOUNT 12 months on `bank_payout_sent` <- "Bank Deposit payouts sent ... dated less than twelve whole months before the day of the credit"; `notice_lead` DAYS(payout, notice) <- prompt sentence; `result` RND sum. Equivalent.
- `cash_ext_reactivation_fee`: `network_share_pct` 0/60/100 <- network sentence; `lateness_multiplier` on DAYS(expired_date, NOW) <- lateness sentence ("expiry day not counted"); `shared_fee` RND(fee x share x mult) <- "the product rounded half up to the cent"; three discounts; `result` RND(MX(0, ...)) <- "never below zero ... taken off the rounded product together". Equivalent.
- `cash_ext_reactivation_window`: `reactivated_base` ceil(W x fraction) or W <- "each fraction rounded up to a whole day"; network / loyalty / tenure / correction / principal days <- their sentences; `result` int sum. Equivalent.
- `cash_ext_correction_fee`: `bundle_share_pct` conjunction of `reactivation_fee_charges >= 1` and `id_mismatch_refusals` <- bundle sentence; `days_since_disclosed` DAYS(date_available, NOW) <- "from the disclosed date of availability"; multiplier, loyalty, wallet XCOUNT 12 months on `wallet_credit_sent`; `result` RND(MX(0, ...)). Equivalent.
- `cash_ext_correction_extension`: `days_left` DAYS(NOW, pickup_expiry_date); `gap` MX(0, guarantee - days_left); `result` ceil(gap x multiplier) <- "converted by the gap multiplier and rounded up to a whole day"; `history_days` counts corrections before this one <- "already recorded ... before this one"; `waiting_days` from date_available. Equivalent.
- Factor ladders vs rule: every tier of every `factors[].ladder` is stated in the rule with its condition and value/method, and every branch of each `decides` binding is a tier the rule states. No tier lives only in compute.

Verdict: PASS (no SOURCE-POLICY finding).

### action_binding_and_uuids

- `(target_tool, computes)`: (choose_shortfall_reissue_92bb83b1, reissue_window_days), (book_shortfall_credit_cb14652e, amount_usd), (pay_reactivation_fee_6d9bfacd, amount_usd), (reactivate_expired_pickup_d4e94bda, pickup_window_days), (pay_name_correction_fee_e426b8ef, amount_usd), (record_name_correction_726c5192, extension_days): each claimed by exactly one policy.
- uuid8s 92bb83b1, cb14652e, 6d9bfacd, d4e94bda, e426b8ef, 726c5192: pairwise distinct, no shared prefix or tail, no sequence, no sign of batch derivation.
- Docstrings: grep for before/after/first/prior/until/then finds only "The credit/charge then appears ..." and "The recipient can then collect" (each describing that tool's own result). No docstring states a position in a sequence or names another tool.
- Tool bodies: none reads status, ledger or cases to refuse or warn; each writes what it is given (`ctx.find` is used only to copy customer_id, fees/principal held, previous name, next correction_seq). The tool layer judges no prerequisite.
- Owners: the two fee payments and the remedy choice are `owner="user"` and are described as the customer's own authorisation in both rule and docstring; reactivation, correction and credit are `owner="agent"`. Consistent with the base (`cash_evt_expiry_and_reactivation`: "the agent carries it out"; `cash_evt_error_resolution`: "the choice is the customer's own").

Verdict: PASS.

### prerequisite_graph

| Edge | From (blocked) | To (problem) | kind | gate | form | resolved_by = target of To? |
| --- | --- | --- | --- | --- | --- | --- |
| A | cash_ext_shortfall_credit | cash_ext_shortfall_reissue_window | value_input | uplift_pct (binding exists) | state | choose_shortfall_reissue_92bb83b1 yes |
| B | cash_ext_reactivation_window | cash_ext_reactivation_fee | state_gate | cash_ledger.fee_type | state | pay_reactivation_fee_6d9bfacd yes |
| C | cash_ext_correction_fee | cash_ext_reactivation_fee | value_input | bundle_share_pct (binding exists) | state | pay_reactivation_fee_6d9bfacd yes |
| D | cash_ext_correction_extension | cash_ext_reactivation_window | value_input | days_left (binding exists) | state | reactivate_expired_pickup_d4e94bda yes |
| E | cash_ext_correction_extension | cash_ext_correction_fee | state_gate | cash_ledger.fee_type | state | pay_name_correction_fee_e426b8ef yes |

- `prerequisite` filled on all six (`[]` on cash_ext_shortfall_reissue_window and cash_ext_reactivation_fee). Every `problem` is an extended id of this file, none a base policy, none self.
- Acyclic: topological order credit-component {reissue_window -> credit}; correction-component {reactivation_fee -> (reactivation_window, correction_fee) -> correction_extension}.
- Each `policy_source` located verbatim in its own policy's `rule` (A in cash_ext_shortfall_credit; B and D's blocked rules; C in cash_ext_correction_fee; E in cash_ext_correction_extension) — checked by string match.
- All edges `form: state`, no `fallback_reason`, consistent.
- `condition` vs sentence strength: A condition "remedy_choice reissue_shortfall or refund_shortfall" = sentence "remedy choice between a refund and a re-issue"; B/C condition "fee_seq equal to reactivation_count plus one" = "numbered with that reactivation's number" / "for the reactivation that pickup awaits"; D condition = "stands reactivated, ... count raised, ... last day ... no earlier than the day of the correction"; E condition = "numbered with that correction's number". None strengthened or weakened.
- `effect`: each resolving tool genuinely writes the row/field the gate or binding reads (tool bodies above).
- Observation P-1 (world-specific phrasing in general text): the `effect` of A ("moves from no uplift to the re-issue uplift (the payout recorded a rate below the disclosed rate)") and of C ("moves from the whole fee to the ID-mismatch bundle share (a name-mismatch refusal is on record), so the correction fee is computed on half the tier fee") describe the branch an instantiating world takes rather than the edge's general effect (on a world with no mismatch refusal C's binding moves to the plain bundle share, 75, not 50). Read with the parentheticals as qualifying conditions they agree with the rules; no reader-facing sentence is affected, so recorded as an observation, not a red light.
- Observation P-2 (condition narrower than the binding it feeds): C's condition names the charge "with fee_seq equal to reactivation_count plus one", while `bundle_share_pct` reads `COUNT(cash_ledger, fee_type='reactivation_fee') >= 1`, i.e. any reactivation fee charge ever on the transfer. On a transfer with an earlier paid reactivation (possible on Express Plus, max_reactivations 2) the binding would already sit on the bundle tier at the opening while the edge's condition is unmet. Bites only on such a world; checked per task.

Verdict: PASS (two observations).

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength = condition):

- A: "Paloma's shortfall credit is fixed only after the error notice carries the customer's remedy choice between a refund and a re-issue of the shortfall." — "only after"; state = a remedy choice recorded on the notice (cash_cases cash_remedy_chosen answering the notice; `find_cash_cases(related_case_id=...)` is described as returning "the remedy the customer chose"); no tool/id; strength matches. Writes of this difficulty that bring the state about: only choose_shortfall_reissue_92bb83b1 (no refund-choice tool exists in this module). Derivation: credit waits on a remedy choice on the notice -> cash_ext_shortfall_reissue_window's rule "the choice is the customer's own, and it is recorded on the notice together with the re-issue" -> the customer's re-issue choice, handed to the customer. Single reading. PASS.
- B: "An expired pickup is not made collectable again until the transfer's ledger carries the reactivation fee charge numbered with that reactivation's number." — "not ... until"; state = a ledger fee charge (record words "reactivation fee charge"); no tool. Only pay_reactivation_fee_6d9bfacd writes `fee_type reactivation_fee`. Derivation: cash_ext_reactivation_fee's rule "paid by the customer's own card authorisation in the app, as one reactivation fee charge numbered with the reactivation it pays for (the transfer's reactivation count plus one)". Single reading. PASS.
- C: "On a pickup that has expired, a name-correction fee is fixed only after the transfer's ledger carries the reactivation fee charge for the reactivation that pickup awaits." — "only after"; same state and same single write as B. PASS.
- D: "On a pickup that has expired, the days a name correction adds to the pickup window are fixed only after the pickup stands reactivated, with its reactivation count raised and its last day of collection no earlier than the day of the correction." — "only after"; state = status/reactivation count/last day; only reactivate_expired_pickup_d4e94bda raises reactivation_count (choose_shortfall_reissue does not touch it and applies to paid_out). Derivation via cash_ext_reactivation_window's rule. PASS.
- E: "A name correction beyond the free corrections is not recorded until the transfer's ledger carries the name-correction fee charge numbered with that correction's number." — "not ... until"; only pay_name_correction_fee_e426b8ef writes `fee_type name_correction_fee`. Derivation via cash_ext_correction_fee's rule ("as one name-correction fee charge numbered with the correction it pays for"). PASS.
- No depended-on rule restates the blocked sentence; no rule carries a second wording, a tool name or a policy id.
- Undeclared orders: extended rules state no cross-problem order beyond A-E. Base `cash_evt_name_correction` states "an expired pickup must first be reactivated" (a base sentence carrying a cross-problem order); the correction tree's extended rule carries its own sentence D for that edge, so the tree does not rest on the base sentence -> observation S-1 only. Base `cash_evt_error_resolution` "A remedy can be chosen only after a decision of error_found on that notice" orders against a system write (the decision), not an extended problem -> no edge, no finding.

Verdict: PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (quantity that is finally scored):

- cash_ext_shortfall_reissue_window vs cash_evt_availability_and_holds: "pickup_expiry_date is available_date plus pickup_window_days" -> declared superseded for a re-issue of a shortfall. Remaining sentences (refusal recording, refused-pickup hold, RFI, hold release with fresh window) untouched by the re-issue. vs cash_evt_error_resolution: notice window, one open notice per type, decision, fee refund on error_found, "remedy only after error_found", "re-issue made available within reissue_business_days" — all followed. No undeclared override.
- cash_ext_shortfall_credit vs cash_evt_error_resolution: "For incorrect_amount Paloma credits the shortfall (credit_reason incorrect_amount_shortfall)" -> declared superseded ("Beyond that standard amount ..."); the standard sentence of the extended rule reproduces the base amount (the shortfall), so base's value is the extended baseline, not a second answer. Fee refund on error_found and the customer's remedy choice inherited. No anonymous intermediate, 0/1 multiplier or dropped branch found (the uplift's zero tier leaves the shortfall as is; the refund-uplift tier is reachable via refund_shortfall).
- cash_ext_reactivation_fee vs cash_evt_expiry_and_reactivation: "carries reactivation_fee_usd as fee_type reactivation_fee with fee_seq equal to the new reactivation_count when that fee is above 0.00" -> declared superseded. Note the replaced text drops "when that fee is above 0.00": a 0.00 charge row is now written when two out-of-cash refusals waive the fee (network share 0), which B's gate requires; internally consistent (observation O-3). vs cash_evt_pricing / cash_evt_name_correction: no sentence of either governs the reactivation fee; nothing overridden.
- cash_ext_reactivation_window vs cash_evt_expiry_and_reactivation: "Reactivation sets available_date to the reactivation date and pickup_expiry_date to that date plus pickup_window_days," -> declared superseded. Inherited: reactivation window (30/45/15 days from expired_date, inclusive), max_reactivations, same Pickup Number/rate/amount, count +1.
- cash_ext_correction_fee vs cash_evt_name_correction: "The first free_name_corrections corrections are free and each later one carries name_correction_fee_usd ..." -> declared superseded; the extended rule keeps "beyond the tier's free corrections", so the free count is retained. Other sentences inherited.
- cash_ext_correction_extension vs cash_evt_name_correction: the character-distance sentence (accents now ignored) and "the Pickup Number and pickup window do not change." -> both declared superseded. Inherited: spelling only, correctable status ("an expired pickup must first be reactivated"), max_name_corrections including the new one, recorded exactly as given, saved recipient untouched.

Every conflict found is named in `overwrite`; merged semantics unique. PASS (consequences, if any, per task file).

### factor_ladders

| Policy | Factor | Label | Ladder (tiers incl. fall-through) | Multi-source | Cross-difficulty | Label honest? |
| --- | --- | --- | --- | --- | --- | --- |
| shortfall_reissue_window | window_anchor | method | keep days left / days left + 15 / full tier window afresh | no | — | yes: tier 3 computes from the tier window counted afresh, tiers 1-2 from the original last day — a different algorithm |
| | network_days | parameter | 7 / 3 / 0 | no | — | yes |
| | loyalty_days | parameter | 10 / 5 / 0 | no | labelled rewards (O-1) | yes |
| | tenure_days | parameter | 7 / 3 / 0 | no (level and opened_date are two fields of one sender_accounts row) | account (sender_verification_and_limits) | yes |
| shortfall_credit | shortfall_uplift | parameter | 8 / 4 / 0 | yes (remedy-choice case row AND payout ledger row's rate vs the transfer's rate) | — | yes |
| | finding_delay | method | per-day accrual / flat / none | no | — | yes: per-day product vs flat amount are different computations |
| | loyalty_courtesy | parameter | 3.00 / 1.50 / 0 | no | rewards (O-1) | yes |
| | multiproduct_courtesy | parameter | 2.00 / 1.00 / 0 | no | bank (bank_deposit_transfers) | yes |
| | prompt_notice | parameter | 1.00 / 0.50 / 0 | no | — | yes |
| reactivation_fee | reactivation_network_share | parameter | 0 / 60 / 100 % | no | — | yes |
| | reactivation_lateness | **method** | x1.4 / x1.2 / x1 ("charged as it stands") | no | — | **no** — see F-1 |
| | reactivation_loyalty_discount | parameter | 1.00 / 0.50 / 0 | no | rewards (O-1) | yes |
| | reactivation_tenure_discount | parameter | 0.50 / 0.25 / 0 | no | account | yes |
| | reactivation_principal_relief | parameter | 0.30 / 0.15 / 0 | no | — | yes |
| reactivation_window | reactivated_lateness_base | **method** | ceil(W x 0.5) / ceil(W x 0.75) / W | no | — | **no** — see F-1 |
| | reactivated_network_days | parameter | 7 / 4 / 0 | no | — | yes |
| | reactivated_loyalty_days | parameter | 4 / 2 / 0 | no | rewards (O-1) | yes |
| | reactivated_tenure_days | parameter | 2 / 1 / 0 | no | account | yes |
| | reactivated_correction_days | parameter | 2 / 1 / 0 | no | — | yes |
| | reactivated_principal_days | parameter | 2 / 1 / 0 | no | — | yes |
| correction_fee | correction_bundle_share | parameter | 50 / 75 / 100 % | yes (ledger reactivation charge AND cases refusal) | — | yes |
| | correction_lateness | **method** | x1.2 / x1.1 / x1 ("charged as it stands") | no | — | **no** — see F-1 |
| | correction_loyalty_discount | parameter | 0.75 / 0.40 / 0 | no | rewards (O-1) | yes |
| | correction_wallet_discount | parameter | 0.60 / 0.30 / 0 | no | wallet (mobile_wallet_transfers) | yes |
| correction_extension | correction_gap_multiplier | **method** | ceil(gap x 1.5) / ceil(gap x 1.25) / gap | no | — | **no** — see F-1 |
| | correction_history_days | parameter | 21 / 14 / 0 | no | — | yes |
| | correction_loyalty_days | parameter | 10 / 5 / 0 | no | rewards (O-1) | yes |
| | correction_tenure_days | parameter | 6 / 3 / 0 | no | account | yes |
| | correction_waiting_days | parameter | 7 / 3 / 0 | no | — | yes |

Structure checks:

- Factor counts 4 / 5 / 5 / 6 / 4 / 5 — within 4..6. `parameter` counts >= 2 everywhere. Every ladder has 3 pairwise-disjoint tiers, the fall-through counted, all stated in the rule and implemented in compute; no two tiers of one ladder select the same value or method; every `decides` is an input binding (never `result`); binding sets per policy are disjoint; every factor's `baseline` equals its fall-through tier and the policy's `baseline.rule` (full tier window / standard shortfall / full fee / no added days).
- Honest `method` count after the label test: shortfall_reissue_window 1, shortfall_credit 1, **reactivation_fee 0, reactivation_window 0, correction_fee 0, correction_extension 0** (F-1).
- Multi-source factors: shortfall_uplift (shortfall component), correction_bundle_share (correction component). Every component therefore holds one.
- Cross-difficulty factors: account (tenure, four policies), bank (multiproduct), wallet (wallet discount). Every component holds at least one (shortfall: bank, account; correction: account, wallet).
- Ladder realism: conditions are ones a remittance business plausibly weighs (cash-out refusals at the agent network, loyalty tier, tenure, lateness, principal, investigation delay, notice promptness, cross-product activity); no condition holds of every customer reaching its write; no fall-through value is a treatment the business would not publish (each is the plain tier fee/window). Observation O-2 below on the tenure ladder's shape.

### findings

**F-1 — SOURCE-FACTOR RED (charter-global structure; bears on task 1 only).**

- Symptom: four factors labelled `effect: method` select only a number substituted into one unchanged formula.
- Root cause: the "method" tiers are multipliers/fractions, i.e. parameters.
- Evidence (verbatim):
  - cash_ext_reactivation_fee `shared_fee: "RND(P('reactivation_fee_usd') * network_share_pct / 100 * lateness_multiplier, 2)"`, `lateness_multiplier: "K('late_long_multiplier') if days_since_expiry > K('late_long_days') else (K('late_mid_multiplier') if days_since_expiry >= K('late_mid_days') else 1)"`; ladder methods "the shared fee is multiplied by the long lateness multiplier" / "... by the middle lateness multiplier" / "the shared fee is charged as it stands" (= multiplied by 1).
  - cash_ext_correction_fee `shared_fee: "RND(P('name_correction_fee_usd') * bundle_share_pct / 100 * correction_multiplier, 2)"`, `correction_multiplier` 1.2 / 1.1 / 1; ladder "multiplied by the long ... multiplier" / "... middle ..." / "charged as it stands".
  - cash_ext_reactivation_window `reactivated_base: "int(-((-P('pickup_window_days') * K('late_long_fraction')) // 1)) if ... else (int(-((-P('pickup_window_days') * K('late_mid_fraction')) // 1)) if ... else P('pickup_window_days'))"` — every tier is ceil(W x f) with f in {0.5, 0.75, 1} (ceil(W x 1) = W for integer W).
  - cash_ext_correction_extension `result: "int(-((-(gap * gap_multiplier)) // 1))"`, `gap_multiplier` 1.5 / 1.25 / 1; ladder "converted at the two-refusal multiplier and rounded up" / "... one-refusal ..." / "the gap is taken as it is" (= ceil(gap x 1) for integer gap).
- Demonstrated consequence: for each of the four, the three tiers are one expression evaluated with a different constant, exactly the shape the skill names "a factor labelled method whose tiers only substitute a different number into the same formula". Counting only honest labels, each of these four computations has 0 `method` factors against the floor of 1. The per-task consequence (task 1's four computations all fall below the floor) is demonstrated in `1.md`.
- Affected artifact: `cash.extended.yaml` -> `extended_policies[cash_ext_reactivation_fee].factors[reactivation_lateness]`, `[cash_ext_reactivation_window].factors[reactivated_lateness_base]`, `[cash_ext_correction_fee].factors[correction_lateness]`, `[cash_ext_correction_extension].factors[correction_gap_multiplier]`.
- Relation to previous revisions: first audit of this difficulty.

**Observations (no demonstrated consequence; not grounds for rework under this skill):**

- O-1: four `factors[].cross_difficulty: rewards` labels name a category no difficulty claims (`blueprint.yaml` difficulties claim account, bank, cash, wallet, business). The cross-difficulty requirement is met in both components through account/bank/wallet factors, so nothing hinges on the label.
- O-2: the tenure ladder (four policies) is non-monotonic in level: e.g. a Paloma Enhanced account open 12-23 months (12-35 in the re-issue window) gets nothing while a Paloma Verified account open 12 months gets the middle tier, and Paloma Starter never qualifies. Plausible as a published level-and-tenure scheme; not shown unreal.
- O-3: reactivation fee may be booked as a 0.00 charge (two out-of-cash refusals), required by edge B's gate; the base "when that fee is above 0.00" is superseded, so consistent.
- P-1, P-2: see prerequisite_graph.
- S-1: base `cash_evt_name_correction` "an expired pickup must first be reactivated" states a cross-problem order; the extended sentence D carries the edge, so it grounds nothing on its own.
- E-1: replay row for 0.json absent from the gate snapshot (see charter_global_frozen).

## closing_checklist

Written after both reveals (2026-10-04T16:40:27Z onward). **The difficulty does not close**: task 1 is SOURCE-FACTOR RED, so the "all four relationships PASS for every task" precondition of Step 4 fails. Item by item, as it stands:

- Audit files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first revision (no older revisions). Comparison verdicts: task 0 PASS; task 1 SOURCE-FACTOR RED.
- Coverage and scopes: `charter_scope` of task 0 = {cash_ext_shortfall_reissue_window, cash_ext_shortfall_credit}, task 1 = {cash_ext_reactivation_fee, cash_ext_reactivation_window, cash_ext_correction_fee, cash_ext_correction_extension} — equal to the two graph components derived pre-reveal (§policy_conflict_scan); pairwise disjoint, jointly all six extended policies; each scope spans its whole tree. Task tools and GT closed (every GT write is a tool of its own scope); uuid8s independent (§action_binding_and_uuids). — holds.
- Trees: task 0 one prerequisite problem, 1 value_input edge, one user write; task 1 three prerequisite problems, 2 value_input edges, two user writes; both acyclic; the difficulty's five edges form a DAG with no cross-task reference. — holds.
- Factors: every computation has a self-sufficient baseline giving a definite number different from gold, 4-6 factors with >= 2 parameter, every factor bearing weight on its world, a multi-source and a cross-difficulty factor in each task — holds; **>= 1 honest `method` factor per computation — fails for all four computations of task 1 (F-1 / `1.md` T1-F1)**.
- Instantiation-stage gates on a final form: not re-run — no final form exists while F-1 stands; the gate snapshot in the brief is the only gate evidence (observation E-1 on its replay section).

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-04 from 17:16Z, before any round-2 GT field was opened. Nothing in this section derives from a round-2 GT field.
- Inputs: `cash.extended.yaml` sha256 295ebc623d577fbb94a9046deb727390806e4cc0c3fb7a9087c32a265a40c96d (**changed** from 647e1c87…85ed6 → every charter-global section is re-derived in full below); `task_tools.py` 64510a2f…f39f0 (unchanged → tool-module conclusions carried forward on that hash, re-read nonetheless). Masked views re-verified against VIEW_MANIFEST: tasks/0.json view e2c170ff…fb88 and tasks/1.json view eb5e55a8…8d04c are byte-identical to round 1. Note: the manifest shows **both** task source files changed (0.json source dcd378bd… → 93da2ab5…, 1.json 374efe58… → ce2421d2…); the brief said only 1.json's masked fields changed.
- No copy of the round-1 charter survives (the view was rebuilt in place), so the change set was established by re-reading the whole extended section against the round-1 text quoted in the sections above, not by a mechanical diff.
- Base section: `diff` of lines 1-1391 against `blueprint/products/cash.yaml` → identical.
- Gate snapshot r2 (`/tmp/erl0030_gates/cash_pickup_transfers.r2.txt`): all gates exit 0; the replay section now prints rows for both tasks (`0.json 14 … 38 38 True`, `1.json 18 … 47 47 True`) → E-1 resolved.
- contamination_disclosure (revision 2): this auditor revealed and read the round-1 GT of both tasks (values, orders, factor_sensitivity, design_rationale). It is in context for this round. Round-2 blind derivations are recomputed from the round-2 charter and the unchanged views; wherever a round-2 figure equals a round-1 GT figure, that is because the inputs did not change, and the file says so.

### change set found (re-read)

| Policy | Changed in round 2 |
| --- | --- |
| cash_ext_shortfall_reissue_window | loyalty_days `cross_difficulty` rewards → null. Rule, compute, ladders unchanged. |
| cash_ext_shortfall_credit | edge A `effect` rewritten in general form; loyalty_courtesy `cross_difficulty` rewards → null. Rule, compute, ladders unchanged. |
| cash_ext_reactivation_fee | lateness multiplier replaced by an additive **reactivation lateness charge** (per-day 0.05 above 21 days / flat 0.50 for 8-21 / none); `shared_fee` no longer multiplied; new sentence "a fee that works out at zero is still booked as a charge of zero"; overwrite `replaced_by` updated; factor renamed `reactivation_lateness_charge`; loyalty `cross_difficulty` → null. |
| cash_ext_reactivation_window | window base now: tier window less (days late − 7 grace) above 21 days / less 7 flat days for 8-21 / full window; params `late_grace_days 7`, `late_flat_days 7` replace the fractions; loyalty `cross_difficulty` → null. |
| cash_ext_correction_fee | lateness multiplier replaced by an additive **correction lateness charge** (0.20 per started week beyond 45 days / flat 0.25 for 15-45 / none); edge C `condition` and `effect` rewritten; factor renamed `correction_lateness_charge`; loyalty `cross_difficulty` → null. |
| cash_ext_correction_extension | gap multiplier removed; new factor `correction_gap_method` decides `gap` directly: ≥2 ID-mismatch refusals → max(7, guarantee − days left); exactly 1 → max(0, guarantee − (days left − 1)); none → max(0, guarantee − days left); `result` = int(gap); loyalty `cross_difficulty` → null. |

### policy_conflict_scan (revision 2)

Re-run in full. Subjects, triggers, time anchors, cross-category reads and terminal states are those of round 1. The rework changed amounts and windows inside the same subjects and added no new subject, anchor or read. Scopes are unchanged: two graph components, disjoint and jointly complete. No conflict.

### rule_compute_equivalence (revision 2)

- Unchanged policies (shortfall pair): compute and compute_basis re-read; equivalent as in round 1.
- cash_ext_reactivation_fee: `shared_fee: "RND(P('reactivation_fee_usd') * network_share_pct / 100, 2)"` ⇐ "The network-shared fee is the tier's reactivation fee times the network share, rounded half up to the cent."; `lateness_charge` three branches ⇐ "when more than the long lateness days have passed, it accrues by the day, as those days times the per-day lateness charge, rounded half up to the cent; when from the middle lateness days up to the long lateness days have passed, it is the flat lateness charge …; and when fewer … no lateness charge is worked out."; `result` RND(MX(0, shared + lateness − three discounts)) ⇐ "The lateness charge is added to the network-shared fee, the three discounts are taken off that sum together, and the result is rounded" + "never below zero". Equivalent.
- cash_ext_reactivation_window: `reactivated_base` `P − (days − K('late_grace_days'))` / `P − K('late_flat_days')` / `P` ⇐ "the tier window is shortened by the day, one day for every day late beyond the grace days; … shortened by the flat lateness days …; … the full tier window is given." Equivalent. No negative base is reachable: tier 1 needs more than 21 days, and the base reactivation windows (30 / 45 / 30 days, Large Amount 15) cap the days, so the base is at least 30 − 23 = 7.
- cash_ext_correction_fee: `lateness_charge` ceil((days − 45) / 7) × 0.20 / 0.25 / 0 ⇐ "accrues by the started week, as the number of started weeks beyond the long correction lateness days times the per-week lateness charge; … flat …; … none". `result` ⇐ the summing sentence + "never below zero". Equivalent.
- cash_ext_correction_extension: `gap` three branches ⇐ "after two or more such refusals the gap is the guarantee less the days left, but never less than the two-refusal minimum days; after exactly one such refusal the last day of collection is not counted among the days left either, so the gap is the guarantee less one day fewer than the days left; and with no such refusal the gap is the guarantee less the days left." plus "in whole days and never below zero". `result: int(gap)`. Equivalent.
- Every ladder tier is stated in the rule and implemented in compute, and every branch of each `decides` binding is a stated tier. PASS.

### action_binding_and_uuids (revision 2)

`task_tools.py` hash unchanged; `(target_tool, computes)` pairs unchanged. Carried forward: PASS.

### prerequisite_graph (revision 2)

- Edges A-E: `problem`, `kind`, `gate`, `form`, `resolved_by` unchanged. Every `policy_source` is still found verbatim in its own rule. The graph is acyclic.
- Edge A `effect` now reads "the uplift binding leaves no uplift and, when the payout recorded a rate below the disclosed exchange rate, takes the re-issue uplift or the refund uplift matching that choice". This is general and agrees with the rule. Edge C `effect` now reads "takes the ID-mismatch bundle share when a name-mismatch refusal is on record, or the plain bundle share when none is". Also general and in agreement. **P-1 closed.**
- Edge C `condition` now reads "at least one cash_fee_charged row … with fee_type reactivation_fee; on an expired pickup awaiting its reactivation this is the charge with fee_seq equal to the transfer's reactivation_count plus one". This equals the binding (`COUNT ≥ 1`), and within the sentence's own scope ("On a pickup that has expired …") it is no broader than the sentence. **P-2 closed.**
- PASS.

### prerequisite_sentences (revision 2)

All five sentences are unchanged, and each is still in its own blocked rule. The four-point test, the single resolving write and the derivations are as in round 1. No new cross-problem order appears in any reworked rule: the new sentences concern amounts and day counts only. S-1 is unchanged (the base sentence; the reworker did not act on it, as claimed). PASS.

### override_declarations (revision 2)

- cash_ext_reactivation_fee: the superseded base sentence is unchanged. The new `replaced_by` names the new composition. The new zero-charge sentence is consistent with the superseded "when that fee is above 0.00" and with edge B's gate. This addresses the substance of O-3, though the reworker listed O-3 as left unchanged.
- cash_ext_reactivation_window, cash_ext_correction_fee, cash_ext_correction_extension: the superseded clauses are unchanged. The replacements describe the new composition. The inherited base sentences are as in round 1.
- No undeclared override. PASS.

### factor_ladders (revision 2)

Label test re-applied to every `method` factor:

| Policy | Method factor | Tiers | Honest? |
| --- | --- | --- | --- |
| shortfall_reissue_window | window_anchor | keep days left / days left + 15 / full window afresh | yes (unchanged) |
| shortfall_credit | finding_delay | days × 0.10 / flat 0.75 / none | yes (unchanged) |
| reactivation_fee | reactivation_lateness_charge | days × 0.05 / flat 0.50 / none | **yes**. The per-day tier depends on the day count and the flat tier does not, so the tiers compute differently (same shape as finding_delay). |
| reactivation_window | reactivated_lateness_base | W − (days − 7) / W − 7 / W | **yes**. Day-by-day shortening against a flat shortening. |
| correction_fee | correction_lateness_charge | ceil((days − 45)/7) × 0.20 / flat 0.25 / none | **yes**. Per-started-week accrual against a flat charge. |
| correction_extension | correction_gap_method | max(7, g − L) / max(0, g − L + 1) / max(0, g − L) | **no**. See F-1 (revision 2). |

Other structure checks:
- Factor counts are 4 / 5 / 5 / 6 / 4 / 5.
- Every policy has at least 2 `parameter` factors.
- Every ladder has 3 disjoint tiers, all stated in the rule, with no two tiers giving the same outcome.
- Every baseline equals its fall-through tier and the policy's `baseline.rule`.
- Multi-source factors: shortfall_uplift and correction_bundle_share. Tenure remains single-record.
- Cross-difficulty factors: account (×4), bank, wallet. The rewards factors are now `cross_difficulty: null`, so **O-1 is closed**.

New observation O-4 (correction lateness charge): the ladder is not monotone in lateness. A correction 15-45 days after the disclosed date pays the flat 0.25, but one 46-52 days after pays ceil(1..7/7) × 0.20 = 0.20, so it pays less for being later. It returns to 0.40 from 53 days. The tiers are distinct, and each tier on its own is a treatment a business could publish. This is not shown to be unreal, and it does not bite on task 1 (56 days → 0.40).

O-2 (tenure shape) and S-1 are unchanged, as the reworker stated.

### findings (revision 2)

**F-1 (revision 2): SOURCE-FACTOR RED. Partly closed; still open for cash_ext_correction_extension. Bears on task 1.**
- Closed: reactivation_fee, reactivation_window and correction_fee now each carry a genuine `method` factor (per-unit accrual against a flat amount against none).
- Still open: `correction_gap_method`.
  - Evidence: `gap: "MX(K('two_refusal_min_days'), guarantee - days_left) if id_mismatch_refusals >= 2 else (MX(0, guarantee - (days_left - 1)) if id_mismatch_refusals == 1 else MX(0, guarantee - days_left))"`, with ladder methods "selection: the larger of the guarantee less the days left and the two-refusal minimum days" / "day count: the last day of collection is not counted among the days left, so the gap is the guarantee less one day fewer than the days left (never below zero)" / "the gap is the guarantee less the days left as counted (never below zero)".
  - All three tiers are the one expression max(F, guarantee − days left + o). Only the constants change: (F, o) = (7, 0) / (0, 1) / (0, 0). Tier 2 is "one more day" relabelled as a counting convention: for every input with guarantee ≥ days left it returns exactly tier 3 + 1. Tier 1 is a floor of 7 in place of a floor of 0: for every input with guarantee − days left ≥ 7 it returns exactly tier 3.
  - The tiers substitute numbers (a threshold and a one-day offset) into one unchanged formula. This is the shape the skill names as a mislabelled `method`.
  - The conditions do not rescue it as a "method the business genuinely varies". No remittance business changes its day-counting convention according to how many times the recipient's ID was refused. What it would do is grant one more day, which is a parameter.
  - Consequence: cash_ext_correction_extension still has 0 honest `method` factors against a floor of 1. Demonstrated on task 1's world in `1.md` revision_2.
  - Affected: `cash.extended.yaml` extended_policies[cash_ext_correction_extension].factors[correction_gap_method] and the rule's gap sentence.

Status of the round-1 items:

| Item | Status |
| --- | --- |
| F-1 | partly closed (open for correction_extension) |
| O-1 | closed |
| O-2 | unchanged |
| O-3 | addressed in substance (zero-charge sentence added) |
| P-1 | closed |
| P-2 | closed |
| S-1 | unchanged |
| E-1 | resolved by the r2 snapshot |

New in this round: O-4 (observation).

### closing_checklist (revision 2)

Written after the round-2 reveals (17:16:52Z). **The difficulty still does not close.**

| Item | Status |
| --- | --- |
| Task verdicts | task 0 PASS; task 1 SOURCE-FACTOR RED (correction_extension method floor, F-1 revision 2) |
| Coverage and scopes | unchanged and holding: the two charter_scope sets are disjoint and jointly complete; tools and GT closed; uuid8s independent |
| Trees | unchanged and holding: 1 and 3 prerequisite problems; 1 and 2 value_input edges; user writes in both; difficulty-wide DAG |
| Factors | every computation has a definite baseline that differs from gold. Factor counts are 4-6 with at least 2 parameter each. Each task has a multi-source factor and a cross-difficulty factor. Every factor bears weight. **At least 1 honest method factor per computation fails for cash_ext_correction_extension (task 1).** |
| Gates | the r2 snapshot is all green (exit 0), and the replay rows now show both tasks. Not re-run by the auditor. No final form exists while F-1 stands. |

Round-1 items:

| Item | Status |
| --- | --- |
| F-1 / T1-F1 | 3 of 4 closed, 1 open |
| O-1, P-1, P-2, T0-O1, T1-O1 | closed |
| O-3 | addressed |
| E-1 | resolved |
| O-2, S-1 | unchanged (observations) |

New: O-4 (observation). Nothing regressed.

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-04 from 17:28Z, before any round-3 GT field was opened.
- Inputs:
  - `cash.extended.yaml` f6ca632224651f63a90123fa0ec724746aef200be29bf26d7d173a85a4355b7b, **changed**. The charter-global sections are re-derived below against a mechanical `diff` with the archived round-2 view `/tmp/erl0030_views/archive/cash_pickup_transfers.r1/cash.extended.yaml` (sha256 295ebc62…0c96d = the round-2 charter).
  - `task_tools.py` 64510a2f…f39f0, unchanged (carried forward).
  - Task views e2c170ff…fb88 and eb5e55a8…8d04c, unchanged.
- Manifest note: **both** task source files changed again (0.json 93da2ab5… → d3a27428…; 1.json ce2421d2… → 239984ab…), although the brief says task 0 was untouched. This is checked after reveal.
- Base section (lines 1-1391) is identical to `blueprint/products/cash.yaml`.
- Gate snapshot r3: all exit 0, and the replay rows show both tasks.
- contamination_disclosure: the round-1 and round-2 GT of both tasks are in this auditor's context. The round-3 figures are recomputed from the round-3 charter.

### change set (mechanical diff, round-2 → round-3 charter)

1. **cash_ext_correction_fee** (acting on O-4): `late_per_week_usd` 0.20 → 0.05, and the per-week tier now counts started weeks beyond the **middle** (15) days instead of the long (45) days. The rule sentence, compute, compute_basis and ladder text were changed in step.
2. **cash_ext_correction_extension** (acting on F-1 rev2):
   - `two_refusal_min_days` removed;
   - the "top the days left up to the guarantee" sentence was rewritten;
   - the gap sentence was replaced by a guarantee-anchor sentence;
   - `gap` is now: ≥2 ID refusals → guarantee + max(0, −days left) + days since the most recent ID refusal; exactly 1 → guarantee + max(0, −days left); none → max(0, guarantee − days left);
   - the factor `correction_gap_method` was replaced by `correction_guarantee_anchor`;
   - edge D's `effect` text was rewritten.
3. Nothing else changed. The shortfall pair, reactivation fee and reactivation window are byte-identical to round 2.

### policy_conflict_scan / override_declarations (revision 3)

- No new subject, anchor, read or terminal state.
- The extension's overwrites are unchanged. Its replacement text ("the last day of collection moves later by the correction extension days") still covers the new composition.
- PASS.

### rule_compute_equivalence (revision 3)

- **correction_fee** `lateness_charge` = RND(ceil((days − 15)/7) × 0.05) above 45 days. This matches "accrues by the started week, as the number of started weeks beyond the middle correction lateness days times the per-week lateness charge". Equivalent.
- **correction_extension**, extension = new last day − current last day:
  - Exactly one refusal: "the guarantee runs from the later of the current last day of collection and the day of the correction, so the extension is the whole guarantee plus any days by which the last day of collection has already passed" gives max(last, today) + G − last = G + max(0, −L). This equals the compute.
  - Two or more: the same plus "the days lost since the most recent such refusal, counted from that refusal to the day of the correction with the refusal day not counted". This equals `DAYS(LATEST(… id_name_mismatch), NOW)`.
  - None: "only tops the days left up to the guarantee and is zero when the days left already reach it" gives max(0, G − L). Equivalent.
  - `result: int(gap)` matches "in whole days and never below zero". Every tier is ≥ 0.
- PASS.

### prerequisite_graph / prerequisite_sentences (revision 3)

- The sentences of edges A-E and their `problem`, `kind`, `gate`, `form` and `resolved_by` are unchanged. They are still verbatim in their own rules, and the graph is still acyclic.
- Edge D's new `effect` is general and true.
- P-1 and P-2 remain closed.
- **New structural note N-1** (its consequence is per task):
  - Edge D is `value_input` on `days_left`. Under the new anchor tiers that apply whenever one or more ID-mismatch refusal is on record, `days_left` enters the extension only as max(0, −days left).
  - Edge D's own state-form sentence requires, before the extension is fixed, that the pickup stand reactivated "with … its last day of collection no earlier than the day of the correction", i.e. days left ≥ 0.
  - So, once the edge is resolved, that term is 0 for every reactivated window. The reactivation's computed window no longer reaches the extension; only the fact of reactivation does.
  - Under the no-refusal tier the edge still carries a value (max(0, G − L)).
  - This was not the case in rounds 1-2: round 1's ceil((G − L) × m) and round 2's max(0, G − (L − 1)) both read L.

### factor_ladders (revision 3)

| Policy | Method factor | Tiers | Honest? |
| --- | --- | --- | --- |
| correction_fee | correction_lateness_charge | ceil((d − 15)/7) × 0.05 / flat 0.25 / none | yes. Per-started-week accrual against a flat charge. Now monotone: 0.25 for 15-50 days, 0.30 from 51. |
| correction_extension | correction_guarantee_anchor | G + max(0, −L) + days since the latest ID refusal / G + max(0, −L) / max(0, G − L) | **yes**. The no-refusal tier subtracts the days left (a top-up), while the refusal tiers add the whole guarantee from the later anchor, ignoring the days left when they are positive. The two-refusal tier also reads a new input, the date of the latest refusal. The tiers change which inputs the extension depends on and how; this is not a constant swapped into one expression. The replacement is genuine, not a relabel. |
| others | unchanged from revision 2 | | yes |

- Factor counts and parameter counts are unchanged.
- The baseline of the new factor is `MX(0, guarantee - days_left)`, which is its fall-through and consistent with `baseline.rule` ("adds no days": guarantee 0 gives 0).
- Ladder realism: granting a larger extension, anchored later, after a recipient has been turned away for the name is a plausible published courtesy.
- O-4 closed (the lateness charge is monotone).

### findings (revision 3)

- **F-1 (rev2): closed.** Every computation now has an honest `method` factor.
- **N-1 → SOURCE-CHAIN RED, demonstrated on task 1** (see `1.md` revision_3). This is a regression introduced by this round's rework, and it bears on task 1's tree:
  - Its consequence: edge D no longer carries a value into a calculation on a world with an ID-mismatch refusal.
  - Task 1 is such a world by construction (the recipient was turned away for the name).
  - Edge D therefore functions as a state gate there, and task 1's tree falls below the value_input floor.
- Item status:

| Item | Status |
| --- | --- |
| O-1, P-1, P-2, T0-O1, T1-O1, E-1 | remain closed (not reopened) |
| O-3 | remains addressed |
| O-4 | closed |
| O-2, S-1 | unchanged observations |

### closing_checklist (revision 3)

Written after the round-3 reveals (17:29:16Z). **The difficulty still does not close.**

| Item | Status |
| --- | --- |
| Task verdicts | task 0 PASS; task 1 **SOURCE-CHAIN RED** (T1-C1, from N-1; new this round), otherwise PASS |
| Coverage, scopes, tools, uuid8s | unchanged and holding |
| Trees | task 0 holds. Task 1 has 3 prerequisite problems and 2 declared value_input edges, but only 1 carries a value in substance. Edge D reduces to a state gate under the refusal tiers of correction_guarantee_anchor. **Floor of 2 fails.** |
| Factors | all computations hold: baselines definite and different from gold; 4-6 factors; at least 2 parameter and at least 1 honest method each; multi-source and cross-difficulty factors per task; every factor bears weight. F-1 is fully closed. |
| Gates | the r3 snapshot is all exit 0, with replay rows for both tasks. Not re-run by the auditor. |

Item tally:

| Item | Status |
| --- | --- |
| F-1 / T1-F1 (all rounds) | closed |
| O-1, O-4, P-1, P-2, T0-O1, T1-O1, E-1 | closed |
| O-3 | addressed |
| O-2, S-1 | unchanged observations |
| N-1 / T1-C1 | new RED |

## revision_4

### charter_global_frozen (revision 4)

- Written 2026-10-04 from 17:33Z, before any round-4 GT field was opened.
- Inputs:
  - `cash.extended.yaml` 60d87bc8ba11dc47d2bea45a21483d98ee1db113f4bfbccd0ae75291e510e4a1 (changed). Diffed mechanically against the archived round-3 view `/tmp/erl0030_views/archive/cash_pickup_transfers.r2/cash.extended.yaml` (f6ca6322…5b7b = the round-3 charter).
  - `task_tools.py` unchanged.
  - Task views unchanged.
- Base section identical to the blueprint.
- Gate snapshot r4: all exit 0, with replay rows for both tasks.
- Manifest: task source hashes 0.json d3a27428… → 03375aa3…; 1.json 239984ab… → 3a981171….
- contamination_disclosure: the GT of rounds 1-3 is in context. The round-4 figures are recomputed from the round-4 charter.

### change set (mechanical diff, round 3 → round 4)

Only **cash_ext_correction_extension** changed:
- the gap sentence of the rule;
- compute `gap`;
- compute_basis (`id_mismatch_refusals`, `gap`);
- edge D's `effect`;
- the factor `correction_guarantee_anchor`, replaced by `correction_extension_method`.

The new `gap`, with top-up T = max(0, guarantee − days left) and days lost D = days from the most recent id_name_mismatch refusal to the correction:

| Refusals | Extension |
| --- | --- |
| ≥ 2 | max(T, D) |
| exactly 1 | T + D |
| none | T |

All other policies are byte-identical to round 3.

### rule_compute_equivalence (revision 4)

- The rule now says: "The top-up is the guarantee less the days left, never below zero; the days lost are the calendar days from the most recent such refusal to the day of the correction, the refusal day not counted. After two or more such refusals the extension is the larger of the top-up and the days lost. After exactly one such refusal the extension is the top-up with the days lost given back on top of it. With no such refusal the extension is the top-up alone …"
- That is `MX(0, guarantee - days_left, DAYS(LATEST(…id_name_mismatch), NOW))`, `MX(0, guarantee - days_left) + DAYS(…)` and `MX(0, guarantee - days_left)`.
- The "most recent such refusal" filter is the id_name_mismatch reason only. Equivalent. PASS.

### prerequisite_graph / prerequisite_sentences (revision 4)

- Sentences, kinds, gates and resolvers are unchanged. The graph is acyclic.
- **N-1 closed.** Every tier now reads `days_left` through T = max(0, G − L), which stays live after the edge is resolved (L ≥ 0). A longer reactivated window lowers the top-up whenever L < G. Edge D carries the window figure again.
- Observation O-6: the new edge-D `effect` says the top-up "shrinks by the length of that window". In general it shrinks by the window plus the days already passed, clipped at 0 (for task 1: from 58 to 10, i.e. by 48, not by the window's 22). The statement is imprecise; nothing reader-facing rests on it.

### factor_ladders (revision 4)

- `correction_extension_method`: the three tiers are max(T, D), T + D and T.
  - The combining operation differs between tiers (larger-of against sum), and the fall-through drops the days-lost input altogether.
  - No single expression with substituted constants yields both max(T, D) and T + D.
  - **Honest method. F-1 stays closed.**
- Observation O-5, ladder shape: the two-refusal tier is never more generous than the one-refusal tier (max(T, D) ≤ T + D, smaller by min(T, D)). A recipient turned away twice gets a shorter extension than one turned away once.
  - There is a conceivable business rationale: repeated ID mismatches are a screening signal, and the base charter already holds payouts after refused_pickups_before_hold refusals. So the auditor cannot show that no business would publish it. Recorded as an observation.
  - Disclosure: the round-2 ladder had the same inversion on a smaller scale (max(7, x) against x + 1), and it was not noted in revision 2.
- Other ladders unchanged. O-4 remains closed (the correction-fee policy is unchanged).

### findings (revision 4)

- N-1 / T1-C1: closed.
- F-1: remains closed.
- Charter-global items: O-1, O-4, P-1, P-2 and E-1 remain closed; O-3 remains addressed; O-2 and S-1 are unchanged.
- New observations: O-5 (refusal-count inversion) and O-6 (edge D effect wording).

### closing_checklist (revision 4)

Written after the round-4 reveals (17:33:59Z).

| Item | Status |
| --- | --- |
| Task verdicts | task 0 PASS; task 1 PASS. All four relationships hold for both. |
| Audit files | one per task plus `_difficulty.md`; revisions 1-4 kept intact and appended in order |
| Coverage and scopes | the two charter_scope sets are disjoint and jointly cover all six extended policies; tools and GT closed; uuid8s independent and unchanged |
| Trees | task 0: 1 prerequisite problem, 1 value edge, user write. Task 1: 3 prerequisite problems, 2 value-carrying edges (C, D), two user writes. The difficulty-wide graph is a DAG. |
| Factors | every computation has a self-sufficient baseline giving a definite number that differs from gold; 4-6 factors with at least 2 parameter and at least 1 honest method; each task has a multi-source factor (shortfall_uplift; correction_bundle_share) and a cross-difficulty factor (bank and account; account and wallet); every factor bears weight on its task's world |
| Gates | the r4 snapshot (`/tmp/erl0030_gates/cash_pickup_transfers.r4.txt`) is all exit 0 on the final form, with replay rows for both tasks. The auditor cites it and did not re-run it. check_traceability is deferred to the KB stage. |

Open observations (not grounds for rework): O-2 (tenure ladder shape), O-5 (refusal-count inversion in the extension method), O-6 (edge D effect wording), S-1 (base cross-problem order sentence).

**The difficulty passes the source-layer audit at revision 4.**
