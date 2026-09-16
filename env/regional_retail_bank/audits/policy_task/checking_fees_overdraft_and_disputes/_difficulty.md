# Policy-task audit — checking_fees_overdraft_and_disputes / charter-global

## charter_global_frozen

- Auditor: independent source-layer auditor (not the instantiating agent).
- Freeze time: 2026-09-16T09:17:56Z (charter-global section); written in full **before** any task's GT fields were read.
- Frozen inputs and their hashes:
  - `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/checking.extended.yaml`
    sha256=`66b4c1ac6efc37a5e6f1cfb9b24579d8d31afcf87eed6cc4366c0749cc2d783a`
  - `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/task_tools.py`
    sha256=`a22e33a5631acf9bc0078440989072933f86e8d2516c3c293dac75a71a85b9ef`
  - `env/regional_retail_bank/blueprint/products/checking.yaml`
    sha256=`635b57c460d5d54e087b3c1e82483b6cf808521a115d07b15d86489c54166046`
- Fields permitted for this section: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml`), the extended charter's `base` + `extended_policies` (`rule`, `compute`, `compute_basis`, `overwrite`, `prerequisite`, `factors`, `baseline`, `params`, `inputs`, `cross_category`), and `task_tools.py`.
- Fields explicitly masked and not read while writing this section: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, and all prior audit conclusions.

### entry_conditions (Step 0)

The brief supplied the instantiation-gate snapshot with its actual output lines: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (2 tasks, det=True, nonvac=True, errs=0, closure matches initial_state), SOLVABILITY OK, COMPUTE OK (branch mean 55.50, step mean 16.00, history_rows_max 62, branches_max 73), GROUNDING OK, SCOPE OK. Masked views were supplied with sha256 hashes; both were re-hashed at the start of this audit and both match (`be3ef7c…3c6f` for 0.json, `25d41c4…8ad9` for 1.json), and each was confirmed to hold exactly the three keys `frozen_time`, `user_scenario`, `initial_state`. `check_traceability.py` is legitimately deferred to the render stage. Entry conditions are **complete**; the gates were cited, not re-run.

A machine green light qualifies the bundle for this audit; it does not prove the structured policy self-consistent, and the findings below were all reached by hand against the charter and the two seeded worlds.

### policy_conflict_scan

The charter is the verbatim base section of `blueprint/products/checking.yaml` plus seven `extended_policies`. The base copy was compared key-by-key against the blueprint (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`): **all ten identical**, so the base copy has not been rewritten.

Seven extended policies, seven task tools, a 1:1 `(target_tool, computes)` map:

| policy | trigger | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- | --- |
| `checking_ext_fee_schedule_correction` | state_due | checking_fee_refund | correction_amount | `post_fee_schedule_correction_961f83a2` | agent |
| `checking_ext_dispute_credit_reversal` | state_due | checking_provisional_reversal | reversal_amount | `post_dispute_credit_reversal_956f6db8` | agent |
| `checking_ext_closure_payout` | on_request | checking_close | payout_amount | `confirm_closure_payout_0546356c` | **user** |
| `checking_ext_relationship_tier_conversion` | state_due | checking_change_product | target_variant_name | `convert_account_tier_569988a7` | agent |
| `checking_ext_dispute_provisional_credit` | state_due | checking_provisional_credit | credit_amount | `post_dispute_provisional_credit_b16208c2` | agent |
| `checking_ext_overdraft_protection_source` | state_due | checking_set_overdraft_link | overdraft_link_savings_account_id | `authorize_overdraft_protection_source_1d4e232c` | **user** |
| `checking_ext_overdraft_courtesy_relief` | on_request | checking_fee_refund | relief_amount | `post_overdraft_courtesy_relief_64b96dbf` | agent |

**Overlapping subject.** `checking_fee_refund` is the subject of two policies (`fee_schedule_correction`, `overdraft_courtesy_relief`). They are separated by ground (`adjustment_reason` bank_error vs courtesy_waiver), by the base's own ordering of grounds, and — decisively — by each policy's own terminal exclusion sentence: "An account carrying no overdraft charge above the schedule is outside this rule and no corrective entry is made" and "An account whose entries leave it at or above zero is outside this rule and no goodwill relief is granted". Each task's world was evaluated against **all seven** policies to test whether an out-of-scope policy also fires; results are recorded per task. No compatible-conclusions conflict was found on triggers, eligibility, time anchors, action parameters, terminal states or cross-category read boundaries between the extended policies themselves, with the single exception recorded as CG-1 below (an intra-policy contradiction inside `checking_ext_dispute_credit_reversal`).

**Claimed scopes of the M tasks.** Task 0's tree spans `{closure_payout, dispute_credit_reversal, fee_schedule_correction}`; task 1's tree spans `{overdraft_courtesy_relief, overdraft_protection_source, dispute_provisional_credit, relationship_tier_conversion}`. The two sets are **pairwise disjoint** and their union is **all seven** extended policies: jointly complete.

### rule_compute_equivalence

Check 2 was run over all seven policies in both directions. Every `compute` binding carries a `compute_basis` entry, and every `compute_basis` entry is a verbatim substring of that policy's `rule` (checked mechanically). Every `factors[].ladder` `when` clause is a verbatim substring of its policy's `rule` (checked mechanically; zero misses). Ladder `method` strings are faithful active-voice paraphrases of the same rule sentence (e.g. rule "only the overdraft charges posted inside the review window count toward the charges under review" vs ladder "only the overdraft charges posted inside the review window are summed") — same semantics, not a missing tier.

Every `IfExp` in every `compute` was matched against a declared factor's `decides`. Two branch clusters are not a factor's `decides`, and both are legitimate: `target_tier` in `relationship_tier_conversion` (the tier threshold ladder, stated in full in its own rule sentence) and `stmt_cover` in `overdraft_protection_source` (the twin of the declared `mm_cover`, listed in that factor's `bindings` and covered by its `baseline`).

Equivalence failures found: **CG-1** (netting base) and **CG-4**, **CG-6**, **CG-7** below.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair repeats. Each tool writes exactly one atomic effect and none reads history, applies a schedule, or judges a business condition — the function bodies were read in full:

- `post_fee_schedule_correction_961f83a2`: creates one `checking_transactions` row, updates `ledger_balance`. No branch on any prerequisite.
- `post_dispute_credit_reversal_956f6db8`: creates one row, updates `ledger_balance`.
- `confirm_closure_payout_0546356c`: creates a `checking_closure_requests` row in `completed`, creates the paying-out debit row, sets `status=closed`, `closed_date`, `ledger_balance=0.00`, clears `overdraft_link_savings_account_id`.
- `convert_account_tier_569988a7`: single `ctx.update` of `variant_name`.
- `post_dispute_provisional_credit_b16208c2`: creates one row, sets `dispute_status='provisional_credited'`, updates `ledger_balance`.
- `authorize_overdraft_protection_source_1d4e232c`: single `ctx.update` of `overdraft_link_savings_account_id`.
- `post_overdraft_courtesy_relief_64b96dbf`: creates one row, updates `ledger_balance`.

**No tool refuses a call, raises, or emits a hint while a prerequisite is unresolved.** There is no `if` on any gate field anywhere in the module. The tool layer therefore judges no prerequisite.

uuid8 tails: `961f83a2`, `956f6db8`, `0546356c`, `569988a7`, `b16208c2`, `1d4e232c`, `64b96dbf`. All seven are 8-character lowercase hex, all seven distinct, no shared prefix, no arithmetic sequence, no shared tail, no evidence of batch derivation from a common seed. **PASS.**

Docstrings: no docstring names another task tool, states an action's position in a business sequence, or names a policy id. The phrase "before calling" appears as parameter-sourcing guidance ("take it from the checking account lookup for this owner before calling"); this is recorded as observation CG-10, not a red light, because it names no tool and leaks no problem-tree ordering.

### prerequisite_graph

Check 7 over the whole graph. Every one of the seven policies has `prerequisite` present; four carry `[]` and three carry edges. Five edges in all:

| blocked policy | problem (depended-on) | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `dispute_credit_reversal` | `fee_schedule_correction` | value_input | `corrections_standing` | state | `post_fee_schedule_correction_961f83a2` |
| `closure_payout` | `dispute_credit_reversal` | value_input | `takebacks_out` | state | `post_dispute_credit_reversal_956f6db8` |
| `overdraft_courtesy_relief` | `overdraft_protection_source` | state_gate | `checking_accounts.overdraft_link_savings_account_id` | state | `authorize_overdraft_protection_source_1d4e232c` |
| `overdraft_courtesy_relief` | `dispute_provisional_credit` | value_input | `claim_credits_posted` | state | `post_dispute_provisional_credit_b16208c2` |
| `overdraft_courtesy_relief` | `relationship_tier_conversion` | value_input | `relief_share` | state | `convert_account_tier_569988a7` |

- Every `problem` names another extended policy id in this file; none names a base policy and none names itself.
- **Acyclic.** Two components: the chain `fee_schedule_correction -> dispute_credit_reversal -> closure_payout`, and the fan-in `{protection_source, provisional_credit, tier_conversion} -> courtesy_relief`. No edge crosses between them, so no cycle is created by cross-task references either.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (checked mechanically: 5/5 True) and is **not** restated in the depended-on policy's `rule` (5/5 False).
- `form` is `state` on all five; `fallback_reason` is absent on all five — correct, since the state form carries no fallback. No action-form edge exists, so no fallback needed testing.
- `resolved_by` equals the depended-on policy's `target_tool` on all five.
- `kind` matches `gate`: `corrections_standing`, `takebacks_out`, `claim_credits_posted` and `relief_share` are all real binding names in the blocked policy's own `compute` (value_input); `checking_accounts.overdraft_link_savings_account_id` is a real column in `db_schema.json` and is the subject of the blocked policy's own eligibility sentence (state_gate).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world", "gold") appears anywhere in any `prerequisite` block (scanned mechanically; zero hits).
- `condition` neither strengthened nor weakened relative to the sentence, with one scope looseness recorded as CG-9.

**PASS**, with observation CG-9.

### prerequisite_sentences

Check 6, four-point test per edge. All five sentences are written from the blocked policy's own result toward what it waits on, with an explicit ordering connective, in the state form, naming no tool, no policy id, no snake_case token and no row id.

1. `dispute_credit_reversal <- fee_schedule_correction`
   "**The amount taken back is settled only after the ledger carries a corrective entry against every overdraft charge standing above the published fee schedule.**"
   Connective "only after"; waited-on state is record-visible ("the ledger carries a corrective entry"). Derivation: the reader sees the account's posted activity carries no bank-error correction; scanning the other policies' rules for a write that leaves that state, exactly one rule describes it — `fee_schedule_correction`'s "the bank puts the difference back as one corrective entry on the bank-error ground". No other policy of this difficulty creates a bank-error correction entry (`overdraft_courtesy_relief` creates a *goodwill* entry and says so in its own rule). **One reading.**
2. `closure_payout <- dispute_credit_reversal`
   "**The closing payout is worked out only once every temporary credit standing on the account for a claim decided in the bank's own favour has been taken back on the ledger.**"
   Connective "only once"; state "has been taken back on the ledger". Exactly one write of this difficulty creates a take-back entry: `post_dispute_credit_reversal_956f6db8`, and its policy's own rule is the only one that describes taking a temporary credit back. **One reading.**
3. `overdraft_courtesy_relief <- overdraft_protection_source`
   "**Goodwill relief on overdraft charges is granted only once the account's record names an active savings account of the owner as the source the bank may draw on to cover items.**"
   Connective "only once"; state is a named field value in business words. Two tools touch `overdraft_link_savings_account_id`, but `confirm_closure_payout_0546356c` only **clears** it; only `authorize_overdraft_protection_source_1d4e232c` can make it *name* an active savings account, and only `overdraft_protection_source`'s rule describes doing so. **One reading.**
4. `overdraft_courtesy_relief <- dispute_provisional_credit`
   "**The goodwill relief is worked out only after every temporary credit owed on a claim still being looked into stands posted to the account.**"
   Connective "only after"; state "stands posted to the account". Exactly one write creates a `checking_provisional_credit` row. **One reading.**
5. `overdraft_courtesy_relief <- relationship_tier_conversion`
   "**The goodwill relief is settled only once the account stands on the tier its relationship balance supports.**"
   Connective "only once"; state "the account stands on the tier …". Exactly one write of this difficulty rewrites `variant_name`. **One reading.**

No blocked rule carries a second wording of the same dependency, a tool name, or another problem's id (scanned mechanically over all seven rules for all seven tool names and all seven policy ids: zero hits). No depended-on rule restates its blocker's sentence.

Cross-problem orders stated in rules that ground no declared edge: none among the extended policies. Two **base** rule sentences state cross-policy orders — `checking_evt_overdraft_and_returned_item_fees` ("an overdraft protection transfer under checking_evt_overdraft_protection_transfer is attempted first") and `checking_evt_fee_refund` ("There are two refund grounds, checked in this order"). Neither grounds any task's tree (no task's tree rests on either), so both are recorded as observation CG-8 rather than red lights.

**PASS**, with observation CG-8 and CG-9.

### override_declarations

Check 1's finding half, run sentence by sentence against every `base_policy_refs` entry of all seven extended policies. Conclusions reached on every base sentence; the consequences are demonstrated in the task files.

