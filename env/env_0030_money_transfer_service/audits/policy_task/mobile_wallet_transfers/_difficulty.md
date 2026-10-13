# Policy-task audit — mobile_wallet_transfers / charter-global

## charter_global_frozen

- Freeze time: written 2026-10-04 between 16:37Z and 16:43:52Z (file mtime of the last pre-reveal edit, the F-1 upgrade); the first GT reveal ran after 16:44:39Z. This section contains nothing derived from a revealed GT. (Timestamp corrected at 16:46Z: the draft carried estimated clock labels; the mtimes are the authority.)
- Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Inputs and sha256 (verified against the coordinator's VIEW_MANIFEST.txt and against the live files):
  - `wallet.extended.yaml` d5562602b395be27763011385d1864c9e094cb34101466a4181b267ac3edbf8f (view = source)
  - `task_tools.py` ab149dfa2e7920be36fe8c8d9a943501012b11297b678f41e2f905d7cf4e3976 (view = source)
  - blueprint read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/wallet.yaml`, and, for the cross-category reads only, the level table of `products/account.yaml` and the ledger event definitions of `products/bank.yaml` / `products/cash.yaml`, the state lists of `topup.yaml` / `business.yaml`.
  - Evaluator semantics read from `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `RND`, `CPARAM`, `CFIELD`, `XSUM`, `XCOUNT`) — tool code, no GT.
