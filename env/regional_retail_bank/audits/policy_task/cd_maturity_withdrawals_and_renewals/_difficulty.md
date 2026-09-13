# Policy-task audit — cd_maturity_withdrawals_and_renewals / charter-global

## charter_global_frozen

- freeze time: 2026-09-12T19:23:29Z (file mtime of the completed charter-global section, written before any task's GT was revealed; it contains nothing derived from a revealed GT). Pre-reveal sha256 eb0725fbfe312b648b43bb6943e355309a9edf63bc3f4370303ce2f5989dc881. GT reveal began at 2026-09-12T19:27:17Z.
- auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the author of the artifacts
- frozen inputs (sha256):
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/cd.extended.yaml` d947404d7c4650b7b7eeb30f4c98ac4c0d123d8df9b40f0c0bdd73dcdf912205
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/task_tools.py` 81ab63ad81355c784573787d6c8e5b82e017035c214e67ba4611d40fdd6d6641
  - `env/regional_retail_bank/blueprint/products/cd.yaml` 7a14550e7c6bc9cfc2f59401c8032dd5371b4809ce2874ec58315695dc044aa8
  - `env/regional_retail_bank/blueprint/db_schema.json` e5cf164d9f3a18fbf3bb5b53a7d65e828a35873ef6eb470162f5b29a9cbdba7a
  - `env/regional_retail_bank/blueprint/share_tools.py` 7b7ec28e118fa3ff7eeefc0a9db02d2de87143232a1ff0effe601b1bbb765d87
  - `env/regional_retail_bank/blueprint/blueprint.yaml` 61655924be9b095fe53a5a783e4c99f485cd197d3d7feef5df0b3eeb338ab54a
- permitted: blueprint (cd charter, schema, share tools, checking/savings charters for cross-category parameter lookup), the extended charter, task_tools.py, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics only), and the orchestrator's masked views (frozen_time, user_scenario, initial_state).
- masked / unread at the time of this section: every field of `tasks/*.json` except the three above (design_rationale, db_closure*, solvability_contract, evaluation_criteria, prerequisite_closure, charter_scope, required_documents, computations); no prior audit of this difficulty exists.

### entry_conditions (Step 0)

- Gate snapshot supplied by the orchestrator: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all exit 0. Cited, not re-run.
- Masked views supplied with hashes; re-hashed on disk and matching (task_0 view fd5516af…, task_1 view 15702de0…; extended yaml and task_tools.py hashes identical to the manifest).
- Incomplete input (recorded, not a RED): `check_traceability` is absent from the snapshot; the orchestrator defers it until the KB is published.
- Base copy: lines 1-1072 of the extended yaml are byte-identical to `blueprint/products/cd.yaml` (only a trailing blank line differs); after parsing, all ten base keys compare equal. The base copy is verbatim.

### policy_conflict_scan

Structured policy surface: 11 base policies + 7 extended policies + 1 workflow.

| id | trigger | subject | target_tool | computes | prerequisite |
| --- | --- | --- | --- | --- | --- |
| P1 cd_ext_penalty_rate_reversal | state_due | cd_penalty_reversal | reverse_penalty_error_2ccc5de3 | amount | [] |
| P2 cd_ext_closed_payout_instruction | state_due | cd_update_instructions | update_maturity_instruction_96ab509d | renewal_instruction | [] |
| P3 cd_ext_post_grace_renewal_rate | state_due | cd_renew | renew_certificate_term_21cb639a | interest_rate | P1 (value_input), P2 (state_gate) |
| P4 cd_ext_term_add_on_amount | on_request | cd_deposit | add_term_deposit_5f936ecf (user) | amount | P3 (value_input) |
| P5 cd_ext_grace_withdrawal_penalty_reversal | state_due | cd_penalty_reversal | reverse_grace_penalty_e6d62385 | amount | [] |
| P6 cd_ext_interest_payout_repoint | state_due | cd_update_instructions | update_interest_disposition_67b383bc | payout_account_id | [] |
| P7 cd_ext_grace_jumbo_top_up | on_request | cd_deposit | add_grace_deposit_522b16cc (user) | amount | P5 (value_input), P6 (state_gate) |
| W cd_wf_post_grace_renewal_and_add_on | — | — | P1 → P2 → P3 → P4 tools | — | [] |

Overlapping subjects, pairwise:

- **cd_penalty_reversal (P1, P5).** Disjoint triggers (P1: rate or penalty days differ from the charter's; P5: penalty posted on day 1..grace_period_days after maturity_date). They overlap on a grace-withdrawal penalty that is also booked at a non-charter rate. Both would then reverse the same booked amount, through two different tools, and the per-certificate dedup lets only the first one through. No text says which tool governs that overlap. Neither task world reaches it (task 0's penalty is not in grace; task 1's penalty matches the charter rate). Recorded as observation O14.
- **cd_update_instructions (P2, P6).** Both are state_due and both are keyed on "the payout account it names has been closed". Both read that account from the single field `cd_certificates.payout_account_id`, and both target tools overwrite that same field (`update_maturity_instruction_96ab509d(..., payout_account_id)`, `update_interest_disposition_67b383bc(..., payout_account_id)`). No sentence orders the two. When a payout `renewal_instruction` and a payout `interest_disposition` name the same closed account, applying P6 first makes P2's condition false. This is **finding G4**, and its consequence is demonstrated in task 0.
- **cd_deposit (P4, P7).** State-disjoint: P4 requires `status == 'active'` and P7 requires `status == 'grace_period'` within the grace window. No conflict.
- **cd_renew (P3 only).** It is consistent with base cd_evt_maturity_and_grace. The due day P3 uses (day > grace_period_days) is the first day after the last grace day that P5 and P7 allow (day ≤ grace_period_days). The anchors are consistent.
- **Cross-category reads.** checking is read by P1, P3, P5 and P6; savings by P2, P4, P5, P6 and P7. All are reads of status, tier, opened_date, ids or current_balance, and none writes another category. No boundary conflict.
- **Terminal states.** P3 moves grace_period to active, which base allows (`grace_period -> active by system`). P4 and P7 raise principal. P1 and P5 raise principal. P2 and P6 update fields only. No terminal-state conflict beyond G4.

Scope exclusivity and completeness, judged from the problem trees the charter declares (the tasks' charter_scope is masked until the reveal): the P1-P2-P3-P4 tree and W form one scope, and the P5-P6-P7 tree forms the other. They share no node. Together they cover all 7 extended policies and the single workflow. The blueprint claims the event types cd_withdrawal, cd_penalty, cd_close and cd_bump_rate, but no extended policy or task tool writes them (observation O10).

### rule_compute_equivalence

DSL semantics are taken from `skills/erl-task-instantiate/scripts/check_compute.py::build_env`. SUM, COUNT, MAX and LATEST are scoped to the holding. `CFIELD(cat, field, **eq)` returns the field of the *first* matching row of that category for the same customer. `DAYS(a, b)` is `(b - a).days`. `within_months=1` keeps rows whose `MONTHS(posted, NOW)` falls in [0, 1). `RND` is Python `round(float, 2)`.

Every binding of every extended policy has a `compute_basis` quotation that is locatable verbatim in its `rule`. Sweeping back sentence by sentence:

- **P1.** pen_amount ("largest cd_penalty amount"), pen_rate, pen_days and pen_date ("read from the most recent cd_penalty entry"), prior_reversals, standard_at_start, relationship_earned, charter_rate, charter_days ("no more than six calendar days after the term_start_date" → `DAYS(...) <= 6`), misassessed (tolerance 0.001) and result all match. Non-equivalences:
  - The rule is existential ("an active checking account of a tier listed …"), but `checking_tier` / `checking_opened` read the first active checking row only (O1).
  - The rule checks against "the term in which the withdrawal was taken", but compute rebuilds the rate from the *current* term's certificate fields. A penalty from an earlier term would be judged against the wrong term (O2).
  
  Neither bites a task world. Task 0 has one checking account, one penalty and renewal_count 0. Task 1 has one active checking account and one penalty in the current term.
- **P2.** instr, pays_out, payout_status, payout_closed, renew_offered and result match. Three rule sentences have no binding:
  - "recorded … at the latest on the day after the grace period ends": compute has no time bound (O5).
  - "replaced on the record by an active checking or savings account of the owner that the owner names": this is a tool argument supplied by customer input, not a computed value, which is admissible.
  - "a mail_check instruction pays the whole balance by official check": this needs no write.
- **P3.** in_grace, days_after, due (`days_after > grace_period_days`), auto (including `auto_renew_available`), same_tier, the five ledger sums, principal, jumbo, relationship, new_rate (+ bonuses, `RND(…, 2)` once at the end) and result all match. The rule defines apy ("standard_apy plus the same bonus points"), but it is not computed, because `computes: interest_rate` only. relationship uses the first active checking row (O1).
- **P4.** active, offered, funded, last_addon_date / in_term (posted_date ≥ term_start_date), prior_total, count_left, term_room, ceiling_room, funding_room, amount (smallest of three, `RND`) and result all match.
  - count_left equals base cd_msr_term_add_ons for every tier, because term_add_on_max_count ≤ 1 on all six variants.
  - funding_room reads the first active savings row, where the rule says "that savings or money market account" (O1).
  - The concentration-cap sentence has no binding. It restates the inherited base eligibility `cd_agg_combined_principal.concentration_cap` (applies_to cd_deposit), so it is not an empty promise of its own.
- **P5.** pen_amount, pen_date, taken_in_grace (`1 <= DAYS(maturity_date, pen_date) <= grace_period_days`), proceeds_account ("most recent cd_withdrawal"), paid_to_owner (`CFIELD` scoped to the same customer), prior_reversals and result all match. The rule reads the proceeds account from the most recent withdrawal, not from the withdrawal the penalty points at through source_item_id (O3). In task 1 they are the same row, 7846e65b….
- **P6.** disp, to_checking, payout_status, payout_closed, same_kind_active, other_kind_active and result all match.
  - same_kind_active reads the first active row, where the rule says "the owner's active account of the same kind" (O1).
  - The fallback "the disposition becomes compound" is a tool argument, not computed.
- **P7.** in_grace, renews_same, tier_ok, the ledger sums, principal, prior_grace, shortfall, top_up, funding, fits and result all match.
  - prior_grace (`within_months=1`) agrees with base cd_msr_grace_add_ons (from the day after maturity_date through the frozen date) wherever in_grace holds. In that case frozen − maturity ≤ 10 days, and any earlier grace period lies ≥ 6 months back. Equivalent on the evaluated domain.
  - funding reads the first active savings row (O1).
  - **The rule sentence "New money added during grace joins the principal of the renewed term, so before it is added, a payout disposition that names a closed payout account is repointed to an open account of the owner" is implemented by no binding and quoted by no `compute_basis` entry.** No term of P7's compute reads `interest_disposition` or `payout_account_id`. P7 has no `eligibility` of its own, and none of its base refs (cd_evt_maturity_and_grace, cd_agg_combined_principal, cd_open_and_funding, cd_evt_term_add_on, cd_rate_and_bonuses) gates a deposit on the payout account. This is **finding G5**.

Every other ordering sentence in the charter's rules has a compute counterpart:

| Rule sentence | Compute binding |
| --- | --- |
| P3: "a payout instruction that must be replaced is replaced before the renewal is booked" | `auto` |
| P3: "Every penalty reversal owed … is posted before the renewal is booked" | `reversals` |
| P4: "… has that renewal booked first" | `active` / `in_term` |
| P7: "Every penalty reversal owed … before the shortfall is measured" | `reversals` |

G5 is the only ordering sentence without one.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (2ccc5de3, amount), (96ab509d, renewal_instruction), (21cb639a, interest_rate), (5f936ecf, amount), (e6d62385, amount), (67b383bc, payout_account_id) and (522b16cc, amount). Each is claimed by exactly one policy.
- Docstrings give each tool one business reading:
  - reverse_penalty_error: early withdrawal penalty, bank-error correction.
  - reverse_grace_penalty: penalty on money taken out during a grace period.
  - update_maturity_instruction: maturity instruction + payout account; interest disposition left as is.
  - update_interest_disposition: disposition + payout account; maturity instruction left as is.
  - renew_certificate_term: new term.
  - add_term_deposit: in-term add-on on an active certificate.
  - add_grace_deposit: grace add-on.
- Two of the tools write the same field `payout_account_id`, which is the substrate of G4.
- Tool bodies (task_tools.py lines 43-54, 86-89, 137-148, 185-198, 227-238, 268-271, 308-321) perform one write each. None reads a policy parameter, checks status, due dates, instruction or ownership, or refuses on business grounds. No tool judges a prerequisite.
- Invented procedure: none. No tool or workflow step adds a confirmation, review or wait.
- renew tool docstring: `maturity_date` is described as "last day of the new term". The policy fixes it as "matures term_months calendar months later" (O9).
- uuid8s: 2ccc5de3, 96ab509d, 21cb639a, 5f936ecf, e6d62385, 67b383bc, 522b16cc. All seven are distinct. None shares a prefix or suffix of more than one hex character with another, none is a sequence or an adjacent value, and none is a tail-mutated copy. They are consistent with independent generation. Reuse across other difficulties was not checked, because read isolation forbids opening sibling task directories; the orchestrator's check_task_tools gate is green.

### prerequisite_graph

- `prerequisite` is filled on all 7 extended policies and on the workflow (`[]` where empty). Every `problem` names an extended policy id in this file. None names a base policy, and none names itself.
- Edges: P3→P1, P3→P2, P4→P3, P7→P5, P7→P6. They form two disjoint trees, and the graph is acyclic.
- Per-edge checks:

| Edge | kind / gate | policy_source verbatim in rule? | condition vs cited sentence | resolved_by makes effect hold? |
| --- | --- | --- | --- | --- |
| P3←P1 | value_input / `reversals` (binding exists in P3) | yes: "Every penalty reversal owed on the certificate is posted before the renewal is booked, because the jumbo bonus is judged on the principal on the renewal date." | same | yes: 2ccc5de3 creates a cd_penalty_reversal row, and `reversals` sums it |
| P3←P2 | state_gate / `cd_certificates.renewal_instruction` (`auto` in P3) | yes: "A certificate renews only under the auto_renew instruction, so a payout instruction that must be replaced is replaced before the renewal is booked." | same | yes: 96ab509d writes renewal_instruction |
| P4←P3 | value_input / `active` (binding exists in P4) | yes: "A term add-on is made on an active certificate, so a certificate still in grace_period status whose renewal is due has that renewal booked first; the renewal starts a new term, and an add-on of the previous term no longer counts." | same | yes: 21cb639a writes status=active and term_start_date |
| P7←P5 | value_input / `reversals` (binding exists in P7) | yes: "Every penalty reversal owed on the certificate is posted before the shortfall is measured, because a reversal credit is principal and the jumbo bonus is judged on principal." | same | yes |
| P7←P6 | state_gate / `cd_certificates.payout_account_id` | yes: "New money added during grace joins the principal of the renewed term, so before it is added, a payout disposition that names a closed payout account is repointed to an open account of the owner." | same wording | 67b383bc does write payout_account_id, but the gate the effect describes ("the grace add-on may be taken") exists in no P7 eligibility and no P7 compute binding. See G5. |

- Notes on the P4←P3 edge: `gate: active` is a boolean state binding. The value channel is the renewal's new term_start_date, which moves the previous add-on out of `in_term` and so changes prior_total, count_left and term_room (O7). The edge passes check 7 literally.
- No prerequisite field uses authoring-viewpoint phrasing ("in this task", "at the opening", "the current world").
- Because every edge's policy_source is quotable from its rule, no prerequisite is undiscoverable from the policy surface.

### override_declarations

This is the sentence-by-sentence sweep of each extended policy against each of its `base_policy_refs`, recording findings only. Each task file demonstrates what a finding costs against its own world.

**P1 cd_ext_penalty_rate_reversal** (`overwrite: []`; refs cd_evt_penalty_reversal, cd_evt_early_withdrawal, cd_rate_and_bonuses)

- cd_evt_penalty_reversal:
  - "reversed in full, never in part, as one cd_penalty_reversal row whose source_item_id is the penalty row": followed.
  - "reversed with adjustment_reason bank_error when … at a penalty_days or rate other than the charter's": followed.
  - "A penalty can be reversed at most once": **handled differently**. The base contract is per penalty (`dedup_contract.object_bindings {source_item_id}`). P1 is per certificate: "A certificate whose ledger already carries a cd_penalty_reversal entry is not reversed again." The difference is not declared. See G1.
- cd_evt_early_withdrawal:
  - "The penalty equals the penalty basis times interest_rate …", with penalty_rate_basis = "the interest_rate on the certificate": **handled differently**. P1's "charter rate" is an anonymous intermediate: standard_at_start + jumbo (if applied) + relationship (if *earned from the checking record*). It equals the certificate's interest_rate only when relationship_bonus_applied agrees with the checking record. The difference is not declared. See G2.
  - penalty_days sentence: P1 anchors on term_start_date where base says "within six calendar days after funding". These differ only for a renewed term, where days 1-10 after the new term_start are grace days and carry no penalty, so the two can never disagree. Followed.
- cd_rate_and_bonuses:
  - "A bonus that is later lost, for example by closing the qualifying checking account, stays in the rate until the term ends": **handled differently**. P1 requires "its active status" today, so a lost bonus is removed from the charter rate. The difference is not declared. See G2.
  - The other sentences are followed.

**P2 cd_ext_closed_payout_instruction** (`overwrite`: names cd_evt_maturity_and_grace's payout clause)

- The named replacement is declared, and the merged semantics are unique: a payout to a closed account becomes auto_renew where auto_renew_available.
- cd_instructions:
  - "A change to the renewal instruction must be recorded before the grace period ends to govern this maturity; a change recorded after that governs the next maturity" is not named. P2 records the replacement "at the latest on the day after the grace period ends".
  - The conclusion is nevertheless the same under both readings. The declared overwrite fixes this maturity's outcome from the instruction in force when grace ends ("cannot be carried out when the grace period ends and is replaced by auto_renew"), and it does so independently of the recording date. No divergent conclusion, so this is observation O4.
  - "The payout account must be … active … when the instruction is recorded": followed.

**P3 cd_ext_post_grace_renewal_rate** (`overwrite: []`)

- cd_rate_and_bonuses:
  - Rate = standard + stacked bonuses: followed.
  - Jumbo on "principal_balance on the renewal date after any grace-period add-ons and withdrawals": followed. P3 reconciles from the ledger, which equals principal_balance on every ledger-consistent record, and orders owed reversals before booking.
  - Relationship bonus on the renewal date: followed.
  - renewal_rate_basis published_on_maturity_date: followed. Published rates are the variant parameters.
- cd_evt_maturity_and_grace:
  - "On the day after the grace period ends … under auto_renew it renews into renewal_target_tier … with a new term starting on the maturity date": followed.
  - "honored only where auto_renew_available": followed.
- P3 narrows itself to same-tier renewals ("a renewal into a different tier is outside it"). This is a scope limit, not a changed quantity.

**P4 cd_ext_term_add_on_amount** (`overwrite: []`)

- cd_evt_term_add_on: every sentence is followed (count and total via the most recent in-term add-on, ≤ maximum_opening_deposit, active only, no maturity change).
- cd_agg_combined_principal: restated.
- cd_open_and_funding: the PCB-account debit and same-owner rule are followed; the funding_room cap is additive.
- cd_evt_maturity_and_grace: "After the grace period ends, any withdrawal is again an early withdrawal of the new term" is consistent.
- No undeclared override.

**P5 cd_ext_grace_withdrawal_penalty_reversal** (`overwrite: []`)

- cd_evt_penalty_reversal:
  - "on a grace-period withdrawal" → bank_error reversal, in full: followed, and extended to "whatever withdrawal kind the entry was recorded under". That is consistent with cd_evt_maturity_and_grace's "A grace withdrawal is kind grace_period and carries no penalty".
  - "A penalty can be reversed at most once": **handled differently**. The dedup is per certificate. See G1.
- Base reverses every penalty on a grace-period withdrawal. P5 **adds a condition**: "the proceeds … must have gone to a checking or savings account that belongs to the certificate's owner". Base cd_evt_early_withdrawal (inherited into grace payouts through payout_methods [checking, savings, official_check]) lets the owner's proceeds go "by official check", with an empty counterparty. The difference is not declared. See G3.

**P6 cd_ext_interest_payout_repoint** (`overwrite: []`)

- cd_instructions:
  - Active same-customer payout account: followed.
  - Disposition within interest_payout_options: followed.
  - "takes effect from the next crediting date": followed.
  - "The owner may change …": P6 is a bank-owed change. Base grants the owner a permission and forbids no bank-side correction.
- cd_evt_interest: "otherwise the interest compounds for that period" is a per-period fallback while the record names an unusable account. P6 changes the record for future periods, which is not the same quantity at the same time.
- No undeclared override. See G4 for its interaction with P2.

**P7 cd_ext_grace_jumbo_top_up** (`overwrite: []`)

- cd_evt_maturity_and_grace: grace window, add-on min and grace cap via cd_msr_grace_add_ons are followed (equivalent window, see rule_compute_equivalence).
- cd_rate_and_bonuses: jumbo judged on principal at renewal is followed.
- cd_agg_combined_principal and cd_open_and_funding: followed.
- cd_evt_term_add_on: not engaged, because the certificate is in grace.
- No undeclared override. The repoint-before-deposit sentence adds an order that no base sentence imposes. See G5.

### findings

Each finding names the tasks it bears on. Those task files carry the demonstration.

- **G1 — SOURCE-POLICY (charter-level, latent).**
  - Symptom: base dedup is per penalty; P1 and P5 dedup per certificate.
  - Evidence: base cd_evt_penalty_reversal: "A penalty can be reversed at most once." with `dedup_contract: {table: cd_transactions, mode: separate_record, object_bindings: {source_item_id: source_item_id}}`, and "A penalty is reversed with adjustment_reason bank_error when it was assessed contrary to this charter: on a grace-period withdrawal …". P1 and P5 each say: "A certificate whose ledger already carries a cd_penalty_reversal entry is not reversed again." Both have `overwrite: []`.
  - Demonstrated consequence on a constructed situation: a certificate has penalty X, already reversed, and a later penalty Y on a grace-period withdrawal. Base reverses Y for its booked amount. P5 computes `prior_reversals = 1` and writes 0.
  - Affected: cd.extended.yaml P1 (rule last sentence, compute `prior_reversals`, `result`) and P5 (same).
  - Bears on: task 0 (P1) and task 1 (P5). In both worlds the ledger has exactly one penalty and no prior reversal, so the two readings coincide (see the task files).
- **G2 — SOURCE-POLICY (charter-level, latent).**
  - Symptom: P1's charter rate replaces base's certificate-interest-rate penalty basis and drops a lost bonus that base keeps in the rate.
  - Evidence:
    - Base parameter_schema: penalty_rate_basis "'certificate_interest_rate' means the interest_rate on the certificate". cd_evt_early_withdrawal: "The penalty equals the penalty basis times interest_rate divided by 100 …". cd_rate_and_bonuses: "A bonus that is later lost, for example by closing the qualifying checking account, stays in the rate until the term ends".
    - P1: "relationship_apy_bonus points are added when the owner held on the term_start_date an active checking account …, judged from that checking account's tier, its active status and an opened_date on or before the term_start_date". Compute: `checking_tier: CFIELD('checking', 'variant_name', status='active')`. `overwrite: []`.
  - Demonstrated consequence on a constructed situation: an 18-Month certificate with interest_rate 3.58 and relationship_bonus_applied true, whose owner closed the qualifying checking account mid-term. A penalty of 20125.00 × 3.58% × 180/365 = 355.30 is booked at rate 3.58, which is base-correct, so base does not reverse it. P1 computes charter_rate = 3.43 + 0 = 3.43, |3.58 − 3.43| > 0.001, and reverses 355.30.
  - Affected: P1 rule sentences 5-6 and compute `checking_tier`, `relationship_earned`, `charter_rate`.
  - Bears on: task 0. In its world Premier Checking is active and opened 2016-03-01, so the charter rate equals the certificate rate, 3.58.
- **G3 — SOURCE-POLICY (charter-level, latent).**
  - Symptom: P5 withholds the reversal of a grace-withdrawal penalty whose proceeds went by official check.
  - Evidence: base cd_evt_penalty_reversal reverses "on a grace-period withdrawal". Base payout_methods [checking, savings, official_check], and cd_evt_early_withdrawal says "Proceeds go by one of payout_methods to an account of the same customer or by official check". P5: "the proceeds of the withdrawal must have gone to a checking or savings account that belongs to the certificate's owner"; compute `paid_to_owner` is false for counterparty ''. `overwrite: []`.
  - Demonstrated consequence on a constructed situation: a grace withdrawal by official check with a penalty. Base reverses it; P5 writes 0.
  - Affected: P5 rule sentence 4 and compute `proceeds_account`, `paid_to_owner`.
  - Bears on: task 1. In its world the proceeds went to the owner's Interest Checking d9c9a0f9…, so the readings coincide.
- **G4 — shared-field order conflict between P2 and P6.** Consequence is SOURCE-TASK in task 0.
  - Symptom: two state_due policies read "the payout account it names" from the one field `cd_certificates.payout_account_id`, and each target tool overwrites that field. The charter never orders them.
  - Evidence:
    - P2: "When a certificate's renewal_instruction is pay_out_to_checking or pay_out_to_savings and the payout account it names has been closed, the instruction cannot be carried out when the grace period ends and is replaced by auto_renew …"; "a payout instruction whose payout account is not closed [is] left as [it is], and nothing is written."
    - P6: "When a certificate's interest_disposition is pay_to_checking or pay_to_savings and the payout account it names has been closed, the disposition is repointed: … the payout account on record becomes the owner's active account of the same kind".
    - Tool signatures: 96ab509d and 67b383bc both take `payout_account_id`.
    - The workflow `order_rationale` discusses no P6 step, and no rule sentence places P6 after P2.
  - Consequence is demonstrated in `0.md`.
  - Affected: P2 and P6 rules and computes (`payout_status`), and task 0's seed, where both instruction and disposition point at the closed 54cb0521….
- **G5 — state_gate with no gate (checks 2 and 7).** Consequence is SOURCE-CHAIN in task 1.
  - Symptom: the P7←P6 edge is `kind: state_gate, gate: cd_certificates.payout_account_id`, but P7 has no eligibility and no compute term on payout_account_id or interest_disposition, and no base ref of P7 gates a deposit on it. The sentence behind the edge is implemented by nothing.
  - Evidence: P7 compute (in_grace, renews_same, tier_ok, deposits … fits, result), where no payout term appears; P7 compute_basis, where the sentence is not quoted; P7 `prerequisite[1]`.
  - Consequence (the edge does not bear weight) is demonstrated in `1.md`.
  - Affected: P7 rule sentence 5, `prerequisite[1]`, compute.

Observations (not grounds for rework; no consequence demonstrable in either task world):

- **O1.** CFIELD first-row reads stand where the rule is existential or definite: P1/P3 checking tier, P4/P7 funding savings, P6 same-kind account. Both task worlds hold at most one active account of each kind.
- **O2.** P1 takes the amount from the largest penalty and the rate, days and date from the most recent penalty, which may be different rows. It judges them against the current term.
- **O3.** P5 reads the proceeds account from the most recent withdrawal, not from the penalty's source_item_id.
- **O4.** cd_instructions' recording-timing sentence is not named in P2's overwrite; the conclusions coincide (see above).
- **O5.** P2's compute has no binding for "at the latest on the day after the grace period ends".
- **O6.** The workflow `dataflow` lists only step 2→3 on `status`.
  - It omits step 0→2 (the reversal credit feeds P3 `reversals` / `jumbo`), step 1→2 (`renewal_instruction` feeds P3 `auto`) and step 2→3 on `term_start_date` (feeds P4 `in_term`).
  - It also asserts that the status write establishes `cd_agg_combined_principal.concentration_cap`. That gate counts every certificate whose status is not closed, so grace_period→active does not change it.
- **O7.** The P4←P3 edge is value_input with a boolean gate name (`active`). The value channel is term_start_date.
- **O8.** The workflow in the charter carries no `requires_external_wait` / `zero_wait_proof`. Per erl-task-instantiate these live in the task's `solvability_contract`, masked until the reveal.
- **O9.** The renew tool describes `maturity_date` as "last day of the new term". The policy fixes it as term_start_date + term_months. Base interest accrues "through the day before maturity_date", which invites a day-before reading, but the policy text excludes it.
- **O10.** The blueprint claims cd_withdrawal, cd_penalty, cd_close and cd_bump_rate, but no extended policy or task tool writes them.
- **O11.** `RND` is binary-float `round`, not decimal half-up. No scored value in either task sits on a half-cent tie.
- **O12.** add_term_deposit and add_grace_deposit post no savings-side debit, although base cd_open_and_funding says the debit happens "through the deposit's trigger". This is a tool-effect gap, and no scored value depends on it.
- **O13.** check_traceability is deferred.
- **O14.** The P1/P5 overlap on a grace penalty booked at a non-charter rate has no tool precedence.

## closing_checklist

This section was written after both reveals (2026-09-12T19:27:17Z onward). It is the only part of this file that depends on revealed GT. **The difficulty does not close**, because not every task passes all three relationships.

### Per-task verdicts

| Task | Policy self-consistency | Problem tree | Unique solution | File |
| --- | --- | --- | --- | --- |
| 0 | charter-level SOURCE-POLICY RED G1, G2 on claimed P1 (latent: no divergent value in this world) | **SOURCE-CHAIN RED** (T0-2: design_rationale's "renewal 3.93" counterfactual; recomputed 3.83. The tree itself holds and matches prerequisite_closure value for value.) | **SOURCE-TASK RED** (T0-1: the P6-before-P2 order gives a second defensible terminal state, from G4) | `0.md` |
| 1 | charter-level SOURCE-POLICY RED G1, G3 on claimed P5 (latent: no divergent value in this world) | **SOURCE-CHAIN RED** (T1-1: the P7←P6 edge does not bear weight, leaving 1 load-bearing prerequisite, from G5) | PASS | `1.md` |

### Checklist

1. **Audit files.** `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them. This is the first round, so there are no older revisions. Both comparison sections are complete, but neither is PASS on all three relationships.
2. **Coverage and scope.**
   - charter_scope (revealed): task 0 = {P1, P2, P3, P4, W; 2ccc5de3, 96ab509d, 21cb639a, 5f936ecf} and task 1 = {P5, P6, P7; e6d62385, 67b383bc, 522b16cc}.
   - The two scopes are pairwise disjoint, and together they cover all 7 extended policies.
   - There is exactly one workflow, claimed only by task 0. Each of the 7 task tools belongs to exactly one scope. The uuid8s show no sign of batch derivation.
   - Scope exclusivity by *claim* holds. However, task 0's world ignites P6, which task 1 claims, at the opening (see G4 and T0-1). The cross_fire gate reported SCOPE OK and did not surface this.
3. **Problem trees.**
   - Task 0: 3 prerequisites, 2 value_input edges, acyclic, every edge load-bearing.
   - Task 1: 2 prerequisites declared, 1 value_input edge, acyclic, but only 1 edge is load-bearing (T1-1). The "at least 2 prerequisites" requirement is not met in substance.
   - Difficulty-wide, the edges P3→P1, P3→P2, P4→P3, P7→P5 and P7→P6 form two disjoint DAGs. There are no cross-task edges and no cycle.
4. **Gate re-run on the final form.** Not performed. The difficulty does not close, and this audit changed no audited artifact. The orchestrator's gate snapshot in `### entry_conditions` stands, with check_traceability still deferred.

### Difficulty verdict

The difficulty does **not** pass the source-layer audit. Four findings stand in the way:

- charter-level SOURCE-POLICY G1, G2 and G3 (latent);
- G4, which surfaces as SOURCE-TASK in task 0;
- G5, which surfaces as SOURCE-CHAIN in task 1;
- the proof-assertion error T0-2 (SOURCE-CHAIN in task 0).

---

## revision_2

Re-audit after rework. Everything above this line is revision 1 and is left untouched.

### charter_global_frozen (r2)

- Started 2026-09-12T19:42:53Z. Written before any round-2 GT field was read.
- Auditor: the same independent auditor as round 1.
- Frozen inputs (sha256):

  | File | Round 2 | Round 1 |
  | --- | --- | --- |
  | cd.extended.yaml | 701fe9cabd7bf07a80df0e013a6bc2172f864a04e5ecf1866d13ea79a51d6c2c | d947404d… |
  | task_tools.py | d2dc551eec2c627b7e1ae048299ca450e5aee33f9bd1800417a30d7641922470 | 81ab63ad… |

  The blueprint files (cd.yaml 7a14550e…, db_schema e5cf164d…, share_tools 7b7ec28e…, blueprint.yaml 61655924…) are byte-for-byte unchanged since round 1.
- Both shared inputs changed, so every charter-global section is **re-derived in full** below rather than carried forward.
- Permitted: the same as round 1, with round-2 views at `…/views/policy_task/cd_maturity_withdrawals_and_renewals/round2/`. Masked and unread until the per-task freezes: every round-2 task field except frozen_time, user_scenario and initial_state.
- **contamination_disclosure (r2)**: the auditor read the round-1 GT of both tasks during revision 1. Those values are 340.42 / auto_renew + 5d5b8ccf… / 4.08 + 4.15 / 21406.18, and 58.73 / d9c9a0f9… / 5714.66. Round-2 derivations are therefore **not blind to round-1 GT**, and any round-2 value equal to a round-1 GT value is not independent evidence. The round-2 verdicts rest on recomputation of the round-2 charter compute on the round-2 views and on the demonstrations written here, not on blindness. Nothing from round-2 GT was seen before the freezes below.

### entry_conditions (r2)

- The orchestrator's gate snapshot after rework is all exit 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. It is cited, not re-run.
- check_traceability is declared out of this layer's entry conditions, so the round-1 "incomplete input" note (O13) is withdrawn.
- View hashes re-computed on disk all match MANIFEST: task_0 78f7537d…, task_1 15702de0… (unchanged from round 1).
- Base copy: lines 1-1072 of the extended yaml are byte-identical to `blueprint/products/cd.yaml`, and all ten parsed base keys compare equal. It is verbatim.

### change_inventory (r2)

**Extended charter**

- **P1 cd_ext_penalty_rate_reversal** (rewritten):
  - adds an `overwrite` on cd_evt_early_withdrawal (the clause "times interest_rate divided by 100")
  - reads amount, rate, days and date from one entry, the most recent cd_penalty (`pen_id`)
  - adds `grace_penalty` to exclude grace-period penalties
  - dedups per penalty (`source_item_id=pen_id`)
  - earns the relationship bonus from a checking account opened on or before, and not closed before, term start, with `CFIELD('checking', …)` and **no status filter**
  - adds cd_evt_maturity_and_grace to base_policy_refs
- **P2 cd_ext_closed_payout_instruction**:
  - adds the `not_late` binding (DAYS(maturity, NOW) ≤ grace_period_days + 1)
  - adds a sentence: when the interest_disposition pays to the same closed account, the replacement account receives that interest too, and "cd_ext_interest_payout_repoint does not apply to the certificate"
- **P5 cd_ext_grace_withdrawal_penalty_reversal**:
  - adds an `overwrite` on cd_evt_penalty_reversal ("on a grace-period withdrawal")
  - reads the withdrawal through the penalty's source_item_id
  - counts `official_check` proceeds as the owner's own
  - dedups per penalty
- **P6 cd_ext_interest_payout_repoint**: adds the exclusion `maturity_payout_on_record`. When renewal_instruction is pay_out_to_*, nothing is written.
- **P7 cd_ext_grace_jumbo_top_up**:
  - adds an `overwrite` on cd_evt_maturity_and_grace's grace add-on clause: grace add-ons are accepted "only while the certificate's interest_disposition names no closed payout account"
  - adds the bindings `payout_status` and `instructions_open` to `result`
  - the P7←P6 edge becomes `kind: value_input, gate: instructions_open`
  - adds a checking cross_category read
- **P3, P4 and the workflow** are textually unchanged. This includes the dataflow and the order_rationale.

**Tool module**: only the renew docstring for `maturity_date` changed (lines 117-118): "the maturity date of the new term, the calendar date on which the new term matures". Every tool body sits at the same lines and is unchanged: 43-54, 86-89, 137-148, 185-198, 227-238, 268-271, 308-321.

### policy_conflict_scan (r2)

- **cd_penalty_reversal (P1, P5)**: now disjoint by construction.
  - P1 `result` requires `not grace_penalty`; P5 requires `taken_in_grace`. Both test the same day-1..grace_period_days window on the same `pen_id`.
  - The round-1 overlap O14 is closed.
- **cd_update_instructions (P2, P6)**: the order dependence is removed.
  - P6 writes nothing while `renewal_instruction` is pay_out_to_*, whatever the account status.
  - Once P2 has recorded auto_renew with an active account, P6's `payout_closed` is false.
  - Both orders therefore reach P2's outcome. Probe on the task-0 world with the round-1 seed shape (disposition pay_to_savings on the same closed account): P6 applied first gives `maturity_payout_on_record = True`, and result = the unchanged payout_account_id, so nothing is written.
  - G4 is closed at the charter level.
  - Residual edge case R2-O6: P2 lets the owner name an account of a different kind than a payout disposition, and says that account "receives that interest too". No task world has this.
- **cd_deposit (P4, P7)**: still state-disjoint.
  - P7's new gate `instructions_open` restricts every grace add-on, not only jumbo top-ups. The restriction is declared (see override_declarations).
- **cd_renew (P3)**: unchanged; consistent.
- **Cross-category reads**:
  - P1 now reads checking `variant_name`, `opened_date` and `closed_date` of the **first checking row of any status** (R2-O2).
  - P7 now also reads the status of the checking or savings payout account.
  - All of these are reads only.
- **Scope**: the two declared trees are still disjoint and together cover all seven policies and the one workflow. This is confirmed against charter_scope at the reveal.

### rule_compute_equivalence (r2)

Verbatim quotations were checked sentence by sentence for every changed binding.

- **P1**:
  - `pen_id`: "The penalty checked is the certificate's most recent cd_penalty entry"
  - `pen_amount`, `pen_rate`, `pen_days`, `pen_date`: "…all read from that one entry"
  - `grace_penalty`: "day 1 through day grace_period_days …"
  - `prior_reversals`: "A penalty that already has a cd_penalty_reversal entry whose source_item_id is that penalty …"
  - `relationship_earned`: "opened on or before the term_start_date and not closed before it", implemented as `checking_closed == '' or checking_closed > term_start_date`
  - `result`: "not grace_penalty"
  - Match. Non-equivalence R2-O2: the rule is existential ("a checking account of a tier listed …"), while `CFIELD('checking', 'variant_name')` returns the first checking row of any status. Demonstration in the task-1 world with the two checking rows swapped: `checking_tier` becomes Everyday Checking (closed), so `relationship_earned` is false, `charter_rate` is 3.82 and `misassessed` is true. `grace_penalty` = true masks this and the result stays 0. It is not scored in either world (O1 widened).
- **P2**: `not_late` quotes "no longer made once more than grace_period_days plus one calendar days have passed". Match; O5 is closed. The new P6-exclusion sentence is informational for P2 and is implemented in P6.
- **P5**:
  - `source_withdrawal` quotes "the withdrawal it belongs to is the cd_withdrawal entry named by its source_item_id"; O3 is closed.
  - `wd_destination` / `wd_account` quote "read from that withdrawal's destination and counterparty account".
  - `owners_withdrawal` quotes "paid by official check or to a checking or savings account that belongs to the certificate's owner". The schema enum includes `official_check`.
  - `prior_reversals` is per penalty.
  - Match. `inputs.history` still lists "latest counterparty_account_id over cd_withdrawal", a stale metadata line with no effect on compute.
- **P6**: `maturity_payout_on_record` quotes "A certificate whose renewal_instruction is itself pay_out_to_checking or pay_out_to_savings on that same closed payout account is outside this policy". Compute tests only the instruction. The single `payout_account_id` field makes "that same account" automatic, and `payout_closed` supplies "closed". Equivalent.
- **P7**: `payout_status` quotes "read from the status of the account named by payout_account_id, the checking account for pay_to_checking and the savings account for pay_to_savings". `instructions_open` quotes "a disposition of compound names no payout account. While the disposition pays to a closed payout account, no top-up is written." `result` includes `instructions_open`.
  - The round-1 G5 sentence ("before it is added, a payout disposition that names a closed payout account is repointed") now has a compute counterpart through `instructions_open`. G5 is closed.
- **P3 and P4**: unchanged. Round-1 conclusions (revision 1 `### rule_compute_equivalence`) carry forward, because their text and bindings are byte-identical.
- **O1** (first-row CFIELD) is left as-is by the reworker and is widened in P1 (R2-O2).

### action_binding_and_uuids (r2)

- The seven `(target_tool, computes)` pairs and uuid8s are unchanged, each claimed once.
- Tool bodies are unchanged. No tool judges a prerequisite.
- O9 is closed: the renew docstring now gives `maturity_date` as "the calendar date on which the new term matures", which agrees with P3's "matures term_months calendar months later".

### prerequisite_graph (r2)

- Edges: P3←P1 (value_input, reversals), P3←P2 (state_gate, renewal_instruction), P4←P3 (value_input, active), P7←P5 (value_input, reversals), P7←P6 (**value_input, instructions_open**). Two disjoint DAGs, no cycle.
- Every `problem` names an extended policy of this file.
- P7←P6:
  - `policy_source` is still verbatim in P7's rule.
  - `gate: instructions_open` is a binding in P7's compute.
  - `effect` ("instructions_open turns true and the top-up is written at the shortfall; while the closed account stays on record the top-up is nothing") matches the compute: `result` requires `instructions_open`.
  - `resolved_by` update_interest_disposition_67b383bc writes `payout_account_id`, which flips `payout_status`.
  - Check 7 passes.
- No authoring-viewpoint phrasing.

### override_declarations (r2)

- **P1**:
  - The base cd_evt_early_withdrawal penalty-rate clause is now named in `overwrite` and replaced by the charter rate. The merged semantics are unique: the charter rate governs, and the declaration explicitly sets aside "a rate recorded on the certificate that disagrees with it".
  - cd_rate_and_bonuses "A bonus that is later lost … stays in the rate until the term ends" is now **followed**: the bonus is earned if the checking account was not closed before term start.
  - cd_evt_penalty_reversal "A penalty can be reversed at most once" is now **followed**, per penalty.
  - G1 is closed for P1. G2 is closed.
  - R2-O1: base `parameter_schema.penalty_rate_basis` ("'certificate_interest_rate' means the interest_rate on the certificate") and the variant value `certificate_interest_rate` are base schema text, not a policy sentence, and are not named. They are superseded in meaning by the declaration's own words, so no second conclusion survives the declaration.
  - R2-O5: P1 checks only the most recent penalty. An older unreversed misassessed penalty falls back to base cd_evt_penalty_reversal, which still orders it reversed, with no extended compute. This is a scope limit, not a contrary conclusion.
- **P5**:
  - The base clause "on a grace-period withdrawal" is named. The replaced_by text carries only the exclusion ("a penalty on a withdrawal whose proceeds went to an account that does not belong to the owner … is not reversed under this policy"). The positive half (grace penalties are reversed, including official-check proceeds) lives in P5's rule. The merged semantics are unique.
  - Official-check proceeds are now reversed, as base wants. G3 is closed.
  - Dedup is per penalty. G1 is closed for P5.
  - R2-O3 (wording): the replaced_by alone reads as removing grace penalties from base's reversal list.
- **P7**:
  - The base grace add-on clause is named and replaced by the same limits plus the new condition "only while the certificate's interest_disposition names no closed payout account".
  - The condition is declared, so legal, and the merged semantics are unique.
  - R2-O4: this adds a business condition to every grace add-on. The rule's rationale ("New money added during grace joins the principal of the renewed term, so …") still does not connect interest routing to principal. This is a matter of wording and design, with no consequence.
- **P2**: the declared overwrite is unchanged. The cd_instructions recording-timing sentence is still unnamed, and the new `not_late` bound gives the same last day (O4 kept as observation).
- **P6**: `overwrite: []`. The new exclusion narrows P6's own scope. No base sentence governs the bank-side repoint, so there is no conflict.
- **P3 and P4**: unchanged from revision 1.

### findings (r2)

**Status of the round-1 items**

| Item | Round-2 status | Evidence |
| --- | --- | --- |
| G1 | **closed** | P1 and P5 `prior_reversals` keyed on `source_item_id=pen_id`; rule "A penalty that already has a cd_penalty_reversal entry whose source_item_id is that penalty is not reversed again." |
| G2 | **closed** (residual R2-O1, observation) | P1 overwrite on cd_evt_early_withdrawal; closed_date test keeps a later-lost bonus |
| G3 | **closed** | P5 `owners_withdrawal: wd_destination == 'official_check' or owners_account`; remaining exclusion declared |
| G4 | **closed** at charter level | P6 `maturity_payout_on_record`; P2 sentence; probe above |
| G5 | **closed** at charter level | P7 `instructions_open` in `result`; declared overwrite; edge re-kinded |
| O2, O3, O5, O9, O14 | **closed** | see sections above |
| O1 | left as-is; **widened** in P1 (R2-O2) | — |
| O4, O6, O8, O10, O11, O12 | left as-is; still present | workflow dataflow and tool effects unchanged; O8's fields to be re-checked at reveal |
| O13 | withdrawn | traceability declared outside this layer |

**New charter-level items**: observations only, with no divergence demonstrated in either task world.

- **R2-O1**: the base parameter_schema text for penalty_rate_basis is not named.
- **R2-O2**: P1's first-row CFIELD now spans closed checking rows.
- **R2-O3**: P5's replaced_by carries only the exclusion.
- **R2-O4**: P7's new condition applies to all grace add-ons.
- **R2-O5**: P1 and P5 each check only the most recent penalty.
- **R2-O6**: P2 allows a replacement account whose kind differs from the payout disposition.

No new charter-level SOURCE-POLICY finding.

### closing_checklist (r2)

This section was written after the round-2 reveals (from 2026-09-12T19:50:09Z). **The difficulty does not close**: task 0 carries a new SOURCE-TASK RED.

**Per-task verdicts (revision 2)**

| Task | Policy self-consistency | Problem tree | Unique solution |
| --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-TASK RED (R2-T0-1)** — new; introduced by the seed change (interest_disposition → compound) made to close T0-1, with the persona line "where the CD's interest or its money should go … the money market ending in 4417" left unchanged |
| 1 | PASS | PASS | PASS |

**Verification of the reworker's claims**

- Closed as claimed: G1, G2 (residual R2-O1 is an observation), G3, G4/T0-1, G5/T1-1, T0-2, T1-O2, O2, O3, O5, O9, O14.
- T1-O3: withdrawn. The rationale now defines "satisfied".
- Left as-is and confirmed still present:
  - O1 (widened in P1 as R2-O2)
  - O4
  - O6 (workflow dataflow unchanged)
  - O8 (gold steps still carry the zero-wait fields)
  - O10
  - O11
  - O12
- O13: no longer applicable, because traceability is declared outside this layer.

**New in round 2**

- One RED: R2-T0-1.
- Six observations: R2-O1 through R2-O6.
- No regression of any round-1 PASS item. Task 1's unique solution and task 0's problem tree still hold.

**Checklist**

1. **Files.** 0.md and 1.md map one-to-one to tasks 0 and 1, alongside this file. Revision 1 is preserved verbatim above each `## revision_2`.
2. **Scope.** charter_scope is unchanged: task 0 = {P1–P4, W, 4 tools}, task 1 = {P5–P7, 3 tools}. The scopes are disjoint and together complete. There is one workflow, claimed once. The uuid8s are unchanged and independent. In-world cross-fire of task 1's P6 into task 0 is gone: P6 writes nothing on task 0's opening world.
3. **Problem trees.**
   - Task 0: 3 prerequisites, 2 value_input edges, all load-bearing.
   - Task 1: 2 prerequisites, 2 value_input edges, both load-bearing (5773.39 / 0).
   - Across the difficulty, the dependencies form two disjoint DAGs with no cycle.
4. **Gate re-run on the final form.** Not performed. The difficulty does not close, and the orchestrator's post-rework snapshot stands.

---

## revision_3

Re-audit after the round-2 rework. Revisions 1 and 2 above are left untouched.

### charter_global_frozen (r3)

- Started 2026-09-12T19:55:50Z. This section was written before any round-3 GT field was read.
- Auditor: the same as in rounds 1 and 2.
- Hashes:

  | Input | Round 3 | Round 2 |
  | --- | --- | --- |
  | cd.extended.yaml | **ebbf85fb37dc7978cba6fe80bb6eda54a4ff47ae91a3d6989389d581dccea930** (changed) | 701fe9ca… |
  | task_tools.py | d2dc551eec2c627b7e1ae048299ca450e5aee33f9bd1800417a30d7641922470 (**unchanged**) | d2dc551e… |

  The blueprint files are unchanged.
- **Re-derivation rule applied.**
  - The charter changed, so policy_conflict_scan, rule_compute_equivalence, prerequisite_graph and override_declarations are re-derived for every changed policy.
  - Byte-identical policy blocks are carried forward from revision 2.
  - action_binding_and_uuids is carried forward by the unchanged task_tools.py hash. The `(target_tool, computes)` lines in the charter are also unchanged.
- **contamination_disclosure (r3).** The auditor has read the round-1 and round-2 GT of both tasks. Round-3 derivations are not blind to those values. The verdicts rest on recomputing the round-3 charter compute on the round-3 views (helper `scratchpad/audit_cd/r3.py`) and on the demonstrations recorded here.

### entry_conditions (r3)

- The orchestrator's snapshot shows all seven gates at exit 0, with traceability deferred by design. The snapshot is cited, not re-run.
- The recomputed view hashes match MANIFEST:
  - task_0: c418442c…
  - task_1: 15702de0…, byte-identical to the round-2 view
- Base copy: lines 1-1072 are still byte-identical to `blueprint/products/cd.yaml`.

### change_inventory (r3)

Diffed by reading against revision 2. The round-3 file is saved as `scratchpad/audit_cd/ext_r3.yaml` for later rounds.

- **P1 cd_ext_penalty_rate_reversal**
  - `overwrite.replaced_by` gains "the tier's penalty_rate_basis of certificate_interest_rate is read as this rate". The rule gains the same clause.
  - The rule gains "An earlier penalty is checked under this policy only while it is the certificate's most recent penalty; otherwise it is left to cd_evt_penalty_reversal."
  - The relationship test is now "checked over the owner's active checking account and the owner's closed checking account, one qualifying account being enough".
  - Compute splits the relationship test into an active branch (`checking_tier` / `checking_opened` with `status='active'`) and a closed branch (`closed_tier` / `closed_opened` / `checking_closed` with `status='closed'`). The closed branch requires closed_date > term_start_date.
  - cross_category reads now include `status`.
- **P2 cd_ext_closed_payout_instruction.** The rule gains "when the certificate's interest_disposition pays out, the account named must be of the kind that disposition pays to, a checking account for pay_to_checking and a savings account for pay_to_savings". Compute is unchanged; the payout account is owner-named input.
- **P5 cd_ext_grace_withdrawal_penalty_reversal**
  - `overwrite.replaced_by` now restates the owner's-withdrawal definition (official check, or an account of the owner) before the exclusion.
  - The rule gains the same "earlier penalty … left to cd_evt_penalty_reversal" sentence.
  - Compute is unchanged.
- **P7 cd_ext_grace_jumbo_top_up.** The rationale sentence and the matching P7←P6 `policy_source` now read: "New money added during grace becomes principal on which the renewed term's interest is credited and paid out, so before it is added, a payout disposition that names a closed payout account is repointed to an open account of the owner." Compute, overwrite and edge kind are unchanged.
- **Unchanged:** P3, P4, P6 and the workflow, including dataflow and order_rationale. These are byte-identical blocks as read.

### policy_conflict_scan (r3)

The pairwise conclusions of revision 2 still hold:

- **P1/P5** stay disjoint through `grace_penalty` / `taken_in_grace`.
- **P2/P6** stay order-independent. P6 is unchanged, and the probe on the round-1 seed shape still gives `maturity_payout_on_record = True` and no write.
- **P4/P7** stay state-disjoint.

New conflict checks for the round-3 changes:

- **P2's kind-match clause vs P6.** When a payout disposition exists, the owner-named replacement must match its kind. After P2, P6's `payout_status` then reads the right table: the account is active, so nothing is written. R2-O6 is closed.
- **P1's "earlier penalty … left to cd_evt_penalty_reversal", and the same sentence in P5.** Both hand the non-latest penalty back to base explicitly. No extended policy now claims or denies it. R2-O5 is closed.

### rule_compute_equivalence (r3)

**P1.**
- `checking_tier` and `closed_tier` share one compute_basis quote: "checked over the owner's active checking account and the owner's closed checking account, one qualifying account being enough".
- `relationship_earned` quotes "one opened on or before the term_start_date and not closed before it".
- The active branch needs no closed test (an active account is not closed). The closed branch tests `checking_closed > term_start_date`, which matches "not closed before it". So the rule and the compute are equivalent.
- **R2-O2 is closed.** The first-row CFIELD no longer mixes active and closed rows. Demonstration in the task-1 world with the checking rows in reverse order: `checking_tier` is Interest Checking (active), `relationship_earned` is true and charter_rate is 3.97, the same as the natural order. Previously this order flipped `misassessed`.
- **O1 remains latent.** The rule's definite singulars ("the owner's active checking account", "the owner's closed checking account") and CFIELD's first row only coincide when the owner holds at most one checking account per status. Base cd_rate_and_bonuses is existential ("holds an active checking account of a tier listed"). Neither task world holds more than one checking account per status.

**P2.** The kind-match clause adds no compute binding. It constrains the owner-named tool argument, not `renewal_instruction`, so no binding is needed and there is no empty promise.

**P5.** Compute is unchanged. The added sentence narrows scope and needs no binding.

**P7.** Compute is unchanged. The rationale sentence has no computed quantity of its own; its gate is still `instructions_open`.

**P3, P4, P6.** Carried forward from revision 2.

### action_binding_and_uuids (r3)

Carried forward from revision 2 by the unchanged task_tools.py hash (d2dc551e…) and the unchanged `target_tool` / `computes` lines.

### prerequisite_graph (r3)

- The edges are unchanged: P3←P1, P3←P2, P4←P3, P7←P5, P7←P6 (value_input, `instructions_open`).
- The P7←P6 `policy_source` was reworded and still appears verbatim in P7's rule (lines 1571-1573).
- The graph is still acyclic.
- Check 7 passes.

### override_declarations (r3)

- **P1.** The declaration now also names the tier's `penalty_rate_basis` reading, so base schema text and the extended rate no longer disagree anywhere. **R2-O1 is closed.**
- **P5.** `replaced_by` now carries the owner's-withdrawal definition together with the exclusion. The merged base clause reads "reversed … when it was assessed contrary to this charter: [a grace withdrawal is the owner's own withdrawal when …; a penalty on a withdrawal whose proceeds went to an account that does not belong to the owner … is not reversed under this policy]". Taken with P5's rule, the merged semantics are unique. **R2-O3 is closed.** One small wording point remains: the replaced clause still does not say "is reversed" in so many words. That is a style matter with no consequence.
- **P7.** The declared overwrite is unchanged, and the new rationale supplies the link between interest routing and principal that was missing. **R2-O4 is closed** as far as design wording goes. The condition still governs every grace add-on, and it is declared.
- **P2, P3, P4, P6.** As in revision 2.

### findings (r3, charter-level)

| Item | Status in round 3 |
| --- | --- |
| R2-O1 | closed |
| R2-O2 | closed |
| R2-O3 | closed |
| R2-O4 | closed |
| R2-O5 | closed |
| R2-O6 | closed |
| O1 | latent only for multiple checking accounts of the same status; recorded as an observation, not reopened |
| O4, O6, O8, O10, O11, O12 | left as-is and confirmed present (charter workflow and tool effects unchanged) |

No new charter-level SOURCE-POLICY finding and no new observation.

### closing_checklist (r3)

Written after the round-3 reveals (2026-09-12T19:58:39Z onward).

**Per-task verdicts (revision 3)**

| Task | Policy self-consistency | Problem tree | Unique solution |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS (R2-T0-1 closed) |
| 1 | PASS | PASS | PASS |

**Reworker's claims**

- **Verified closed:** R2-T0-1, R2-O1, R2-O2, R2-O3, R2-O4, R2-O5, R2-O6.
- **O1:** R2-O2 is closed. Its first-row order dependence across active and closed rows is gone, as demonstrated in the task-1 world. The underlying O1 stays latent only for owners holding more than one checking account with the same status. No task world reaches that case.
- **Left as-is and confirmed still present:** O4, O6, O8, O10, O11, O12. These are observations, not grounds for rework.
- No new defect was found, and no round-1 or round-2 PASS regressed.

**Checklist**

1. **Files.** 0.md and 1.md correspond one-to-one with the tasks, alongside this file. Revisions 1 and 2 are preserved verbatim. Every task's revision-3 comparison carries PASS on all three relationships.
2. **Coverage and scope.**
   - Every extended policy is claimed by a task: task 0 = {P1-P4, W, 2ccc5de3, 96ab509d, 21cb639a, 5f936ecf}; task 1 = {P5-P7, e6d62385, 67b383bc, 522b16cc}.
   - The two scopes are pairwise disjoint and together jointly complete.
   - There is exactly one workflow, and task 0 alone claims it.
   - Task tools and GT are closed. Each task tool carries an independently generated uuid8, unchanged since round 1.
   - No out-of-scope policy writes anything on either task's opening world. For task 0: P5 = 0, P6 has no write, P7 = 0. For task 1: P1-P4 give no write.
3. **Problem trees.**
   - Task 0 has 3 prerequisites, 2 of them value_input, all load-bearing (3.98 / 0 / 0).
   - Task 1 has 2 prerequisites, both value_input, both load-bearing (5773.39 / 0).
   - Across the difficulty, the prerequisite edges form two disjoint DAGs with no cross-task edge.
4. **Gate re-run on the final form.** Not performed by this auditor. The orchestrator's post-rework snapshot is cited instead (all seven gates exit 0, with check_traceability deferred to the KB step by design). The audited artifacts are unchanged since that snapshot: cd.extended.yaml ebbf85fb…, task_tools.py d2dc551e…, tasks/0.json 77436c72…, tasks/1.json 78208a53…

**Difficulty verdict (r3):** the difficulty passes the source-layer policy-task audit. It does so on the orchestrator's gate snapshot, with check_traceability to be confirmed after KB publication.

---

## revision_4

This round is a re-audit prompted by source-layer items that the render-layer (KB) audit reported: `env/regional_retail_bank/audits/policy_kb/cd_maturity_withdrawals_and_renewals/0.md` D2, D3 and D4, and `1.md` D3 and D4. Revisions 1-3 above are left untouched.

### charter_global_frozen (r4)

- **Started:** 2026-09-12T21:36:30Z. This section was written before any round-4 GT field was read.
- **Auditor:** same as in rounds 1-3.
- **Hashes:**

  | File | Round 4 | Round 3 |
  | --- | --- | --- |
  | cd.extended.yaml | **a6145375bb3c8af05d1c4b25cdd7525e49c0ada5ac1f9f8b3291f652b1253bc0** (changed) | ebbf85fb… |
  | task_tools.py | d2dc551eec2c627b7e1ae048299ca450e5aee33f9bd1800417a30d7641922470 (unchanged) | d2dc551e… |

  The blueprint files are unchanged. Both round-4 views are byte-identical to round 3 (task_0 c418442c…, task_1 15702de0…), while the source task JSONs changed (0.json 6e1c3c60…, 1.json 3970fb1e…).
- **Re-derivation:** at the coordinator's instruction, every charter-global section is **re-derived in full** below. The round-3 charter copy (`scratchpad/audit_cd/ext_r3.yaml`) was machine-diffed against the round-4 file (`ext_r4.yaml`).
- **contamination_disclosure (r4):** round-4 derivations are not blind.
  - The auditor has read the round-1 to round-3 GT of both tasks.
  - At the coordinator's instruction, the auditor also read the two KB audit reports named above, which quote scored values in their GT comparison.
  - The verdicts therefore rest on recomputing the round-4 charter compute on the round-4 views (`scratchpad/audit_cd/r4.py`) and on the textual checks recorded here.

### entry_conditions (r4)

- **Gates:** all seven exit 0 in the orchestrator snapshot, cited rather than re-run. check_traceability is deferred by design.
- **Views:** hashes match MANIFEST.
- **Base copy:** lines 1-1072 are byte-identical to `blueprint/products/cd.yaml`.
- **Characters:** the charter contains no non-ASCII character at all, so no hair-space-style token splitting exists at source.

### change_inventory (r4)

Result of the machine diff of the round-3 charter against the round-4 charter:

- **Unchanged:** every `compute` block, every `(target_tool, computes)` pair, every prerequisite `(problem, kind, gate, resolved_by)` tuple, and the workflow steps and dataflow. The diff is **text only**.
- **P2 cd_ext_closed_payout_instruction:** a second `overwrite` entry. It names base `cd_instructions`' clause "a change recorded after that governs the next maturity" and replaces it with: "A change the owner records after the grace period ends governs the next maturity, but this bank-owed replacement, recorded at the latest on the day after the grace period ends, governs the maturity that has just passed, because the outcome of that grace period has not yet been booked." The same sentence is added to the rule. This addresses **D3**.
- **P3 cd_ext_post_grace_renewal_rate:**
  - `overwrite` goes from `[]` to one entry. It names base `cd_rate_and_bonuses`' clause "for a renewal it is the principal_balance on the renewal date after any grace-period add-ons and withdrawals" and replaces it with the ledger reconciliation plus: "Where the recorded principal_balance differs from this reconciled figure, the reconciled figure governs the jumbo test." The rule and the `jumbo` compute_basis gain the same sentence. This addresses **D4**.
  - The rule sentence, the P3←P2 `condition`, `policy_source` and `effect`, and the `auto` compute_basis now say "an instruction to renew automatically" instead of "the auto_renew instruction". The P3←P1 `effect` is de-tokenised. This addresses the **D2 source cause**.
- **P4 cd_ext_term_add_on_amount:** in the rule and the P4←P3 `policy_source`, "grace_period status" becomes "grace period status". The `effect` says "term start date".
- **P7 cd_ext_grace_jumbo_top_up:**
  - A second `overwrite` entry on the same `cd_rate_and_bonuses` clause, replaced by the ledger reconciliation plus "the reconciled figure governs the shortfall". The rule and the `shortfall` compute_basis gain the same sentence. This addresses **D4**.
  - The P7←P5 and P7←P6 `effect` texts are de-tokenised.
- **Workflow:** `order_rationale` now says "an instruction to renew automatically".

### policy_conflict_scan (r4)

The structured surface is 11 base policies, 7 extended policies and 1 workflow.

| Subject | Policies | Result |
| --- | --- | --- |
| cd_penalty_reversal | P1 (rate or days off the charter, not a grace penalty, most recent penalty, per-penalty dedup); P5 (grace penalty, owner's own withdrawal including official check, most recent penalty, per-penalty dedup) | Disjoint by `grace_penalty` / `taken_in_grace` on the same `pen_id`. An earlier penalty is expressly left to base. No conflict. |
| cd_update_instructions | P2 (payout instruction to a closed account → auto_renew, owner-named replacement account whose kind matches any payout disposition, deadline `not_late`, now also expressly governs this maturity); P6 (payout disposition to a closed account → same-kind active account, excluded while a pay_out_to_* instruction is on record) | Order-independent. The probe on the round-1 seed shape still gives P6 no write. No conflict. |
| cd_deposit | P4 (active; term add-on); P7 (grace_period, open-account condition) | State-disjoint. No conflict. |
| cd_renew | P3 only | — |

- **Time anchors:**
  - P2's deadline (day ≤ grace_period_days + 1) equals the day P3 becomes due (day > grace_period_days). P2's recording on that day now also governs this maturity by declaration, which aligns it with P3's booking on the same day.
  - P5 and P7 act on day 1..grace_period_days.
- **Cross-category:** reads only (checking, savings). No write crosses into another category.
- **Terminal states:** consistent with the lifecycle.
- **Two overwrites on one base clause:** P3 and P7 both supersede the same `cd_rate_and_bonuses` clause, with replacement texts that end differently: "…governs the jumbo test" and "…governs the shortfall". Both define the renewal-date principal as the same ledger reconciliation. P7's shortfall exists only to reach P3's jumbo threshold. The merged semantics are unique (R4-O2, wording).
- **Scope:** the two trees, {P1-P4, W} and {P5-P7}, remain disjoint and jointly complete.

### rule_compute_equivalence (r4)

A programmatic check confirms that every `compute_basis` quotation of all seven policies, each piece split on " | ", is verbatim in its rule after whitespace normalisation. No quotation is missing.

Sentence-by-sentence sweep:

- **P1.** Bindings are unchanged since round 3 and are equivalent to the rule, as recorded in revision 3. O1 is latent only for more than one checking account per status.
- **P2.**
  - `not_late` implements the recording deadline.
  - The new "governs the maturity that has just passed" sentence is a governance statement about which maturity the write controls. It has no quantity of its own. The written `renewal_instruction` value is `result`.
  - The kind-match clause constrains the owner-named argument.
  - Equivalent.
- **P3.**
  - `principal` is the ledger sum, and the new sentence ("the reconciled figure governs the jumbo test") is exactly what `jumbo` reads.
  - `auto` quotes "A certificate renews only under an instruction to renew automatically". Its compute test `F('renewal_instruction') == 'auto_renew'` is that instruction's stored value.
  - Equivalent.
- **P4.** Unchanged except wording. The `active` binding and its quote ("A term add-on is allowed only while the certificate's status is active") still hold.
- **P5.** Unchanged since round 3.
- **P6.** Unchanged since round 2.
- **P7.** `shortfall` now also quotes "the reconciled figure governs the shortfall", which is what `principal` feeds. `instructions_open` is unchanged. Equivalent.

The rule never makes an empty promise and the compute never invents a basis.

### action_binding_and_uuids (r4)

Re-derived from the unchanged tool module (d2dc551e…) and the unchanged `target_tool` / `computes` lines.

- Each of the seven pairs is claimed once.
- Tool bodies perform one write and judge no prerequisite:

  | Tool | task_tools.py lines |
  | --- | --- |
  | 2ccc5de3 | 43-54 |
  | 96ab509d | 86-89 |
  | 21cb639a | 137-148 |
  | 5f936ecf | 185-198 |
  | e6d62385 | 227-238 |
  | 67b383bc | 268-271 |
  | 522b16cc | 308-321 |

- The uuid8s are 2ccc5de3, 96ab509d, 21cb639a, 5f936ecf, e6d62385, 67b383bc and 522b16cc. They are distinct and show no batch derivation.
- The renew docstring's `maturity_date` agrees with P3.

### prerequisite_graph (r4)

**Edges.** Two disjoint DAGs, with no cycle. Every `problem` is an extended-policy id in this file.

| Edge | Kind | Gate |
| --- | --- | --- |
| P3 ← P1 | value_input | `reversals` |
| P3 ← P2 | state_gate | `cd_certificates.renewal_instruction` |
| P4 ← P3 | value_input | `active` |
| P7 ← P5 | value_input | `reversals` |
| P7 ← P6 | value_input | `instructions_open` |

**Per-edge check (programmatic):**
- Every `policy_source` is verbatim in the cited rule after the rewording.
- No prerequisite field now contains the token `auto_renew`. The D2 source sentence ("The certificate carries the auto_renew instruction …") now reads "The certificate carries an instruction to renew automatically at the moment its renewal is booked."
- Each `condition` matches its source sentence.
- Each `resolved_by` makes its `effect` hold. The compute and the tools are unchanged, and the recomputed skip values are 3.98 / 0 / 0 for task 0 and 5773.39 / 0 for task 1.
- The kinds match their gates.
- No authoring-viewpoint phrasing appears.

**Remaining enum literals.** The literal `auto_renew` is still present in three rules: P2 ("replaced by auto_renew", "An auto_renew instruction … left as they are"), P3's first and last sentences ("whose renewal_instruction is auto_renew", "the instruction is not auto_renew"), and P7 ("its renewal_instruction is auto_renew").
- These are field-value literals of the kind the whole charter uses (for example `pay_out_to_savings`, `grace_period`, `early_partial`). They are not a source-layer defect under the three relationships. How they are worded in the KB is the renderer's remit (D2-render), so this is recorded as observation R4-O3.
- The specific sentence that became the KB "Entry condition" is the prerequisite condition, and it is clean.

### override_declarations (r4)

Every extended policy is swept sentence by sentence against its `base_policy_refs`. Each `superseded_clause` was checked programmatically to be verbatim in the named base rule, and each `replaced_by` verbatim in the extended rule.

- **P1** (refs cd_evt_penalty_reversal, cd_evt_early_withdrawal, cd_rate_and_bonuses, cd_evt_maturity_and_grace).
  - The penalty-rate clause is declared, including the `penalty_rate_basis` reading.
  - A lost bonus stays, which follows base.
  - Dedup is per penalty, which follows base.
  - An earlier penalty is left to base.
  - The grace penalty is carved out to P5.
  - No undeclared override.
- **P2** (refs cd_instructions, cd_evt_maturity_and_grace).
  - The payout-to-closed-account clause is declared, as before.
  - **D3 is now declared.** The cd_instructions clause "a change recorded after that governs the next maturity" is named, and the replacement separates an owner's late change (next maturity) from the bank-owed replacement (this maturity).
  - The base sentence's first half, "A change to the renewal instruction must be recorded before the grace period ends to govern this maturity", is not itself named (R4-O1). The declared replacement states its exception expressly ("but this bank-owed replacement, recorded at the latest on the day after the grace period ends, governs the maturity that has just passed"), so specific-over-general gives one reading.
  - "The payout account must be … active … when the instruction is recorded" is followed.
  - No undeclared override remains. My round-1 note O4 recorded this tension as an observation because both readings reached auto_renew for this maturity. It is now **closed by declaration**.
- **P3** (refs cd_rate_and_bonuses, cd_evt_maturity_and_grace).
  - **D4 is now declared.** The base clause "for a renewal it is the principal_balance on the renewal date after any grace-period add-ons and withdrawals" is named and replaced by the ledger reconciliation, with an explicit tie-break ("Where the recorded principal_balance differs from this reconciled figure, the reconciled figure governs the jumbo test").
  - Revisions 1-3 recorded this clause as "followed", because the reconciliation equals principal_balance on every ledger-consistent record. The KB audit is right that on an inconsistent record the two diverge, and until round 4 that divergence was undeclared. It was latent: in both task worlds the recorded balance equals the ledger (99951.82 in task 0; 94226.61 in task 1).
  - Every other cd_rate_and_bonuses and cd_evt_maturity_and_grace sentence is followed.
- **P4.** No undeclared override. It is unchanged in meaning.
- **P5.** The "on a grace-period withdrawal" clause is declared with both halves.
- **P6.** No base sentence is contradicted.
- **P7.**
  - The grace add-on clause is declared with the open-account condition.
  - **D4 is also declared here.** The same cd_rate_and_bonuses clause is named, with "the reconciled figure governs the shortfall".
  - The two replacements on one clause agree on the measure (R4-O2).

### findings (r4)

**Items raised by the render-layer audit:**

| Item | Status | Basis |
| --- | --- | --- |
| **D3** | **closed** | The override is now declared in P2's `overwrite` and rule. The merged semantics are unique (see R4-O1). Task 0's replacement on day 11 governs this maturity by declaration. |
| **D4** | **closed** | Declared in P3 and P7. In both worlds, recorded balance = ledger, so no value moves. |
| **D2 source cause** | **closed** | The prerequisite condition, policy_source and effect sentences no longer carry `auto_renew`. The charter has no non-ASCII characters. D2-render, and whether enum literals in rule text should be worded in the KB, remain with the renderer (R4-O3). |

**Round 1-3 items re-checked for regression:**

- **Still closed:** G1, G2, G3, G4, G5, O2, O3, O5, O9, O14, R2-O1 to R2-O6.
- **O13:** withdrawn, as recorded in revision 2.
- **Now closed by declaration:** O4 (subsumed by D3).
- **Latent only:** O1 (for more than one checking account per status).
- **Left as-is and still present:** O6, O8, O10, O11, O12.

The compute, the prerequisite tuples, the tools and the workflow structure are unchanged, and the recomputed values match round 3:
- Task 0: 340.42 / auto_renew / 4.08 / 21406.18.
- Task 1: 58.73 / d9c9a0f9… / 5714.66.

**New observations (no consequence in either world):**

- **R4-O1.** The first half of base cd_instructions' timing sentence is not named in P2's overwrite. The declared replacement's express exception makes the merged reading unique.
- **R4-O2.** One base clause is superseded twice (P3, P7) with differently ending but compatible replacements.
- **R4-O3.** Enum literals such as `auto_renew` remain in P2/P3/P7 rule text, as everywhere else in the charter. This is not a source-layer defect.

No new charter-level SOURCE-POLICY finding.

### closing_checklist (r4)

This section was written after the round-4 reveals (from 2026-09-12T21:39:52Z).

**Per-task verdicts (revision 4)**

| Task | Policy self-consistency | Problem tree | Unique solution |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

**Reworker's claims**

- D3, D4 and the D2 source cause are **verified closed** (see `### findings (r4)`).
- D1, D2-render, D5 and D6 belong to the renderer. This audit does not rule on them.
- No round-1 to round-3 closure regressed. O4 is now also closed by declaration.
- New items are observations only: R4-O1, R4-O2 and R4-O3.

**Correction to my earlier rounds**

- In revisions 1 to 3 I recorded the principal-basis clause of cd_rate_and_bonuses as "followed".
- In the same revisions I recorded the cd_instructions timing tension as observation O4.
- The render-layer audit correctly identified both as undeclared at the source layer. They were latent: neither changed a scored value in either world.
- Both are now declared, so no rework is outstanding on them.

**Checklist**

1. **Files.** 0.md and 1.md correspond one-to-one with tasks 0 and 1, and this file sits alongside them. Revisions 1 to 3 are preserved verbatim, and both task files carry a revision-4 comparison with PASS on all three relationships.
2. **Coverage and scope.**
   - The seven extended policies are fully covered.
   - The scopes are disjoint and complete: task 0 = {P1–P4, W, 4 tools}; task 1 = {P5–P7, 3 tools}.
   - There is exactly one workflow, claimed only by task 0.
   - The uuid8s are independent and have not changed since round 1.
   - No out-of-scope policy writes on either opening world.
3. **Problem trees.**
   - Task 0: 3 prerequisites, 2 value_input edges, all load-bearing.
   - Task 1: 2 prerequisites, 2 value_input edges, both load-bearing.
   - Across the difficulty the trees form two disjoint DAGs, with no cycle.
4. **Gates.** I did not re-run the gates. The orchestrator's post-rework snapshot is cited: all seven exit 0, and traceability is deferred to the KB step. The audited artifacts are unchanged since that snapshot: cd.extended.yaml a6145375…, task_tools.py d2dc551e…, tasks/0.json 6e1c3c60…, tasks/1.json 3970fb1e….

**Difficulty verdict (r4).** The difficulty passes the source-layer policy-task audit. The render-layer items that remain (D1, D2-render, D5, D6) belong to the KB audit.

---

## revision_5

This round re-audits the charter against the source-layer items S1–S3 raised by the KB re-audit (`audits/policy_kb/cd_maturity_withdrawals_and_renewals/0.md` and `1.md`, revision_2). Revisions 1–4 above are left untouched.

### charter_global_frozen (r5)

- **Started:** 2026-09-12T21:58:27Z. This section was written before any round-5 GT field was read.
- **Hashes:**

  | Input | Hash | Status |
  | --- | --- | --- |
  | cd.extended.yaml | **7be56d046b97beb70eefbb40318ce917fa97252d7510716a1afa27df032480d9** | changed; round 4 was a6145375… |
  | task_tools.py | d2dc551e… | unchanged |
  | blueprint files | — | unchanged |
  | task_0 view | c418442c… | byte-identical to round 4 |
  | task_1 view | 15702de0… | byte-identical to round 4 |
  | source 0.json | a21352cb… | changed |
  | source 1.json | 06078172… | changed |

- **Re-derivation:** every charter-global section is re-derived in full, as instructed. I machine-diffed `ext_r4.yaml` against `ext_r5.yaml` and saved the round-5 copy.
- **contamination_disclosure (r5):** these derivations are not blind. The auditor has read the GT of both tasks from rounds 1–4 and has read both KB audit reports, which quote scored values. The verdicts rest on recomputing the round-5 charter compute on the round-5 views (`r5.py`, `r5_day12.py`) and on the text checks recorded here.

### entry_conditions (r5)

- All seven gates exit 0 (orchestrator snapshot, cited).
- The view hashes match the MANIFEST.
- Base lines 1-1072 are byte-identical to `blueprint/products/cd.yaml`.
- The charter contains no non-ASCII characters.

### change_inventory (r5)

A machine check confirms that for all seven extended policies these fields are identical to round 4: `compute`, `target_tool`, `computes`, `prerequisite`, `cross_category`, `inputs`, `base_policy_refs`, `trigger` and `subject`. The workflow is identical too. The rework changed text only, in three places:

- **P2, S2.**
  - The second `overwrite` now supersedes the **whole** cd_instructions timing sentence: "A change to the renewal instruction must be recorded before the grace period ends to govern this maturity; a change recorded after that governs the next maturity."
  - The replacement text is: "A change the owner makes to the renewal instruction must be recorded before the grace period ends to govern this maturity, and a change the owner records after that governs the next maturity; the one exception is this bank-owed replacement, which, recorded at the latest on the day after the grace period ends, governs the maturity that has just passed …"
  - The rule states the same.
- **P3, S3 and S1.**
  - The `replaced_by` and the rule add: "This reconciled principal is the principal on the renewal date for the jumbo test of every renewal, including a renewal into a different tier chosen during grace and a renewal the owner books during grace."
  - The rule adds: "The target tier whose published standard rates a renewal follows is the tier the certificate renews into: its renewal_target_tier when the owner made no term change during grace, otherwise the tier the owner chose during grace."
  - compute_basis quotes for `same_tier` and `principal` were extended to cover these sentences.
- **P7, S3.** The `replaced_by` and the rule add: "This is the same reconciled principal on which the jumbo test of every renewal is judged."

### policy_conflict_scan (r5)

Pairwise results carried over from revision 4 are unchanged, because no compute or scope field moved:

- P1/P5 are disjoint.
- P2/P6 are order-independent.
- P4/P7 are state-disjoint.
- Cross-category access is read-only.
- The scopes {P1-P4, W} and {P5-P7} are disjoint and together complete.

The two overwrites of the cd_rate_and_bonuses renewal-principal clause (P3 and P7) now state the same scope, "every renewal", and the same measure. R4-O2 is closed.

**New in this round: the recording deadline in P2 against P3's due window.**

- P2 records its replacement only while `DAYS(maturity_date, NOW) <= grace_period_days + 1`: "so it is no longer made once more than grace_period_days plus one calendar days have passed after the maturity_date".
- P3 is due whenever `days_after > grace_period_days`, with no upper bound. It renews only under auto_renew.
- On day grace_period_days + 2 or later, a certificate still in grace_period that carries a payout instruction to a closed account has no governed outcome. See **R5-G1** in findings (r5).

### rule_compute_equivalence (r5)

Every `compute_basis` quotation, split on " | ", is verbatim in its rule (programmatic check, no misses). Every prerequisite `policy_source` is verbatim in its rule. Bindings are unchanged from round 4, so the equivalences recorded in revision 4 hold. The new sentences are checked here:

- **P3.**
  - "This reconciled principal is the principal on the renewal date for the jumbo test of every renewal…" is quoted under `principal` and is what `jumbo` reads.
  - The target-tier definition is quoted under `same_tier`. P3 prices only renewals where renewal_target_tier equals the held tier, so the definition's other branch (the tier chosen in grace) is general charter text with no binding in this policy. It restates cd_evt_maturity_and_grace ("into renewal_target_tier, or into the tier the owner chose during grace"), so it invents nothing.
- **P2.** The owner/bank timing sentence is a governance statement with no computed quantity. `not_late` implements the bank-side deadline.
- **P7.** The added sentence is the same measure as `principal`.

**Correction to revision 2.** Round-1 O2 had two parts, and only the first is fixed.

- Fixed: mixing the "largest" penalty with the "most recent" one.
- **Not fixed:** the rule checks a penalty "against the rate and the penalty days that the charter fixes for the term in which the withdrawal was taken", but `standard_at_start` / `charter_rate` rebuild the rate from the *current* term's certificate fields.
- For a most-recent penalty taken in a term before a renewal, the rule and the compute diverge. I record this as **O2b** (observation, latent). Both task worlds have renewal_count 0 with the penalty in the current term.
- Revision 2's "O2 closed" was therefore incomplete.

### action_binding_and_uuids (r5)

This is re-derived from the unchanged task_tools.py (d2dc551e…) and the unchanged `target_tool` / `computes` lines:

- The 7 pairs are each claimed once.
- Bodies are at lines 43-54, 86-89, 137-148, 185-198, 227-238, 268-271 and 308-321. Each performs one write and judges no prerequisite.
- The uuid8s are distinct and independent.

### prerequisite_graph (r5)

The edges are unchanged: P3←P1 (value_input, reversals), P3←P2 (state_gate, renewal_instruction), P4←P3 (value_input, active), P7←P5 (value_input, reversals) and P7←P6 (value_input, instructions_open). They form two disjoint DAGs.

- Every `policy_source` is verbatim in its rule.
- No prerequisite field carries an enum token.
- Kinds and gates match.
- No authoring-viewpoint phrasing is present.

### override_declarations (r5) — retirement-domain sweep

For every `overwrite`, I checked three things: that the superseded clause is verbatim in its base (programmatic, all true), what domain the base clause governed, and whether the charter, after the retirement, governs that whole domain.

| # | Retired base clause | Base domain | Governed after retirement by | Whole domain governed? |
| --- | --- | --- | --- | --- |
| 1 | cd_evt_early_withdrawal "times interest_rate divided by 100" (P1) | the rate factor of every early-withdrawal penalty | P1 replacement: the charter rate of the term, with the tier's penalty_rate_basis "read as this rate" | yes. The replacement is stated generally for any term. Wording note R5-O1: the replacement does not restate the "divided by 100" it retires. The rate is in percent throughout (`parameter_schema`), so the formula stays computable. |
| 2 | cd_evt_maturity_and_grace "under a payout instruction the whole balance is paid as kind maturity_payout … and the certificate closes" (P2) | the grace-end outcome of every payout instruction: open account, closed account, mail_check | open account and mail_check: P2 rule "carried out as written … and a mail_check instruction pays the whole balance by official check"; closed account: `replaced_by` → auto_renew | **no, for one sub-domain.** A closed-account payout instruction whose grace outcome is still unbooked more than grace_period_days + 1 days after maturity has no bookable outcome. See R5-G1. |
| 3 | cd_instructions timing sentence, now whole (P2) | every renewal-instruction change, by owner or bank, before or after grace | `replaced_by`: owner before grace governs this maturity; owner after grace governs the next; bank-owed replacement (≤ day after grace) governs this maturity | yes. The only bank-side renewal-instruction change in the charter is P2's replacement. **S2 / R4-O1 closed.** |
| 4 | cd_rate_and_bonuses "for a renewal it is the principal_balance on the renewal date after any grace-period add-ons and withdrawals" (P3, P7) | the jumbo principal of every renewal: same-tier, cross-tier, owner-booked in grace, automatic at grace end | P3 `replaced_by`: reconciled principal "for the jumbo test of every renewal, including a renewal into a different tier chosen during grace and a renewal the owner books during grace"; P7 the same measure | yes. **S3 closed.** |
| 5 | cd_evt_penalty_reversal "on a grace-period withdrawal" (P5) | the reversal ground for every grace-withdrawal penalty | P5: owner's own grace withdrawal (account of the owner or official check) is reversed; proceeds to a non-owner account are not reversed ("handled as a disputed transaction"); an earlier penalty is left to base, whose general ground "assessed contrary to this charter" still covers it via cd_evt_maturity_and_grace "A grace withdrawal … carries no penalty" | yes. The non-owner branch's outcome is stated as "not reversed". No CD policy handles the dispute itself, so it is out of scope. |
| 6 | cd_evt_maturity_and_grace grace add-on clause (P7) | every grace add-on | P7 `replaced_by`: the same limits, plus the open-account condition | yes |

- **S1** is closed. The "target tier" is now tied to fields (`renewal_target_tier` or the tier chosen in grace) in P3's rule, consistent with cd_evt_maturity_and_grace. It needs no overwrite because no quantity changes.
- The sentence-by-sentence sweep of all other base sentences in each policy's refs is unchanged from revision 4: followed, or declared as above.

### findings (r5)

**R5-G1 — SOURCE-POLICY (charter-level, latent; new finding, present since round 2).**

- **Symptom.** After the recording deadline, a closed-account payout instruction can be neither replaced nor renewed, yet the declared overwrite says it "is replaced by auto_renew".
- **Root cause.** The round-2 fix for O5 added P2's deadline. The P2 rule reads "so it is no longer made once more than grace_period_days plus one calendar days have passed after the maturity_date", with compute `not_late: DAYS(F('maturity_date'), NOW) <= P('grace_period_days') + 1`. P3's due window is open-ended: "The renewal is due when the certificate's status is still grace_period and more than grace_period_days calendar days have passed after the maturity_date", with compute `due: in_grace and days_after > P('grace_period_days')`. P3 also renews only under auto_renew. The base payout clause for this case is retired by P2's declared overwrite: "the instruction cannot be carried out when the grace period ends and is replaced by auto_renew".
- **Demonstrated consequence** (constructed situation: task 0's seed with the clock moved one day, frozen 2026-09-15; helper `scratchpad/audit_cd/r5_day12.py`).
  - P2 gives `not_late = False` and result pay_out_to_savings, so nothing is written.
  - P3 gives days_after 12, `due = True`, `auto = False`, result 0, so no renewal is written. It would give 3.98 if auto_renew were on record.
  - The retired base clause no longer pays out.
  - Conclusion A, from the declared overwrite: the instruction "is replaced by auto_renew" and the certificate renews.
  - Conclusion B, from P2's deadline plus P3's "A certificate renews only under an instruction to renew automatically … no renewal is written": no replacement and no renewal.
  - The two passages reach different conclusions in the same situation. Either reading leaves the certificate's grace outcome with no write the charter permits.
- **Bears on.** Task 0 claims P2. Its world is day 11, where `not_late` is true, so **no divergent value in task 0**. Task 1 is not engaged.
- **Affected.** cd.extended.yaml cd_ext_closed_payout_instruction (rule sentence on the deadline; compute `not_late`; `overwrite[0].replaced_by`) together with cd_ext_post_grace_renewal_rate (`due`, `auto`).
- **Relation to previous revisions.** The defect was introduced in round 2 (O5 fix). I did not catch it in revisions 2–4. It is reported now because this round's retirement-domain sweep examines each retired clause's whole domain.

**KB items S1, S2, S3: all closed** (see the sweep).

**Regression check.** No regression was found.

- G1-G5, T-level items, O3, O5, O9, O14, R2-O1 to R2-O6, D3, D4, the D2 source cause and O4 remain closed.
- R4-O1 is closed (S2). R4-O2 is closed (the scopes are now aligned). R4-O3 (enum literals in rule text) stands as an observation.
- O1 is latent. O6, O8, O10, O11 and O12 are as before.
- Correction: O2 is reopened as **O2b** (observation, latent), as explained above.
- Recomputed values are unchanged:
  - task 0: 340.42 / auto_renew / 4.08 / 21406.18, with skip runs 3.98 / 0 / 0
  - task 1: 58.73 / d9c9a0f9… / 5714.66, with skip runs 5773.39 / 0

**New observations.**

- **R5-O1.** The P1 replacement does not restate "divided by 100".
- **O2b.** See rule_compute_equivalence (r5).

### closing_checklist (r5)

Written after the round-5 reveals, from 2026-09-12T22:02:39Z.

**Per-task verdicts (revision 5)**

| Task | Policy self-consistency | Problem tree | Unique solution |
| --- | --- | --- | --- |
| 0 | PASS for its world; charter-level SOURCE-POLICY R5-G1 on claimed P2 (latent, no divergent value on day 11) | PASS | PASS |
| 1 | PASS | PASS | PASS |

**Reworker's claims**

- S1, S2 and S3 are **verified closed**. The retirement-domain sweep holds for retirements 1, 3, 4, 5 and 6.
- The claim "no compute binding, scored value, persona line or seed field changed" is **verified**. Non-text fields are machine-identical, both views are byte-identical, and the recomputed values are unchanged.
- **Not closed:** retirement 2 (P2's payout clause) leaves a sub-domain without a bookable outcome. This is **R5-G1**, which dates from round 2 and was missed by me in revisions 2–4.
- I also correct my revision-2 closure of O2. Its current-term half remains and is recorded as O2b, an observation.

**Checklist**

1. **Files.** 0.md and 1.md map one-to-one to the two tasks, and revisions 1–4 are preserved.
2. **Scope.**
   - The scopes are disjoint and together complete: task 0 = {P1–P4, W, 4 tools}; task 1 = {P5–P7, 3 tools}.
   - There is one workflow, claimed once.
   - The uuid8s are independent.
   - No out-of-scope policy writes on either opening world.
3. **Problem trees.**
   - Task 0: 3 prerequisites, 2 of them value_input, all load-bearing.
   - Task 1: 2 prerequisites, both value_input, both load-bearing.
   - The trees form two disjoint DAGs.
4. **Gates.** I did not re-run them. The orchestrator snapshot is cited (all exit 0), and the artifacts are unchanged since it: 7be56d04…, d2dc551e…, a21352cb…, 06078172….

**Difficulty verdict (r5)**

Both tasks pass on their own worlds. However, the charter carries a latent charter-level SOURCE-POLICY finding, R5-G1, on P2.

- In revision 1, I held that latent charter-level findings (G1–G3) keep the difficulty from passing, and I apply the same standard here. **The difficulty does not pass the source layer until R5-G1 is resolved.**
- What R5-G1 costs is demonstrated on a constructed day-12 situation; it moves no scored value in either task.

---

## revision_6

Re-audit after the round-5 rework. Revisions 1–5 above are left untouched.

### charter_global_frozen (r6)

- **Started:** 2026-09-12T22:07:02Z. This section was written before any round-6 GT field was read.
- **Hashes:**
  - cd.extended.yaml: **b45ac3e25e410b49b654668c6f49848fe86200ddd5413bd0404c0f35720d07f2**, changed from round 5 (7be56d04…). A copy is saved as `ext_r6.yaml`.
  - task_tools.py: d2dc551e…, unchanged. The blueprint is unchanged.
  - Both views are byte-identical to round 5.
  - Sources: 0.json 48cb6b10…, 1.json b240b591…
- **Re-derivation:** every section is re-derived in full, including the retirement sweep across all seven overrides.
- **contamination_disclosure (r6):** these derivations are not blind. I have seen round 1–5 GT and the KB audit reports. Values were recomputed with `r6.py`, and probes were run with `r6_probes.py`.

### entry_conditions (r6)

- The gate snapshot shows all seven gates at exit 0. It is cited, not re-run.
- The view hashes match MANIFEST.
- Base lines 1-1072 are byte-identical to the blueprint.
- There are no non-ASCII characters.

### change_inventory (r6)

A machine diff against round 5 finds changes in only two policies: **P1** and **P2**, in the fields compute, overwrite, rule and compute_basis. P3–P7 and the workflow are field-for-field identical.

- **P1:**
  - `overwrite.replaced_by` and the rule restate the retired factor in full: "In the penalty formula this rate takes the place of interest_rate, so a penalty equals the penalty basis times this rate divided by 100 times penalty_days divided by day_count_basis, rounded half-up to the cent." This addresses R5-O1.
  - A new sentence reads "This policy checks a penalty taken in the certificate's current term, one whose posted_date is on or after the term_start_date …; a penalty taken in an earlier term is left to cd_evt_penalty_reversal".
  - A new binding `in_current_term: pen_date != '' and pen_date >= F('term_start_date')` enters `result`. This addresses O2b.
- **P2:**
  - The recording deadline is removed, together with the binding `not_late`.
  - A new binding `outcome_open: status active or grace_period` implements the new text: "while the certificate is active or in its grace period, and it is recorded before the outcome of the grace period is booked, however many days have passed since the grace period ended; a certificate whose grace outcome has been booked is no longer in its grace period and is not concerned".
  - `result` becomes: `instr` unless (payout_closed and outcome_open), and otherwise `'auto_renew'` if renew_offered, else `'mail_check'`.
  - `overwrite[0].replaced_by` and the rule now read "…replaced by auto_renew where the tier's auto_renew_available is true, and by mail_check, under which the whole balance is paid by official check, where it is not".
  - The exception in `overwrite[1].replaced_by` now reads "recorded before the outcome of the grace period is booked, governs the maturity that has just passed". This addresses R5-G1.

### policy_conflict_scan (r6)

- **P1/P5** stay disjoint: `grace_penalty` against `taken_in_grace`. The new P1 current-term gate only narrows P1.
- **P2/P6** stay order-independent, since P6 is unchanged.
  - P6 writes nothing while a pay_out_to_* instruction is on record.
  - After P2 writes auto_renew or mail_check with an owner-named active account, P6 finds `payout_closed` false.
- **P4/P7** stay state-disjoint.
- **Time anchors:**
  - P2 now records whenever the grace outcome is open, meaning status is active or grace_period.
  - P3 is due whenever status is grace_period and day > grace_period_days.
  - So P2 and P3 now cover the same open-ended post-grace window. The day-12+ hole of R5-G1 is gone (see findings).
- **Cross-category:** reads only.
- **Scopes:** {P1–P4, W} and {P5–P7} are disjoint and together complete.

### rule_compute_equivalence (r6)

A programmatic check confirms that every compute_basis piece and every prerequisite policy_source is verbatim in its rule, and that every compute binding has a basis entry. The new or changed bindings:

- **P1 `in_current_term`** quotes "This policy checks a penalty taken in the certificate's current term, one whose posted_date is on or after the term_start_date". The compute expression `pen_date >= term_start_date` is equivalent to that sentence. The earlier-term case goes back to base, and O2b is closed: the rule's "term in which the withdrawal was taken" and the compute's current-term rebuild now cover the same set.
- **P2 `outcome_open`** is equivalent to "active or in its grace period". A certificate whose grace outcome is booked is either closed (a payout) or active in a new term with auto_renew already on record, so `payout_closed` is false there anyway.
- **P2 `result`** implements both branches of "replaced by auto_renew where … true, and by mail_check … where it is not".
- Unchanged bindings are as recorded in revision 5, with the P1 half of O2b now closed.

### action_binding_and_uuids (r6)

This follows from the unchanged task_tools.py (d2dc551e…) and the unchanged `target_tool` and `computes` lines:

- The seven pairs are each claimed once.
- Tool bodies are at lines 43-54, 86-89, 137-148, 185-198, 227-238, 268-271 and 308-321. Each performs one write and judges no prerequisite.
- The uuid8s are distinct and independent.
- The mail_check value written by P2 falls within update_maturity_instruction_96ab509d's documented enum.

### prerequisite_graph (r6)

- The edges are unchanged: P3←P1, P3←P2, P4←P3, P7←P5 and P7←P6. They form two disjoint DAGs.
- Each `policy_source` is verbatim, and the kinds match their gates.
- P3←P2's effect ("Once the closed-account payout instruction is replaced by the instruction to renew automatically, the renewal is due and is priced") is still true on auto-renew tiers, which covers all six tiers.
- On a hypothetical tier without automatic renewal, P2 would write mail_check, and P3 then writes no renewal. That branch has no tier in this charter (auto_renew_available is true on all six), so the edge is unaffected.

### override_declarations (r6) — whole-domain retirement sweep, all overrides

The superseded clauses are verbatim in the base, and the replacements are verbatim in the rules; all seven were checked by program.

| # | Retired clause | Base domain | Governed after retirement | Whole domain governed? |
| --- | --- | --- | --- | --- |
| 1 | cd_evt_early_withdrawal "times interest_rate divided by 100" (P1) | rate factor of every early-withdrawal penalty, any tier, any term | P1 `replaced_by`: full formula with the charter rate "divided by 100 times penalty_days divided by day_count_basis, rounded half-up to the cent". The charter-rate definition is general for any term. P1 checks only current-term penalties; earlier-term penalties go to base cd_evt_penalty_reversal, which judges them against the same general definition. | **yes**. R5-O1 closed. |
| 2 | cd_evt_maturity_and_grace "under a payout instruction the whole balance is paid as kind maturity_payout … and the certificate closes" (P2) | grace-end outcome of every payout instruction | Open payout account and mail_check: P2 rule "carried out as written … and a mail_check instruction pays the whole balance by official check". Closed payout account: replaced by auto_renew (tier offers it) or mail_check (tier does not), recorded at any point while the outcome is open. There is no longer a deadline. | **yes**. R5-G1 closed (probe below). |
| 3 | cd_instructions timing sentence (whole) (P2) | every renewal-instruction change | Owner before grace: this maturity. Owner after grace: the next maturity. Bank-owed replacement "recorded before the outcome of the grace period is booked": the maturity whose outcome is unbooked. | **yes**. Wording observation R6-O1: the replacement says "governs the maturity that has just passed", which presumes a recording after maturity. P2 now also records while the certificate is active (mid-term). There the only unbooked outcome is the coming maturity's, so the reading stays unique. No task world records mid-term. |
| 4 | cd_rate_and_bonuses "for a renewal it is the principal_balance on the renewal date …" (P3, P7) | jumbo principal of every renewal | reconciled ledger principal "for the jumbo test of every renewal, including a renewal into a different tier chosen during grace and a renewal the owner books during grace" | **yes** (unchanged since round 5) |
| 5 | cd_evt_penalty_reversal "on a grace-period withdrawal" (P5) | reversal ground for grace-withdrawal penalties | P5, with owner's-own-withdrawal definition, non-owner exclusion, and earlier penalties left to base, which still covers them through "assessed contrary to this charter" | **yes** (unchanged) |
| 6 | cd_evt_maturity_and_grace grace add-on clause (P7) | every grace add-on | P7 `replaced_by`: same limits plus the open-account condition | **yes** (unchanged) |

- **Declarations.** No undeclared override remains. The sentence-by-sentence sweep of the other base-ref sentences is unchanged from revisions 4 and 5 (followed).
- **Base consistency.** P2's mail_check fallback agrees with base cd_evt_maturity_and_grace: "An auto_renew instruction is honored only where auto_renew_available is true".

**Probes** (`r6_probes.py`, task 0 seed):

- **R5-G1, day 11 / 12 / 47 after maturity** (frozen 2026-09-14 / 09-15 / 10-20). P2 gives `outcome_open = True` and result auto_renew every time. P3 then renews every time: 3.98 in this probe, which omits the reversal. The hole is closed.
- **Tier without automatic renewal** (auto_renew_available flipped to false in the probe only): P2 writes **mail_check**.
- **Certificate already closed:** P2 writes nothing (the instruction is left as is).
- **O2b, most recent penalty (2026-01-20) now before term_start 2026-09-03** (a simulated renewal): `in_current_term = False`, so P1 gives 0 even though `misassessed = True`. The penalty is left to base, as the rule says.

### findings (r6)

**Status of round-5 items:**

| Item | Status | Evidence |
| --- | --- | --- |
| **R5-G1** | **closed** | deadline removed; `outcome_open`; mail_check fallback; probes at days 12 and 47 |
| **O2b** | **closed** | `in_current_term`; earlier-term penalty left to base; probe |
| **R5-O1** | **closed** | factor restated |

**Regression check:** none found.

- G1–G5, O2, O3, O5 and O9 remain closed. On O5: the deadline binding it introduced is replaced by `outcome_open`, which still bounds recording, now by booking status rather than by day count.
- O14, R2-O1 to R2-O6, D3, D4, the D2 source cause, O4, R4-O1, R4-O2 and S1–S3 remain closed.
- The recomputed values match earlier rounds:

  | Task | Values | Skip runs |
  | --- | --- | --- |
  | task 0 | 340.42 / auto_renew / 4.08 / 21406.18 | 3.98 / 0 / 0 |
  | task 1 | 58.73 / d9c9a0f9… / 5714.66 | 5773.39 / 0 |

- On both opening worlds, the out-of-scope policies still write nothing.

**New observation:** R6-O1 (wording, row 3 of the sweep).

**Standing observations:** O1 (latent, more than one checking account per status), R4-O3, O6, O8, O10, O11, O12.

No charter-level SOURCE-POLICY finding remains.

### closing_checklist (r6)

Written after the round-6 reveals (from 2026-09-12T22:10:04Z).

**Per-task verdicts (revision 6)**

| Task | Policy self-consistency | Problem tree | Unique solution |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

**Reworker's claims**

- R5-G1, O2b and R5-O1 are verified closed (see findings (r6) and the probes).
- The whole-domain retirement sweep passes for all six retired clauses (seven overwrite entries).
- No round-1 to round-5 closure regressed.
- New in this round: one wording observation, R6-O1.

**Checklist**

1. **Files.** 0.md and 1.md correspond one-to-one with the tasks, and _difficulty.md sits alongside them. Revisions 1–5 are preserved verbatim. Both revision-6 comparisons are PASS on all three relationships.
2. **Coverage and scope.**
   - All seven extended policies are covered: task 0 = {P1–P4, W, 4 tools}; task 1 = {P5–P7, 3 tools}.
   - The two scopes are disjoint and together complete.
   - There is one workflow, claimed once.
   - The uuid8s are independent.
   - No out-of-scope policy writes on either opening world.
3. **Problem trees.**
   - Task 0: 3 prerequisites, 2 value_input edges, all load-bearing.
   - Task 1: 2 prerequisites, both value_input, both load-bearing.
   - Together they form two disjoint DAGs.
4. **Gates.** I did not re-run the gates. The orchestrator's post-rework snapshot is cited: all seven exit 0, and traceability is deferred to the KB step. The artifacts are unchanged since that snapshot: b45ac3e2…, d2dc551e…, 48cb6b10…, b240b591….

**Difficulty verdict (r6):** the difficulty passes the source-layer policy-task audit. No charter-level SOURCE-POLICY finding remains open.