**`checking_ext_fee_schedule_correction`** (refs `checking_evt_fee_refund`, `checking_evt_electronic_dispute`, `checking_evt_overdraft_and_returned_item_fees`; one overwrite).
Base "A fee is refunded in full, never in part, as one checking_fee_refund row whose source_item_id is the fee row and whose amount equals that fee's amount." — the sub-clause "whose amount equals that fee's amount" is declared; "as one … row whose source_item_id is the fee row" is followed. The sub-clause **"A fee is refunded in full, never in part" is not named in this policy's `overwrite`** although the corrective entry is by construction a partial give-back (CG-5). Base's bank_error paragraph ("an overdraft fee beyond overdraft_daily_item_limit … or a fee at an amount other than the tier's parameter; a bank_error refund has no time limit and does not count toward any courtesy limit") is followed. Base's dedup, status and dispute clauses are inherited unweakened. Base `checking_evt_overdraft_and_returned_item_fees` limits overdraft fees "to overdraft_daily_item_limit fees per account **per business day**"; the extended applies one day's allowance once across the whole run of charges under review and says so in its own words but names no base sentence (CG-6).

**`checking_ext_dispute_credit_reversal`** (refs `checking_evt_electronic_dispute`; one overwrite). Base "A provisional credit may be reversed only when the dispute's dispute_status is resolved_bank_favor or withdrawn, for the full provisional credit amount, with the provisional credit row as source_item_id." — "for the full provisional credit amount" is declared; the status gate and the source_item_id binding are inherited and restated in the extended's own words; "When the dispute is resolved_customer_favor the provisional credit becomes final with no new row" is honoured by the extended's terminal sentence. **No undeclared base override.** The defect in this policy is internal (CG-1).