- Permitted: the charter, the tool module, the blueprint, erlbench/, the masked task views (frozen_time, user_scenario, initial_state).
- Masked and unread at the time of writing: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; every `worklog.md`.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl0030_gates/mobile_wallet_transfers.txt`): check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability / check_compute / check_grounding OK, check_cache_diff INFO, check_cross_fire SCOPE OK; check_traceability not run (no KB yet — expected at this stage). Masked views and hashes supplied. Entry conditions met. Note: the replay_tasks block of the snapshot prints a row only for `1.json` (`1.json 15 True True 0 41 41 True`); no row for `0.json` appears in the snapshot text — recorded as observation O-0 below (cannot tell from the snapshot whether task 0 was replayed).
- Base copy check: every top-level key of the base charter (`category` … `policies`) in `wallet.extended.yaml` is equal (parsed-YAML equality) to `blueprint/products/wallet.yaml`. The base copy is verbatim.

### policy_conflict_scan

Extended policies (6), their subjects, computed quantity and tool:

| policy | subject | computes | target_tool | owner |
|---|---|---|---|---|
| wallet_ext_resend_charge | wallet_fee_charged (retry_fee) | amount_usd | charge_resend_fee_8300b1da | agent |
| wallet_ext_resend_credit | wallet_credit_retried, wallet_credit_sent | receive_amount | resend_failed_credit_8d2e2e1a | agent |
| wallet_ext_shortfall_makegood | wallet_paloma_credit (incorrect_amount_shortfall) | amount_usd | book_shortfall_makegood_2311834f | agent |
| wallet_ext_shortfall_recredit | wallet_remedy_chosen (recredit_shortfall), wallet_credit_sent | receive_amount | choose_shortfall_recredit_f54302ef | user |
| wallet_ext_wrong_wallet_funding | wallet_paloma_credit (error_recredit) | amount_usd | fund_wallet_recredit_aebfda78 | agent |
| wallet_ext_wrong_wallet_recredit | wallet_remedy_chosen (recredit), wallet_credit_sent | receive_amount | choose_wallet_recredit_d4ef146e | user |

- Overlapping subjects: `wallet_credit_sent` is a subject of three policies (resend_credit, shortfall_recredit, wrong_wallet_recredit). Their triggers are disjoint on the records: a resend needs `status credit_failed` (base `failed_status`, "A retry or redirect is accepted only while the transfer is credit_failed"); a shortfall re-credit needs an `error_found` decision on an `incorrect_amount` notice; a wrong-wallet re-credit needs an `error_found` decision on a `wrong_wallet_credited` notice. `wallet_paloma_credit` is split by `credit_reason` (incorrect_amount_shortfall vs error_recredit). `wallet_remedy_chosen` is split by `remedy_choice` (recredit_shortfall vs recredit). No two policies reach different conclusions on one record.
- Eligibility / time anchors: every extended policy inherits the base gates (retry window `failed_credit_hold_days` from the date part of `failed_at`; `max_retries`; error notice window; "A remedy can be chosen only after a decision of error_found on that notice"). None is weakened by an extended rule, a tool or a persona.
- Terminal states: resend and both re-credits move the transfer to `processing`, set `released_at` now and `date_available` today, principal held to 0.00 — consistent with base `wallet_credit_retried` (credit_failed→processing; credited→processing).
- Cross-category read boundaries: every read is declared in `cross_category` and matches the other charter's definitions (`bank_funds_received` / `bank_payout_sent` in bank.yaml; `cash_funds_received` / `cash_payout_made` in cash.yaml; `topup_orders.status` delivered in topup.yaml; `business_accounts.status`/`variant_name` in business.yaml; `sender_accounts.variant_name`→`level_number`, `opened_date` in account.yaml, levels Verified Plus = 3, Enhanced = 4).
- Cross-holding gate: `wallet_ext_shortfall_recredit` gates one transfer's re-credit on the status of another transfer of the same customer. Base `wallet_agg_multi_holding` says "Transfers are never combined: a retry, redirect or refund on one transfer never touches another." The gate changes no value on the other transfer, so no two conclusions differ; recorded as observation O-3.
- Scopes: the extended file's own section comments assign resend_charge, resend_credit, shortfall_makegood, shortfall_recredit to task 0 and wrong_wallet_funding, wrong_wallet_recredit to task 1. The two prerequisite graphs (below) are disconnected, so the two trees are pairwise disjoint and together cover all six extended policies (whether `charter_scope` agrees is checked only after the reveal, in the task files).

### rule_compute_equivalence

Mechanical sweep (script over the parsed charter): for all six policies every `compute_basis` quotation is a verbatim substring of the policy's own `rule`; the set of compute binding names equals the set of `compute_basis` keys; every `overwrite.replaced_by` is a verbatim sentence of the extended rule; every sentence of every `baseline.rule` is a verbatim sentence of the rule. Manual sweep, quantity by quantity:

- resend_charge: resend number = COUNT(wallet_credit_sent) ("the number of credits already sent"); charge only above `free_retries`; charge form bands (≥1500 → 0.25 % of principal; 1000–1499.99 → retry_fee_usd + 0.10 % rounded; below → retry_fee_usd); cause share from the latest reversal (0 / 0.80 / 1); account-standing relief (level ≥ 4 and ≥ 24 whole months → 1.00; level = 3 and ≥ 24 months → 0.50; else 0); Bank Deposit relief on `bank_funds_received` in the window (≥ 3000 → 0.30; ≥ 1000 → 0.15; else 0); bounce taper (≥ 3 → 0.70; = 2 → 0.85; else 1); one product rounded half up; collection route (card_funding_fee entry → ×(1+credit_card_fee_pct/100) rounded; pay_by_bank → minus pay_by_bank_fee_discount_usd floor 0; else as is). Each has its quotation; compute adds nothing. Gap: the rule's collection sentence names three funding cases (credit card, pay-by-bank, debit card); the compute's `else` also covers `ach_debit` and `wire` (Economy, Large Amount tiers), for which the rule says nothing — O-4.
- resend_credit: held principal (funds + reversals + Paloma credits − sent − refunds), locked rate `F('fx_rate')`, paid charge = retry_fee entry with `fee_seq` = resend number, paid uplift (≥ retry_fee_usd → 0.20; > 0 → 0.10; else 0), held-from (all bounces provider_unavailable → booked date; ≥ 2 bounces with ≥ 1 recipient-side → date of reversal of attempt 1; else date part of `failed_at`), held-days uplift (≥ 14 → 0.30; ≥ 7 → 0.15), principal uplift (≥ 1500 → 0.10; ≥ 1000 → 0.05), Cash Pickup uplift on `cash_funds_received` in 6 months (≥ 1000 → 0.10; ≥ 300 → 0.05); rate = RND(locked × (1 + Σ/100), 4); amount = RND(held × rate, 2). Two-way equivalent.
- shortfall_makegood: shortfall_local = disclosed `receive_amount` − Σ `receive_amount` of credit_sent; ÷ locked rate unrounded; clock (notice lag ≤ 3 → from date_available; > 30 → from decision date; else from notice date); delay (≥ 10 → 5 %; ≥ 5 → 2.5 %); hardship (medical/education and short share > 2 % → 4 %; family_support and > 2 % → 2 %); tenure (≥ 60 → 3.00; ≥ 36 → 1.50); Top-Up delivered orders in 12 months (≥ 6 → 1.00; ≥ 3 → 0.50); result RND(shortfall_usd × (1 + (delay+hardship)/100) + tenure + topup, 2). Two-way equivalent.
- shortfall_recredit: held principal; base rate (latest credit's `fx_rate_applied` < locked → RND(locked/(1 − margin/100), 4); = locked and its `receive_amount` < disclosed → RND(locked × (1 + 0.5 × margin/100), 4); else locked); margin = tier fx_margin_pct less reduction at/above threshold; level points (≥ 4 → 0.30; = 3 → 0.15); `cash_payout_made` count in 12 months (≥ 4 → 0.20; ≥ 2 → 0.10); `bank_payout_sent` count in 12 months (≥ 6 → 0.20; ≥ 3 → 0.10); size points on held (≥ 25 → 0.20; ≥ 10 → 0.10); rate RND(base × (1+Σ/100), 4); amount RND(held × rate, 2). Two-way equivalent. Note: the "margin the transfer carried" is defined as the tier margin less the reduction, silent on the base `wallet_evt_pricing` promotional margin ("the promotional margin replaces both") — O-5.
- wrong_wallet_funding: misdirected principal = Σ amount_usd of credit_sent; clock (credit_promise_minutes > 0 → date part of released_at; else notice lag ≤ 2 → date_available; else notice date) to the decision date; misdirection (≥ 7 → 2 %; ≥ 4 → 1 %); standing (level ≥ 4 and ≥ 36 months → 5.00; level = 3 and ≥ 36 → 2.50); Bank Deposit `bank_funds_received` in 12 months (≥ 5000 → 1.5 %; ≥ 2000 → 0.75 %); result RND(misdirected × (1 + (misdirect+bank)/100) + standing, 2). Two-way equivalent.
- wrong_wallet_recredit: held principal; investigation days notice→decision (≥ 5 → mid-market implied; ≥ 2 → locked × (1 + 0.5 × margin/100); else locked); purpose points (education/medical and principal ≥ 500 → 0.25; family_support and ≥ 500 → 0.10); business points (active on Growth/Pro/Scale/Enterprise → 0.20; active on Starter/Essentials → 0.10); Top-Up delivered in 6 months (≥ 5 → 0.15; ≥ 3 → 0.08); size on held (≥ 500 → 0.20; ≥ 100 → 0.10). Two-way equivalent. Same promotional-margin silence as above (O-5).
- Conventions common to all: "rounded half up" in the rule vs `RND = round(float(x), n)` (binary/banker's) in the checker — they diverge only at exact half-cent / half-1e-4 ties; checked per task (O-6). "Whole calendar months" = `MONTHS` (month difference, minus one when the day-of-month has not been reached) — matches. "In the last N calendar months" = `_within`: `0 ≤ MONTHS(entry_date, today) < N` (rolling anniversary window); the rule states no counting convention and the prose also admits calendar-month-aligned readings — finding F-1 below. `LATEST` breaks equal-date ties by first row seen; checked per task.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (six distinct tools, table above). Each docstring describes only its own write; the business readings are single.
- Docstring sweep of `task_tools.py` for sequence wording (before, after, first, then, prior, until) and for other tools' names: none found. The module header says "No tool checks eligibility, prerequisites or amounts: the values passed in are booked as given", and the function bodies confirm it: each body only `find`s the transfer row, `create`s its ledger/case row(s) and `update`s the transfer; no branch reads another policy's state, raises, or returns a hint.
- uuid8s: 8300b1da, 8d2e2e1a, 2311834f, f54302ef, aebfda78, d4ef146e — no shared prefix, no shared suffix, no arithmetic progression, no copy-with-new-tail. Nothing indicates batch derivation (independence of generation cannot be proved from the text; no counter-evidence).
- `charge_resend_fee` docstring defines `fee_seq` as "one more than the resends already made on the transfer"; the policy defines the resend number as "the number of credits already sent on the transfer". The two agree whenever every credit after the first was a resend (no redirect or error re-credit on the transfer) — true in task 0's world; recorded as O-8.

### prerequisite_graph

- `prerequisite` filled on all six policies: resend_charge [], shortfall_makegood [], wrong_wallet_funding [] ; resend_credit → [resend_charge]; shortfall_recredit → [shortfall_makegood, resend_credit]; wrong_wallet_recredit → [wrong_wallet_funding].
- Every `problem` is an extended policy id of this file, none a base policy, none self. Graph: resend_charge → resend_credit → shortfall_recredit ← shortfall_makegood; wrong_wallet_funding → wrong_wallet_recredit. Acyclic; two disconnected components.
- Every `policy_source` is a verbatim sentence of the blocked policy's own rule (script check: True ×4).
- `form: state` on all four edges; no `fallback_reason` anywhere — consistent.
- `condition` vs sentence: (1) resend_credit/resend_charge — "for a resend whose number is above free_retries, a wallet_fee_charged entry with fee_type retry_fee and fee_seq equal to that resend's number stands" = "For a resend beyond the tier's free resends … the charge assessed for that resend stands on the transfer's ledger": same scope. (2) shortfall_recredit/makegood — "a wallet_paloma_credit entry with credit_reason incorrect_amount_shortfall stands" = "Paloma's own shortfall credit stands on the transfer's ledger". (3) shortfall_recredit/resend_credit — "no other wallet_transfers row of the same customer with an earlier booked_at and the same wallet_number has status credit_failed" = "no earlier-booked transfer of the same customer addressed to that wallet number stands with a failed credit". (4) wrong_wallet_recredit/funding — "a wallet_paloma_credit entry with credit_reason error_recredit stands" = "Paloma's funding for that re-credit stands". None strengthened or weakened.
- `resolved_by` = the depended-on policy's `target_tool` in all four; each tool body creates exactly the row (or status change) the condition names: charge tool creates `wallet_fee_charged/retry_fee/fee_seq`; makegood tool creates `wallet_paloma_credit/incorrect_amount_shortfall`; resend tool sets `status processing`; funding tool creates `wallet_paloma_credit/error_recredit`.
- `kind`/`gate`: value_input edges name bindings that exist in the blocked compute (`paid_charge`, `held_usd`, `held_usd`); the state_gate edge names `wallet_transfers.status`, which is the gate the prerequisite sentence states (the extended policy has no separate `eligibility` entry; the gate lives in the rule sentence).
- Authoring-viewpoint phrasing: the `effect` texts of the two re-credit edges say "held_usd rises from 0.00 to …" — a statement about the typical opening world rather than "in this task"; not a red-light form, recorded as O-9.

### prerequisite_sentences

Four-point test, each edge:

1. resend_credit ← resend_charge: "For a resend beyond the tier's free resends, the amount it credits is fixed only after the charge assessed for that resend stands on the transfer's ledger." Connective "only after" joins this policy's own result (the amount credited) to a state; the state ("the charge … stands on the transfer's ledger") is record-visible in finder words (find_wallet_ledger shows "fees charged … (transfer, card, retry and redirect fees)"); no tool, id or snake_case token; scope "beyond the tier's free resends" = the condition. Writes in this difficulty that create a retry_fee entry: only `charge_resend_fee_8300b1da`. Derivation: sentence → "a charge for this resend on the ledger" → the only rule describing such an entry is resend_charge's "A resend charge is booked … one wallet_fee_charged entry with fee_type retry_fee … whose fee_seq is the resend's number" → its tool. One reading.
2. shortfall_recredit ← shortfall_makegood: "The amount a shortfall re-credit delivers is fixed only after Paloma's own shortfall credit stands on the transfer's ledger." Passes the four points; only `book_shortfall_makegood_2311834f` writes an incorrect_amount_shortfall Paloma credit; makegood's rule "Paloma owes a make-good for the shortfall: one wallet_paloma_credit entry with credit_reason incorrect_amount_shortfall" identifies it. One reading.
3. shortfall_recredit ← resend_credit: "A shortfall re-credit is not sent to a wallet until no earlier-booked transfer of the same customer addressed to that wallet number stands with a failed credit." Connective "not … until"; state record-visible (status credit_failed on another wallet transfer, visible through find_wallet_transfers); no tool/id; scope matches. Writes of this difficulty's tool set that move a transfer out of credit_failed: only `resend_failed_credit_8d2e2e1a`. The base charter also describes two other ways out of credit_failed — a failed-credit refund (wallet_evt_refunds; credit_failed → refunded) and a redirect (wallet_evt_failed_credit; the redirected credit is sent, and the wallet number changes) — but no tool of this difficulty (task or share) performs either, and base `wallet_evt_failed_credit` makes the route the customer's call ("A failed credit waits with Paloma for the customer's instruction"). So on the tool surface the hop resolves to one write; on the policy surface it resolves only once the customer instructs. Recorded as O-1 (the per-task consequence, if any, is judged in 0.md).
4. wrong_wallet_recredit ← wrong_wallet_funding: "The amount a wrong-wallet re-credit delivers is not fixed until Paloma's funding for that re-credit stands on the transfer's ledger." Passes; only `fund_wallet_recredit_aebfda78` writes an error_recredit Paloma credit. One reading.

- No rule restates another edge in a second wording, names a tool or another policy id. The depended-on rules do not restate the sentences.
- Cross-problem orders stated in rules that ground no edge: (a) wrong_wallet_funding's rule opens "When the error-resolution team decides error_found … and the customer chooses to have the money re-credited to the transfer's own wallet, Paloma funds the re-credit"; the recorded remedy choice is written only by the root's own tool (`choose_wallet_recredit_d4ef146e`), which the root's prerequisite sentence places after the funding. Read as the recorded choice this would invert the declared edge; read as the customer's stated choice (as the resend_charge rule's "when the customer instructs" is read) it is consistent. The declared edge's explicit "not fixed until" leaves one consistent order, so no second terminal state is demonstrable — O-2. (b) resend_charge's "A resend charge is booked when the customer instructs Paloma to send a bounced credit again" — the instruction is spoken, not a write; no order.
- Base rule sentences carrying a cross-problem order: base `wallet_evt_error_resolution` "A remedy can be chosen only after a decision of error_found on that notice" — the decision is a system event (`wallet_error_decided`), not a problem of any tree here; no tree rests on a base sentence.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusions only; consequences are demonstrated in the task files):

- resend_charge vs wallet_evt_failed_credit: "After a failure on the sender's side, each retry beyond free_retries carries retry_fee_usd (fee_type retry_fee, fee_seq the retry number)" — replaced, declared (superseded_clause verbatim). This one clause also carries the retry numbering, so the extended numbering ("number of credits already sent", which also counts credits sent after a Paloma-side failure or a redirect) is covered by the declaration. "after a failure on Paloma's side retries and redirects are free" — followed (cause share 0 for provider_unavailable). "and do not count toward max_retries" — extended does not compute max_retries; inherited. Redirect fee, window, max_retries, credit_failed-only — not touched, inherited.
- resend_charge vs wallet_evt_pricing: every pricing sentence governs booking quantities (transfer fee, promotion, card_fee_usd, margin, fx_rate, receive_amount, date_available, booking-fee rows with fee_seq 1). Extended reuses `credit_card_fee_pct` and `pay_by_bank_fee_discount_usd` on a different quantity (the resend charge), which no pricing sentence governs. No conflict.
- resend_credit vs wallet_evt_failed_credit: "A retried or redirected credit uses the transfer's original fx_rate and receive_amount, and date_available is re-disclosed as the retry day." — replaced, declared; extended keeps "date_available the resend day". Retry window, credit_failed-only, "once the recipient has fixed its cause", max_retries — inherited.
- resend_credit vs wallet_evt_release_holds_and_credit: "release sends the first credit (credit_attempt 1) at the transfer's fx_rate" concerns the first credit only; followed (credit_attempt numbering consistent with base `wallet_credit_sent`).
- shortfall_makegood vs wallet_evt_error_resolution: "for incorrect_amount Paloma credits the shortfall (credit_reason incorrect_amount_shortfall)" — replaced, declared. "On error_found every fee collected is refunded with fee_refund_reason paloma_error unless already refunded under the on-time promise" — not overridden, inherited: an independent obligation outside every tree (no task tool books it; whether it is already met in each world is checked per task). Notice window, one open notice per type, resolution_due_date, no_error rule, remedy after error_found, refund/re-credit business days — inherited.
- shortfall_recredit vs wallet_evt_failed_credit: rate sentence replaced, declared. vs wallet_evt_error_resolution: "the customer chooses to have the shortfall re-credited (recredit_shortfall)" — followed; "a re-credit within recredit_business_days Paloma business days" — not declared; extended adds the cross-transfer gate, which can defer the re-credit while an earlier transfer to the same wallet stays failed. Whether that deadline is breached is a fact about a world (O-3; judged in 0.md). vs release_holds: followed.
- wrong_wallet_funding vs wallet_evt_error_resolution: "or a re-credit to the correct wallet at no cost, funded by Paloma (wallet_paloma_credit, credit_reason error_refund or error_recredit)" — replaced, declared. Fee refund on error_found — inherited (per task).
- wrong_wallet_recredit vs failed_credit: rate sentence replaced, declared; vs error_resolution: "the customer chooses … a re-credit to the correct wallet at no cost" — followed; "a re-credit within recredit_business_days" — followed (sent at once).
- Disguised forms: no anonymous intermediate outside the declared replaced_by texts (the "booking-day mid-market rate implied by the locked rate" and the deduction rate are inside the declared replacements); the only 0-multiplier (cause share 0 for provider_unavailable) restates base's "free" rather than overriding it; no base branch is dropped by a selector (refund remedies are separate remedies, not branches of these computations). No author note calls a base output a "wrong value".
- Undeclared overrides found: none.

### factor_ladders

| policy | factor | effect | tiers | cross_difficulty | multi-source (every non-fall-through tier a conjunction/disjunction over distinct records) |
|---|---|---|---|---|---|
| resend_charge | charge_form | method | 3 | – | no |
| | cause_share | parameter | 3 | – | no |
| | account_standing_relief | parameter | 3 | account | no — level and opened_date are both fields of the one sender_accounts row |
| | bank_deposit_relief | parameter | 3 | bank | no |
| | bounce_taper | parameter | 3 | – | no |
| | collection_route | method | 3 | – | no |
| resend_credit | paid_resend_uplift | parameter | 3 | – | no |
| | held_days_clock | method | 3 | – | no — tier 1 is a single condition |
| | held_days_uplift | parameter | 3 | – | no |
| | principal_uplift | parameter | 3 | – | no |
| | cash_pickup_uplift | parameter | 3 | cash | no |
| shortfall_makegood | shortfall_clock | method | 3 | – | no |
| | delay_goodwill | parameter | 3 | – | no |
| | hardship_goodwill | parameter | 3 | – | **yes** — transfer_purpose (wallet_transfers row) AND short share (credit_sent ledger rows vs disclosed amount) on both non-fall-through tiers |
| | tenure_goodwill | parameter | 3 | account | no |
| | topup_goodwill | parameter | 3 | – (topup is not a difficulty of this scenario; label correct) | no |
| shortfall_recredit | shortfall_rate_basis | method | 3 | – | no — tier 1 single condition |
| | level_points | parameter | 3 | account | no |
| | pickup_points | parameter | 3 | cash | no |
| | deposit_points | parameter | 3 | bank | no |
| | size_points | parameter | 3 | – | no |
| wrong_wallet_funding | misdirect_clock | method | 3 | – | no — tier 1 single condition |
| | misdirection_goodwill | parameter | 3 | – | no |
| | standing_goodwill | parameter | 3 | account | no — one sender_accounts row |
| | bank_deposit_goodwill | parameter | 3 | bank | no |
| wrong_wallet_recredit | wrong_wallet_rate_basis | method | 3 | – | no |
| | purpose_points | parameter | 3 | – | **yes** — transfer_purpose (holding row) AND principal collected (funds_received ledger rows) on both non-fall-through tiers |
| | business_points | parameter | 3 | business | no — one business_accounts row |
| | topup_points | parameter | 3 | – | no |
| | size_points | parameter | 3 | – | no |

- Counts per policy: resend_charge 6 (4 parameter, 2 method); resend_credit 5 (4/1); shortfall_makegood 5 (4/1); shortfall_recredit 5 (4/1); wrong_wallet_funding 4 (3/1); wrong_wallet_recredit 5 (4/1). All within 4–6, ≥ 2 parameter, ≥ 1 method.
- Per-task structure (scopes as above): task 0's computations carry one multi-source factor (hardship_goodwill) and cross-difficulty factors reading account, bank and cash; task 1's carry one multi-source factor (purpose_points) and cross-difficulty factors reading account, bank and business. The difficulties of this scenario (blueprint.yaml) are account, bank, cash, wallet, business; topup and rewards are not difficulties, so the topup factors are correctly `cross_difficulty: null`.
- `decides` is an input binding in every factor (never `result`); binding sets are pairwise disjoint within each policy.
- Every ladder: 3 pairwise-disjoint tiers including the fall-through; no two tiers of any ladder select the same value or method (values listed in rule_compute_equivalence); every tier — condition and value/method — is stated in the rule prose and implemented as a branch of the `decides` binding; no tier lives only in compute.
- Labels: every `method` factor changes the computation (bands with different formulas; surcharge vs discount vs none; different start dates for a day count; mid-market-implied vs deduction-adjusted vs locked rate); every `parameter` factor substitutes a number. Every method tier names a rule the charter states (in the extended rule).
- Each factor's `baseline` equals its fall-through tier, and equals what `baseline.rule` yields for that input (baseline.rule says nothing about the factor, i.e. the input is absent/neutral: share 1, relief 0, taper 1, points 0, rate = locked, clock = failed_at / notice date as the baseline sentence implies). Checked per task for weight.
- Ladder realism notes (not demonstrable as RED, recorded as observations):
  - O-10 bounce_taper: a charged resend needs resend number > free_retries ≥ 1 (every tier has free_retries ≥ 1), and on a credit_failed transfer whose credits all bounced the number of bounces equals the number of credits sent, so the fall-through "a single bounce leaves it whole" is reachable at a charged resend only through an unusual history (a credit sent without a reversal, e.g. an earlier error re-credit). For ordinary customers who reach this write the live tiers are "exactly two" and "three or more".
  - O-11 shortfall_rate_basis: a customer who reaches this write has an error_found incorrect_amount decision, i.e. a short credit; the fall-through "otherwise: the locked rate" (credit at or above the locked rate and not short) is reachable only by an unusual history (credit above the locked rate yet short in local currency).
  - O-12 paid_resend_uplift: raising a resend's FX rate because a resend fee was paid is an unusual treatment; not shown to be one no remittance business would publish.

### findings

Charter-global: one SOURCE-POLICY finding (F-1), the rest observations.

- O-0 (input completeness, observation): the supplied replay_tasks snapshot prints a row only for `1.json`; the brief's summary line likewise. Bears on task 0 (the gate snapshot gives no positive replay evidence for it). Not re-run by the auditor (Step 0 forbids it).
- O-1 (check 6, observation): the state-form edge shortfall_recredit ← resend_credit can, on the policy surface, also be satisfied by refunding or redirecting the earlier failed transfer (base wallet_evt_refunds / wallet_evt_failed_credit); no tool of this difficulty performs either, and the base charter makes the route the customer's instruction. Bears on task 0.
- O-2 (check 6, observation): wrong_wallet_funding's rule conditions the funding on "the customer chooses to have the money re-credited"; the recorded choice is written only by the root's tool, which the root's own prerequisite sentence places after the funding; the stated-choice reading is the only one consistent with both rules. Bears on task 1.
- O-3 (check 1 / conflict scan, observation): the cross-transfer gate of shortfall_recredit is not declared against base error_resolution's "a re-credit within recredit_business_days Paloma business days" nor against base wallet_agg_multi_holding's "never combined". A consequence would need a world where the gate defers the re-credit past the deadline. Bears on task 0.
- O-4 (check 2, observation): resend_charge's collection sentence is silent on ach_debit / wire funding; compute treats them as debit card. No consequence in a credit-card / debit-card / pay-by-bank world.
- O-5 (check 2, observation): "the margin the transfer carried" ignores the base promotional margin on a first transfer booked under the promotion. Consequence only on such a transfer.
- O-6 (check 2, observation): rule "rounded half up" vs checker `round()`; consequence only at an exact tie — checked per task.
- F-1 (check 2, SOURCE-POLICY RED — upgraded from O-7 at 2026-10-04T16:43Z (mtime 16:43:52Z), before any reveal, on the strength of task 1's masked world alone): every history window of the extended charter is stated in the rule only as "in the last N calendar months" (resend_charge bank 6; resend_credit cash 6; shortfall_makegood topup 12; shortfall_recredit cash payouts 12 and bank payouts 12; wrong_wallet_funding bank 12; wrong_wallet_recredit topup 6). No sentence of any rule says where such a window starts; the compute fixes it through `within_months` (`_within`: `0 <= MONTHS(entry_date, today) < N`, a rolling window keyed to today's day-of-month), a counting convention with no quotation in the rule or compute_basis. The prose equally admits the calendar-aligned readings "the N complete calendar months before the current one" and "the current month and the N-1 before it". Symptom: a world whose window-boundary record falls between the rolling start and the first day of that calendar month gets two defensible tiers. Demonstrated consequence: task 1 (topup order dde46573…, 2026-04-02, against frozen 2026-10-08: excluded rolling, included under "April–September") — see 1.md. Task 0's boundary rows fall the same way under every reading (0.md, factor_weight), so no consequence there. Affected: the rule sentences quoted above and the `within_months` bindings of all six computes.
- O-8 (check 3, observation): `fee_seq` docstring wording ("one more than the resends already made") vs the policy's "number of credits already sent" agree unless the transfer has a redirect or error re-credit.
- O-9 (check 7, observation): edge `effect` texts state "rises from 0.00".
- O-10, O-11, O-12 (factor realism, observations) as above.

## closing_checklist

Written after both reveals (post-reveal section; the charter-global section above is pre-reveal and unchanged by the reveals).

The difficulty does **not** close: task 1 carries SOURCE-POLICY RED (F-1). Status of each Step 4 item:

- Per-task files correspond one-to-one with tasks 0 and 1, alongside this file; first revision, nothing older to trace. Comparison sections: 0.md PASS; 1.md SOURCE-POLICY RED.
- Extended policies fully covered; scopes pairwise disjoint (task 0: resend_charge, resend_credit, shortfall_makegood, shortfall_recredit; task 1: wrong_wallet_funding, wrong_wallet_recredit — equal to each task's `charter_scope`); task tools and GT closed (every gold write uses its scope's tools); uuid8s show no batch derivation.
- Trees: task 0 — 3 prerequisite problems, 2 value_input edges, owner=user root, acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user root, acyclic. The difficulty's prerequisite edges form a DAG with no cross-task reference.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (≥ 2 parameter, ≥ 1 method); each task has a multi-source factor (hardship_goodwill; purpose_points) and cross-difficulty factors (account/bank/cash; account/bank/business); every factor bears weight against an honest baseline with a definite fall-back different from gold. The window sentences behind seven factors carry F-1; in task 1 it yields a second value.
- Gate re-run on the final form: not applicable — the difficulty does not close in this revision; the auditor does not run the gates (Step 0).

---

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-04 after the round-2 brief, before any round-2 GT reveal; contains nothing derived from a revealed GT. Auditor: same independent agent.
- Inputs (sha256, view = source): `wallet.extended.yaml` aa6f8c57ebd079a87ab3ae6a8dc7f6ce776ee6f99f0333f3894d3b590e16539d (changed from d5562602…); `task_tools.py` 3dcae286eac2abefe5f948b1d4d3084af1962043392fd43162732824915c3f0a (changed from ab149dfa…). Both changed, so every charter-global section is re-derived below (diff against the archived round-1 view `/tmp/erl0030_views/archive/mobile_wallet_transfers.r1/`, then the full checks re-run on the new text).
- Gate snapshot `/tmp/erl0030_gates/mobile_wallet_transfers.r2.txt`: all gates exit 0; replay now prints rows for `0.json` (20 acts) and `1.json` (15 acts). Entry conditions met.
- Masked as before: every task's evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*; all worklog.md.

### what changed (structured diff, round-1 view → round-2 view)

- Base section: still equal to `blueprint/products/wallet.yaml` (parsed equality).
- Unchanged in every extended policy: `compute`, `params`, `trigger`, `subject`, `computes`, `target_tool`, `overwrite`, `baseline`, `cross_category`, `inputs`, each prerequisite edge's `policy_source`/`condition`/`kind`/`gate`/`form`/`resolved_by`, every factor's `effect`/`decides`/`bindings`/`baseline`/tier values and methods.
- Changed rule sentences (and the matching `compute_basis` quotations and ladder `when` texts):
  1. The seven history-window sentences (resend_charge Bank Deposit relief; resend_credit Cash Pickup uplift; shortfall_makegood Top-Up goodwill; shortfall_recredit Cash Pickup points and Bank Deposit points; wrong_wallet_funding Bank Deposit goodwill; wrong_wallet_recredit Top-Up points) now each add: "a rolling window that holds the entries whose entry_date [ordered_at] lies fewer than N whole calendar months before today, the whole calendar months from a date to today being the difference between the two calendar months, less one when today's day of the month is lower than that date's". The first ladder tier of each factor adds "(rolling, counted in whole calendar months back from today)".
  2. resend_charge collection sentence: "for a transfer paid by debit card, ACH debit or wire it is collected as it stands" (was "debit card"); ladder fall-through likewise.
  3. wrong_wallet_funding opening sentence: "and the customer asks for the money to be re-credited" (was "chooses to have the money re-credited").
  4. Edge `effect` texts of the two re-credit edges: "held_usd rises by the … booked" (was "rises from 0.00 to …").
- `task_tools.py`: one docstring line — `charge_resend_fee_8300b1da` `fee_seq` now "an integer count starting at 1, equal to the number of credits already sent on the transfer" (was "one more than the resends already made on the transfer"). No code line, signature, owner or tool name changed.

### re-derived charter-global checks (revision 2)

- policy_conflict_scan: unchanged conclusion — subjects, triggers, terminal states, cross-category reads unchanged; scopes still split {resend_charge, resend_credit, shortfall_makegood, shortfall_recredit} / {wrong_wallet_funding, wrong_wallet_recredit}, two disconnected graph components.
- rule_compute_equivalence: script re-check on the new text — every `compute_basis` quotation is a verbatim substring of its rule; compute names = basis keys; every `replaced_by` and every `baseline.rule` sentence is in the rule. The window convention is now stated in the rule and is exactly the compute's `_within` (`0 <= MONTHS(entry, today) < N`, `MONTHS` = month difference minus one when today's day-of-month is lower): the rule's "fewer than N whole calendar months before today" ⇔ `MONTHS < N`; "less one when today's day of the month is lower than that date's" ⇔ `if day2 < day1: m -= 1`. The calendar-aligned readings are now excluded by the text. The collection sentence now names ach_debit and wire, matching the compute's `else` branch. No new compute-only basis; no rule promise without compute.
- action_binding_and_uuids: tool names and uuid8s unchanged; each `(target_tool, computes)` still claimed once; docstring sweep for before/after/first/then/prior/until on the new module: none; the new `fee_seq` wording equals the policy's resend number by definition.
- prerequisite_graph: unchanged edges, all `policy_source` verbatim in own rules, all state form, no fallback; `effect` texts no longer assert an opening value.
- prerequisite_sentences: the four sentences are unchanged and pass as in round 1. The rewritten funding sentence ("the customer asks for the money to be re-credited") names a spoken request, not the recorded remedy choice, so it no longer reads as an order against the root's prerequisite sentence. No new cross-problem order appears in any changed sentence (checked: the seven window clauses, the collection clause and the funding clause contain no ordering connective tying one problem to another).
- override_declarations: no base sentence newly touched; overwrite entries unchanged; conclusion unchanged (no undeclared override).
- factor_ladders: counts, labels, tier values/methods, baselines and multi-source/cross-difficulty structure unchanged (table of round 1 stands). The rolling-window wording adds no tier and no condition.

### status of round-1 charter-global items (revision 2)

| item | round-1 status | round-2 finding |
|---|---|---|
| F-1 window convention | SOURCE-POLICY RED | **Closed.** All seven window sentences state the rolling convention verbatim-equivalent to the compute; the second reading is excluded by text. |
| O-0 replay snapshot lacked 0.json | observation | Resolved by input: the r2 snapshot prints a 0.json row (20 acts, det/nonvac True, match True). |
| O-1 refund/redirect also clear credit_failed | observation | Unchanged (no tool performs them; persona fixes route). Stays an observation. |
| O-2 funding "the customer chooses" | observation | Acted on: now "asks for"; no ordering ambiguity left. Closed. |
| O-3 gate vs recredit_business_days / multi_holding | observation | Unchanged; stays an observation. |
| O-4 collection rule silent on ach/wire | observation | Acted on: rule and ladder name ACH debit and wire. Closed. |
| O-5 promotional margin | observation | Unchanged; stays an observation. |
| O-6 half-up vs round() | observation | Unchanged; stays an observation (checked per task). |
| O-8 fee_seq docstring wording | observation | Acted on: docstring now equals the policy's definition. Closed. |
| O-9 effect "from 0.00" | observation | Acted on: "rises by … booked". Closed. |
| O-10, O-11, O-12 ladder realism | observation | Unchanged; stay observations. |

New charter-global defects found in revision 2: none.

### closing_checklist (revision 2)

Written after both round-2 reveals.

- Per-task files 0.md and 1.md correspond one-to-one with the tasks, each with round 1 untouched and a `revision_2` appended; both revision-2 comparisons PASS.
- All six extended policies covered; scopes disjoint and equal to each task's `charter_scope` (task 0: resend_charge, resend_credit, shortfall_makegood, shortfall_recredit; task 1: wrong_wallet_funding, wrong_wallet_recredit); task tools and GT closed; uuid8s unchanged and unremarkable.
- Trees: task 0 — 3 prerequisite problems, 2 value_input edges, user-owned root; task 1 — 1 prerequisite problem, 1 value_input edge, user-owned root; the difficulty's edge set is a DAG with no cross-task reference.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (≥ 2 parameter, ≥ 1 method); per task one multi-source factor (hardship_goodwill; purpose_points) and cross-difficulty factors (account/bank/cash; account/bank/business); all ladders 3 tiers stated in the rule with distinct outcomes; every factor bears weight against an honest baseline with a definite fall-back different from gold. All history windows now state their counting convention in the rule.
- Gates on the final form: the coordinator's r2 re-run (`/tmp/erl0030_gates/mobile_wallet_transfers.r2.txt`) — EXTENDED, TASK TOOL CONTRACT, REPLAY (both tasks), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK, CACHE-DIFF INFO, all exit 0; check_traceability deferred to the KB stage. The hashes the auditor audited (charter aa6f8c57…, tools 3dcae286…, task sources 43ed6fea…, 18913235…) are the ones in the r2 VIEW_MANIFEST.
- Open charter-global observations carried forward (no task consequence): O-1, O-3, O-5, O-6, O-10, O-11, O-12.

**The difficulty passes the source-layer audit in revision 2.**

---

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-04 after the round-3 brief, before any round-3 GT reveal; nothing here derives from a revealed GT.
- Inputs (sha256, view = source): `wallet.extended.yaml` aa6f8c57…16539d — **unchanged** since revision 2; `task_tools.py` 68723cac77fc1263940e783ba605590d5c263bb55ea81901616d454a76c3b4d5 — changed. Per the re-audit rule the charter-only sections (policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders) are carried forward from revision 2 by reference on the unchanged charter hash; the section that rests on the tool module (action_binding_and_uuids) is re-derived below.
- Gate snapshot `/tmp/erl0030_gates/mobile_wallet_transfers.r3.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY (0.json 20 acts / 73 rows match; 1.json 15 / 41 match), SOLVABILITY, COMPUTE, GROUNDING, TRACEABILITY (0.json 25 copied / 0 missing; 1.json 18 / 0), SCOPE OK, CACHE-DIFF INFO, all exit 0. Entry conditions met.