**`checking_ext_closure_payout`** (refs `checking_evt_closure`, `checking_evt_interest`; four overwrites, all against `checking_evt_closure`).
Declared and correct: the two-step confirmation, the early-closure-fee booking, the interest *placement*, the disbursement sentence. Inherited unweakened: "Closing an account is the owner's own decision"; "The ledger balance must be zero or above"; "An account with a dispute in submitted or provisional_credited status cannot be closed until the dispute is resolved".
Undeclared:
- **`checking_evt_interest` carries no `overwrite` entry at all**, yet the extended replaces its entire method (daily end-of-day balances × the tier's `interest_apy_ladder` band ÷ 365, summed over the cycle) with `reconciled_money × closing_rate ÷ 100 × MN(age_days, 30) ÷ 365`, where `closing_rate` is a K-param ladder selected by card-payment count and money-market balance rather than by the account's own balance band. The declared overwrite covers only *where* the interest goes, never *how much* it is. This is check 1's "dropped branch" shape, made sharper by the fact that the three K rates (0.02 / 0.05 / 0.15) are three of the four values in Premier Checking's own `interest_apy_ladder` `{0.00: 0.02, 10000: 0.05, 25000: 0.1, 100000: 0.15}` — the same value set, re-selected by a different condition. **CG-4 (SOURCE-POLICY RED); consequence demonstrated in `0.md`.**
- Base eligibility `early_window` ("The early closure fee applies when the account is closed within early_closure_window_days calendar days after the account was opened") is not declared superseded and is not implemented: `compute` subtracts `closing_charge` unconditionally (CG-7).
- Base "The fee is reduced so it never takes the ledger balance below zero" is neither declared nor implemented (CG-7).

**`checking_ext_relationship_tier_conversion`** (refs `checking_agg_relationship_balance`, `checking_product_change`; two overwrites). The summation basis and the "credit card balances … never count" prohibition are both declared. "A checking account with a negative ledger balance contributes zero" is honoured by the fall-through `MX(0.0, reconciled_money)`. The measurement date ("the frozen date on which the request is handled") is honoured (`NOW`). `checking_product_change`'s active-account, entry-gate, no-fee, one-per-cycle and tier-in-force clauses are all inherited and consistent. Undeclared: base "Mortgage principal is added only for tiers whose relationship_balance_includes_mortgage is true" — the four components omit mortgage entirely, with no `overwrite` entry (CG-7).

**`checking_ext_dispute_provisional_credit`** (refs `checking_evt_electronic_dispute`; one overwrite). "The provisional credit amount is the dispute's claimed_amount, but never more than the disputed item's amount." is declared in full, which legitimises both the different basis and the removal of the item-amount cap. The channel list, the notice window, the business-day credit-due count, the new-account substitution, `submitted_only` and `one_credit` are all inherited unweakened, and the extended's terminal sentence ("A claim that has already been decided is outside this rule") restates the status gate. **No undeclared base override.**

**`checking_ext_overdraft_protection_source`** (refs `checking_evt_overdraft_protection_transfer`; `overwrite: []`). Sentence by sentence: "may name one savings account as its overdraft protection source" ✔; "must belong to the same customer_id" ✔ (`CFIELD` scopes to the customer); "must be in active status when the link is recorded" ✔ (`status='active'`); "Removing the link is always allowed" ✔ (the tool accepts an empty string). The transfer-mechanics and transfer-fee sentences govern `checking_overdraft_transfer`, a subject this policy does not claim. Undeclared/unimplemented: **"The savings tier must have overdraft_protection_source_eligible true in the savings charter"** is neither in `compute` nor in the extended `rule` (CG-7). `overwrite: []` is otherwise correct.

**`checking_ext_overdraft_courtesy_relief`** (refs `checking_evt_fee_refund`, `checking_evt_electronic_dispute`; one overwrite). "A fee is refunded in full, never in part" is declared. Inherited and honoured: the eligible-fee-code list (`extended_overdraft` is on it), the rolling-365-day courtesy limit read at the frozen-date tier, the active-account requirement, and the "most recently posted first" ordering (the extended records the entry against "the most recently posted of the charges it covers"). Undeclared aggregate-level conflicts: the relief **pool** reaches back one/three/six months and so can include fees outside the tier's `courtesy_refund_window_days` (60/90/120), and can include a fee that base's `refund_once` dedup says has already been refunded (CG-3).

### factor_ladders

Charter-global structure only. Whether each factor bears weight is a fact about one world and lives in each task file's `factor_weight`.

| policy | factors | parameter | method | ≥3 disjoint tiers | multi-source non-fall-through tiers | cross_difficulty (categories) |
| --- | --- | --- | --- | --- | --- | --- |
| `fee_schedule_correction` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (savings, card, cd) |
| `dispute_credit_reversal` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (savings, card, cd) |
| `closure_payout` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (savings, cd, card) |
| `relationship_tier_conversion` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (savings, cd, card) |
| `dispute_provisional_credit` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (card, savings, cd) |
| `overdraft_protection_source` | 4 | 2 | 2 | 4/4 | 4/4 | 3 (card, savings, cd) |
| `overdraft_courtesy_relief` | 6 | 3 | 3 | 6/6 | 6/6 | 3 (savings, card, cd) |

Every ladder is a three-tier `when/when/otherwise` with the fall-through counted; the two non-fall-through tiers of every ladder are mutually exclusive as stated (each second tier opens "the case above does not apply and …"), so the tiers are pairwise disjoint. Every non-fall-through tier is a conjunction or a disjunction of two or more conditions drawn from **distinct records** (e.g. `savings_accounts.current_balance` ∧ a `checking_transactions` aggregate; `card_transactions` count ∨ `cd_certificates.principal_balance`), so **every** ladder in the charter is multi-source, comfortably above the floor of 2 per computation. Each computation has at least 3 factors whose tier is decided from another difficulty's records (savings, cd, card), above the floor of 2.

`decides` bindings are disjoint within each policy and none is the literal `result`; each is a named intermediate that `result` then aliases.

Label honesty was checked tier by tier. Every `parameter` factor substitutes a different **number** into an unchanged formula (`day_cap`, `per_item_charge`, `netting_share`, `allowance_share`, `closing_charge_level`, `closing_rate`, `deposit_share`, `certificate_share`, `credited_share`, `charge_offset`, `required_cover`, `cover_reserve`, `relief_share`, `episode_ceiling`, `relief_window`). Every `method` factor changes the **operation, base, window or order** (`charges_under_review` sum-all → sum-in-window → take-max; `standing_credit` likewise; `corrective_entry`/`take_back`/`closing_payout`/`temporary_credit`/`relief_entry` rounding grain; `closing_charge` full → halved → amortised over started months; `relationship_balance` max-of-three → sum-of-three → sum-of-four; `checking_component` reconciled → windowed credits → half of them; `mm_cover`/`stmt_cover` share of balance; `source_choice` candidate order; `relief_pool` largest → windowed OD → windowed OD+RI+EXT; `shortfall_standing` half → whole → whole-plus-pool). **No mislabel found.** Every `method` tier names a computation rule the charter itself states (all `when` clauses verbatim in the `rule`; the methods are paraphrases of the same sentences).

`baseline.rule` self-sufficiency, per policy — each was computed by hand from `baseline.rule` and the records alone, with no factor applied, and each yields a definite number/value (figures appear in the task files): `fee_schedule_correction` ✔, `dispute_credit_reversal` ✔, `closure_payout` ✔ (with the wording observation CG-11), `relationship_tier_conversion` ✔, `dispute_provisional_credit` ✔, `overdraft_protection_source` ✔ (definite value: no source named), `overdraft_courtesy_relief` ✔. Every sentence of every `baseline.rule` is a sentence of its policy's `rule`. Every factor's fall-through tier equals that policy's baseline for the binding it decides (checked ladder by ladder). `baseline.params` names the default keys the baseline actually uses in every case.

**Structure PASS.**

### findings

Numbered CG-n; each names the tasks it bears on so their files pick up the demonstration.

---

**CG-1 — SOURCE-POLICY RED — the netting base contradicts itself, and `compute_basis` justifies a different expression from the one `compute` evaluates.**

- *Symptom.* `checking_ext_dispute_credit_reversal` states two incompatible bases for the netting in the same rule, and the `compute_basis` quotation attached to `netted_credit` is the one `compute` does **not** implement.
- *Root cause.* The sentence that fixes the netting's base was written by copying the parallel sentence that fixes the owner-allowance's base, without changing the noun.
- *Evidence.* `checking.extended.yaml`, `checking_ext_dispute_credit_reversal.rule`:
  - "Where the owner's money market balance reaches the tier's relationship maintenance threshold and a corrective entry stands on the account, **the whole of the corrective entries standing is netted off**; where the case above does not apply … **half of the corrective entries standing is netted off**."
  - "**The netting is worked out on the temporary credit standing** and rounded half-up to the cent before it is taken off."
  The first says the netting's base is `corrections_standing`; the second says it is `standing_credit`. `compute` implements the first: `netted_credit: standing_credit - RND(corrections_standing * netting_share, 2)`. `compute_basis.netted_credit` quotes the **second** sentence verbatim, so the declared basis does not justify the implemented expression. (Contrast `owner_allowance`, where the identically-shaped sentence "The part left with the owner is worked out on the temporary credit standing …" *is* matched by `RND(standing_credit * allowance_share, 2)` — which is what shows the two sentences were meant to differ.)
- *Demonstrated consequence.* Bears on **task 0**. Two conclusions in the same situation; the figures are in `0.md` → `findings` → CG-1.
- *Affected artifact and location.* `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/checking.extended.yaml`, `extended_policies[checking_ext_dispute_credit_reversal].rule` (the netting-base sentence) and `.compute_basis.netted_credit`.

---

**CG-2 — observation — the same rule phrase, "the owner's money market balance", is implemented two different ways across the charter.**

- *Symptom.* Four policies bind it to `CFIELD('savings','current_balance', variant_name='Premier Money Market', status='active')`; three bind it to `CFIELD('savings','current_balance', status='active')` with no variant filter, which returns whichever active savings row the store yields first.
- *Evidence.* Variant-filtered: `relationship_tier_conversion`, `dispute_provisional_credit`, `overdraft_protection_source`, `overdraft_courtesy_relief`. Unfiltered: `fee_schedule_correction`, `dispute_credit_reversal`, `closure_payout` — all three of which nonetheless write "the owner's money market balance" in their rules.
- *Consequence.* Not demonstrable on either seeded world: task 0's owner holds exactly one savings account, and it is a Premier Money Market, so the two readings coincide; task 1's owner holds two savings accounts but every policy in task 1's scope uses the variant-filtered form. For an owner who holds a Statement Savings account and a money market, the three unfiltered policies would silently read the wrong one. Recorded as an observation, not a red light.
- *Affected artifact.* `checking.extended.yaml`, the `mm_balance` binding of the three unfiltered policies.

---

**CG-3 — observation — the goodwill relief pool crosses two base gates that are not declared superseded.**

- *Symptom.* `checking_ext_overdraft_courtesy_relief` builds its `relief_pool` from charges posted inside a relief window of one, three or six months, and its `overwrite` declares only base's "A fee is refunded in full, never in part".
- *Evidence.* Base `checking_evt_fee_refund` also states "The fee must have posted no more than courtesy_refund_window_days calendar days before the courtesy refund is granted" (`courtesy_refund_window_days` is 60 for Everyday/Interest, 90 for Premier, 120 for Private Client) and "A fee can be refunded at most once". The six-month long relief window (~180 days) reaches past all of those, and the pool excludes no already-refunded fee.
- *Consequence.* Bears on **task 1**, where it is not demonstrable: the relief is bound by the shortfall cap, so every pool reading in range gives the same scored figure (shown in `1.md` → `factor_weight` and `findings` CG-3). This is the "anonymous intermediate factor" shape — the deviation hides in an intermediate with no new parameter name — and it is recorded even though its consequence is masked here.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_overdraft_courtesy_relief.overwrite` (missing entries) and `.compute.relief_pool` / `.compute.od_windowed`.

---

**CG-4 — SOURCE-POLICY RED — `checking_evt_interest` is cited as a base ref and silently replaced, with no `overwrite` entry.**

- *Symptom.* `checking_ext_closure_payout` lists `checking_evt_interest` in `base_policy_refs` and carries **zero** `overwrite` entries against it, while substituting a wholly different method and a different rate selector for the closing interest.
- *Root cause.* The author declared the interest's *placement* (four overwrites, all against `checking_evt_closure`) and treated that as covering its *amount*.
- *Evidence.* Base `checking_evt_interest.rule`: "Each day's balance earns the APY of the **highest band floor in the tier's interest_apy_ladder that the balance reaches**, applied to the whole balance, divided by interest_day_count_basis. Daily amounts are summed unrounded over the statement cycle…". Base `checking_evt_closure.rule`: "For an interest-bearing tier, **interest earned** through the day before closure is credited before disbursement" — declared superseded only by "The closing interest is **added to the money paid out rather than credited as a separate entry**", which changes where it lands, not what it is. The extended rule instead says "The closing rate is the base account rate. Where the owner has made at least ten card payments in the last twelve months and the owner's money market balance reaches the tier's relationship maintenance threshold, the closing rate is the premier relationship rate; …", and `compute` evaluates `closing_rate: K('premier_relationship_rate') if (card_payments_12m >= 10 and mm_balance >= P('waiver_relationship_balance')) else (…)`. The three K rates are `base_account_rate: 0.02`, `standard_relationship_rate: 0.05`, `premier_relationship_rate: 0.15` — three of the four values of Premier Checking's own `interest_apy_ladder` `{0.00: 0.02, 10000.00: 0.05, 25000.00: 0.1, 100000.00: 0.15}`, re-selected by a condition base nowhere states.
- *Demonstrated consequence.* Bears on **task 0**; two defensible payouts, figures in `0.md` → `findings` → CG-4.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_closure_payout.overwrite` (no entry against `checking_evt_interest`), `.rule` (the closing-rate ladder) and `.compute.closing_rate` / `.compute.closing_interest`.

---

**CG-5 — observation — "A fee is refunded in full, never in part" is left standing in `fee_schedule_correction`'s own `overwrite`.**

- *Symptom.* `checking_ext_fee_schedule_correction.overwrite` names only the sub-clause "whose amount equals that fee's amount", while the corrective entry is by construction a part of the charges it corrects.
- *Evidence.* Base `checking_evt_fee_refund.rule` sentence 1 carries both clauses. The sibling policy `checking_ext_overdraft_courtesy_relief` **does** declare "A fee is refunded in full, never in part" superseded, which shows the author knew the clause needed naming.
- *Consequence.* Not demonstrable as a second number on **task 0**: the declared clause ("whose amount equals that fee's amount") is what fixes the amount, and the extended replacement states the amount outright, so a reader reaches the same figure. Recorded as an observation about the completeness of the declaration.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_fee_schedule_correction.overwrite`.

---

**CG-6 — observation — base's per-business-day overdraft cap is narrowed to a once-per-run cap with no declaration.**

- *Symptom.* Base limits overdraft-item fees "to overdraft_daily_item_limit fees per account **per business day**"; the extended applies one day's allowance once to the whole set of charges under review, however many days they span.
- *Evidence.* Base `checking_evt_overdraft_and_returned_item_fees.rule` (the per-business-day limit). Extended `checking_ext_fee_schedule_correction.rule`: "The account is taken to carry the number of chargeable overdraft items the tier allows **for one business day**" and "The charge the schedule produces is the charge for each chargeable item multiplied by the smaller of the number of overdraft charges standing and the number of chargeable items allowed". `compute`: `schedule_charge: per_item_charge * MN(assessed_count, day_cap)`. No `overwrite` entry names the base sentence.
- *Consequence.* Bears on **task 0** and is not demonstrable there: every charge in the review window posted on a single business day (2025-06-27), so the per-day and per-run readings coincide. Recorded as an observation.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_fee_schedule_correction.overwrite` and `.compute.schedule_charge`.

---

**CG-7 — observation — four inherited base provisions are implemented by nothing.**

- *Symptom.* Four base sentences are neither declared superseded nor present in any `compute`:
  1. `checking_evt_closure` eligibility `early_window`: "The early closure fee applies when the account is closed within early_closure_window_days calendar days after the account was opened." — `closure_payout.compute` subtracts `closing_charge` with no age condition whatever.
  2. `checking_evt_closure`: "The fee is reduced so it never takes the ledger balance below zero."
  3. `checking_agg_relationship_balance`: "Mortgage principal is added only for tiers whose relationship_balance_includes_mortgage is true …" — `relationship_tier_conversion`'s four components contain no mortgage term, and Premier Checking's `relationship_balance_includes_mortgage` is `true`.
  4. `checking_evt_overdraft_protection_transfer`: "The savings tier must have overdraft_protection_source_eligible true in the savings charter." — `overdraft_protection_source.compute` filters candidates only on `variant_name` and `status`, never on that flag (`Goal Builder Savings` is `false` in `blueprint/products/savings.yaml`).
- *Consequence.* None is demonstrable on these two worlds: task 0's account is 81 days old against a 90-day early-closure window so the charge is genuinely owed, and its payout stays far above zero; neither seeded customer holds a mortgage; task 1's selected source is a Premier Money Market, whose flag is `true`. Recorded as observations, each with the world fact that masks it.
- *Affected artifact.* `checking.extended.yaml` — `closure_payout.compute.closing_charge`, `relationship_tier_conversion.compute.relationship_balance`, `overdraft_protection_source.compute.mm_cover`/`.stmt_cover`/`.source_choice`.

---

**CG-8 — observation — two base rule sentences state cross-policy orders.**

- *Evidence.* `checking_evt_overdraft_and_returned_item_fees`: "an overdraft protection transfer under checking_evt_overdraft_protection_transfer is attempted first". `checking_evt_fee_refund`: "There are two refund grounds, checked in this order."
- *Consequence.* Neither grounds any declared edge and no task's tree rests on either; in each task the other refund ground is excluded by the relevant extended policy's own terminal sentence (task 0's account has a non-negative shortfall so no goodwill relief arises; task 1's schedule test yields nothing so no corrective entry arises). Per the skill's rule for base-stated cross-problem orders, this is an observation, not a red light.
- *Affected artifact.* `blueprint/products/checking.yaml` (base rules), read against the extended trees.

---

**CG-9 — observation — one prerequisite sentence describes a state its resolving write does not literally produce.**

- *Symptom.* Edge `dispute_credit_reversal <- fee_schedule_correction` waits on "the ledger carries **a corrective entry against every overdraft charge** standing above the published fee schedule" (plural, distributive), while the depended-on policy makes exactly **one** entry: "the bank puts the difference back as **one** corrective entry on the bank-error ground, recorded against **the largest** of the overdraft charges under review".
- *Consequence.* The hop still resolves to one write and one reading (only `post_fee_schedule_correction_961f83a2` creates a bank-error correction entry, and only that policy's rule describes one), so this is a scope looseness in the sentence rather than an undiscoverable or ambiguous edge. Recorded as an observation.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_dispute_credit_reversal.prerequisite[0].policy_source` / `.condition` read against `checking_ext_fee_schedule_correction.rule`.

---

**CG-10 — observation — argument docstrings carry the word "before".**

- *Evidence.* Every id parameter in `task_tools.py` is documented as e.g. "take it from the checking account lookup for this owner **before calling**" / "read it from the account's posted activity **before calling**".
- *Consequence.* No docstring names another task tool, names a policy, or states any business action's position in a sequence; the phrase describes only where an argument value is read from. It leaks nothing of the problem tree. Recorded because the skill's check 3 bars the bare ordering word.
- *Affected artifact.* `env/regional_retail_bank/tasks/checking_fees_overdraft_and_disputes/task_tools.py`, all seven docstrings.

---

**CG-11 — observation — `closure_payout.baseline.rule` opens a sentence with a dangling pronoun.**

- *Evidence.* `baseline.rule` runs "… The closing charge is then taken at the level it was set, in full. **It** is the money reconciled from the account's own entries multiplied by the closing rate …". The sentence that introduces "the closing interest" ("The closing interest is added to the money paid out rather than credited as a separate entry.") is present in the full `rule` but was not carried into `baseline.rule`, so "It" has no antecedent there.
- *Consequence.* The baseline still yields a definite number (a reader can only be speaking of the interest), so the self-sufficiency test passes. Wording only; recorded as an observation.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_closure_payout.baseline.rule`.

---

**CG-12 — observation — `overdraft_protection_source.compute` cannot be evaluated for an owner with no Statement Savings account.**

- *Symptom.* `stmt_balance: CFIELD('savings','current_balance', variant_name='Statement Savings', status='active')` returns `None` when the owner holds no such account, and `stmt_cover` then evaluates `RND(None * K('minimum_cover_share'), 2)`, raising `TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'`. Reproduced by evaluating this policy against task 0's world (one savings account, a Premier Money Market).
- *Evidence.* The rule itself contemplates the absence — "the owner holds **any** statement savings balance" is a ladder condition, and "where no savings account reaches it, no protection source is named" is the terminal sentence — so `rule` promises a branch `compute` cannot produce.
- *Consequence.* Not demonstrable on either scored world: task 1's owner holds both a Statement Savings and a Premier Money Market, and this policy is out of task 0's scope. Recorded as an observation.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_overdraft_protection_source.compute.stmt_balance` / `.stmt_cover`.

---

## closing_checklist

Written after both reveals (2026-09-16T09:41:06Z), and therefore placed **below** the charter-global section, which remains pre-reveal by construction and was not edited after the reveal.

**The difficulty does not close out.** Step 4's precondition is that all M tasks PASS all four relationships; task 0 carries two `SOURCE-POLICY RED` findings (`_difficulty.md` CG-1 and CG-4, demonstrated in `0.md` → T0/CG-1 and T0/CG-4). The checklist is recorded item by item so that what does hold is not lost with what does not.

| checklist item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | **✔** `0.md`, `1.md`, `_difficulty.md` in `env/regional_retail_bank/audits/policy_task/checking_fees_overdraft_and_disputes/` |
| old revisions traceable | **✔** — see `## revision_provenance` below. The superseded audit is preserved in git at commit `427143d`; it audits a different charter (`e0472aea…`, 6 extended policies) and was already absent from the working tree when this audit began. Freeze hashes for this round are recorded in each file's `source_gt_comparison`. |
| every comparison section carries a PASS | **✘** — `1.md` PASSes all four; `0.md` carries SOURCE-POLICY RED on policy self-consistency and, in consequence, an unclean unique-solution relationship. |
| this difficulty's extended policies fully covered | **✔** — 7 extended policies; task 0 claims 3, task 1 claims 4; union is all 7 (confirmed post-reveal against both `charter_scope` blocks). |
| the M tasks' scopes pairwise disjoint, spanning each whole problem tree | **✔** — `{fee_schedule_correction, dispute_credit_reversal, closure_payout}` ∩ `{overdraft_protection_source, dispute_provisional_credit, relationship_tier_conversion, overdraft_courtesy_relief}` = ∅. Each scope is exactly its task's root problem plus all of its prerequisite problems. Confirmed on the worlds as well as on paper: every out-of-scope policy was evaluated against each task's seed and each is excluded by its own terminal sentence or by a base gate (`0.md` → `policy_self_consistency`; `1.md` → `problem_chain` → *Scope exclusivity on this world*). |
| task tools and GT closed | **✔** — 7 task tools, 3 + 4 disjoint, union complete; every scored argument of every gold write is reachable from a shared read tool or from the persona, and no field is visible only in the raw seed. |
| each task tool uses an independently generated, frozen uuid8 | **✔** — see `### action_binding_and_uuids`. |
| every tree has 1–3 prerequisite problems | **✔** — task 0: 2; task 1: 3. |
| at least max(n−1, 1) `value_input` edges | **✔** — task 0: 2 ≥ 1; task 1: 2 ≥ 2. |
| at least one problem resolved by an `owner=user` tool | **✔** — task 0: `confirm_closure_payout_0546356c` (the root); task 1: `authorize_overdraft_protection_source_1d4e232c`. Both handed over passively by the persona at the agent's direction. |
| no cycle, including across tasks | **✔** — two disjoint components, a 3-node chain and a 3-into-1 fan-in; no edge crosses between them, so the difficulty-wide `prerequisite` graph is a DAG. |
| every computation declares a self-sufficient baseline giving a definite number different from gold | **✔** — 7/7: 140.00 vs 144.25; 2455.00 vs 1893.50; 4640.00 vs 4658.30; `""` vs `1e3886c8…`; 415.00 vs 650.25; "Everyday Checking" vs "Premier Checking"; 10.00 vs 96.40. |
| 4–6 factors per computation, 2 of each effect, 2 multi-source, 2 cross-difficulty | **✔** — six computations carry 4 factors and one carries 6; every one has ≥2 `parameter`, ≥2 `method`, **all** tiers multi-source, and 3 cross-difficulty factors. See `### factor_ladders`. |
| every ladder ≥3 tiers, stated in full in its own rule | **✔** — 30 ladders, 3 tiers each; every `when` clause verbatim in its policy's `rule` (checked mechanically, zero misses). |
| every factor proved to bear weight on its task's world against an honest baseline | **✔ 30/30** — 12 in task 0, 18 in task 1; each substitution recomputed independently and each moves the scored value. Every factor's `baseline` was checked against what that policy's `baseline.rule` states for that input: no straw man, no correct-value-under-another-name, and every fall-through tier equals the baseline. |
| a genuine near-miss per computation | **✔ 7/7** — recorded per computation in each task's `factor_weight`. |
| instantiation-stage gates re-run on the final form | **deferred** — outside this audit's boundary (the brief directs the auditor to cite the supplied snapshot, not to run the gates). The snapshot is cited in `### entry_conditions`. A re-run belongs after the two SOURCE-POLICY findings are dispositioned, since both touch `checking.extended.yaml`. |

### independent-derivation agreement

Both tasks were derived blind from the charter, `frozen_time`, `user_scenario` and `initial_state` alone, frozen to disk, and only then compared. **The derivations reproduced GT on every scored item of both tasks** — all 13 scored arguments across 7 gold writes, both owners splits, both write orders, both terminal states, all 7 `baseline_result` figures, all 30 `factor_sensitivity` figures and all 5 edge-load-bearing figures. Two prose miscounts were found in the proof fields (`0.md` → T0/OBS-2, `1.md` → T1/OBS-1); neither moves a relationship.

### what blocks the close-out

Two findings, both charter-global in origin, both demonstrated on task 0's world:

1. **CG-1** — `checking_ext_dispute_credit_reversal` states the netting's base twice, incompatibly, and `compute_basis.netted_credit` certifies the sentence `compute` does not implement. On task 0 the two readings give `reversal_amount` 1893.50 and 0.00, and 0.00 is a value the tool contract refuses.
2. **CG-4** — `checking_ext_closure_payout` names `checking_evt_interest` in `base_policy_refs`, carries no `overwrite` entry against it, and replaces its method and its rate selector outright. On task 0 the two readings give `payout_amount` 4658.30 and 4657.80.

Ten further items are recorded as observations (CG-2, CG-3, CG-5 through CG-12, plus T0/OBS-1, T0/OBS-2, T1/OBS-1, T1/OBS-2). None demonstrates a consequence on either seeded world, and each is recorded with the world fact that masks it, so that a later task built on this charter is not caught by one of them unwarned.

---

## revision_provenance

This audit is a **full re-derivation on regenerated artifacts**, not a re-audit of the artifacts the committed audit examined.

| | superseded revision (git `427143d`, HEAD) | this audit |
| --- | --- | --- |
| `checking.extended.yaml` | sha256 `e0472aea4fae9ecb35d3689208866aa3c4540de7b0ef3d422cd9af44b2273241` | sha256 `66b4c1ac6efc37a5e6f1cfb9b24579d8d31afcf87eed6cc4366c0749cc2d783a` |
| `task_tools.py` | sha256 `b8ef325356f86f4c55b3a98eed5e600b1ecc8f5c66c05d3be111fdf15da8758f` | sha256 `a22e33a5631acf9bc0078440989072933f86e8d2516c3c293dac75a71a85b9ef` |
| base policies | 17 | 19 |
| extended policies | 6 (`checking_ext_cycle_close_relationship_refund`, `checking_ext_autopay_dispute_provisional_credit`, …) | 7 (`checking_ext_fee_schedule_correction`, `checking_ext_dispute_credit_reversal`, `checking_ext_closure_payout`, `checking_ext_relationship_tier_conversion`, `checking_ext_dispute_provisional_credit`, `checking_ext_overdraft_protection_source`, `checking_ext_overdraft_courtesy_relief`) |
| uuid8s | `033d9cbf`, `5453b90d`, `e9518b99`, `6b0f4e50`, `22b46ecc`, `696add48` | `961f83a2`, `956f6db8`, `0546356c`, `569988a7`, `b16208c2`, `1d4e232c`, `64b96dbf` |
| task worlds | different customers, different seeds | Marisol Etheridge (task 0), Wendell Pruitt (task 1) |

Both shared inputs changed, so the skill's carry-forward-by-reference rule does not apply and **every** charter-global section was re-derived in full rather than inherited. Not one policy id, tool uuid8, scored value, task world or persona survives from the superseded round, so its findings (F1–F4, N1, P1–P5, T0-C1 and the revision_2…revision_5 chain) have **no counterpart** in the present artifacts and none of them was carried into the verdicts above. The correct reading of "relation to previous revisions" on every finding in this audit is therefore **new against these artifacts**, which is how each is marked.

The superseded revision's text is preserved unaltered in git at commit `427143d` (`git show 427143d:env/regional_retail_bank/audits/policy_task/checking_fees_overdraft_and_disputes/_difficulty.md`, and likewise `0.md` and `1.md`). It was already absent from the working tree when this audit began — the scenario's `audits/` tree was mid-regeneration — so no on-disk revision was overwritten by this round, and no old blind answer was rewritten to accommodate new GT.

---

# revision_2

Round 2, 2026-09-16T10:01:09Z. Everything above this line is revision 1 and has not been edited. This round is a **verification pass, not a blind audit**: both tasks' GT was already revealed in revision 1, so no freezing rule applies and none is claimed.

## what moved

| artifact | revision 1 | revision 2 | |
| --- | --- | --- | --- |
| `checking.extended.yaml` | `66b4c1ac…d2783a` | `061a329f9bbbd9398d79d5dfc274de57cf6fb40bd8e0a63edebafeeb03faf883` | **changed** |
| `task_tools.py` | `a22e33a5…85b9ef` | `a22e33a5631acf9bc0078440989072933f86e8d2516c3c293dac75a71a85b9ef` | unchanged |
| `blueprint/products/checking.yaml` | `635b57c4…166046` | `635b57c460d5d54e087b3c1e82483b6cf808521a115d07b15d86489c54166046` | unchanged |
| `tasks/0.json` | `88d4c302…0898de` | `836573f3d37f7fa0f663a50cbce36159c130057f0890135065b2b54e0b9a4a2f` | changed |
| `tasks/1.json` | `895da252…4be7f35` | `8bac0bfa190a791bc92c5c2bb7cdcfc066572d8897b14c8cb895f4c0c0ea9607` | changed |
| masked view 0.json | `be3ef7c5…3c6f` | `be3ef7c5…3c6f` | unchanged |
| masked view 1.json | `25d41c4f…8ad9` | `25d41c4f…8ad9` | unchanged |

Both masked views re-hashed and byte-identical, so **neither seeded world, clock nor persona moved**; revision 1's reading of both worlds stands and was not rebuilt. The base section of the charter is still verbatim identical to the blueprint (all ten top-level keys compared equal after YAML load).

`task_tools.py` is byte-identical, so `### action_binding_and_uuids` is **carried forward by reference** on the strength of that hash rather than re-derived.

**Per-policy diff (revision 1 → revision 2), by field:**

| policy | changed fields |
| --- | --- |
| `checking_ext_closure_payout` | `overwrite`, `baseline` |
| `checking_ext_dispute_credit_reversal` | `rule`, `compute_basis`, `baseline` |
| `checking_ext_dispute_provisional_credit` | — none |
| `checking_ext_fee_schedule_correction` | — none |
| `checking_ext_overdraft_courtesy_relief` | — none |
| `checking_ext_overdraft_protection_source` | — none |
| `checking_ext_relationship_tier_conversion` | — none |

**`compute` is byte-identical on all seven policies**, as are `factors`, `params`, `prerequisite`, `cross_category`, `inputs`, `trigger`, `subject`, `computes`, `target_tool` and `base_policy_refs`. Within the two changed policies, `baseline.params` and every `factors[].baseline` substitution dict are also byte-identical; only `baseline.rule` prose moved. The reworker's claim that **no compute expression changed at all** is confirmed mechanically, and so is its claim that **task 1's four policies were not touched** — all four hash equal field by field.

## CG-1 — verified CLOSED

*Claim:* the sentence that licensed the second reading is gone; `compute_basis` and `baseline.rule` carry the corrected sentence; a parallel sentence elsewhere still names the other base deliberately.

**The retired wording is gone charter-wide.** Searching the whole loaded charter (rules, compute_basis, baselines, factors, everything):

| phrase | occurrences |
| --- | --- |
| "The netting is worked out on **the temporary credit standing**" | **0** |
| "The netting is worked out on **the corrective entries standing**" | 3 — `rule`, `compute_basis.netted_credit`, `baseline.rule` |
| "The part left with the owner is worked out on the temporary credit standing" | 3 — the same three places |

Exactly one noun changed, in exactly three places, and the three places are the three faces a solver reads.

**The corrected basis is verbatim in the rule and genuinely justifies the expression evaluated.** `compute_basis.netted_credit` is now "The netting is worked out on the corrective entries standing and rounded half-up to the cent before it is taken off", which is a verbatim sentence of `rule` (mechanical check, below), and `compute` still evaluates the untouched `netted_credit: standing_credit - RND(corrections_standing * netting_share, 2)`. Base × share, rounded, then subtracted — the sentence and the expression now say the same thing in the same order.

**The surviving parallel sentence does not reintroduce the ambiguity.** The two sentences now name different bases, and — this is what makes the repair substantive rather than cosmetic — **each is independently confirmed by its own ladder**:

| quantity | the "worked out on" sentence | its own ladder, as the rule states it | the expression |
| --- | --- | --- | --- |
| netting | "worked out on **the corrective entries standing**" | "None of **the corrective entries standing** … is netted off"; "the whole of **the corrective entries standing** is netted off"; "half of **the corrective entries standing** is netted off" | `RND(corrections_standing * netting_share, 2)` |
| owner allowance | "worked out on **the temporary credit standing**" | "No part of **the temporary credit** is left with the owner"; "the deep relationship share of **the temporary credit standing** is left with the owner"; "the modest share of **the temporary credit standing** is left with the owner" | `RND(standing_credit * allowance_share, 2)` |

In revision 1 the two sentences named **one** base between them while the ladders named two, which is what made the parallel a trap. Now each sentence agrees with its own three-tier ladder and with its own expression: a reader has two independent confirmations per quantity, and the bases genuinely differ because the two subtractions genuinely differ. The parallelism is now a real contrast, not a copying error.

**The second answer is retired.** No sentence remaining anywhere in the charter licenses netting on the temporary credit standing. Recomputed on task 0's handling-time world, the only available reading gives `reversal_amount` = **1893.50**; the revision-1 alternative of **0.00** — the value `post_dispute_credit_reversal_956f6db8` refuses — has no textual support left. Its knock-on to `payout_amount` (6552.03) is retired with it.

**Not merely renamed.** The repair did not invent a new term, move the defect behind a new name, or add a gloss: it changed the noun in one sentence so that the stated basis matches the ladder that was already there and the expression that was already there. Three faces that disagreed now agree.

## CG-4 — verified CLOSED

*Claim:* three clause-by-clause override entries against `checking_evt_interest`, each `superseded_clause` verbatim in the base rule and each `replaced_by` verbatim in the extended rule; the base policy carries no eligibility so no gate is retired.

**The three declarations are verbatim both ways.** All seven of `closure_payout`'s `overwrite` entries were re-checked (the four pre-existing against `checking_evt_closure` and the three new against `checking_evt_interest`): `superseded_clause` verbatim in the named base policy's `rule` and `replaced_by` verbatim in the extended `rule`, **7/7 in both directions**.

**The base reading is actually retired, clause by clause.** `checking_evt_interest.rule` decomposes into seven sentences; the three now named are exactly the three limbs of its method:

| base sentence | status | what it governed |
| --- | --- | --- |
| "Only tiers with interest_bearing true earn interest." | survives | a tier gate |
| "Interest accrues daily on each calendar day's end-of-day ledger balance … taken from the daily series checking_msr_cycle_end_of_day_balances; a day with a zero or negative balance earns nothing." | **superseded** | the accrual basis |
| "Each day's balance earns the APY of the highest band floor in the tier's interest_apy_ladder that the balance reaches, applied to the whole balance, divided by interest_day_count_basis." | **superseded** | **the rate selector** |
| "Daily amounts are summed unrounded over the statement cycle and the total is rounded half-up to the cent and credited on the cycle closing date as one checking_interest_credit row." | **superseded** | the summation and the row |
| "A total that rounds to 0.00 writes no row." | survives | moot — the extended writes no separate row, declared by the third entry |
| "The tier and ladder used for each day are those in force on that day." | survives | points at a retired mechanism (see R2-O2) |
| "Dormant and restricted accounts still earn interest; charged-off and closed accounts do not." | survives | a status rule; no competition |

The sentence that produced revision 1's second payout is the **rate selector**, and it is the second of the three named. On task 0's world it selected the `0.00` band floor of Premier Checking's `interest_apy_ladder`, that is 0.02%, giving 4657.80. With it declared superseded it is no longer in force, and the extended's own three-sentence ladder ("The closing rate is the base account rate" plus its two tier sentences) is the only rate rule standing. `payout_amount` = **4658.30**, uniquely.

**The merged semantics are unique, not merely licensed.** Declaring an override makes it legal; the separate question is whether anything still competes. Nothing does, on any of the three limbs:

- *basis* — the extended supplies one complete formula ("It is the money reconciled … multiplied by the closing rate as an annual percentage, multiplied by the closing days and divided by three hundred and sixty-five, rounded half-up to the cent; the closing days are the days the account has been open, capped at one full statement cycle"); base's daily-series basis is retired.
- *rate* — the extended supplies a three-tier ladder whose tiers are pairwise disjoint and whose fall-through is stated; base's band-floor selector is retired, and base never carried a default that could fill a gap.
- *placement* — the extended says "added to the money paid out rather than credited as a separate entry"; base's "credited on the cycle closing date as one checking_interest_credit row" is retired.

Each limb has exactly one rule in force. No surviving base sentence offers a competing number.

**No gate was lost — verified, not accepted.** `checking_evt_interest.eligibility` is `[]`, so the three new entries can retire nothing. Separately, every `overwrite` entry of every policy in the charter was tested against every eligibility `condition` of its named base policy: the only substring hit is `dispute_credit_reversal`'s pre-existing, unchanged entry, whose `superseded_clause` ("for the full provisional credit amount") is a fragment of the longer `reversal_needs_bank_favor` condition — it retires the amount sub-clause only, while the status requirement survives and is restated in the extended rule's own words, exactly as recorded in revision 1's `### override_declarations`. **No gate was retired by this round's edits**, which is consistent with the SOLVABILITY base-gate counts holding at 8 and 15.

## nothing regressed

**Mechanical sweep, all seven policies, revision-2 artifacts — ALL PASS**, zero failures across: every `compute_basis` entry verbatim in its own rule; every compute binding carrying a basis; every factor ladder `when` verbatim in its own rule; every `policy_source` verbatim in the blocked rule and absent from the depended-on rule; every `resolved_by` equal to the depended-on `target_tool`; no `fallback_reason` on a state-form edge; every `baseline.rule` sentence a verbatim rule sentence; no rule naming a tool or a policy id; every `overwrite` entry verbatim both ways; every `base_policy_refs` entry resolving.

Two of these flipped from fail to pass in this round — `compute_basis.netted_credit` (CG-1) and `closure_payout.baseline.rule`'s dangling antecedent (CG-11). None flipped the other way.

**Factor structure unchanged and re-confirmed:** 4/4/4/4/4/4/6 factors, ≥2 `parameter` and ≥2 `method` each, 3 cross-difficulty each, every ladder ≥3 tiers.

**Every figure reproduced.** All computations were re-run from scratch against the revision-2 charter on both unchanged worlds. **7 scored values, 7 `baseline_result` figures, 30 `factor_sensitivity` figures and 5 edge-load-bearing figures are identical to revision 1**, and the two task files' `evaluation_criteria` arguments, `charter_scope` blocks and step counts (15 and 17) are unchanged. Per-task detail is in `0.md` and `1.md` under their own `## revision_2`.

## observations acted on

| item | verdict |
| --- | --- |
| **CG-11** (dangling pronoun in `closure_payout.baseline.rule`) | **CLOSED** — the antecedent sentence "The closing interest is added to the money paid out rather than credited as a separate entry." is now carried into `baseline.rule` ahead of "It is the money reconciled…". The baseline still computes 4640.00, and every `baseline.rule` sentence remains a verbatim rule sentence. |
| **T0/OBS-2** (base-policy miscount) | **CLOSED** — task 0's `design_rationale` now reads "nineteen base policies", which is `len(blueprint/products/checking.yaml['policies'])`. The correction is itself disclosed in the rationale. |
| **T1/OBS-1** (business-day recount) | **CLOSED** — see `1.md` → `## revision_2`. Corrected in all three places and written out day by day; the recount matches this audit's. |

## observations not acted on

CG-2, CG-3, CG-5, CG-6, CG-7, CG-8, CG-9, CG-10, CG-12, T0/OBS-1 and T1/OBS-2 stand as recorded in revision 1. Each remains an observation with **no demonstrated consequence on either seeded world**, and the world fact that masks each is on record above, so nothing turns on leaving them.

One correction to the stated ground, for the record. The reworker gives as its reason that each "would need a compute or tool edit on material you passed". That is true of CG-2, CG-3, CG-7, CG-10 and CG-12, and CG-8 concerns base rules it may not edit at all. It is **not** true of three of them: **CG-5** and **CG-6** are `overwrite` declarations (the same text-only instrument used to close CG-4), and **CG-9** is a `prerequisite` sentence. All three could have been closed without touching a compute expression or a tool. This changes no verdict — all three are observations that produce no second value on either world — but the reason given does not fit them, and a reader of this report should not carry away that it does.

## new observations from this round

**R2-O1 — observation — a surviving `checking_evt_interest` sentence is not honoured by the compute; an auditor miss in revision 1.**

- *Symptom.* "Only tiers with interest_bearing true earn interest." survives the three new declarations, and `closure_payout.compute` carries no `interest_bearing` test: `closing_interest` is added whatever the tier.
- *Root cause, honestly stated.* This is not a defect the rework introduced — it pre-existed. Revision 1 folded the whole of `checking_evt_interest` into CG-4 without enumerating which of its sentences survive, so this one was never separated out. The rework's clause-by-clause declaration is what makes the survivors individually visible. **The miss is this audit's, in revision 1.**
- *Consequence.* None on either world: task 0's tier is Premier Checking, `interest_bearing: true`, so both readings give 0.58; `closure_payout` is not in task 1's scope. For an Access, Student or Everyday Checking account — all `interest_bearing: false` — the extended would add closing interest where base says none is earned. Observation, same shape as CG-7.
- *Affected artifact.* `checking.extended.yaml`, `checking_ext_closure_payout.compute.closing_interest`; the surviving sentence in `blueprint/products/checking.yaml`, `checking_evt_interest.rule`.

**R2-O2 — observation — a surviving base sentence points at a retired mechanism.**

- *Evidence.* "The tier and ladder used for each day are those in force on that day." survives, but "the ladder" is `interest_apy_ladder`, whose selector is retired by the second new `overwrite` entry, and "each day" is the daily series retired by the first.
- *Consequence.* None — the sentence governs a mechanism no longer in force for the closing interest, and offers no competing number. Cosmetic residue of the clause-by-clause repair.
- *Affected artifact.* `checking_ext_closure_payout.overwrite` read against `checking_evt_interest.rule`.

**R2-O3 — observation — one `replaced_by` is a dangling pronoun as a standalone declaration.**

- *Evidence.* The first new entry's `replaced_by` begins "**It** is the money reconciled from the account's own entries multiplied by the closing rate…". It reads correctly in the extended `rule`, where the preceding sentence supplies "the closing interest", but as a declaration read on its own the antecedent arrives only in the *third* entry's `replaced_by`.
- *Consequence.* None — the clause is verbatim in the extended rule and the merged semantics are unique. This is the same shape as CG-11, which the rework fixed in `baseline.rule`; it reappears in the declaration text.
- *Affected artifact.* `checking_ext_closure_payout.overwrite`, the entry superseding "Interest accrues daily on each calendar day's end-of-day ledger balance…".

## revision_2 verdicts

| item | revision 1 | revision 2 |
| --- | --- | --- |
| CG-1 / T0-CG-1 | SOURCE-POLICY RED | **CLOSED** — retired wording absent charter-wide; corrected basis verbatim and agreeing with its own ladder and its own expression; the parallel sentence confirmed correct for its own quantity; the 0.00 reading has no textual support left |
| CG-4 / T0-CG-4 | SOURCE-POLICY RED | **CLOSED** — three clause-by-clause declarations, verbatim both ways, retiring all three limbs of base's method including the rate selector that produced 4657.80; merged semantics unique on each limb; no gate retired (`eligibility: []`) |
| CG-11 | observation | **CLOSED** |
| T0/OBS-2 | observation | **CLOSED** |
| T1/OBS-1 | observation | **CLOSED** |
| CG-2, CG-3, CG-5–CG-10, CG-12, T0/OBS-1, T1/OBS-2 | observations | **standing**, unchanged, no consequence on either world |
| new this round | — | R2-O1 (auditor miss in revision 1), R2-O2, R2-O3 — all observations, no consequence on either world |

**No new defect was introduced, and nothing regressed.** Two mechanical checks flipped fail→pass; none flipped pass→fail; every figure on both tasks is identical.

## closing_checklist — revision_2

Revision 1's checklist stands except for the one row that blocked it. Re-stating only what changed:

| checklist item | revision 1 | revision 2 |
| --- | --- | --- |
| every comparison section carries a PASS | ✘ — `0.md` carried two SOURCE-POLICY REDs | **✔** — `0.md` and `1.md` both PASS all four relationships |
| instantiation-stage gates re-run on the final form | deferred | **✔ cited** — the coordinator re-ran the full block after the rework; every count is identical to the round-1 snapshot, including the base-gate counts of 8 and 15, which corroborates the no-gate-retired finding. `check_traceability.py` remains deferred to the render stage by design. |

Every other row of revision 1's checklist is unaffected by this round's edits and carries forward: policies fully covered and scopes pairwise disjoint (`charter_scope` blocks byte-identical), task tools and GT closed, uuid8s independently generated (`task_tools.py` hash unchanged), trees of 2 and 3 prerequisite problems with 2 and 2 `value_input` edges and an `owner=user` write each, the difficulty-wide graph a DAG, seven self-sufficient baselines each giving a definite value different from gold, 4–6 factors per computation with the required effect and source mix, every ladder ≥3 tiers stated in full, all 30 factors bearing weight, and a near-miss per computation.

### **The difficulty CLOSES OUT.**

Policy self-consistency **PASS** · problem tree **PASS** · factors bear weight **PASS** · unique solution **PASS**, on both tasks. Fourteen observations stand on record (eleven from revision 1, three new), none of which demonstrates a consequence on either seeded world, each recorded with the world fact that masks it so that a later task built on this charter is not caught by one of them unwarned.

---

# revision_3

Round 3, 2026-09-16T11:31:49Z. Revisions 1 and 2 above are untouched. This round verifies two repairs sent back from the render layer, and — on the coordinator's instruction — re-runs checks 1 and 2 across the whole charter at the **corrected threshold**, which is the threshold this audit should have used from the start.

## the standard this round corrects

Rounds 1 and 2 ran check 1 (`override_declarations`) and check 2 (`rule_compute_equivalence`) against **the quantity ultimately scored**: a divergence that moved no number on either seeded world was written down as an observation. That is the right bar for a red light under "Core constraints", but it is the **wrong bar for these two checks**, which are requirements about the artifact, not about a task:

- Check 1 is categorical in the skill's own words — "Every conflict must name, in that policy's `overwrite`, the base sentence being replaced — **not naming it IS an undeclared override**, recorded as `SOURCE-POLICY RED`." No number is required; the demonstration the table asks for is "quote the two passages … and show that they reach different conclusions in the same situation", and the situation need not be a scored one.
- Check 2 is a **two-way losslessness** requirement between `rule` and `compute`. Rounds 1 and 2 tested it as a *verbatim-substring* check — is the quoted `compute_basis` sentence present in the `rule` — which is a citation check, not an equivalence check. K2 passed that test in both rounds while saying "started months" over a binding that computes completed months.

Both returned items are of these two shapes, and the sweep below finds that **they are not the only ones**. Four further divergences of exactly the same two classes are recorded as `SOURCE-POLICY RED` in this round; three of them are promotions of items rounds 1–2 wrote down as observations on the discredited "no number moved" ground, and one was never recorded at all.

## what moved

| artifact | revision 2 | revision 3 | |
| --- | --- | --- | --- |
| `checking.extended.yaml` | `061a329f…faf883` | `78b195290e32c9f96db8a0c42354c3972bb2aab43c34541dcdcf7381f885b3ef` | **changed** |
| `task_tools.py` | `a22e33a5…85b9ef` | `a22e33a5…85b9ef` | unchanged |
| `blueprint/products/checking.yaml` | `635b57c4…166046` | `635b57c4…166046` | unchanged |
| `tasks/0.json` | `836573f3…9a4a2f` | `a779a071ebe0bae6669c80ec6966089764cb8fa8f869aab3504405fbc877b15f` | changed |
| `tasks/1.json` | `8bac0bfa…ea9607` | `e9f901a22a8389db845873f61aaa963d16028fe938c7cc244651cd66c58dca0f` | changed |
| masked views | `be3ef7c5…` / `25d41c4f…` | identical | unchanged |

Masked views byte-identical for the third round running, so **no seeded row moved**; the prose-only claim is corroborated on that side. Base section still verbatim identical to the blueprint (all ten top-level keys).

**Per-policy field diff, revision 2 → revision 3:**

| policy | changed fields |
| --- | --- |
| `checking_ext_closure_payout` | `rule`, `compute_basis`, `factors` |
| `checking_ext_fee_schedule_correction` | `overwrite` |
| the other five | — none |

**`compute` is byte-identical on all seven policies**, as are `params`, `prerequisite`, `baseline`, `cross_category`, `inputs`, `trigger`, `subject`, `computes`, `target_tool` and `base_policy_refs`. Within `closure_payout`, the `factors` change is confined to `closing_charge_basis.ladder[0].method` wording; every `factors[].baseline` substitution dict is unchanged. The prose-only and no-compute-change claims are confirmed mechanically.

**On the gate scripts.** `check_compute.py` and `check_extended.py` were both modified at 11:08, during this run, and rounds 1–2 cited the superseded versions. It matters here because this audit evaluates the charter through `check_compute.py::build_env`. I diffed the evaluator against the version rounds 1–2 used: `build_env`, `eval_compute`, `substitute`, `MONTHS`, `DAYS`, `_parse_date` and `validate_ast` are **all identical**. The evaluator this audit depends on did not move, so every figure recomputed in rounds 1–2 remains valid on its own terms. The changes lie elsewhere in those files.

## K2 — verified CLOSED

*Claim:* resolved toward the compute; the rule now states whole elapsed months; the new sentence also gives a home to a floor at one that the compute always applied.

**The divergence was real and was a second answer.** `months_open` is `MONTHS(F('opened_date'), NOW)`, which counts **completed** months; the rule said "spread evenly over the **started** months the account has been open". On task 0's world, opened 2025-04-28 against a frozen date of 2025-07-18: completed = 2, started = 3, so `closing_charge` = round(18.50/2, 2) = **9.25** against round(18.50/3, 2) = **6.17**, and `payout_amount` = **4658.30** against **4661.38**. This passed through both of my earlier rounds because the `compute_basis` sentence *was* verbatim in the `rule` — the substring check it was given.

**The new wording is lossless, endpoints included.** The rule now reads: "the closing charge is instead spread evenly over **the whole months the account has been open, a month counting only once the day of the month the account was opened has come round again and the count never falling below one**, and the result rounded half-up to the cent". `MONTHS` increments exactly when the day-of-month reaches or passes the anchor day (`if day2 < day1: m -= 1`). Tested against the binding at the boundaries:

| opened → now | `MONTHS` | what the new sentence says |
| --- | --- | --- |
| 2025-04-28 → 2025-07-27 (day before the anniversary) | 2 | the 28th has not come round in July → 2 ✔ |
| 2025-04-28 → 2025-07-28 (**on** the anniversary) | 3 | the 28th has come round → 3 ✔ |
| 2025-04-28 → 2025-05-27 | 0 | not yet come round → 0, floored to 1 ✔ |
| 2025-04-28 → 2025-05-28 | 1 | come round → 1 ✔ |
| 2025-01-31 → 2025-02-28 (short month) | 0 | the 31st has not come round in February → 0 ✔ |

"Has come round again" is inclusive on the anniversary day itself, which is what the binding does, and the awkward short-month case agrees too. **Lossless in both directions.**

**The floor is real, is now stated, and introduces no divergence.** `closing_charge` divides by `MX(1.0, float(months_open))`; `months_open` is 0 for any account open less than one whole month, so without the floor the expression divides by zero. The floor was applied by every evaluation and stated by no sentence — a silent operation of exactly the kind check 2 exists to catch. "the count never falling below one" states it exactly: `MX(1.0, ·)` and no more. On task 0 `months_open` = 2, so the floor does not bind and the scored figure is unmoved; stating it adds no new branch and changes no value anywhere.

**On the reworker's argument for the direction of the repair — conclusion sound, stated reason false.** It argues the other direction "has no exact expression in the restricted grammar". That is not so: `Add` is an allowed AST node and `MONTHS(F('opened_date'), NOW) + 1` both parses and passes `validate_ast` against the charter's own name set — I ran it. The *sound* reason is the one the reworker did not give: **"started months" is itself ambiguous prose**. On the exact anniversary, 2025-04-28 → 2025-07-28, three months are complete and a fourth has started, so "started months" is 3 or 4 depending on the reading, and "calendar months in which the account was open" gives 4 by a third route. Resolving toward the rule would have required picking one rendering while the phrase still named none of them — relocating the defect rather than closing it. The conclusion is right and the repair is the right one; the argument offered for it is not, and an audit checks the proof submitted, not only the outcome. Recorded as R3-O1.

**Verdict: K2 CLOSED.** Consequence on task 0's world demonstrated in `0.md` → `# revision_3`.

## K1 — verified CLOSED

*Claim:* a second `overwrite` entry names the clause verbatim; a sibling policy already declared the same clause against its own ground; the charter therefore retires it on both grounds the difficulty uses and on neither more; no eligibility gate is caught.

**The clause is now named by both policies that write the subject, each against its own ground:**

| policy | ground | `superseded_clause` | `replaced_by` |
| --- | --- | --- | --- |
| `checking_ext_fee_schedule_correction` | `bank_error` | "A fee is refunded in full, never in part" | "Where the overdraft charges standing … are larger than the charges the published fee schedule produces …, the bank puts the difference back as one corrective entry on the bank-error ground …" |
| `checking_ext_overdraft_courtesy_relief` | `courtesy_waiver` | "A fee is refunded in full, never in part" | "The goodwill relief is the charges in the relief pool taken at the goodwill share …" |

All **eight** `overwrite` entries in the charter are verbatim in both directions (`superseded_clause` in the named base policy's `rule`, `replaced_by` in the extended `rule`) — re-checked mechanically, 8/8.

**The scope of the retirement is exactly right, and that is checkable rather than assertable.** Base `checking_evt_fee_refund` names **two** refund grounds ("There are two refund grounds, checked in this order" — `bank_error` and `courtesy_waiver`) and separately notes a third kind that is not a courtesy refund ("A dispute_final refund is written under `checking_evt_electronic_dispute`"). The extended policies whose `subject` is `checking_fee_refund` are exactly two, and they are exactly the two now declaring the clause. So the clause is withdrawn on both grounds the difficulty writes and on neither more: a `dispute_final` refund — which no task tool of this difficulty writes — keeps base's full-refund rule intact. **Claim verified.**

**No eligibility gate is caught — verified, not accepted.** "A fee is refunded in full, never in part" is not among `checking_evt_fee_refund`'s five gates (`eligible_fee_code`, `courtesy_window`, `courtesy_limit`, `account_active`, `refund_once`). Testing every `overwrite` entry in the charter against every eligibility `condition` of its named base policy, the only substring hit remains the pre-existing, unchanged `dispute_credit_reversal` entry analysed in revisions 1 and 2, which retires the amount sub-clause of `reversal_needs_bank_favor` while the status requirement survives and is restated in the extended rule's own words. Corroborated by the SOLVABILITY base-gate counts holding at 8 and 15.

**Verdict: K1 CLOSED.**

## the charter-wide re-sweep at the corrected threshold

Checks 1 and 2 were re-run over all seven policies — every `compute` binding carrying a window, a floor, a cap, a rounding point or a record filter was read against the sentence `compute_basis` cites, asking whether the sentence **means** the expression rather than whether it appears in the rule; and every sentence of every `base_policy_refs` entry was re-read asking whether it is **named** where it is displaced, not whether a number moves. Four divergences of the two returned classes are found. Each is stated with two passages that fix the same quantity and reach different values.

---

**R3-1 — SOURCE-POLICY RED (check 2) — "the number of overdraft charges standing" is computed as a windowed count, and the charter's own adjacent sentences prove the words mean otherwise.**

- *Symptom.* `checking_ext_fee_schedule_correction.compute` binds `assessed_count` to `COUNT('checking_transactions', within_months=K('correction_review_months'), date_field='posted_date', event_type='checking_fee', fee_code='overdraft_item')` — a count restricted to the one-month review window — while every sentence that consumes it says **standing**.
- *Root cause.* One binding is made to serve two different populations: the windowed sum needs a windowed count, and the ladder tests and the schedule cap were written in the language of the unwindowed one.
- *Evidence.* The charter fixes the vocabulary itself, in the same rule, two sentences apart: "Every overdraft-item charge **standing** on the account counts toward the charges under review, **whenever it posted**" against "only the overdraft charges **posted inside the review window** count toward the charges under review". So *standing* is defined as unwindowed and the windowed set is given different words. `compute_basis.assessed_count` then cites "The charge the schedule produces is the charge for each chargeable item multiplied by the smaller of **the number of overdraft charges standing** and the number of chargeable items allowed" over the windowed expression. The same word governs three further ladder tiers — "at least four overdraft charges **stand on the account**" in `chargeable_item_allowance`, `per_item_charge_level` and `charges_under_review_basis`, and "at least two overdraft charges **stand on the account**" — each of which is evaluated in `compute` against the windowed count.
- *Demonstrated consequence.* Take task 0's own seed and re-date two of the five 2025-06-27 charges to 2025-05-27, changing nothing else. Standing = 7 (as seeded), inside the review window = 3. **Compute's reading** (windowed, 3): `day_cap` = 2, `per_item_charge` = 32.50, `charges_under_review` = 42.00 → `correction_amount` = **0.00**, and the policy's terminal sentence would put the account outside the rule altogether. **The rule's reading** (standing, 7): `day_cap` = 1, `per_item_charge` = 30.75, `charges_under_review` = 108.50 → `correction_amount` = **77.75**. The two readings diverge on three ladder tiers at once and on whether any corrective entry is owed at all — a wider divergence than K2's.
- *Affected artifact and location.* `checking.extended.yaml`, `checking_ext_fee_schedule_correction.compute.assessed_count`, `.compute_basis.assessed_count`, and the four `factors[].ladder` `when` clauses phrased "stand on the account".
- *Relation to previous revisions.* **Never recorded.** Rounds 1 and 2 computed `assessed_count` = 5 and moved on, because on the seeded world both readings give 144.25. This is an auditor miss of rounds 1 and 2, of precisely the class the render-layer audit returned.

---

**R3-2 — SOURCE-POLICY RED (check 2) — "the owner's money market balance" is computed as the first active savings account of any kind, so which balance is read is decided by row order.**

- *Symptom.* Three policies bind `mm_balance` to `CFIELD('savings','current_balance', status='active')` while their rules say "the owner's **money market** balance". `CFIELD` returns `hs[0]` — the first matching row — so with more than one active savings account the value is fixed by store order, not by any sentence.
- *Root cause.* The variant filter that four sibling policies carry was omitted in three.
- *Evidence.* Unfiltered: `checking_ext_fee_schedule_correction`, `checking_ext_dispute_credit_reversal`, `checking_ext_closure_payout`. Filtered by `variant_name='Premier Money Market'`: `relationship_tier_conversion`, `dispute_provisional_credit`, `overdraft_protection_source`, `overdraft_courtesy_relief`. The charter proves it knows the difference: `overdraft_protection_source`'s rule distinguishes "the owner's **money market** balance" from "the owner's **statement savings** balance" in adjacent ladder tiers and binds each to its own variant-filtered expression.
- *Demonstrated consequence.* Task 1's owner holds two active savings accounts — `1e3886c8…` Premier Money Market 12000.00 and `d3f01445…` Statement Savings 3400.00. Evaluated on those two seeded rows, the filtered expression returns **12000.00** in either store order; the unfiltered expression returns **12000.00** as the rows happen to be stored and **3400.00** when the same two rows are presented in the other order. A rule that says "money market balance" therefore reads a Statement Savings balance, and the tier every ladder that consumes `mm_balance` selects turns on the order of two rows rather than on a rule. Every ladder in all three policies that tests `mm_balance` against `waiver_relationship_balance` (25000.00) or `protection_source_minimum` (5000.00) flips between 12000.00 and 3400.00.
- *Affected artifact and location.* `checking.extended.yaml`, the `mm_balance` binding of `fee_schedule_correction`, `dispute_credit_reversal` and `closure_payout`.
- *Relation to previous revisions.* Recorded in revision 1 as observation **CG-2** and carried unchanged through revision 2, on the ground that neither seeded world exhibits it. **Promoted** here: the divergence is a check-2 failure whatever the seed, and the order-dependence makes the reading indeterminate rather than merely loose.

---

**R3-3 — SOURCE-POLICY RED (check 2) — the extended's own rule conditions the closing charge on the opening window; its own compute applies the charge unconditionally.**

- *Symptom.* `checking_ext_closure_payout.rule` says "The closing charge **owed for an account closed inside its opening window** is taken out of the money paid out rather than booked as a separate entry on the account." `compute` subtracts `closing_charge` with no age condition of any kind.
- *Root cause.* The declared overwrite moved the charge from a booked entry into the payout and carried the condition across in words, but the condition was never given a branch.
- *Evidence.* Extended `rule`, the sentence above, against `compute.closing_payout`, which computes `reconciled_money - closing_charge + closing_interest` in all three of its rounding branches with `closing_charge` never zeroed. Base `checking_evt_closure` fixes the window at `early_closure_window_days`, 90 for every tier, and carries the matching eligibility `early_window`.
- *Demonstrated consequence.* Take task 0's world and move `opened_date` to 2024-11-28, changing nothing else: `account_age_days` = 232, far outside the 90-day opening window, so by the rule **no closing charge is owed** and the payout is reconciled money plus closing interest = **4667.55**. The compute still levies one — `months_open` = 7, `closing_charge` = 2.64 — giving **4664.91**. Two payouts on one world from the same policy's two faces.
- *Affected artifact and location.* `checking.extended.yaml`, `checking_ext_closure_payout.rule` (the opening-window sentence) against `.compute.closing_charge` / `.compute.closing_payout`.
- *Relation to previous revisions.* Recorded in revision 1 as **CG-7(1)** and carried through revision 2, on the ground that task 0's account is 81 days old and inside the window. **Promoted**: this is the purest form of a check-2 failure, a policy's rule and its own compute disagreeing, and the seed's 81 days merely places the task nine days inside a boundary the compute does not have.

---

**R3-4 — SOURCE-POLICY RED (check 1) — `checking_evt_overdraft_and_returned_item_fees` is cited as a base ref, its per-business-day cap is reworked into a per-run cap, and no `overwrite` entry names it.**

- *Symptom.* `checking_ext_fee_schedule_correction` lists `checking_evt_overdraft_and_returned_item_fees` in `base_policy_refs` and carries **zero** `overwrite` entries against it, while rebuilding the fee cap that policy fixes.
- *Root cause.* The same shape as CG-4, which this audit red-lighted in revision 1 and the reworker closed in revision 2: a base policy declared as lineage, deviated from, and never named.
- *Evidence.* Base: overdraft-item fees are "limited to `overdraft_daily_item_limit` fees per account **per business day**". Extended: "The account is taken to carry the number of chargeable overdraft items the tier allows **for one business day**", and `compute` evaluates `schedule_charge: per_item_charge * MN(assessed_count, day_cap)` — one day's allowance applied **once** to the whole run of charges under review, however many business days they span. The extended states the simplification in its own words but names no base sentence, so a reader merging base and extended has two caps for one quantity.
- *Demonstrated consequence.* Take task 0's seed and split the five June charges across two business days — three on 2025-06-27, two on 2025-06-30, amounts unchanged. **Extended's cap**: the allowance of 1 applied once → schedule charge 30.75 → `correction_amount` = **144.25**. **Base's cap**: the allowance applies on each of the two days → 2 chargeable items → schedule charge 61.50 → `correction_amount` = **113.50**.
- *Affected artifact and location.* `checking.extended.yaml`, `checking_ext_fee_schedule_correction.overwrite` (no entry against `checking_evt_overdraft_and_returned_item_fees`) and `.compute.schedule_charge`.
- *Relation to previous revisions.* Recorded in revision 1 as observation **CG-6** and carried through revision 2, because task 0's charges all fell on one business day. **Promoted** on check 1's categorical standard: the base sentence is displaced and unnamed, which is the defect whether or not a seed exposes it — exactly the ground on which K1 was returned.

---

## nothing regressed

Mechanical sweep over all seven policies on the revision-3 artifacts — **ALL PASS**, zero failures: every `compute_basis` entry verbatim in its own rule and every binding carrying one; every factor ladder `when` verbatim in its own rule; every `policy_source` verbatim in the blocked rule and absent from the depended-on rule; every `resolved_by` equal to the depended-on `target_tool`; no `fallback_reason` on a state-form edge; every `baseline.rule` sentence a verbatim rule sentence; no rule naming a tool or a policy id; every `overwrite` entry verbatim both ways; every `base_policy_refs` entry resolving. Factor structure unchanged: 4/4/4/4/4/4/6, ≥2 `parameter` and ≥2 `method` each, 3 cross-difficulty each, every ladder ≥3 tiers.

**Every figure reproduced.** Recomputed from scratch against the revision-3 charter on both unchanged worlds: **7 scored values, 7 `baseline_result` figures, 30 `factor_sensitivity` figures and 5 edge-load-bearing figures are identical to revisions 1 and 2**, as are both `evaluation_criteria` blocks, both `charter_scope` blocks and the step counts of 15 and 17. The four new REDs move no scored value on either seeded world — which is exactly why they survived three rounds of this audit and the render-layer pass, and exactly why the corrected threshold is needed.

Nothing that passed in revision 1 or 2 has regressed. Neither K1's nor K2's repair introduced a new defect: K2's rewording is lossless at every boundary tested and its floor is stated at exactly the strength the compute applies; K1's second declaration widens no retirement beyond the two grounds the difficulty writes.

## observations

**Closed this round:** none beyond K1 and K2 — the reworker acted on no observation this round, and the two it carried forward in the task dossier are noted in `0.md` and `1.md`.

**Standing, unchanged and with no demonstrated consequence on either world:** CG-3, CG-5 (now superseded by K1's closure), CG-7(2), CG-7(3), CG-7(4), CG-8, CG-9, CG-10, CG-11 (closed in revision 2), CG-12, T0/OBS-1, T1/OBS-2, R2-O1, R2-O2, R2-O3. CG-2, CG-6 and CG-7(1) are **withdrawn as observations** and reissued as R3-2, R3-4 and R3-3 above.

**New observations this round:**

**R3-O1 — observation — the reason given for K2's repair direction is false, though the direction is right.** The reworker argues the opposite resolution "has no exact expression in the restricted grammar". `MONTHS(F('opened_date'), NOW) + 1` parses and validates against the charter's own name set — `Add` is an allowed node. The sound reason, which was not given, is that "started months" is ambiguous prose admitting at least three renderings, so resolving toward it would leave the phrase naming none of them. No verdict turns on this; recorded because an audit verifies the proof submitted.

**R3-O2 — observation — `posted_shortfall` cites a sentence about a different quantity, and its floor is unstated.** `checking_ext_overdraft_courtesy_relief.compute.posted_shortfall` is `MX(0.0, RND(…, 2))` and its `compute_basis` cites "The shortfall standing on the account is **half** of the money by which the account's own entries leave it below zero" — the fall-through sentence of `shortfall_standing`, a different binding, in which the halving happens. `posted_shortfall` is the whole of that money, and its `MX(0.0, ·)` is stated by no sentence, though the rule's terminal exclusion ("An account whose entries leave it at or above zero is outside this rule") covers the same ground. No divergence on either world.

**R3-O3 — observation — `cd_principal` reads one certificate where the prose says "the owner's certificate principal".** `CFIELD('cd','principal_balance', status='active')` returns the first active certificate; an owner holding two would have the second silently ignored. Both seeded owners hold exactly one, and the prose is singular, so no divergence arises. Same family as R3-2 but materially weaker, and recorded as an observation rather than promoted.

## revision_3 verdicts

| item | before | revision 3 |
| --- | --- | --- |
| **K2** | SOURCE-POLICY RED (render layer) | **CLOSED** — wording lossless at every boundary tested; floor real, stated at exactly `MX(1.0, ·)`, no new divergence; repair direction right, its stated reason false (R3-O1) |
| **K1** | SOURCE-POLICY RED (render layer) | **CLOSED** — clause named verbatim by both policies that write the subject, one per ground; retirement covers the two grounds the difficulty uses and no more; no eligibility gate caught |
| CG-1, CG-4 | closed in revision 2 | **still closed** — re-verified; no regression |
| **R3-1** | never recorded | **SOURCE-POLICY RED (new)** — `assessed_count`; 0.00 vs 77.75 |
| **R3-2** | observation CG-2 | **SOURCE-POLICY RED (promoted)** — `mm_balance` unfiltered; 12000.00 vs 3400.00 |
| **R3-3** | observation CG-7(1) | **SOURCE-POLICY RED (promoted)** — opening-window condition; 4667.55 vs 4664.91 |
| **R3-4** | observation CG-6 | **SOURCE-POLICY RED (promoted)** — per-business-day cap; 144.25 vs 113.50 |
| R3-O1, R3-O2, R3-O3 | — | observations, no consequence on either world |

## closing_checklist — revision_3

**The difficulty does NOT close out at the source layer.**

| checklist item | revision 2 | revision 3 |
| --- | --- | --- |
| every comparison section carries a PASS | ✔ | **✘** — `0.md` carries four SOURCE-POLICY REDs (R3-1 through R3-4); `1.md` PASSes all four relationships |
| instantiation-stage gates re-run on the final form | ✔ cited | ✔ cited — all seven green on the current scripts, base-gate counts unchanged at 8 and 15 |

Every other row of the revision-1 checklist stands: policies fully covered, scopes pairwise disjoint, task tools and GT closed, uuid8s frozen and unreused, trees of 2 and 3 prerequisite problems with 2 and 2 `value_input` edges and an `owner=user` write each, the difficulty-wide graph a DAG, seven self-sufficient baselines each giving a definite value different from gold, 4–6 factors per computation with the required effect and source mix, every ladder ≥3 tiers stated in full, all 30 factors bearing weight, a near-miss per computation, and every scored figure stable across three rounds.

**All four new REDs lie in task 0's three policies** — `fee_schedule_correction` (R3-1, R3-4), the three unfiltered `mm_balance` policies (R3-2, all of which are task 0's), and `closure_payout` (R3-3). **None reaches task 1**, whose four policies have now been byte-identical for two consecutive rounds. Task 1 remains PASS on all four relationships.

A green gate block is again the qualification to enter this audit, not proof of correctness: all seven gates pass on the current scripts while four rule/compute and declaration divergences stand, because the gates test structure, references and parsability and none of them reads a sentence against the expression beneath it.

---

# revision_4

Round 4, 2026-09-16T11:56:19Z. Revisions 1 through 3 above are untouched. This round verifies the four repairs, applies the corrected standard revision 3 set out — check 1 categorical, check 2 as two-way losslessness rather than a citation check — and tests the two items the reworker found in its own sweep.

## what moved

| artifact | revision 3 | revision 4 | |
| --- | --- | --- | --- |
| `checking.extended.yaml` | `78b19529…85b3ef` | `1e59c44e57892df803140fe41e912194e6ed19202f55f8713bfe98d7dd55cb61` | **changed** |
| `task_tools.py` | `a22e33a5…85b9ef` | `a22e33a5…85b9ef` | unchanged |
| `blueprint/products/checking.yaml` | `635b57c4…166046` | `635b57c4…166046` | unchanged |
| `tasks/0.json` | `a779a071…77b15f` | `0836dd53a3929bb3ff5b1e1f7b79a494500c002168c13e527c10cf8ebaf46674` | changed |
| `tasks/1.json` | `e9f901a2…8dca0f` | `afbd5129f3621b413ac5b71253610158c2491f6ed963139516634f5e5070c362` | changed |
| `check_compute.py` | `bc8faae1…aa9944` | `bc8faae1…aa9944` | unchanged since round 3 |
| masked views | `be3ef7c5…` / `25d41c4f…` | identical | unchanged |

Masked views byte-identical for the fourth round: no seeded row moved. Base section still verbatim identical to the blueprint. The evaluator this audit runs on has not moved since round 3, so figures compare directly.

**Per-policy field diff, revision 3 → revision 4:**

| policy | changed fields |
| --- | --- |
| `fee_schedule_correction` | `rule`, `compute`, `compute_basis`, `factors`, `overwrite`, `cross_category`, `inputs` |
| `closure_payout` | `rule`, `compute`, `compute_basis`, `factors`, `overwrite`, `cross_category` |
| `dispute_credit_reversal` | `rule`, `compute`, `compute_basis`, `factors`, `cross_category` |
| `dispute_provisional_credit` | `rule`, `compute_basis`, `factors`, `cross_category` |
| `overdraft_courtesy_relief` | `rule`, `compute_basis`, `factors`, `baseline`, `cross_category` |
| `overdraft_protection_source` | `rule`, `compute_basis`, `factors`, `baseline` |
| `relationship_tier_conversion` | `rule`, `compute_basis`, `factors`, `baseline`, `cross_category` |

Unlike rounds 2 and 3 this was **not** a prose-only rework: `compute` changed in three policies. That is correct — three of the four findings were resolved toward the rule, which means moving bindings.

## R3-1 — verified CLOSED (resolved toward the rule)

`assessed_count` is rebound from `COUNT(… within_months=K('correction_review_months') …)` to `COUNT('checking_transactions', event_type='checking_fee', fee_code='overdraft_item')` — unwindowed, which is what "the number of overdraft charges **standing**" and "at least four overdraft charges **stand on the account**" say. `assessed_charges` correctly keeps its window, because its own sentence is the one that says "posted inside the review window". `inputs.history` was updated to drop `within_months` from the count entry, so the declared input set matches.

**The claim that the count changed while no scored value moved is verified in both halves.** On task 0 `assessed_count` goes **5 → 7**, and every threshold clears either way: three ladder tiers test `>= 4` (7 and 5 both clear), one tests `>= 2`, and `schedule_charge` takes `MN(assessed_count, day_cap)` with `day_cap` = 1, so `MN(7,1) = MN(5,1) = 1`. `day_cap` = 1, `per_item_charge` = 30.75, `charges_under_review` = 175.00 and `correction_amount` = **144.25**, all unchanged.

**And the divergence is gone where round 3 demonstrated it.** On the world that exposed it — task 0's seed with two of the five 2025-06-27 charges re-dated to 2025-05-27 — round 3 recorded compute **0.00** against rule **77.75**. Re-run on the revision-4 charter: `assessed_count` = 7, `day_cap` = 1, `per_item_charge` = 30.75, `charges_under_review` = 108.50, `correction_amount` = **77.75**. One reading, and it is the rule's.

**A coherence gain beyond the repair.** Every aggregate binding in the charter was re-read against the sentence it cites, asking whether the quantity clause is windowed. The charter now holds one convention throughout: *stands / standing* is unwindowed (`assessed_count`, `assessed_all`, `assessed_largest`, `credits_all`, `credits_largest`, `takebacks`, `corrections_standing`, `od_count`, `od_largest`, `foreign_item_count`, `foreign_largest`, `claim_credits_posted`), and *posted inside the … window* / *over the … window* / *in the last twelve months* is windowed (`assessed_charges`, `credits_recent`, `foreign_windowed`, `od_windowed`, `ri_windowed`, `ext_windowed`, `window_credits`, `refunds_granted_12m`, `courtesy_prior_12m`). `fee_schedule_correction` was the sole outlier and is now in line. One binding tripped my first pass — `credits_largest` — and is a false positive: its quantity clause is "only the largest single temporary credit entry counts", with no window, and the window phrase my scan caught ("in the last twelve months") belongs to the card-payment tier condition beside it. `MAX` is unwindowed and the pairing is correct, as for its three siblings.

## R3-2 — verified CLOSED, on both sides, and the residue was real

The reworker's account is **partial in a way worth correcting**: it describes a prose narrowing in seven policies, but the `compute` changed too. Both halves were needed and both were made.

| policy | `mm_balance` in revision 3 | in revision 4 |
| --- | --- | --- |
| `fee_schedule_correction` | `CFIELD('savings','current_balance', status='active')` | `… variant_name='Premier Money Market', status='active')` |
| `dispute_credit_reversal` | `… status='active')` | `… variant_name='Premier Money Market', status='active')` |
| `closure_payout` | `… status='active')` | `… variant_name='Premier Money Market', status='active')` |
| the other four | already variant-filtered | unchanged |

- **The half I raised** — three expressions reading *any* active savings row under a rule that said "money market balance" — is closed by adding the filter. The order-dependence goes with it: on task 1's two seeded savings rows presented in the other order, round 3 recorded **3400.00**; the revision-4 expression returns **12000.00** in either order.
- **The residue I did not name, and the reworker did** — the four already-filtered expressions read a single variant while the phrase "money market balance" named a wider class. It is real: the savings charter sells **three** money-market tiers, `Money Market Account`, `Premier Money Market` and `Private Client Money Market`. The prose was wider than every expression in the charter. Correctly found.

**Is narrowing seven rules to a tier name lossless against what the compute reads?** Yes. All seven rules now say "the owner's **premier money market** balance" and all seven expressions filter `variant_name='Premier Money Market'` with `status='active'`. The phrase picks out exactly one of the six savings variants — no other variant name contains "premier money market" — so prose and expression denote the same set, which is the definition of lossless here. The sibling phrase in `overdraft_protection_source` is handled the same way: "the owner's statement savings balance" against `variant_name='Statement Savings'`, and "the premier money market account is tried first and the statement savings account second" against `mm_id` / `stmt_id` filtered on those two names.

**Does leaving the persona unnarrowed open a gap?** No, and leaving it is the right call.

- Task 0's owner holds exactly **one** savings account and it is a Premier Money Market (`26eee0f8…`, 54200.00). "my money market", "the money market is the only savings account she has ever had here" resolves to that row and no other.
- Task 1's owner holds **two**, a Premier Money Market (`1e3886c8…`, 12000.00) and a Statement Savings (`d3f01445…`, 3400.00); "the money market" set against "the savings he opened when he joined the bank" separates them, and he declines to choose at all, deferring to the rules.
- The tier name is a field the agent **reads from the record** through `find_savings_accounts`, not a phrase the customer must utter. Nothing in the charter requires the customer to name a tier, and no other tier-named quantity is spoken by either persona — neither says "Premier Checking" either. Narrowing the personas would have made them less natural without making anything derivable that is not already derivable.

Two residues remain, both observations (R4-O1, R4-O2 below): the variant filter narrows the order-dependence without eliminating it, and an owner of one of the other two money-market tiers now reads as absent rather than as wrong.

## R3-3 — verified CLOSED, and CG-7(1) closes with it

A new binding carries the gate the rule stated and the compute ignored:

```
closing_charge_due: closing_charge if account_age_days <= P('early_closure_window_days') else 0.0
```

and `closing_payout` consumes `closing_charge_due` in all three of its rounding branches. The rule gained the matching sentence: "An account closed later than its opening window owes no closing charge at all, and the closing payout is then the money reconciled from the account's own entries together with the closing interest alone; the opening window runs for the tier's early closure window in calendar days counted with the day after the account was opened as day one, and an account closed on the last of those days is still inside it." It is `compute_basis.closing_charge_due` verbatim.

**No factor was handed a second job — checked, not assumed.** `closing_charge_due` is no factor's `decides`, appears in no factor's `bindings`, and appears in no factor's `baseline`. The four factors are untouched and still decide `closing_charge_level`, `closing_charge`, `closing_rate` and `closing_payout`; `closing_charge_basis` still substitutes `closing_charge`, which now flows through the gate rather than around it. The gate is one of three branching bindings in the charter that are not a factor's `decides` — with `target_tier` and `stmt_cover` — and like both of those its basis is verbatim in its rule, which is what makes it a stated gate rather than a hidden branch.

**The boundary matches base inclusively — tested at the edge.** Base `early_window`: "the fee applies when the closure date is on or before `opened_date` plus `early_closure_window_days`", `boundary: inclusive`. The expression is `account_age_days <= P('early_closure_window_days')`, which is the same relation. On task 0's world with `opened_date` moved so the age lands on the boundary: age **90 → `closing_charge_due` = 9.25** (last day inside), age **91 → 0.00** (first day outside). Exactly base's line, and the new sentence says so in words.

**The divergence is gone where round 3 demonstrated it.** Round 3, on task 0's world with `opened_date` moved to 2024-11-28 (age 232, outside the window), recorded rule **4667.55** against compute **4664.91**. Re-run on revision 4: `closing_charge` = 2.64, `closing_charge_due` = **0.00**, `payout_amount` = **4667.55**. The compute now produces the rule's number.

**The branch count is the structural gain claimed, not a side effect.** Counting `IfExp` nodes per policy: `closure_payout` **8 → 9**; every other policy unchanged; task 0's total **24 → 25** and task 1's **47 → 47**. The single added branch is `closing_charge_due` and nothing else moved, which is what the coordinator's 38 → 39 reflects under the gate's own counting. It is a real decision the rule states and the compute now makes.

**CG-7(1) closes at its root with it** — correctly, because CG-7(1) *is* R3-3: revision 1 recorded it as an unimplemented inherited provision and revision 3 promoted it on finding that the extended's own rule carried the condition.

## R3-4 — verified CLOSED

An `overwrite` entry now names the displaced base sentence verbatim: "Overdraft-item and returned-item fees together are limited to `overdraft_daily_item_limit` per account per business day, counted by `checking_msr_overdraft_item_fees_day`", against `checking_evt_overdraft_and_returned_item_fees`, replaced by the extended's own one-day-allowance sentence, verbatim in its rule.

**All 15 `overwrite` entries in the charter are verbatim in both directions** — `superseded_clause` in the named base policy's `rule`, `replaced_by` in the extended `rule` — with **zero** failures. The reworker's count and claim are exact.

**Retirement scope checked against all three of that base policy's eligibility conditions.** `active_only`, `debit_opt_in` and `one_fee_per_item` are each tested against every `overwrite` entry in the charter: **none is caught**. No gate is retired, which is what the unchanged SOLVABILITY base-gate counts of 8 and 15 corroborate.

## the two items the reworker found in its own sweep

**Self-found 1 — `posted_shortfall`, which is this audit's R3-O2. Verified closed on its merits.** A new sentence was added to `overdraft_courtesy_relief`: "The money by which the account's own entries leave it below zero is every debit posted to the account — paid items, charges and take-back entries — less every credit posted to it — deposits, refunds and goodwill entries, temporary credits, surcharge rebates and interest credits — rounded half-up to the cent and never taken below zero." It is verbatim in the rule and is now `compute_basis.posted_shortfall`, replacing the citation of a different binding's sentence. Checked term for term against `MX(0.0, RND(debits_out + fees_out + takebacks_out - deposits_in - refunds_in - interest_in - rebates_in - claim_credits_posted, 2))`: three debit terms named and three subtracted from; five credit terms named and five subtracted; and the order matches — rounded, then floored. **Composition and floor both now stated, losslessly.**

**Self-found 2 — an undefined phrase that collided with another policy's. Verified closed on its merits, and it was worth finding.** `relationship_tier_conversion` used "the account's own reconciled money" without defining it, while `closure_payout` uses "the money reconciled from the account's own entries" for a **seven-event-type** sum that it does define. The two compositions differ — the tier-conversion binding is `RND(SUM(checking_deposit) - SUM(checking_debit), 2)`, two event types — so one phrase carried two meanings across the charter and one of them was defined nowhere. The repair renames the tier-conversion quantity to "the account's own deposits less its paid items" and defines it: "the total of every deposit posted to the account less the total of every paid item posted to it, rounded half-up to the cent", which is the expression exactly. "reconciled money" now appears in `closure_payout` alone, where it is defined. The collision and the undefined phrase are both gone, and the re-render will carry a definition instead of inventing one.

## nothing regressed

**Mechanical sweep over all seven policies — ALL PASS**, zero failures: every `compute_basis` entry verbatim in its own rule and every binding carrying one; every factor ladder `when` verbatim; every `policy_source` verbatim in the blocked rule and absent from the depended-on rule; every `resolved_by` correct; no `fallback_reason` on a state-form edge; every `baseline.rule` sentence a verbatim rule sentence; no rule naming a tool or a policy id; all 15 `overwrite` entries verbatim both ways; every `base_policy_refs` entry resolving. This matters more than usual: the R3-2 repair reworded sentences in **all seven** policies, and rewording is exactly what breaks verbatim ladder and basis matches. None broke.

**Factor structure unchanged:** 4/4/4/4/4/4/6, ≥2 `parameter` and ≥2 `method` each, 3 cross-difficulty each, every ladder ≥3 tiers.

**Every figure reproduced, fourth round running.** Recomputed from scratch on both unchanged worlds: 7 scored values, 7 `baseline_result` figures, 30 `factor_sensitivity` figures and 5 edge-load-bearing figures **all identical to revisions 1, 2 and 3**, together with both `evaluation_criteria` blocks, both `charter_scope` blocks and the step counts of 15 and 17.

**The repairs introduced nothing new.** Three bindings changed and each was tested at its own boundary: the unwindowed count against every threshold that consumes it; the variant filter against both store orders of task 1's two savings rows; the gate at ages 90 and 91. The one added branch is owned by no factor and stated by its own rule sentence.

## observations

**Closed this round:** R3-1, R3-2, R3-3, R3-4, CG-7(1) (with R3-3), R3-O2 (self-found 1), and the undefined-phrase collision (self-found 2). **R3-O1 accepted** — the dossier records the correction and the sound ground, in its own words: "I argued that resolving K2 toward the rule had no exact expression in the restricted grammar; `MONTHS(F('opened_date'), NOW) + 1` parses and validates, and I had not checked that before asserting it."

**Left standing on the distinction this audit drew, and correctly so:** CG-7(2) (base's "The fee is reduced so it never takes the ledger balance below zero") and CG-7(4) (`overdraft_protection_source_eligible` never tested) are inherited base provisions the extended rule is **silent** about, not two rules fixing one quantity — which is the line revision 3 drew when it promoted R3-3 and declined to promote CG-7(4). Applied correctly. R2-O1 (`interest_bearing`) and CG-7(3) (mortgage) are of the same class and stand with them.

**Also standing, unchanged:** CG-3, CG-8, CG-9, CG-10, CG-12, T0/OBS-1, T1/OBS-2, R2-O2, R2-O3, R3-O3.

**New this round:**

**R4-O1 — observation — the variant filter narrows the order-dependence without eliminating it.** `Premier Money Market` carries `max_accounts_per_customer_this_tier: 2` in the savings charter, so an owner may hold two active ones, and `CFIELD` still returns `hs[0]`. The exposure is far smaller than R3-2's — it needs two accounts of one tier rather than any second savings account — and neither seeded owner has two. Same family as R3-O3 (`cd_principal`).

**R4-O2 — observation — an owner of the other two money-market tiers now reads as absent rather than as wrong.** With all seven expressions filtered to `Premier Money Market`, an owner holding a `Money Market Account` or a `Private Client Money Market` yields `mm_balance = None`, which the ladders then compare with `>=`. This is not a divergence — prose and expression agree that there is no premier money market balance — but it puts those owners into `CG-12`'s `None`-arithmetic family. Neither seeded owner is affected.

**Considered and not raised.** `overdraft_protection_source` opens "The protection source is the first of **the owner's own savings accounts**, tried in the order set below", which invites a wider class than the two variants the compute reads. It resolves: "the order set below" points at "the statement savings account first and the premier money market account second", and the middle tier says "whichever of **the two**", so the rule pins the candidate set to two before a reader can act on the general phrase. Recorded here so the sweep's coverage is visible, not as a finding.

## revision_4 verdicts

| item | before | revision 4 |
| --- | --- | --- |
| **R3-1** | SOURCE-POLICY RED | **CLOSED** — count rebound to unwindowed; 5 → 7 on task 0 with every threshold clearing; the divergence world now yields the rule's 77.75 alone; charter now on one convention |
| **R3-2** | SOURCE-POLICY RED | **CLOSED on both sides** — three expressions filtered *and* seven rules narrowed to the tier; lossless against what the compute reads; no persona gap |
| **R3-3** | SOURCE-POLICY RED | **CLOSED** — gate added, owned by no factor, boundary inclusive at exactly ages 90/91; the divergence world now yields the rule's 4667.55; branch count +1 and localized |
| **R3-4** | SOURCE-POLICY RED | **CLOSED** — base sentence named verbatim; 15/15 entries verbatim both ways; no eligibility condition caught |
| CG-7(1) | observation, then R3-3 | **CLOSED** with R3-3 at its root |
| R3-O2 | observation | **CLOSED** — composition and floor stated, lossless |
| undefined-phrase collision | not previously raised by this audit | **CLOSED** — phrase renamed and defined; collision with `closure_payout` gone |
| R3-O1 | observation | **ACCEPTED** by the reworker, sound ground recorded |
| K1, K2, CG-1, CG-4 | closed earlier | **still closed** — re-verified, no regression |
| R4-O1, R4-O2 | — | observations, no consequence on either world |

## closing_checklist — revision_4

### **The difficulty CLOSES OUT at the source layer.**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** | **PASS** |
| The problem tree holds | **PASS** | **PASS** |
| Factors bear weight | **PASS** | **PASS** |
| Policy → task unique solution | **PASS** | **PASS** |

| checklist item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ — revisions 1–3 preserved byte-for-byte above; `## revision_provenance` records the superseded pre-revision-1 audit at commit `427143d` |
| every comparison section carries a PASS | **✔** — no SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR or SOURCE-TASK RED remains in either task |
| extended policies fully covered, scopes pairwise disjoint | ✔ — 3 + 4 = 7, disjoint, each spanning its whole problem tree |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ — `task_tools.py` byte-identical for four rounds |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, an `owner=user` write each, no cycle | ✔ — 2 and 3 problems, 2 and 2 `value_input` edges, DAG |
| every computation: self-sufficient baseline giving a definite value different from gold | ✔ — 7/7 |
| 4–6 factors, 2 of each effect, 2 multi-source, 2 cross-difficulty, ladders ≥3 tiers stated in full | ✔ |
| every factor bears weight against an honest baseline | ✔ — 30/30, figures stable across four rounds |
| a genuine near-miss per computation | ✔ — 7/7 |
| instantiation-stage gates re-run on the final form | ✔ cited — all seven green under the current scripts; base gates 8 and 15; branch mean 56.00 |

Eighteen observations stand on record across the four revisions. None demonstrates a consequence on either seeded world, and each is recorded with the world fact that masks it, so a later task built on this charter is not caught by one unwarned.

A closing note this audit is obliged to keep making about itself: the green gate block is again the qualification to enter, not the finding. Across four rounds this difficulty passed every gate every time while eight defects of the rule/compute and declaration classes stood — two of which only a render-layer reader caught, and four of which this audit had itself written down as observations under a threshold that was wrong. What closes the difficulty is the reading, not the block.