### action_binding_and_uuids (revision 3, re-derived)

- Diff of `task_tools.py` against the archived round-2 view: exactly three hunks, in the bodies of `resend_failed_credit_8d2e2e1a`, `choose_shortfall_recredit_f54302ef` and `choose_wallet_recredit_d4ef146e`: `now = ctx.now()` became `clock = ctx.now()` plus `now = f"{clock[:10]}T{clock[11:19]}"`. No docstring, signature, decorator, owner, tool name or other line changed (confirms the coordinator's statement). uuid8s unchanged.
- Effect check against the erlbench clock: `erlbench/determinism.py` `Clock.now()` returns the task's `frozen_time` string verbatim (its own docstring example is the "YYYY-MM-DD HH:MM:SS TZ" form). For the round-3 frozen_time strings "2026-10-06 11:20:00 CDT" and "2026-10-08 15:05:00 CDT", the rebuilt `now` is "2026-10-06T11:20:00" / "2026-10-08T15:05:00" — byte-equal to what the round-2 bodies wrote from the round-2 strings ("2026-10-06T11:20:00", "2026-10-08T15:05:00"). `now[:10]` (entry_date, date_available, case_date) is unchanged. The bodies that use `ctx.now()[:10]` (charge, make-good, funding) give the same date as before. No `make_id` call takes a time part, so every written row id is unchanged.
- The tool bodies still read no other policy's state and raise nothing; the prerequisite-judgement conclusion of round 1 stands.

### shared-tool timestamp (revision 3, observation O-13)

- `blueprint/share_tools.py` `verify_customer_identity` writes `verified_at=ctx.now()` and `transfer_to_human_agent` writes `created_at=ctx.now()`; with the new frozen_time form these rows now hold "2026-10-06 11:20:00 CDT" style values, while `db_schema.json` describes both fields as "ISO 8601 timestamp YYYY-MM-DDTHH:MM:SS … exactly as returned by ctx.now()" — the two halves of that format text no longer agree. Outside this difficulty's write domain (blueprint) and outside the four relationships: the value is produced identically by gold replay and by any rollout from the same clock, it feeds no policy computation or gate of this difficulty, and replay matches (73/73, 41/41). Recorded as an observation, not a red light.

### clock-dependent policy elements (revision 3)

- Every clock the charter's computations use is the date part: the compute sandbox takes `NOW = str(frozen_time)[:10]` → "2026-10-06" / "2026-10-08", unchanged. The base gates the gold writes rest on (retry window in calendar days from the date part of failed_at; error_found before a remedy) are date-level. No gate of these trees uses elapsed hours or time of day. The new strings denote the same instants on Paloma's operations clock (US Central; 2026-10-06 and 2026-10-08 fall in CDT, before the 2026-11-01 change).

### closing_checklist (revision 3)

Written after both round-3 reveals.

- 0.md and 1.md each carry round 1, `revision_2` and `revision_3`, older text untouched; both revision-3 comparisons PASS.
- Coverage, disjoint scopes, closed tools/GT, uuid8s, trees (task 0: 3 prerequisite problems / 2 value_input; task 1: 1 / 1; user-owned roots; one DAG), factor structure and weight: unchanged from revision 2's checklist (charter hash unchanged; per-task values re-derived and unchanged).
- Rework claims verified: frozen_time of both tasks now "YYYY-MM-DD HH:MM:SS CDT" for the same instants (satisfies `erlbench/validate.py`'s `^\d{4}-\d{2}-\d{2}\b`); the quoted rationale sentence updated in both tasks; three tool bodies rebuild `released_at` to the identical prior value; every policy clock and gate resolves on the unchanged date part; row ids unchanged. New observation O-13 (blueprint shared tools write the raw clock into `verified_at`/`created_at`, now differing from the schema's format text) — outside this difficulty's relationships, no scoring consequence.
- Gates on the final form: coordinator's r3 run (`/tmp/erl0030_gates/mobile_wallet_transfers.r3.txt`), all exit 0 including TRACEABILITY; audited hashes (charter aa6f8c57…, tools 68723cac…, task sources c01fb5f5…, e87bedca…) equal the r3 VIEW_MANIFEST.
- Open charter-global observations carried forward: O-1, O-3, O-5, O-6, O-10, O-11, O-12, O-13.

**The difficulty passes the source-layer audit in revision 3.**
