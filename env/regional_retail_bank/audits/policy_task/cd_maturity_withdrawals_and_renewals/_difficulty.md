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

## revision_7

Re-audit round 7, by a new auditor (a fresh session; the auditor of revisions 1–6 belonged to an earlier session and was not resumed). Everything in this `charter_global_frozen` block was written to disk **before** any task's masked fields, any earlier revision of these three files, or any KB-audit report was opened. Revisions 1–6 above are left untouched (pre-append sha256 of this file: `b22aebd528c3db777733c0f52e3b7d1e3df09e23435c7919a2558816560e4d39`, 1228 lines).

### charter_global_frozen (revision_7)

- auditor: policy-task auditor, revision_7 session (independent of the instantiation author and of the revision 1–6 auditor)
- freeze time: 2026-09-13T17:48:31Z (UTC)
- frozen inputs (sha256, verified against the orchestrator's `MANIFEST.sha256`):
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/cd.extended.yaml` `075133aa807389ef92fa2d34cedca31df5b12b742e2144205202b1de80cdd19f` (1762 lines)
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/task_tools.py` `d2dc551eec2c627b7e1ae048299ca450e5aee33f9bd1800417a30d7641922470`
  - blueprint read: `blueprint.yaml`, `products/cd.yaml`, `db_schema.json`, `share_tools.py` (blueprint identical to git HEAD per the brief)
- permitted fields: the charter (base + `extended_policies` + `workflows`), the tool module, the blueprint, and the per-task masked views (`frozen_time`, `user_scenario`, `initial_state` only)
- masked and unread at freeze: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; revisions 1–6 of all three audit files; `audits/policy_kb/**`; `docs/**`
- entry conditions: the gate snapshot supplied in the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / TRACEABILITY / SCOPE, all OK on the current tree) is cited, not re-run; masked views present with hashes (task_0 `1f22fc8533c739d68cdd12aae8c9859ac58b540049391dfa50c288759735e52b`, task_1 `fff920d368d010d44218e8d697c5d1c4a52bbc56b74f45b6431b235a46d3dec5`) — entry conditions complete.
- base-copy check (mechanical): `products/cd.yaml` (1072 lines) is byte-identical to lines 1–1072 of the extended charter; the only difference is one trailing blank line (line 1073). The base copy is verbatim.
- mechanical verbatim checks (auditor's own script over the parsed YAML, whitespace-normalised): every `compute_basis` quotation of all 7 extended policies is a verbatim substring of its own `rule`; every binding has exactly one `compute_basis` entry and vice versa; every `overwrite.superseded_clause` is verbatim in the named base policy's `rule`, and every `replaced_by` is verbatim in the extended policy's own `rule`; every `prerequisite.policy_source` is verbatim in the citing policy's `rule`; every `resolved_by` is the `target_tool` of the policy named in `problem`. No authoring-viewpoint phrase ("this task", "at the opening", "current world", "wrong value", "algorithm to avoid") occurs anywhere in the charter.

#### policy_conflict_scan

Subjects and triggers of the seven extended policies:

| policy | trigger | subject / target tool / computes | overlaps checked |
| --- | --- | --- | --- |
| cd_ext_penalty_rate_reversal | state_due | cd_penalty_reversal / reverse_penalty_error_2ccc5de3 / amount | shares the subject with cd_ext_grace_withdrawal_penalty_reversal; separated by `grace_penalty` (a penalty posted day 1..grace_period_days after maturity_date is excluded here and is the grace policy's) and by "most recent penalty" in both; base cd_evt_penalty_reversal keeps every earlier penalty |
| cd_ext_closed_payout_instruction | state_due | cd_update_instructions / update_maturity_instruction_96ab509d / renewal_instruction | shares the subject with cd_ext_interest_payout_repoint; separated by field (renewal_instruction vs interest_disposition) and by the explicit hand-off "When the certificate's interest_disposition also pays out to that same closed account … cd_ext_interest_payout_repoint does not apply", mirrored by the repoint's `maturity_payout_on_record` exclusion |
| cd_ext_post_grace_renewal_rate | state_due | cd_renew / renew_certificate_term_21cb639a / interest_rate | only renewal pricer; same-tier renewals only |
| cd_ext_term_add_on_amount | on_request | cd_deposit (term_add_on) / add_term_deposit_5f936ecf / amount | shares cd_deposit with cd_ext_grace_jumbo_top_up; separated by status (active vs grace_period) and deposit_kind (term_add_on vs grace_add_on) and by the customer's request |
| cd_ext_grace_withdrawal_penalty_reversal | state_due | cd_penalty_reversal / reverse_grace_penalty_e6d62385 / amount | see first row |
| cd_ext_interest_payout_repoint | state_due | cd_update_instructions / update_interest_disposition_67b383bc / payout_account_id | see second row |
| cd_ext_grace_jumbo_top_up | on_request | cd_deposit (grace_add_on) / add_grace_deposit_522b16cc / amount | see fourth row |

Eligibility / time anchors: grace window "on or before maturity_date plus grace_period_days" (base `grace_window`, inclusive) is used identically by the top-up (`in_grace`: `DAYS(maturity_date, NOW) <= grace_period_days`) and negated by the renewal (`days_after > grace_period_days`) — the two are complementary on the same anchor, so no date is both "grace action allowed" and "renewal due". The grace-penalty window in both reversal policies is `1 <= DAYS(maturity_date, pen_date) <= grace_period_days` — the same interval. Terminal states: renewal writes `status=active`; the term add-on requires `active`; the top-up requires `grace_period` — mutually exclusive by status. Cross-category reads: checking (tier / status / opened / closed / id) and savings (status / current_balance / id) only, all through the customer-scoped CFIELD primitive (`check_compute.build_env._cross` adds `customer_id = CUST`), matching the `cross_category` declarations.

Cross-fire in both worlds, evaluated by the auditor with the charter's own compute over the masked `initial_state` (script `blind_eval.py` in the auditor's scratch directory, using `check_compute.build_env`/primitives; no task JSON read): task 0 opening world — rate reversal 340.42, closed-payout instruction `auto_renew`, renewal 0 (instruction not auto), term add-on 0, grace reversal 0, repoint = current payout_account_id (no-op, disposition compound), top-up 0; task 1 opening world — rate reversal 0 (grace-excluded; the booked 3.97 / 90 also match the charter), closed-payout instruction = current `auto_renew` (no-op), renewal 0 (day 7, not due), term add-on 0 (not active), grace reversal 58.73, repoint `d9c9a0f9…`, top-up 0 (closed payout account on record). So in each world exactly the claimed policies fire; no unclaimed policy writes anything.

Scope: the charter's 7 extended policies + 1 workflow split into {workflow, cd_ext_penalty_rate_reversal, cd_ext_closed_payout_instruction, cd_ext_post_grace_renewal_rate, cd_ext_term_add_on_amount} (the add-on world: bump-up certificate one day past grace) and {cd_ext_grace_jumbo_top_up, cd_ext_grace_withdrawal_penalty_reversal, cd_ext_interest_payout_repoint} (the in-grace top-up world). Pairwise disjoint and jointly complete over the 7 policies, and each set is exactly one root plus its prerequisite closure in the `prerequisite` graph. (Which task claims which set is confirmed per task after reveal, from `charter_scope`.)

Verdict of the scan: no conflicting conclusion on any overlapping subject, trigger, anchor, parameter or terminal state.

#### rule_compute_equivalence

Sweep in both directions, policy by policy (every quotation below is the `compute_basis` string, verified verbatim by script):

- **cd_ext_penalty_rate_reversal** — pen_id/pen_amount/pen_rate/pen_days/pen_date ← "The penalty checked is the certificate's most recent cd_penalty entry" / "its amount, rate_applied, penalty_days and posted_date are all read from that one entry" (LATEST by posted_date, MAX filtered to that id). grace_penalty ← day-1..grace_period_days sentence. in_current_term ← "one whose posted_date is on or after the term_start_date". standard_at_start ← "interest_rate less jumbo_apy_bonus points when jumbo_bonus_applied is true and less relationship_apy_bonus points when relationship_bonus_applied is true". relationship_earned ← "held on the term_start_date … opened on or before … and not closed on or before it … active … and closed checking account, one qualifying account being enough" (active branch: opened ≤ tsd; closed branch: opened ≤ tsd and closed_date > tsd). charter_rate ← "added back … simple addition". charter_days ← "no more than six calendar days after the term_start_date … greater of". misassessed ← "more than 0.001 percentage point, or whose penalty_days differ". result ← "booked amount to the cent with no further rounding … matches both … nothing is written". Reverse sweep: every rule sentence is either implemented or is scope text (hand-off to cd_evt_penalty_reversal / grace policy). No invented basis.
- **cd_ext_closed_payout_instruction** — instr/pays_out/payout_status/payout_closed/renew_offered/outcome_open/result each quoted; the compute's else-branch of `payout_status` (checking lookup for any non-savings instruction) is only consulted under `pays_out`, so it invents nothing. The rule's payout-account sentence ("replaced on the record by an active checking or savings account of the owner that the owner names") governs a tool argument the compute does not bind (see O-7.4).
- **cd_ext_post_grace_renewal_rate** — in_grace/days_after/due ("more than grace_period_days calendar days have passed … day 1"), auto ("renews only under an instruction to renew automatically", with base "An auto_renew instruction is honored only where auto_renew_available is true"), same_tier, the five ledger sums and `principal` (the declared reconciliation), jumbo ("at least jumbo_threshold … reconciled figure governs"), renewal_date (= old maturity_date), relationship (opened ≤ renewal date, closed > renewal date), new_rate (simple addition), result ("rounded half-up to 2 decimal places once, at the end"). Reverse sweep: the apy / term dates / bonus-flag sentences are rule-only (O-7.4).
- **cd_ext_term_add_on_amount** — active/offered/funded; last_addon_date/in_term/prior_total/count_left ("most recent cd_deposit entry with deposit_kind term_add_on whose posted_date is on or after the term_start_date"; equivalent to base `cd_msr_term_add_ons` because no tier allows more than one add-on per term, which the rule states); term_room/ceiling_room/funding_room/amount/result quoted. The concentration-cap sentence has no binding (O-7.5).
- **cd_ext_grace_withdrawal_penalty_reversal** — pen_id/pen_amount/pen_date/source_withdrawal/wd_destination/wd_account/taken_in_grace/owners_account/owners_withdrawal/prior_reversals/result all quoted; owners_account uses the customer-scoped CFIELD by account id, i.e. "belongs to the certificate's owner".
- **cd_ext_interest_payout_repoint** — disp/to_checking/payout_status/payout_closed/same_kind_active/other_kind_active/maturity_payout_on_record/result quoted. The rule's "the disposition becomes compound" (no same-kind active account) changes a tool argument the compute does not bind (O-7.4); the "no active account of either kind" case is not stated by the rule (result '' ) — not reached in either world.
- **cd_ext_grace_jumbo_top_up** — in_grace/renews_same/tier_ok/ledger sums/principal/prior_grace ("within the one month before the frozen date", equivalent to base `cd_msr_grace_add_ons` for the reason the rule states)/shortfall/top_up/funding/payout_status/instructions_open/fits/result quoted.

Verdict: rule ↔ compute lossless in both directions for every `computes` field. Observations O-7.4–O-7.7 below.

#### action_binding_and_uuids

Seven `(target_tool, computes)` pairs, each claimed by exactly one policy: `reverse_penalty_error_2ccc5de3/amount`, `update_maturity_instruction_96ab509d/renewal_instruction`, `renew_certificate_term_21cb639a/interest_rate`, `add_term_deposit_5f936ecf/amount`, `reverse_grace_penalty_e6d62385/amount`, `update_interest_disposition_67b383bc/payout_account_id`, `add_grace_deposit_522b16cc/amount`. The two reversal tools have identical effects except the id prefix (`cdr_` vs `cdg_`); their docstrings bind them to different subjects ("an early withdrawal penalty … as a bank-error correction" vs "a penalty that was charged on money taken out during a grace period"), matching the two policies' mutually exclusive scopes — one business reading each. uuid8s `2ccc5de3, 96ab509d, 21cb639a, 5f936ecf, e6d62385, 67b383bc, 522b16cc`: all distinct, no shared prefix beyond one hex digit, no shared tail, no sequential or adjacent pattern — consistent with independent generation. Function bodies (task_tools.py lines 43–54, 86–89, 137–148, 185–198, 227–238, 268–271, 308–321): each is a straight write with no branch on business state; the only failure path is `ctx.find(...)[0]` on an unknown certificate id — no tool validates a prerequisite, computes an amount or refuses on business grounds. No confirmation, review or wait is added by any docstring.

#### prerequisite_graph

Every policy and the workflow fill `prerequisite` (`[]` for cd_ext_penalty_rate_reversal, cd_ext_closed_payout_instruction, cd_ext_grace_withdrawal_penalty_reversal, cd_ext_interest_payout_repoint and the workflow). Edges:

| from | to | kind | gate | gate exists? | policy_source verbatim in from's rule | condition vs source |
| --- | --- | --- | --- | --- | --- | --- |
| cd_ext_post_grace_renewal_rate | cd_ext_penalty_rate_reversal | value_input | reversals | binding `reversals` | yes ("Every penalty reversal owed on the certificate is posted before the renewal is booked, because the jumbo bonus is judged on the reconciled principal …") | same ("posted … before the renewal rate is judged") |
| cd_ext_post_grace_renewal_rate | cd_ext_closed_payout_instruction | state_gate | cd_certificates.renewal_instruction | field read by binding `auto` | yes ("A certificate renews only under an instruction to renew automatically, so a payout instruction that must be replaced is replaced before the renewal is booked.") | same |
| cd_ext_term_add_on_amount | cd_ext_post_grace_renewal_rate | value_input | active | binding `active` (and `in_term` moves with term_start_date) | yes ("A term add-on is made on an active certificate, so a certificate still in grace period status whose renewal is due has that renewal booked first; …") | same |
| cd_ext_grace_jumbo_top_up | cd_ext_grace_withdrawal_penalty_reversal | value_input | reversals | binding `reversals` | yes | same |
| cd_ext_grace_jumbo_top_up | cd_ext_interest_payout_repoint | value_input | instructions_open | binding `instructions_open` | yes | same |

All `problem` targets are extended-policy ids of this file (none base, none self). Acyclic: the graph is two disjoint trees (renewal ← {rate reversal, instruction}; add-on ← renewal) and (top-up ← {grace reversal, repoint}). Each `resolved_by` is the problem's own target tool and its synchronous effect makes the `effect` true (a reversal row joins the ledger sums; the instruction/disposition update rewrites the gated field; the renewal sets status and term_start_date). No prerequisite text uses authoring-viewpoint phrasing.

#### override_declarations

Sentence-by-sentence conclusions against each `base_policy_refs` entry (only sentences touching a scored quantity listed; every other sentence of each cited base policy is followed or not reached):

- cd_ext_penalty_rate_reversal → cd_evt_early_withdrawal: "times interest_rate divided by 100" — handled differently (charter rate), **declared**. "penalty_days is early_withdrawal_penalty_days, except … within six calendar days after funding" — ext counts from term_start_date; equal to funding in a first term; for every tier with early_withdrawal_penalty_days ≥ 90 `max(epd,7) = epd`, so the two readings can differ only on a renewed 11-Month No-Penalty term (epd 0), which the default renewal never produces (its renewal_target_tier is the 12-Month Certificate) and only an owner-chosen grace term change could — not reachable in either task world (task 0 is a first-term 18-Month penalty, DAYS(tsd, pen_date) = 323). Recorded as part of O-7.2. → cd_rate_and_bonuses: relationship bonus judged "on the term_start_date" (base: "on the opening date or renewal date"); jumbo re-added from the recorded flag (base: principal at term start ≥ jumbo_threshold) — handled differently, **not named** (O-7.2). → cd_evt_penalty_reversal: "at a penalty_days or rate other than the charter's" — follows; the ext sentence "A penalty that matches both the charter rate and the charter penalty days is not reversed and nothing is written", if read unscoped, withholds for the most recent current-term non-grace penalty the base reversal on other grounds (penalty-free withdrawal after the waiting days, withdrawal of credited interest, basis larger than the principal removed) — **not named** (O-7.1). → cd_evt_maturity_and_grace: grace exclusion — follows.
- cd_ext_closed_payout_instruction → cd_evt_maturity_and_grace payout clause and cd_instructions "recorded before the grace period ends" clause: both **declared**; the merged semantics are unique (owner changes keep the base timing; the bank-owed replacement governs the passed maturity). "An auto_renew instruction is honored only where auto_renew_available is true" — followed (`renew_offered`). "The payout account must be … in active status when the instruction is recorded" — followed.
- cd_ext_post_grace_renewal_rate → cd_rate_and_bonuses "for a renewal it is the principal_balance on the renewal date after any grace-period add-ons and withdrawals" — **declared**. "re-evaluated on the renewal date" / "active checking account … on the renewal date" — ext fixes renewal date = old maturity_date (base: new term starts on the maturity date) and judges "held" by opened/closed dates; equivalent to base "active on that date" — follows. Rounding "once, at the end" — additive of 2-dp parameters; no divergent value possible.
- cd_ext_term_add_on_amount (`overwrite: []`) → cd_evt_term_add_on: count/min/term cap/ceiling — followed (the ext converts the limits into the largest allowed amount, which is what the owner asked for; base limits are all respected). → cd_agg_combined_principal: restated, not weakened. → cd_open_and_funding: same-customer funding account — followed. → cd_evt_maturity_and_grace: renewal at end of grace — followed. `overwrite: []` justified.
- cd_ext_grace_withdrawal_penalty_reversal → cd_evt_penalty_reversal "on a grace-period withdrawal" — narrowed to the owner's own withdrawals, **declared**. Other sentences followed.
- cd_ext_interest_payout_repoint (`overwrite: []`) → cd_evt_interest "otherwise the interest compounds for that period" — describes crediting while the account is closed; the ext changes the record so later periods pay out — compatible, not a replacement. → cd_instructions: disposition from interest_payout_options, active same-customer payout account — followed. `overwrite: []` justified.
- cd_ext_grace_jumbo_top_up → cd_evt_maturity_and_grace grace add-on clause (adds the open-payout-account condition; replaces `cd_msr_grace_add_ons` by a one-month window, equivalent for the reason stated) — **declared**. → cd_rate_and_bonuses renewal-principal clause — **declared**. → cd_agg_combined_principal: not restated, not weakened (base inherited). → cd_open_and_funding / cd_evt_term_add_on: followed / not reached.

Disguised forms: anonymous intermediate factor — `standard_at_start` (rate reversal) is named and quoted; 0/1 multiplier — `instructions_open` (top-up) zeroes the amount and is declared by the first overwrite; dropped branch — none found (the renewal's "different tier" branch is scoped out by the rule itself and base still governs it).

#### findings (charter-global, revision_7)

No charter-global `SOURCE-POLICY RED`. Observations (each names the tasks it bears on; the per-task files demonstrate whether it costs anything):

- **O-7.1** (undeclared-override candidate, cd_ext_penalty_rate_reversal vs cd_evt_penalty_reversal) — see override_declarations. Bears on task 0 (the only world where this policy fires). Consequence to be demonstrated there.
- **O-7.2** (undeclared-override candidates, cd_ext_penalty_rate_reversal vs cd_rate_and_bonuses / cd_evt_early_withdrawal) — relationship bonus at term_start_date instead of the opening date; jumbo from the recorded flag instead of the principal test; the six-day minimum counted from term_start_date instead of funding (differs only on a renewed 11-Month term). Bears on task 0.
- **O-7.3** (naming, cd_ext_penalty_rate_reversal) — `standard_at_start` is defined from the current interest_rate, which a bump-up raises mid-term, so on a bumped certificate "the tier's standard rate at term start" is not what is computed; the rule itself states the computation, so rule and compute agree. Bears on task 0 only if the certificate was bumped.
- **O-7.4** (argument coverage) — each compute binds only its `computes` field; other scored arguments are fixed by rule sentences alone: renewal apy / flags / term dates / tier; the instruction's payout_account_id ("that the owner names"); the repoint's interest_disposition (compound branch only). Bears on tasks 0 and 1.
- **O-7.5** (rule sentence without binding) — cd_ext_term_add_on_amount's concentration-cap sentence is enforced by base eligibility `concentration_cap`, not by compute; the top-up is silent on the cap. Bears on tasks 0 and 1.
- **O-7.6** (rounding primitive) — rules say "half-up"; the DSL's `RND` is Python `round` on binary floats. Matters only on an exact half-cent tie. Bears on tasks 0 and 1.
- **O-7.7** (single-row cross reads) — CFIELD returns the first account of a status; with several active checking or savings accounts, "one qualifying account being enough" / "that savings or money market account" could diverge from the compute. Bears on tasks 0 and 1.
- **O-7.8** (workflow dataflow) — `dataflow` lists only step 2→3 (status → `active_for_add_on`, `concentration_cap`); the reversal→renewal (ledger) and instruction→renewal (renewal_instruction) productions are carried by the `prerequisite` edges and `order_rationale`, not by dataflow entries. `requires_external_wait` / `zero_wait_proof` are carried by the task JSON's `solvability_contract` (per erl-task-instantiate SKILL.md §solvability; the SOLVABILITY gate is green) — to be confirmed at reveal. Bears on task 0.

Base-section observations (base layer, reported for completeness; scored-value impact assessed per task):

- **B-7.1** cd_evt_early_withdrawal `formula.penalty_amount` = `principal_balance * interest_rate / 100 * early_withdrawal_penalty_days / day_count_basis`, while its own rule makes the basis "the requested amount for a partial" and applies the six-day minimum. Base formula ≠ base rule. No extended policy recomputes a penalty amount (both reversal policies reverse the booked amount), so no scored value moves.
- **B-7.2** base `lifecycle` marks grace_period→active and grace_period→closed as `by: system` at the end of grace, while this difficulty books the renewal with an agent task tool on the first day after grace. The renewal is due on the frozen date in the one world that books it; no scored value moves.

---

## revision_8

Re-audit round 8, by a new auditor in a fresh session; not the auditor of revisions 1-7. **Revisions 1-7 above are untouched.** Pre-append sha256 of this file: `304ef565e2ccaf4cad404cbd487b059b428d3e7010780ec33fd3a81162b77e37` (1332 lines).

**Grounds for re-deriving the charter-global section in full rather than carrying it forward.** The shared inputs have moved since the round that produced revision_7: `cd.extended.yaml` was `075133aa807389ef92fa2d34cedca31df5b12b742e2144205202b1de80cdd19f` at revision_7 and is now `0dfc2c4b2268b0b7f7fea4bbf14884e02f359195ef1a8efd8060bd58705638a3`; `task_tools.py` was `d2dc551eec2c627b7e1ae048299ca450e5aee33f9bd1800417a30d7641922470` and is now `7fd301983c9fd6de17f3ece522baed38ff73ec078d2c349b9afaac2fc45a7398`. The difficulty has been regenerated: the four extended policies, their tool names and uuid8s, both task worlds and both problem trees are new, and nothing of revisions 1-7 applies to the artifacts on disk. The whole section below was therefore re-derived from scratch, blind, before any GT was revealed.

**The revision_8 text was written before its author read any part of revisions 1-7.** The earlier revisions were discovered only after both tasks' derivations were frozen and both GTs revealed, when the working tree was compared with git; the first twenty lines of each old file were then read to establish the revision numbering and the old artifact hashes quoted above. No blind answer below was written with any knowledge of an earlier revision's conclusions.

### charter_global_frozen

- auditor: independent source-layer auditor (not the instantiating agent)
- freeze time (charter-global section written, before any task GT was revealed): 2026-09-16T09:34:57Z
- freeze hashes (sha256):
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/cd.extended.yaml` = `0dfc2c4b2268b0b7f7fea4bbf14884e02f359195ef1a8efd8060bd58705638a3`
  - `env/regional_retail_bank/tasks/cd_maturity_withdrawals_and_renewals/task_tools.py` = `7fd301983c9fd6de17f3ece522baed38ff73ec078d2c349b9afaac2fc45a7398`
  - `env/regional_retail_bank/blueprint/products/cd.yaml` = `7a14550e7c6bc9cfc2f59401c8032dd5371b4809ce2874ec58315695dc044aa8`
- fields permitted for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml` (cd plus the five categories the cross-category factors read), the whole of `cd.extended.yaml`, the whole of `task_tools.py`, and `erlbench/` + the instantiation gate scripts used only as arithmetic oracles.
- fields explicitly masked while this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state` of both tasks. The two task worlds were read only through the machine-masked views
  `.../scratchpad/masked/cd_maturity_withdrawals_and_renewals/0.json` (sha256 `5d0d55b7829114f87d2d55c88fd34e972980497f703237134684806bb971b2d5`) and `1.json` (sha256 `7ec8744fde485c6e402a51f4d560fdaa3a64aff7f4deb8af243fb1545d4fbe68`), each carrying only `frozen_time`, `user_scenario`, `initial_state`.
- contamination: none. No unmasked task file was opened before both task derivations were on disk; no recursive grep was run over `env/regional_retail_bank/tasks/`.

#### entry conditions (step 0)

The instantiation gate snapshot was supplied with the brief and is cited, not re-run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 14 acts / 1.json 16 acts, det True, 0 errs, closure matches), SOLVABILITY OK (verify True, 2 base gates, 5 gates, 20/14 seed rows), COMPUTE OK (branches mean 35.00, steps mean 15.00, history_rows_max 10, branches_max 37), GROUNDING OK, SCOPE OK. `check_traceability.py` is correctly deferred to the render stage. Masked views were constructed mechanically with their hashes, and both hashes were re-verified by this auditor and match the brief. **Entry conditions complete.** A green gate block is the qualification to enter this audit, not evidence that the policy is self-consistent over its domain.

#### policy_conflict_scan

The structured policy in force for this category is `cd.extended.yaml`: eleven base policies copied from `blueprint/products/cd.yaml` plus four `extended_policies`. The base section was compared key by key against the blueprint file and is **verbatim identical** (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` all compare equal), so the base copy has not been rewritten.

Overlapping subjects across the four extended policies:

| policy | subject | target_tool | computes | trigger |
| --- | --- | --- | --- | --- |
| cd_ext_overdue_term_renewal_rate | [cd_renew] | record_term_renewal_3666596b | new_interest_rate | state_due |
| cd_ext_partial_early_withdrawal_penalty | [cd_withdrawal] | confirm_partial_withdrawal_44cc2957 | penalty_amount | on_request |
| cd_ext_omitted_withdrawal_entry | [cd_penalty] | credit_mischarged_penalty_7001af6d | entry_amount | state_due |
| cd_ext_term_restoring_add_on | [cd_deposit] | confirm_term_add_on_1e70ab4d | deposit_amount | on_request |

No two extended policies share a subject event type, a target tool or a computed quantity. `cd_ext_partial_early_withdrawal_penalty` and `cd_ext_omitted_withdrawal_entry` both end in a `cd_penalty` ledger row, but the first writes it only as the inseparable companion of a withdrawal it creates in the same call, while the second attaches one to a withdrawal already standing on the ledger; the two can never claim the same row. Time anchors are distinct (renewal anchored on the ended term's maturity date; penalty on the day the principal leaves; entry on the day it is booked; deposit on the day it posts). Terminal states are distinct (certificate carried into a new term / principal reduced by a withdrawal and its penalty / principal reduced by an entry / principal raised by a deposit). Cross-category reads are all read-only through `CFIELD`/`XSUM`/`XCOUNT` on checking, savings, card and auto; no extended policy writes outside `cd_certificates` and `cd_transactions`.

Claimed scopes: the M=2 tasks partition the four extended policies into two problem trees, {cd_ext_overdue_term_renewal_rate → cd_ext_partial_early_withdrawal_penalty} and {cd_ext_omitted_withdrawal_entry → cd_ext_term_restoring_add_on}. The two sets are **pairwise disjoint and jointly complete** over `extended_policies`. (Which task takes which tree is recorded in that task's own file.)

**Result: no policy-to-policy conflict found among the four extended policies.** Conflicts found against the *base* section are recorded under `override_declarations` and `rule_compute_equivalence` below.

#### rule_compute_equivalence

Check 2 was run sentence by sentence over all four policies: every quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and rounding convention in each `compute` was traced to a verbatim `compute_basis` quotation, and each `rule` sentence was swept back to a compute binding. Every `compute_basis` entry is a verbatim substring of its policy's `rule` (checked mechanically). The declared factor ladders were checked tier by tier against the rule prose and against the `decides` binding's branches.

Four divergences were found where the rule sentence and the implementing expression do not say the same thing. They are written up in `findings` as **CG-1** … **CG-4**.

Everything else closes in both directions. In particular:
- the assembled-rate ordering ("added together in that order … rounded down … once, at the end") is implemented once, at `rounded_rate`, with no intermediate rounding;
- the penalty ordering ("after the basis, the rate and the days have been brought together in that order") is implemented as `raw_penalty` → `charged_penalty` → `rounded_penalty` with a single rounding;
- the entry ordering ("after the principal, the rate and the days have been brought together in that order") is implemented as `raw_entry` → single half-up rounding at `result`;
- the add-on caps ("no more than the total the tier accepts … less what has already been added", "no more than the room left under the largest principal", "at least the smallest single add-on") are implemented as `MX(MN(MN(...)))` in exactly that order.

#### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair is claimed twice and no policy claims two tools. Reading each tool's subject, base refs, docstring and terminal state, each admits one business reading. No tool adds a confirmation, review, wait or procedure outside its policy; each function body performs only the writes its policy's terminal state names, and **no function body reads a prerequisite, refuses, errors or hints on a business ground** (verified by reading all four bodies: each does `ctx.find` for the owner/balance, `ctx.create`/`ctx.update`, and returns a confirmation string; there is no conditional refusal anywhere).

uuid8s: `3666596b`, `44cc2957`, `7001af6d`, `1e70ab4d`. All four are 8 hex characters, pairwise distinct, share no prefix, are not adjacent or sequential values, and none is another's tail rewritten. **No evidence of batch derivation.**

Docstring sequence discipline: no docstring names another tool or states this action's position relative to another action. Two phrases were examined and cleared, one retained as an observation (**CG-8**).

#### prerequisite_graph

Check 7 over the whole graph:

| blocked policy | problem | kind | gate | form | fallback_reason | resolved_by | == dep target_tool | gate in blocked compute |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cd_ext_partial_early_withdrawal_penalty | cd_ext_overdue_term_renewal_rate | value_input | applied_rate | state | absent (correct) | record_term_renewal_3666596b | yes | yes |
| cd_ext_term_restoring_add_on | cd_ext_omitted_withdrawal_entry | value_input | entries_booked_year | state | absent (correct) | credit_mischarged_penalty_7001af6d | yes | yes |

`cd_ext_overdue_term_renewal_rate.prerequisite` and `cd_ext_omitted_withdrawal_entry.prerequisite` are both `[]` (filled in, not omitted). Every `problem` points at another extended policy id in this same file; neither points at a base policy nor at itself. The graph has two edges and four nodes and is **acyclic**, and remains acyclic when the two tasks' trees are unioned (they share no node). Both `policy_source` strings were confirmed mechanically to be verbatim substrings of the blocked policy's own `rule` and **not** substrings of the depended-on policy's rule. Both `form` values are `state` and neither carries `fallback_reason`, which is correct for the state form. Neither `condition` is stronger or weaker than what check 6 derives from the sentence. Both `resolved_by` tools genuinely make the `effect` hold (the renewal write sets `interest_rate`/`term_start_date`/`maturity_date`/`status`/`renewal_count`, which is exactly what `applied_rate` reads through `F('interest_rate')` and `checking_opened_before_term`; the entry write creates a `cd_penalty` row, which is exactly what `entries_booked_year` sums). Both `kind` values are `value_input` and both `gate` names are real bindings in the blocked policy's `compute`. No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in either `prerequisite` block.

#### prerequisite_sentences

Check 6, four-point test, on each of the two edges.

**Edge 1** — `cd_ext_partial_early_withdrawal_penalty` waits on `cd_ext_overdue_term_renewal_rate`.
Sentence (verbatim from the blocked policy's own rule): *"The penalty on principal taken out of a certificate before maturity is worked out only after the certificate carries the rate and the term dates of the term running on the day the principal leaves."*
1. Ordering connective: **"only after"**, joining this policy's own result ("the penalty … is worked out") to what it waits on. ✓
2. Declared form is `state`; what is waited on is *"the certificate carries the rate and the term dates of the term running on the day the principal leaves"* — a record-visible state in the words the certificate table and its finder use (`interest_rate`, `term_start_date`, `maturity_date` are shown by `find_cd_certificates` as "the rate and APY of the current term … term start and maturity dates"). No action, no performer, no tool. ✓
3. Names no tool, no policy id, no snake_case token, no row id. ✓
4. Strength and scope match `condition` exactly (status active and the dates spanning the day of the withdrawal). ✓
Exactly one write of this difficulty brings that state about: `record_term_renewal_3666596b` writes `term_start_date`, `maturity_date`, `interest_rate` and `status`. The other three writes create ledger rows and adjust `principal_balance` only, and none writes a term date or a rate onto the certificate. **The hop resolves in one reading.** Derivation a reader performs: the sentence says the penalty waits on the certificate carrying *this* term's rate and dates → the records show dates that do not span today and a status that is not active → the only rule in the charter that describes a certificate being given a new term's rate and dates is `cd_ext_overdue_term_renewal_rate` ("A term that has reached the end of its grace window without the owner closing the certificate is carried into a new term …", "The rate a new term carries is …") → its own target tool is the write. No second reading is available.
No second wording of this dependency appears anywhere in the blocked rule, and the depended-on rule does not restate the sentence.

**Edge 2** — `cd_ext_term_restoring_add_on` waits on `cd_ext_omitted_withdrawal_entry`.
Sentence (verbatim from the blocked policy's own rule): *"The deposit that restores a certificate to the principal its term began with is fixed only after every early partial withdrawal standing on its ledger carries the entry owed for the principal it removed."*
1. Ordering connective: **"only after"**. ✓
2. Declared form is `state`; what is waited on is *"every early partial withdrawal standing on its ledger carries the entry owed for the principal it removed"* — a record-visible state of the ledger, in the words `find_cd_transactions` uses ("early withdrawal penalties … and the entry it relates to (the withdrawal behind a penalty)"). No action, no performer, no tool. ✓
3. Names no tool, no policy id, no snake_case token, no row id. ✓
4. Matches `condition` in strength and scope. ✓
One write brings the state about for a withdrawal already on the ledger: `credit_mischarged_penalty_7001af6d`, which takes a `source_item_id` naming an existing withdrawal. `confirm_partial_withdrawal_44cc2957` also creates a `cd_penalty` row, but only as the companion of a withdrawal it creates in the same call, so it can never attach an entry to a withdrawal that is already standing entry-less. **The hop therefore resolves in one reading**, though the reader must notice that distinction; it is recorded as observation **CG-9**.
Derivation a reader performs: the sentence says the deposit waits on every early partial withdrawal carrying its entry → the ledger shows a withdrawal with no entry against it → the only rule that describes booking the entry a withdrawal owes is `cd_ext_omitted_withdrawal_entry` ("An early partial withdrawal owes the certificate an entry for the principal it removed, and where the ledger carries no such entry against it the entry is still owed and is booked when it is found.") → its own target tool is the write.
No second wording; the depended-on rule does not restate the sentence.

**No cross-problem order is stated in any extended rule that grounds no declared edge.** Every sentence containing an ordering or timing word was enumerated mechanically and each is either one of the two prerequisite sentences or an intra-computation window ("in the twelve months before the deposit", "after the basis, the rate and the days have been brought together in that order", "before the term now running began"), none of which orders one problem against another. No base rule sentence grounds either edge.

#### override_declarations

Check 1, sentence by sentence against every `base_policy_refs` entry. Findings only; each affected task's file demonstrates the consequence against its own world.

**cd_ext_overdue_term_renewal_rate** (refs `cd_rate_and_bonuses`, `cd_evt_maturity_and_grace`); three `overwrite` entries, each naming a base sentence verbatim: the relationship-bonus sentence, the jumbo-bonus clause, and the "for a renewal it is the principal_balance on the renewal date after any grace-period add-ons and withdrawals" clause. Sweeping the remaining base sentences:
- "The rate of a term is fixed at its start." — followed.
- "It is the tier's standard_interest_rate plus bonus points, and the APY is the tier's standard_apy plus the same bonus points." — followed, with the graded figures substituted for the bonus points.
- "The two bonuses stack by simple addition; no other bonus exists." — followed (`assembled_rate` is a sum).
- "A bonus that is later lost … stays in the rate until the term ends; a bonus that becomes available mid-term is not added until the next term." — not contradicted (this is a renewal).
- "On renewal the rate follows renewal_rate_basis: the target tier's published standard rates **on the maturity date**, with both bonuses re-evaluated **on the renewal date** when relationship_bonus_on_renewal is true." — the extended rule anchors everything on *"the day the new term is recorded"* ("the new term's figures are those of the day it is recorded", "the relationship figure and the jumbo figure the certificate earns on the day the new term is recorded"). The extended rule dates the rate and the bonus evaluation from a **different day** than the base sentence does, and that base sentence is **not named in `overwrite`**. Recorded as **CG-5**.
- `cd_evt_maturity_and_grace`: "On the day after the grace period ends, if no grace action closed it, the certificate follows its renewal_instruction: under auto_renew it renews into renewal_target_tier … with a new term starting on the maturity date." — followed exactly (tier from `renewal_target_tier`, term starting on the maturity date). "An auto_renew instruction is honored only where auto_renew_available is true" — inherited, not weakened. "After the grace period ends, any withdrawal is again an early withdrawal of the new term." — inherited and relied on by edge 1.

**cd_ext_partial_early_withdrawal_penalty** (refs `cd_evt_early_withdrawal`, `cd_evt_maturity_and_grace`, `cd_evt_interest`); four `overwrite` entries naming, verbatim, the request/confirm sentence, the penalty-basis sentence, the penalty-formula sentence and the penalty-days sentence. Sweeping the rest of `cd_evt_early_withdrawal`:
- "Principal can be withdrawn before maturity only from a certificate whose status is active." — inherited, not weakened; it is part of why edge 1 is unmet at the opening.
- the ordered classification of withdrawal kinds (interest_withdrawal → death_waiver → penalty_free → early_full/early_partial) — inherited; the extended rule addresses only the early_partial branch.
- "Partial withdrawals are allowed only where partial_early_withdrawal_allowed is true, for at least partial_withdrawal_min_amount, leaving at least minimum_balance_after_partial, and no more than max_partial_withdrawals_per_term per term counted by cd_msr_term_partial_withdrawals; a request breaking any of these is declined, never converted." — inherited. The extended rule restates the remaining-balance limb in its own words ("The largest sum a single partial withdrawal may remove is the principal standing on the certificate less the balance the tier requires to remain after a partial withdrawal") without weakening it. Tension with the inherited limb once the penalty is also taken from principal is recorded as observation **CG-7**.
- "The penalty is taken from principal even when it exceeds interest earned" — inherited; the tool lowers `principal_balance` by the penalty.
- "For a full withdrawal … for a partial the amount paid out is the requested amount and the penalty is deducted from the remaining principal." — followed by the tool body.
- "Proceeds go by one of payout_methods to an account of the same customer or by official check." — inherited; the tool's `destination` enum is exactly `payout_methods` plus `none`.
- `cd_evt_interest`: "Interest accrued but not yet credited is credited on the day of a full early withdrawal before the penalty is computed." — scoped to *full* withdrawals, so it does not reach a partial; not weakened.
**No undeclared override found in this policy** beyond the observation at CG-7.

**cd_ext_omitted_withdrawal_entry** (refs `cd_evt_early_withdrawal`, `cd_evt_interest`); three `overwrite` entries naming, verbatim, the penalty-basis sentence, the penalty-days sentence and the penalty-formula sentence. The remaining base sentences (classification order, partial limits, penalty taken from principal, proceeds) are untouched by this policy, which pays nothing out. The base trigger "Every other withdrawal before maturity is early_full or early_partial and carries a penalty through its trigger" is the very premise this policy acts on. **No undeclared override found.**

**cd_ext_term_restoring_add_on** (refs `cd_evt_term_add_on`, `cd_evt_maturity_and_grace`, `cd_agg_combined_principal`, `cd_open_and_funding`, `cd_evt_early_withdrawal`); one `overwrite` entry naming, verbatim, the add-on limits sentence. Sweeping the rest:
- "Outside the grace period a certificate accepts new principal only on a tier whose term_add_on_max_count is above zero." — inherited, not weakened.
- "A term add-on is allowed only while the certificate's status is active." — inherited.
- "An add-on earns the certificate's existing rate from its posted date and does not change the maturity date or re-evaluate the jumbo bonus." — restated in the extended rule in the same terms and implemented by the tool (which touches neither dates nor rate).
- `cd_agg_combined_principal`: the `combined_principal_cap` of 2,500,000.00 is inherited and not weakened; `cd_open_and_funding`: `funding_sources_allowed` is inherited and is exactly the tool's `funding_source` enum.
**No undeclared override found.**

Three disguised forms were looked for specifically. **Anonymous intermediate factor:** the graded bindings all carry their own names and each is quoted to a rule sentence; none hides inside an unnamed intermediate. **0/1 multiplier:** `retained_share` (0.9/0.95/1) and `restoration_allowance` are multipliers/addends but never zero out a base the rule has already fixed; `interest_days` can be 0, and that is the baseline the rule itself states ("the days over which it runs are none"). **Dropped branch:** base's branches that extended's selectors never produce were checked — `cd_evt_early_withdrawal`'s `interest_withdrawal`, `death_waiver` and `penalty_free` kinds are simply out of these policies' subject, not dropped by a selector. No author note in any `rule` or `compute_basis` calls a base output a "wrong value" or an "algorithm to avoid".

#### factor_ladders

Charter-global structure only. Whether a factor bears weight is a fact about one world and lives in that task's `factor_weight`.

**cd_ext_overdue_term_renewal_rate** — 4 factors.

| id | effect | decides | tiers | multi-source (non-fall-through tiers) | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| relationship_figure_grade | parameter | relationship_figure | 3 | yes (checking_accounts row ∧ checking_transactions rows) | checking |
| jumbo_figure_grade | parameter | jumbo_figure | 3 | yes (carried principal from cd_certificates/cd_transactions ∧ savings_accounts row) | savings |
| carried_principal_measure | method | carried_principal | 3 | yes (cd_transactions rows ∧ cd_certificates.interest_rate against the tier parameter) | — |
| assembled_rate_rounding | method | rounded_rate | 3 | **no** (each tier is one condition on one card-spend aggregate) | card |

Counts: 2 `parameter`, 2 `method`, 3 multi-source, 3 `cross_difficulty` (checking, savings, card). Within bounds (4–6 factors, ≥2 of each effect, ≥2 multi-source, ≥2 cross-difficulty). Binding sets are pairwise disjoint. No `decides` is `result`. Every tier of every ladder appears as a sentence of the `rule` and as a branch of the `decides` expression, except as recorded at **CG-1** (`relationship_figure`, closed enumeration in compute against an open tier-dependent list in the rule) and **CG-2** (`jumbo_figure` tier 1, "holds an active savings or money market account" implemented as `savings_balance > 0`). Labels are honest: the two `parameter` factors substitute percentage-point figures into an unchanged sum; the two `method` factors change the measurement of the base and the rounding operation respectively, and every method tier names a rule the charter states.

**cd_ext_partial_early_withdrawal_penalty** — 5 factors.

| id | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| penalty_basis_measure | method | charged_basis | 3 | yes (cd_transactions interest rows ∧ cd_certificates.interest_rate; cd_transactions withdrawal rows ∧ absence of interest rows) | — |
| charged_rate_grade | parameter | applied_rate | 3 | yes (checking_accounts row ∧ cd_certificates.term_start_date) | checking |
| charged_days_measure | method | charged_days | 3 | yes (card_accounts row ∧ card_transactions rows) | card |
| charged_share_grade | parameter | retained_share | 3 | yes (savings_accounts row ∧ cd_certificates.renewal_count) | savings |
| charged_penalty_rounding | method | rounded_penalty | 3 | tier 1 yes (checking_accounts row ∧ cd_certificates.renewal_count); tier 2 single-source | checking |

Counts: 2 `parameter`, 3 `method`, ≥4 multi-source, 4 `cross_difficulty` (checking, card, savings, checking). Within bounds. Binding sets disjoint; no `decides` is `result`. Labels honest (`charged_rate_grade` and `charged_share_grade` substitute numbers; `penalty_basis_measure`, `charged_days_measure` and `charged_penalty_rounding` change the base, the day count and the rounding operation). Tier-to-rule correspondence holds except as recorded at **CG-3** ("in the month now running" implemented as a rolling `within_months=1` window) and **CG-1** (the same closed/open checking-tier enumeration, here in `applied_rate`, plus a zero-balance gap in `charged_penalty_rounding` tier 2).

**cd_ext_omitted_withdrawal_entry** — 4 factors.

| id | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| entry_principal_measure | method | entry_principal | 3 | yes (card_accounts row ∧ cd_transactions interest rows) | card |
| entry_rate_grade | parameter | entry_rate | 3 | yes (auto_loans row ∧ auto_transactions rows) | auto |
| entry_days_measure | method | entry_days | 3 | yes (savings_accounts row ∧ cd_transactions interest rows) | savings |
| added_days_grade | parameter | added_days | 3 | yes (cd_transactions withdrawal date ∧ savings_accounts row) | savings |

Counts: 2 `parameter`, 2 `method`, 4 multi-source, 4 `cross_difficulty` (card, auto, savings, savings — two distinct categories). Within bounds. Binding sets disjoint. Labels honest (`entry_rate_grade` and `added_days_grade` substitute a rate and a day count; `entry_principal_measure` and `entry_days_measure` change how the base and the day span are measured, including a cap in tier 1). Tier-to-rule correspondence holds except as recorded at **CG-4** (tiers 2 and 3 of `entry_principal_measure` overlap as the rule states them) and **CG-6** ("interest was credited in each of the three months" implemented as a row count, not a distinct-month count).

**cd_ext_term_restoring_add_on** — 5 factors.

| id | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| lost_principal_measure | method | lost_principal | 3 | yes (auto_loans row ∧ cd_transactions withdrawal rows) | auto |
| restored_interest_span | method | interest_days | 3 | yes (checking_accounts row ∧ cd_transactions withdrawal rows) | checking |
| restoration_rate_grade | parameter | restoration_rate | 3 | yes (card_accounts row ∧ card_transactions rows) | card |
| restoration_allowance_grade | parameter | restoration_allowance | 3 | tier 1 yes (savings_accounts row ∧ cd_certificates.renewal_count); tier 2 single-source | savings |
| restoring_deposit_rounding | method | rounded_deposit | 3 | yes (cd_transactions add-on rows ∧ checking_accounts.opened_date) | checking |

Counts: 2 `parameter`, 3 `method`, ≥4 multi-source, 5 `cross_difficulty` (auto, checking, card, savings, checking). Within bounds. Binding sets disjoint. Labels honest. Tier-to-rule correspondence **fails on tier 2 of `lost_principal_measure`**, recorded as **CG-1a** below in findings, and the same closed/open checking-tier enumeration recurs in `restored_interest_span` (**CG-1**).

#### findings

Each finding names the tasks it bears on so that their files can carry the demonstration; the demonstrations themselves are not repeated here.

---

**CG-1 — SOURCE-POLICY RED. The checking-tier list that three ladders call "a tier the certificate's own tier lists as qualifying" is implemented as a fixed three-tier enumeration, so the rule and the compute reach different conclusions for two of the six certificate tiers.**

*Symptom.* Three ladders decide a tier by whether the owner's checking account is "of a tier the certificate's own tier lists as qualifying"; the implementing expressions test membership of the literal set {Interest Checking, Premier Checking, Private Client Checking}.

*Root cause.* `relationship_qualifying_checking_tiers` is a per-variant parameter, not a constant. `blueprint/products/cd.yaml` sets it to `[Interest Checking, Premier Checking, Private Client Checking]` for five tiers but to **`[Premier Checking, Private Client Checking]`** for the 11-Month No-Penalty Certificate. The compute hard-codes the five-tier value.

*Evidence.*
- rule, `cd_ext_overdue_term_renewal_rate`: "an owner who holds an active checking account of a tier the certificate's own tier lists as qualifying and has had fewer than six deposits posted to it in those three months earns three quarters of the tier's relationship bonus points"
- compute, same policy: `relationship_figure: … (P('relationship_apy_bonus') * 3 / 4 if ((qualifying_checking_tier == 'Interest Checking' or qualifying_checking_tier == 'Premier Checking' or qualifying_checking_tier == 'Private Client Checking') and checking_deposit_count < 6) else 0)`
- rule, `cd_ext_partial_early_withdrawal_penalty`: "an owner holding an active checking account of a tier the certificate's own tier lists as qualifying, opened before the term now running began, is charged at the rate the term carries less the tier's relationship bonus points; an owner holding an active checking account of a tier that does not qualify … is charged at the tier's published standard interest rate"; compute `applied_rate` hard-codes the same three tiers as qualifying and `{Access Checking, Student Checking, Everyday Checking}` as non-qualifying.
- rule, `cd_ext_term_restoring_add_on`: "where the owner holds an active checking account of a tier the certificate's own tier lists as qualifying …"; compute `qualifying_checking: 1 if (checking_tier_held == 'Interest Checking' or … ) else 0`.
- `blueprint/products/cd.yaml`, 11-Month No-Penalty Certificate: `relationship_qualifying_checking_tiers: [Premier Checking, Private Client Checking]`.

*Demonstrated consequence.* Take an 11-Month No-Penalty Certificate whose owner holds an active Interest Checking account with fewer than six deposits in the window. The rule places the owner on the fall-through tier ("an owner who holds no active checking account of a qualifying tier earns nothing"): relationship figure **0.00**, assembled rate 3.54 + 0.00 + jumbo. The compute places the owner on tier 2: relationship figure 0.05 × 3/4 = **0.0375**, assembled rate 3.5775 + jumbo. The two readings differ by 0.04 percentage points on the rate written for the term, and in `applied_rate` the same customer is charged at `F('interest_rate') − 0.05` under the compute and at the tier's published 3.54 under the rule. Under `charged_rate_grade` the compute's non-qualifying set is also closed where the rule's is open ("a tier that does not qualify"), so an Interest Checking holder on an 11-Month certificate falls through the compute's second branch into "every other owner" while the rule puts them in the second tier.

*Affected artifact and location.* `cd.extended.yaml`, `extended_policies[cd_ext_overdue_term_renewal_rate].compute[relationship_figure]`, `extended_policies[cd_ext_partial_early_withdrawal_penalty].compute[applied_rate]`, `extended_policies[cd_ext_term_restoring_add_on].compute[qualifying_checking]`, against the matching `rule` sentences.

*Bears on.* Neither task 0 (12-Month Certificate) nor task 1 (18-Month Bump-Up Certificate) instantiates a tier whose qualifying list differs from the hard-coded set, so neither task's scored value moves. The defect is a defect of the charter, which the rendered KB will carry.

---

**CG-1a — SOURCE-POLICY RED. Tier 2 of `lost_principal_measure` is stated one way in the `rule` and a different way in `factors[].ladder` and `compute`.**

*Symptom.* The middle tier of the ladder that measures "the principal the term has lost" is three different things depending on which face of the policy is read.

*Root cause.* A tier present in one face of the policy and absent from the other.

*Evidence.*
- `rule`: "*where the owner has an auto loan at the bank that is not past due and principal was taken out only once in those months, it is the principal that withdrawal removed, **less any credit back posted in them***"
- `factors[lost_principal_measure].ladder[1].method`: "*the loss is the principal that withdrawal removed **together with every entry booked for it in those months**"* (no credit back subtracted)
- `compute[lost_principal]`: `… else ((withdrawn_principal_year + entries_booked_year) if (auto_loan_standing == 'active' and withdrawals_in_year == 1) else …)`

*Demonstrated consequence.* On task 1's own ledger, restricted to the single May withdrawal (6,000.00) with the entry of 130.15 booked for it and no reversal: the `rule` sentence yields a loss of **6,000.00**, the ladder and the compute yield **6,130.15**. The two faces of one policy give two different restoring deposits, 130.15 apart, for the same records. Because tier 1 also carries the entries, the rule's tier 2 is additionally the only tier of the three in which an entry booked in the window is *not* counted, which is the opposite of what the prerequisite edge's `effect` asserts the binding does.

*Affected artifact and location.* `cd.extended.yaml`, `extended_policies[cd_ext_term_restoring_add_on].rule` (the "measured as follows" sentence) against `factors[lost_principal_measure].ladder[1]` and `compute[lost_principal]`.

*Bears on.* Task 1. Task 1's world takes tier 1 (two withdrawals in the twelve months), so its scored number is not moved by this defect; the defect is that the policy cannot be read consistently.

---

**CG-2 — Observation. "Holds an active savings or money market account" is implemented as "savings balance greater than zero" in three places, and "holds an active checking account whose balance is below …" as "balance above zero and below …" in a fourth.**

*Evidence.* `cd_ext_overdue_term_renewal_rate.compute[jumbo_figure]` tier 1: `… and savings_balance > 0`, against the rule's "whose owner holds an active savings or money market account". `cd_ext_omitted_withdrawal_entry.compute[added_days]`: `deposit_balance_for_allowance > 0` / `== 0`, against "the owner holds an active savings or money market account" / "holds no such account". `cd_ext_partial_early_withdrawal_penalty.compute[rounded_penalty]` tier 2: `checking_balance > 0 and checking_balance < P('partial_withdrawal_min_amount')`, against "the owner holds an active checking account whose balance is below the smallest partial withdrawal the tier accepts".

*Why an observation and not a red light.* An owner with an active account of exactly 0.00 is placed on the fall-through tier by the compute and on a graded tier by the rule. Neither task world contains a zero-balance active account (task 0 savings 118,600.00; task 1 savings 41,300.00, checking 12,480.22), so no consequence can be demonstrated on a scored value here.

*Bears on.* Both tasks, as a reading risk only.

---

**CG-3 — SOURCE-POLICY RED. `penalty_basis_measure` says "in the month now running" and computes a rolling one-month window, and the charter's own convention makes the two readings different.**

*Symptom.* The tier-selecting condition "interest has been credited to the certificate in the month now running" is implemented as `SUM('cd_transactions','amount', within_months=1, …) > 0`, which by the engine's `MONTHS()` convention reaches back roughly one month from the frozen date and therefore into the previous calendar month.

*Root cause.* The rule names a period ("the month now running") where every other window in the same charter is written as a rolling span and implemented as one. In this same policy the author writes "in the twelve months before this one" for `within_months=12` and "in the three months before the withdrawal" for `within_months=3`. "The month now running" is deliberately not of that form, and base `cd_evt_interest` fixes the calendar month as the crediting period ("on the last calendar day of each month"), so a reader has every reason to read it as the current calendar month.

*Evidence.*
- rule: "*where interest has been credited to the certificate in the month now running and the rate of the term now running stands above the tier's published standard interest rate, the basis is the sum the withdrawal removes less that credited interest*"
- compute: `interest_credited_this_month: SUM('cd_transactions','amount', within_months=1, date_field='posted_date', event_type='cd_interest_compound')`
- base `cd_evt_interest`: "*Accrued interest is credited according to interest_crediting_frequency: under monthly, on the last calendar day of each month …*"
- engine semantics, `skills/erl-task-instantiate/scripts/check_compute.py` `_within`/`MONTHS`: a row dated 2026-05-28 has `MONTHS('2026-05-28','2026-06-12') = 0` and is therefore inside `within_months=1`.

*Demonstrated consequence.* Demonstrated against task 0's world in `0.md` §`policy_self_consistency`: the compute's reading puts the customer on tier 1 and the calendar-month reading puts the same customer on tier 2, giving a penalty basis of 102,751.01 against 110,554.59 and a scored penalty of 687.42 against 739.62.

*Affected artifact and location.* `cd.extended.yaml`, `extended_policies[cd_ext_partial_early_withdrawal_penalty].rule` (the graded-basis sentence) and `compute[interest_credited_this_month]`; `compute_basis[interest_credited_this_month]` quotes the rule sentence verbatim and therefore certifies an equivalence that does not hold.

*Bears on.* Task 0.

---

**CG-4 — SOURCE-POLICY RED. Tiers 2 and 3 of `entry_principal_measure` overlap as the rule states them, and the compute silently narrows tier 2 to break the tie.**

*Symptom.* An owner who holds no active card and for whom interest was credited in fewer than each of the three months satisfies the stated condition of both tier 2 and tier 3.

*Evidence.*
- rule: "*where the owner holds such a card opened after the term began, **or interest was credited in fewer than each of those three months**, it is the principal taken out by early partial withdrawals in those three months less the interest credited in them; **where the owner holds no active card**, it is the principal taken out by early partial withdrawals in those three months.*"
- compute: `entry_principal: … ((withdrawn_principal_recent - interest_credited_recent) if (**card_held == 1** and (card_before_term == 0 or interest_months_recent < 3)) else withdrawn_principal_recent)` — the `card_held == 1` conjunct appears in no sentence of the rule.

*Demonstrated consequence.* For an owner with no active card and two of the three months credited, the rule's tier 2 gives "principal removed **less** the interest credited" and the rule's tier 3 gives "principal removed" — two different bases for the same records, with no sentence of the charter choosing between them. On task 1's figures those two bases would be 5,210.17 and 6,000.00, an entry of 130.15 against 149.88. The compute resolves the tie by a condition that is not in the rule, so a reader of the policy cannot reproduce it.

*Affected artifact and location.* `cd.extended.yaml`, `extended_policies[cd_ext_omitted_withdrawal_entry].rule` (the "measured as follows" sentence) and `compute[entry_principal]`; the ladder in `factors[entry_principal_measure]` repeats the rule's overlapping wording.

*Bears on.* Task 1. Task 1's owner does hold an active card, so its scored number is not moved; the ladder is nonetheless not pairwise disjoint as stated.

---

**CG-5 — Observation. The extended renewal rule re-anchors the published rate and the bonus evaluation on "the day the new term is recorded", while base `cd_rate_and_bonuses` anchors them on the maturity date and the renewal date, and that base sentence is not named in `overwrite`.**

*Evidence.* base `cd_rate_and_bonuses`: "*On renewal the rate follows renewal_rate_basis: the target tier's published standard rates **on the maturity date**, with both bonuses re-evaluated **on the renewal date** when relationship_bonus_on_renewal is true.*" Extended rule: "*… is carried into a new term whatever the day the bank comes to record it, and the new term's figures are those of the day it is recorded*" and "*the relationship figure and the jumbo figure the certificate earns **on the day the new term is recorded***". `overwrite` names three other base sentences and not this one.

*Why an observation and not a red light.* The charter publishes exactly one `standard_interest_rate` and one `standard_apy` per tier with no rate calendar, so the two anchors select the same published figures and no quantity can be shown to differ on that limb. The bonus-evaluation limb does move the window ends; on task 0's world the shift from 2026-05-28 to 2026-06-12 changes the checking-deposit count from 4 to 5 and the twelve-month card spend from 6,912.70 to 7,341.60, neither of which crosses a tier boundary, so no scored value differs.

*Bears on.* Task 0.

---

**CG-6 — Observation. "Interest was credited in each of the three months" is implemented as a row count over a rolling three-month window, not as a count of distinct months.**

*Evidence.* rule, `cd_ext_omitted_withdrawal_entry`: "*interest was credited to the certificate in each of the three months before the entry is booked*"; compute: `interest_months_recent: COUNT('cd_transactions', within_months=3, date_field='posted_date', event_type='cd_interest_compound')` and the tier tests `interest_months_recent >= 3`. Two credits falling in one month would satisfy the compute and not the rule; conversely a certificate crediting at maturity rather than monthly could have three rows spanning more than three months.

*Why an observation.* On task 1's ledger the four qualifying rows fall in four distinct months (2026-04, 2026-05, 2026-06, 2026-07), so both readings select the same tier.

*Bears on.* Task 1.

---

**CG-7 — Observation. The largest partial withdrawal the extended rule permits leaves the certificate below the minimum balance the inherited base sentence requires, once the penalty is also taken from principal.**

*Evidence.* extended rule: "*The largest sum a single partial withdrawal may remove is the principal standing on the certificate less the balance the tier requires to remain after a partial withdrawal.*" and "*the penalty is deducted from the principal that remains*". base `cd_evt_early_withdrawal`, inherited and not named in `overwrite`: "*Partial withdrawals are allowed only … leaving at least minimum_balance_after_partial … a request breaking any of these is declined, never converted.*"

*Why an observation.* Read as a test on the withdrawal itself, the two sentences agree: the withdrawal leaves exactly `minimum_balance_after_partial`, and the penalty is a separate later deduction. The alternative reading (the test is on the principal that finally stands) would make the largest permitted sum self-referential. The extended sentence is explicit enough to pin the first reading, so no second defensible *amount* follows; the terminal principal nonetheless ends below the tier minimum.

*Bears on.* Task 0.

---

**CG-8 — Observation. One tool docstring positions a read against the consultation.**

*Evidence.* `confirm_term_add_on_1e70ab4d`, `Args.customer_id`: "*taken from the customer profile lookup made at the start of the call*". No task tool is named and no write is ordered against another write; the phrase points at a shared read tool and at the consultation, not at a step of the problem tree. The other three docstrings' uses of "before"/"afterwards" all describe the preparation of an argument or the tool's own after-state.

---

**CG-9 — Observation. Two writes of this difficulty create `cd_penalty` rows, and edge 2's state-form sentence resolves only once the reader notices that one of them cannot attach an entry to an existing withdrawal.**

*Evidence.* `confirm_partial_withdrawal_44cc2957` creates a `cd_withdrawal` row and, in the same call, a `cd_penalty` row whose `source_item_id` is the withdrawal it just minted; `credit_mischarged_penalty_7001af6d` takes `source_item_id` as an argument and attaches the entry to a withdrawal already on the ledger. The waited-on state — "*every early partial withdrawal standing on its ledger carries the entry owed*" — can be made to hold for a withdrawal already standing only by the second tool, so the hop is single-valued; but the reader must reason from the argument list rather than from the sentence alone.

---

**CG-10 — Observation. Task 1's seeded `auto_loans` row contradicts the auto product's own charter in fields the factors do not read.**

*Evidence.* `initial_state.auto_loans` (task 1): `original_principal` 21,400.00, `funded_date` 2026-03-20, `interest_rate` 8.74, `monthly_payment` 442.18, `principal_balance` 18,962.31, with three `auto_payment` rows of 442.18 on 2026-04-20, 2026-05-20 and 2026-06-20. Under `blueprint/products/auto.yaml` `auto_evt_payment_allocation` ("Each payment is applied in payment_allocation_order: first to fees_due, then to interest accrued through the credit date, then to principal"), three payments totalling 1,326.54 with roughly 155.87 of monthly interest each cannot reduce principal by 2,437.69; the largest possible reduction is 1,326.54, to 20,073.46. The seeded rate also does not reconstruct from the Used Vehicle Loan's `base_apr_by_term[60] = 7.99`, credit grade B adder 1.50 and `autopay_discount_pct` 0.25 (which give 9.24, not 8.74).

*Why an observation and not a red light.* The only auto fields any factor reads are `auto_loans.status` (`'active'`) and the count of `auto_transactions` rows with `event_type = 'auto_payment'` (3). Both are present, internally consistent and consistent with the auto charter's lifecycle ("active" ⇄ "delinquent" transitions make `status == 'active'` a faithful rendering of "an auto loan at the bank that is not past due"). No scored value depends on the contradicting fields.

---

**CG-11 — Observation. Task 1's seeded `card_accounts.last_statement_date` (2026-07-12) is later than `frozen_time` (2026-07-08).**

*Evidence.* `initial_state.card_accounts` (task 1): `last_statement_date: "2026-07-12"`, `statement_closing_day: 12`, `payment_due_date: "2026-08-06"`; `frozen_time: "2026-07-08 09:12:00 EDT"`. A *last* statement dated four days in the future is not a state the world can be in. No factor of either policy reads `last_statement_date`.

---

**CG-12 — Observation. Two aggregate bindings carry no window where their rule sentence names one.**

*Evidence.* `cd_ext_overdue_term_renewal_rate.compute[grace_window_deposits]` and `[grace_window_withdrawals]` are `SUM(…)` with no `within_months`, against a rule that says "*where a deposit was posted to the certificate **in the days after its maturity***"; they are scoped only by `deposit_kind='grace_add_on'` / `withdrawal_kind='grace_period'`, so grace rows of an *earlier* grace period would be counted too. `cd_ext_term_restoring_add_on.compute[add_ons_this_term]` uses `within_months=12` against a rule that says "*what has already been added **in this term***"; on an 18-Month, 36-Month or 60-Month term older than twelve months the two differ.

*Why observations.* Task 0 holds exactly one `grace_add_on` row and no `grace_period` withdrawal; task 1 holds no `term_add_on` row at all and is eight months into its term. Neither divergence moves a scored value.

---

### closing_checklist

Written after both tasks' `source_gt_comparison` sections were appended. **This difficulty does not close.** The checklist is recorded item by item with its actual status rather than as a pass.

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` sits alongside them | ✔ `0.md`, `1.md`, `_difficulty.md` in `env/regional_retail_bank/audits/policy_task/cd_maturity_withdrawals_and_renewals/` |
| old revisions traceable | ✔ first audit of this difficulty; no prior revision to preserve |
| every comparison section carries a PASS | ✘ task 0: SOURCE-POLICY / SOURCE-CHAIN / SOURCE-FACTOR / SOURCE-TASK RED. task 1: SOURCE-POLICY / SOURCE-FACTOR / SOURCE-TASK RED, problem tree PASS |
| this difficulty's extended policies fully covered | ✔ all four, {cd_ext_overdue_term_renewal_rate, cd_ext_partial_early_withdrawal_penalty} ∪ {cd_ext_omitted_withdrawal_entry, cd_ext_term_restoring_add_on} |
| the M tasks' scopes pairwise disjoint over the whole problem tree | ✔ disjoint in policies and in task tools |
| task tools and GT closed | ✔ each task's two task tools are exactly the two `target_tool`s of the policies it claims; every gold argument traces to a policy sentence or a persona line |
| each task tool uses an independently generated, frozen uuid8 | ✔ `3666596b`, `44cc2957`, `7001af6d`, `1e70ab4d` — distinct, no shared prefix, not sequential, not batch-derived |
| every task's tree: one to three prerequisite problems | ✔ one each |
| at least max(n−1, 1) `value_input` edges | ✔ one each, against a floor of one |
| at least one problem resolved by an `owner=user` tool | ✔ task 0 `confirm_partial_withdrawal_44cc2957`, task 1 `confirm_term_add_on_1e70ab4d` |
| no cycle; the difficulty's edges together still a DAG | ✔ two edges, four nodes, two disjoint components |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ 4.22 vs 4.14; 1,052.00 vs 687.42; 117.76 vs 130.15; 14,500.00 vs 15,375.00 |
| four to six factors per computation, 2 `parameter`, 2 `method`, 2 multi-source, 2 cross-difficulty | ✔ 4/5/4/5 factors; counts in `factor_ladders` above |
| every ladder at least three tiers stated in full in its rule | ✘ three tiers everywhere, but see **CG-1**, **CG-1a**, **CG-3** and **CG-4**: four ladders are not stated in the rule as they are implemented, and one is not pairwise disjoint as stated |
| every factor proved to bear weight on its task's world against an honest baseline | ✔ all eighteen factor substitutions moved the scored value; every `baseline` matches what `baseline.rule` states for its input |
| a genuine near-miss per computation | ✔ renewal (two checking deposits outside the window, decisive), penalty (the 2026-04-30 credit outside the one-month window, decisive), entry (the 2026-02-19 withdrawal and the 2026-03-31 credit outside the three-month window, decisive); ✘ restoring add-on — see `1.md` **F-12** |
| instantiation-stage gates re-run once on the final form | not run: the brief instructs this auditor to cite the supplied gate snapshot and not to run the gates. **This item is outstanding and is owed on whatever final form follows from these findings.** |

#### summary of red lights, by where they must be settled

| id | where | bears on |
| --- | --- | --- |
| CG-1 | charter (three compute expressions vs their rule sentences) | neither task's scored values; the rendered KB |
| CG-1a | charter (`cd_ext_term_restoring_add_on` tier 2, three faces disagree) | task 1 (`1.md` F-9); no scored value moves |
| CG-3 | charter (`cd_ext_partial_early_withdrawal_penalty`, "the month now running") | task 0 (`0.md` F-1): penalty 687.42 vs 739.62 |
| CG-4 | charter (`cd_ext_omitted_withdrawal_entry`, tiers 2 and 3 overlap) | task 1 (`1.md` F-9); no scored value moves |
| F-2 | `tasks/0.json` `prerequisite_closure.order_uniqueness` | task 0: terminal principal 313.89 vs 220.89 |
| F-3 | `tasks/0.json` `design_rationale` | task 0: an interest credit of 304.23 that is not in the world; an interest total of 4,038.17 that does not close the ledger |
| F-10 | `tasks/1.json` `design_rationale` | task 1: three interest credits named where four are used |
| F-11 | `tasks/1.json` `initial_state.cd_transactions.606b2279-…` | task 1: a crediting date the charter forbids, load-bearing on 130.15/15,375.00 |

Observations that demonstrate no consequence — CG-2, CG-5, CG-6, CG-7, CG-8, CG-9, CG-10, CG-11, CG-12, and the per-task F-4, F-5, F-6, F-8, F-12, F-13, F-14 — are recorded in their files and are not grounds for rework.

---

## revision_9

Re-audit round 9, by the auditor of revision_8, in the same session. **Revisions 1-8 above are untouched**, including revision_8's blind text, which is not edited to accommodate anything found here. Pre-append sha256 of this file: `58718c94f16fed44804b16c9d7b8938cddf2743c3617636ab52e0c7350e6bd8c` (1712 lines).

**This round is not blind.** Revision_8 revealed both GTs, so this round verifies the rework item by item rather than re-deriving from a masked view. Every figure below is this auditor's own recomputation of the charter's `compute` on the current worlds through the engine's own primitives, compared afterwards with the artifacts' proof fields.

### inputs_and_movement

| artifact | revision_8 sha256 | revision_9 sha256 | moved? |
| --- | --- | --- | --- |
| `cd.extended.yaml` | `0dfc2c4b2268b0b7f7fea4bbf14884e02f359195ef1a8efd8060bd58705638a3` | `1a01b8ab9834474275425b160f75ee50727930d248afcff719cdcc095bf37fc4` | **yes** |
| `task_tools.py` | `7fd301983c9fd6de17f3ece522baed38ff73ec078d2c349b9afaac2fc45a7398` | `7fd301983c9fd6de17f3ece522baed38ff73ec078d2c349b9afaac2fc45a7398` | no |
| `blueprint/products/cd.yaml` | `7a14550e7c6bc9cfc2f59401c8032dd5371b4809ce2874ec58315695dc044aa8` | `7a14550e7c6bc9cfc2f59401c8032dd5371b4809ce2874ec58315695dc044aa8` | no |
| masked view `0.json` | `5d0d55b782…b971b2d5` | `5d0d55b782…b971b2d5` | no |
| masked view `1.json` | `7ec8744fde…f4d5bb52` | `a85e728c38ce668efe9ef1c5acd613e5f335344461b60b0a6ac539f7964e2006` | **yes** |
| `tasks/0.json` | — | `dc1dbe69f98517dfdb16eaa195a47e92e231b821fb628657085e0e069be59661` | proof fields only |
| `tasks/1.json` | — | `0dc71414e27989177eef16861c9c30760ea95ad2936e740c30d829c5083784bb` | world + gold + proof |

The base section of `cd.extended.yaml` was re-compared key by key against `blueprint/products/cd.yaml` and is still **verbatim identical** on all ten keys. Policy ids, `target_tool`s, `computes` bindings and all four uuid8s (`3666596b`, `44cc2957`, `7001af6d`, `1e70ab4d`) are unchanged, and `task_tools.py` is byte-identical, so `action_binding_and_uuids` carries forward by reference on unchanged inputs: the four tool bodies still validate nothing, refuse nothing and name no other tool.

Gate snapshot re-run by the coordinator after the rework is cited, not re-run here: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK. The two movements the coordinator flagged are interpreted under `history_depth` below.

### item verdicts

| item | round-8 verdict | claim | revision_9 verdict |
| --- | --- | --- | --- |
| CG-3 / F-1 | SOURCE-POLICY + SOURCE-TASK RED | closed | **CLOSED** |
| F-11 | SOURCE-TASK RED | closed | **CLOSED** |
| CG-1 | SOURCE-POLICY RED | closed | **CLOSED** |
| CG-1a | SOURCE-POLICY RED | closed | **CLOSED** |
| CG-4 | SOURCE-POLICY RED | closed | **CLOSED** |
| F-2 | SOURCE-CHAIN RED | closed | **CLOSED** |
| F-3 | SOURCE-FACTOR RED | closed | **CLOSED** |
| F-9 | SOURCE-POLICY RED (inherited CG-1a + CG-4) | closed | **CLOSED**, consequentially |
| F-10 | SOURCE-FACTOR RED | closed | **CLOSED** |
| F-13 (the false cross-task sentence it found itself) | observation | closed | **CLOSED** |
| CG-6 | observation | incidentally closed on task 1's world | **accurate**; the charter-level wording is unchanged, so the observation stands at charter scope |
| CG-2, CG-5, CG-7 to CG-12, F-4 to F-8, F-12, F-14 | observations | not acted on | **confirmed not acted on**; none has regressed into a consequence |
| — | — | — | **CG-13, new to this report**: five ladder fall-throughs stated as positive conditions rather than "otherwise". Pre-existing in the revision_8 charter and **missed by this auditor in round 8**; not introduced by the rework |

**No regression was found.** Task 0's world is byte-identical and its four scored parameters are unchanged; both problem trees, both prerequisite sentences, both `owner=user` writes, both baselines and all eighteen factor substitutions were re-run and still hold.

---

#### CG-3 / F-1 — CLOSED

*What changed.* The rule's tier condition "interest has been credited to the certificate **in the month now running**" is now "interest has been credited to the certificate **in the one month counted back from the day the principal leaves**", with the matching consequent "the basis is the sum the withdrawal removes **less the interest credited in that one month**" and the second tier's "no interest has been credited **in that one month**". The binding was renamed `interest_credited_this_month` -> `interest_credited_one_month`. The `factors[penalty_basis_measure].ladder`, the `compute_basis[charged_basis]` quotation and the `overwrite[1].replaced_by` text all carry the new wording; each was checked to be a verbatim substring of the `rule`.

*Test 1 — is the rolling reading the one the world is scored on?* Yes. Recomputed on task 0's post-renewal world: the 2026-05-28 credit of 303.58 is inside `within_months=1` (`MONTHS('2026-05-28','2026-06-12') = 0`), tier 1 holds, `charged_basis` = 103,054.59 − 303.58 = 102,751.01, and the scored penalty is **687.42** — which is `computations[1].expected`. The rework did not move task 0's gold to suit the new wording; it worded the rule to the figure already scored.

*Test 2 — is the competing reading now unavailable from the rule's words?* Yes. "The one month counted back from the day the principal leaves" names a span of one month anchored on the withdrawal day and counted backwards. It cannot be read as "the calendar month of June", which was the reading that produced 739.62. Round 8's second answer is gone: there is no sentence of the policy from which a reader can reach 110,554.59.

*Test 3 — does the new wording conflict with base `cd_evt_interest`, and if so is it declared?* **No conflict.** The base sentence — "*Accrued interest is credited according to interest_crediting_frequency: under monthly, on the last calendar day of each month and on the maturity date for the final partial month*" — fixes **when a crediting row may be posted**. The extended sentence fixes **which posted rows are summed** when grading a penalty basis. They govern different quantities and can both hold at once: task 0's ledger posts on month-ends and on the maturity date, exactly as base requires, and the extended window then selects one of those rows. No base sentence anywhere states that a penalty basis is measured over a calendar month, so nothing of base is superseded and no `overwrite` entry is owed for it. The `overwrite` entry that *is* owed — replacing base's "The penalty basis is the principal the request removes…" — is present and its `replaced_by` is the new graded sentence verbatim.

*Residual, recorded as observation **O-9.1** below:* a one-day boundary difference between "one month counted back" and the engine's `MONTHS()` convention.

---

#### F-11 — CLOSED

*What changed.* The world, not the wording. `tasks/1.json` `initial_state.cd_transactions` no longer contains the `cd_interest_compound` row posted 2026-07-08 for period 2026-07. The ledger now holds twelve rows.

*Legality of the rebuilt ledger, checked field by field, not only on the date I named.*

- **Crediting dates.** Eight `cd_interest_compound` rows: 2025-11-30, 2025-12-31, 2026-01-31, 2026-02-28, 2026-03-31, 2026-04-30, 2026-05-31, 2026-06-30. Every one is the last calendar day of its month, which is what base `cd_evt_interest` requires under `interest_crediting_frequency: monthly` and what the `cd_interest_compound` event definition permits ("*Crediting date: the last calendar day of the month, the maturity date, or the closure date*"). The first, 2025-11-30, is the month-end of the term's opening partial month (term start 2025-11-14) — correct, not an extra. No row is dated the maturity date (2027-05-14, in the future) or a closure date (the certificate is open). **No illegal crediting date remains.**
- **`interest_period` values** run 2025-11 through 2026-06 with no gap and no duplicate, matching the grain "one row per certificate per interest period".
- **`rate_applied`** is 3.98 on every credit, which is the rate the certificate has carried since term start.
- **Arithmetic closure.** 84,000.00 opening + 1,968.19 interest (155.71 + 284.47 + 285.43 + 249.23 + 257.94 + 250.47 + 232.48, and 155.71+…+232.48 recomputed = 1,968.19) − 8,500.00 − 6,000.00 withdrawn − 166.83 penalty = **71,301.36**, which is exactly `cd_certificates.principal_balance`. The seed closes to the cent. Interest accrued since 2026-06-30 is simply not yet credited, which is the correct state under base.
- **Withdrawals.** Two `early_partial` rows, 8,500.00 on 2026-02-19 and 6,000.00 on 2026-05-21, both ≥ `partial_withdrawal_min_amount` 500.00, both leaving more than `minimum_balance_after_partial` 2,500.00, two in the term against `max_partial_withdrawals_per_term` 2 — at the cap, not over it. Both carry `destination: official_check` with an empty `counterparty_account_id`, which is what the rule requires of a withdrawal paid by official check.
- **The one existing penalty.** 166.83 on 2026-02-19, `penalty_days` 180 (the tier's published days), `rate_applied` 3.98, `source_item_id` naming the 2026-02-19 withdrawal, posted the same business day as that withdrawal. 8,500.00 × 3.98 / 100 × 180 / 365 = 166.834 -> 166.83 — the base formula exactly, which is right for a penalty booked before the owner held a savings account, an auto loan or a card.
- **The defect the task turns on is intact.** The 2026-05-21 withdrawal (`e6862990-9880-4478-aa33-c50e6a0e2273`) is named by no `cd_penalty` row's `source_item_id`; the only penalty names `606b2279-…`, the 2026-02-19 withdrawal. The ledger ids were reissued in the rebuild and the closure's `evidence` list was updated to the new ids, which this auditor checked row by row.
- **Certificate self-consistency.** 18-Month Bump-Up standard 3.83 + 0.15 relationship = `interest_rate` 3.98; standard APY 3.90 + 0.15 = `apy` 4.05; `jumbo_bonus_applied` false against an opening deposit of 84,000.00 below the 100,000.00 threshold. All three reconstruct.
- **Everything outside the certificate is unchanged**: the checking, savings, card and auto holdings and all of their ledger rows are identical to revision_8, so every cross-difficulty factor reads the same evidence it read before.

*Both scored values moved, to exactly the charter-legal figures revision_8 predicted.* `entry_amount` 130.15 -> **131.51** and `deposit_amount` 15,375.00 -> **15,376.00**; revision_8 §F-11 wrote "*a reader who applies `cd_evt_interest` … reaches `entry_principal` 5,264.59, an entry of **131.51**, and a restoring deposit of **15,376.00***". The two readings that round 8 showed were both live have collapsed into one, because the record a reader would have had to overrule is gone. **This is the legitimate direction of fix: the world was made legal, not the rule bent around it.**

---

#### CG-1 — CLOSED

*What changed.* All three sites that hard-coded `{Interest Checking, Premier Checking, Private Client Checking}` now read the per-variant parameter:

- `cd_ext_partial_early_withdrawal_penalty.compute[applied_rate]`: `… if (checking_tier in P('relationship_qualifying_checking_tiers') and checking_opened_before_term == 1) else (P('standard_interest_rate') if ((checking_tier or '') != '' and checking_tier not in P('relationship_qualifying_checking_tiers') and checking_opened_before_term == 1) else F('interest_rate'))`
- `cd_ext_term_restoring_add_on.compute[qualifying_checking]`: `1 if (checking_tier_held in P('relationship_qualifying_checking_tiers')) else 0`
- `cd_ext_overdue_term_renewal_rate.compute[relationship_figure]` second tier, and `factors[relationship_figure_grade].baseline`, both now `… in P('relationship_qualifying_checking_tiers')`

A sweep over `extended_policies` confirms **no `Interest Checking` literal remains anywhere**. The only surviving literal checking-tier names are `Premier Checking` / `Private Client Checking` in the renewal's first tier, which the rule itself names literally ("*an owner who holds an active Premier Checking or Private Client Checking account*") — correct to hard-code, because that tier is a closed set the rule states, not the per-variant list.

*Six-tier agreement, verified exhaustively.* For every one of the six certificate variants × seven checking states (the six checking tiers plus "no active checking account"), this auditor compared the tier the **rule** prescribes with the tier the **compute** selects, for `applied_rate` and for `qualifying_checking`: **0 mismatches in 42 cells each.** The case that convicted the old code now agrees: on an 11-Month No-Penalty Certificate, whose `relationship_qualifying_checking_tiers` is `[Premier Checking, Private Client Checking]`, an Interest Checking holder now falls to the non-qualifying tier under both faces.

*Did the guard narrow the open set?* **No.** The rule's second tier is "*an owner **holding an active checking account** of a tier that does not qualify, opened before the term now running began*". The guard `(checking_tier or '') != ''` is precisely that rule's own "holding an active checking account" requirement — `CFIELD` returns `None` when the customer has no active checking account, and the rule sends such an owner to "every other owner" anyway. The set stays open through `not in P(…)`: it admits any checking tier absent from the certificate tier's list, including one added to the charter later, which a fixed enumeration could not.

*Parameter safety.* All six certificate variants define `relationship_qualifying_checking_tiers` as a list, so no `in` test can be evaluated against `None`.

---

#### CG-1a — CLOSED

The middle tier of `lost_principal_measure` now reads the same in all three faces. `rule`: "*where the owner has an auto loan at the bank that is not past due and principal was taken out only once in those months, it is the principal that withdrawal removed **together with every entry booked for it in those months***". `factors[lost_principal_measure].ladder[1].method`: the same clause. `compute[lost_principal]`: `(withdrawn_principal_year + entries_booked_year) if (auto_loan_standing == 'active' and withdrawals_in_year == 1)`. The rule's old "*less any credit back posted in them*" is gone from that tier. A verbatim check confirms every tier of this ladder is now a string of the `rule`. The round-8 split of 6,000.00 against 6,130.15 no longer exists: all three faces give "principal removed plus entries booked".

#### CG-4 — CLOSED

The second tier of `entry_principal_measure` now states the card-held conjunct the compute always had. `rule`: "*where the owner holds an active Piedmont Crescent card **and either** that card was opened after the term began **or** interest was credited in fewer than each of those three months, …*". Tiers 2 and 3 ("*where the owner holds no active card*") are now **pairwise disjoint**, and tiers 1–3 are jointly exhaustive: within card-held, tier 2's condition is the exact complement of tier 1's, and tier 3 takes the rest. The compute's `card_held == 1` conjunct is now a sentence of the rule, so a reader can reproduce the tie-break. The round-8 ambiguity between a base of 5,210.17 and one of 6,000.00 for a card-less owner is resolved.

#### F-9 — CLOSED consequentially

Task 1's inherited policy-self-consistency RED was CG-1a plus CG-4, both closed above, plus CG-1, closed above. Nothing of F-9 survives in its own right.

---

### findings (revision_9)

**CG-13 — SOURCE-POLICY RED, new to this report, pre-existing in the artifacts. Five ladder fall-throughs are stated as positive conditions rather than as "otherwise", so the rule is silent on cells the compute nonetheless decides — and in three of them the compute hands the owner the value the rule reserves for someone else.**

*Symptom.* Several ladders state their third tier as a specific negative situation ("where the owner holds no active card", "an owner who holds no active checking account of a qualifying tier", "where the owner holds no active savings or money market account") while the `factors[].ladder` writes "otherwise" and the `compute`'s final `else` catches everything the first two tiers missed. Between the first two tiers and that named third situation there are cells the rule does not reach.

*Root cause.* A tier present in one face of the policy and absent from the other, in the sense of check 2.

*Evidence, instance by instance, with the uncovered cell.*

| policy | factor | rule's third tier | cell the rule never reaches | value the compute assigns there |
| --- | --- | --- | --- | --- |
| cd_ext_overdue_term_renewal_rate | `relationship_figure_grade` | "an owner who holds no active checking account of a qualifying tier earns nothing" | an active **Interest Checking** account with **at least six** deposits in the window, on any of the five certificate tiers that list Interest Checking as qualifying (verified: exactly 5 such cells across the 6 × 7 × 2 grid) | 0 |
| cd_ext_omitted_withdrawal_entry | `entry_days_measure` | "where the owner holds no active savings or money market account, the days are the days the tier publishes" | an **active** savings or money market account whose balance is **below** the tier's `minimum_opening_deposit` | `P('early_withdrawal_penalty_days')` — the no-account value |
| cd_ext_term_restoring_add_on | `restored_interest_span` | "where the owner holds no active checking account of a qualifying tier, no interest is added" | a **qualifying** checking account with **no** early partial withdrawal in the twelve months | 0 |
| cd_ext_term_restoring_add_on | `restoration_rate_grade` | "an owner holding **no active card** earns it at the tier's published standard interest rate less the tier's relationship bonus points" | an **active card of a tier other than** Cash Rewards Visa or Travel Rewards Visa Signature with **at least** eight hundred dollars of purchases in the quarter | `P('standard_interest_rate') - P('relationship_apy_bonus')` — the **no-card** value |
| cd_ext_term_restoring_add_on | `restoration_allowance_grade` | "where the owner holds no active savings or money market account, nothing is added" | balance at or above the tier's largest total add-on but `renewal_count` above zero; and an active account below the tier's `minimum_opening_deposit` | 0 — the no-account value |

*Demonstrated consequence*, on the sharpest instance, `restoration_rate_grade`. Take an owner of an 18-Month Bump-Up Certificate holding an **active Secured Visa** with 900.00 of purchases posted in the three months before the deposit. The rule's first tier excludes them (wrong card tier); the second excludes them (their spend is not "less than eight hundred dollars"); the third names "*an owner holding no active card*", which they are not. The rule therefore yields **no rate at all**, while `compute[restoration_rate]` falls through to `P('standard_interest_rate') - P('relationship_apy_bonus')` = 3.83 − 0.15 = **3.68**, the figure the rule's own words reserve for an owner with no card. Two passages of one policy, one situation, different conclusions. The same shape holds for `entry_days_measure` and `restoration_allowance_grade`.

*Bears on.* **Neither task's scored values.** Task 0's owner holds Interest Checking with five deposits (covered by the renewal ladder's second tier); task 1's owner holds a Cash Rewards Visa with 1,142.39 of quarterly purchases (first tier), an active savings balance of 41,300.00 against a `minimum_opening_deposit` of 2,500.00 and a `term_add_on_max_amount` of 25,000.00 with `renewal_count` 0 (first tiers), a qualifying Premier Checking account with two withdrawals in the year (first tier). Every uncovered cell is unoccupied in both worlds. The defect is a defect of the charter, which the rendered KB will carry.

*Honesty note.* **This is not a regression and was not introduced by the rework.** The revision_8 charter carried the same five sentences with the same holes, and this auditor's round-8 `factor_ladders` check tested the tiers for pairwise disjointness but not for exhaustiveness, so the finding was missed. It is recorded here at charter scope, under the round in which it was found. The rework shows the fix pattern exists: `entry_principal_measure` was a sixth member of this family and CG-4's repair removed its hole by naming the complement explicitly.

*Affected artifact and location.* `cd.extended.yaml`, `extended_policies[cd_ext_overdue_term_renewal_rate].rule` (the graded relationship sentence) against `factors[relationship_figure_grade].ladder[2]` and `compute[relationship_figure]`; `extended_policies[cd_ext_omitted_withdrawal_entry].rule` (the graded days sentence) against `factors[entry_days_measure].ladder[2]` and `compute[entry_days]`; `extended_policies[cd_ext_term_restoring_add_on].rule` (the graded interest-span, rate and allowance sentences) against the matching ladders and `compute[interest_days]`, `compute[restoration_rate]`, `compute[restoration_allowance]`.

*Relation to previous revisions.* Not reported in revisions 1-8; present in the revision_8 artifacts and unchanged by the revision_9 rework.

---

**O-9.1 — Observation, new. "One month counted back" and the engine's month arithmetic disagree on one boundary day.**

`_within` admits a row when `0 <= MONTHS(posted_date, NOW) < 1`, and `MONTHS` subtracts one when the later day-of-month is smaller than the earlier. On task 0's frozen date 2026-06-12 that makes the window **(2026-05-12, 2026-06-12]**: a credit posted 2026-05-13 is inside and one posted 2026-05-12 — exactly one month back — is outside, where the phrase "the one month counted back from the day the principal leaves" would naturally include it. No record in either world is dated on that boundary (task 0's nearest credits are 2026-04-30 and 2026-05-28), so no scored value can be shown to differ. Recorded because the new wording is otherwise exact, and this is the one day on which it is not.

**O-9.2 — Observation, new. Task 1's tier-1 conditions now sit exactly on their thresholds.**

With the 2026-07-08 credit removed, `interest_months_recent` is **3** against a tier condition of `>= 3`. Both `entry_principal_measure` and `entry_days_measure` take their first tier on the strength of that exact equality, where round 8 had a margin of one row. This is not a defect — it is the correct count under the charter, and the rule's own words are "interest was credited in each of the three months", which three credits in three distinct calendar months (2026-04, 2026-05, 2026-06) satisfy precisely. It is recorded because two factors now share one boundary: removing any single in-window credit would flip both.

**O-9.3 — Observation. CG-6 is closed on task 1's world and open at charter scope.**

The compute still counts **rows** (`COUNT(… within_months=3)`) where the rule says "credited in **each of the three months**". On the rebuilt ledger the three qualifying rows fall in three distinct calendar months, so the row count and the distinct-month count agree at 3 and the two readings select the same tier. The charter wording is unchanged, so the divergence remains available on a world where two credits fall in one month; it has simply lost its foothold here. The reworker's claim of an incidental closure is accurate as stated.

---

### history_depth (the coordinator's two flagged movements)

*What the metric counts.* `history_rows_max` is the largest per-task total of **distinct rows of the certificate's own ledger** that the task's computations read, summed across its computations. Recomputed by this auditor on the handling-time worlds:

| task | computation | own-ledger rows read | which rows |
| --- | --- | --- | --- |
| 0 | renewal | 1 | the grace add-on of 2026-06-02 |
| 0 | penalty | 3 | the 2026-05-28 credit and the two 2025 partial withdrawals |
| **1** | entry | **5** | the withdrawals of 2026-02-19 and 2026-05-21 and the credits of 2026-04-30, 2026-05-31, 2026-06-30 |
| **1** | deposit | **4** | both withdrawals, the 2026-02-19 penalty and the entry booked on this call |

Task 1 totals **9**, which is the suite maximum and the source of both movements: it was 10 in round 8, and the single row it lost is the 2026-07-08 credit — precisely the illegal row F-11 required to be removed. The replay closure 37 -> 36 and the seed rows 14 -> 13 are the same one row seen from two other angles. **There is no second, unexplained deletion**: this auditor enumerated the twelve remaining `cd_transactions` rows and matched every one against revision_8's dump.

*Does the ledger still carry the history the task needs?* **Yes**, and the judgement does not rest on the metric's margin.

- The entry computation still reads a two-withdrawal, three-credit ledger spanning 2026-02-19 to 2026-06-30, and its tiers are still decided by aggregates over that span rather than by inspection.
- Its **near misses survive and are still decisive**, which is the substantive test. Recomputed: counting the 2026-03-31 credit, which sits just outside the three-month window (`MONTHS = 3`), moves the entry from **131.51 to 125.07**; counting the 2026-02-19 withdrawal, also just outside it (`MONTHS = 4`), moves it from **131.51 to 343.85**. A careless reader is still punished by the window, exactly as before.
- The deposit computation's twelve-month window is untouched and still spans both withdrawals and the pre-existing penalty.
- What was lost was not history the task needed but a row the charter forbade, and its removal made the ledger's arithmetic and its crediting dates simultaneously correct for the first time.

The floor of 8 is now cleared by one rather than by two. That is a fact about how much margin a future edit has, not a defect in what is on disk; it is recorded so that any further row removal from task 1's certificate ledger is understood to breach the floor.

---

### closing_checklist (revision_9)

| item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks; `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ revisions 1-8 preserved verbatim; this round appended as `revision_9` |
| every comparison section carries a PASS | ✘ **one outstanding**: policy self-consistency fails at charter scope on **CG-13** in both tasks' files. The problem tree, factor weight and unique-solution relationships now PASS for both tasks |
| extended policies fully covered; scopes pairwise disjoint | ✔ unchanged |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ `task_tools.py` byte-identical to revision_8 |
| one to three prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle | ✔ unchanged in both tasks; re-verified against the current `prerequisite` blocks and `evaluation_criteria` |
| every edge bears weight | ✔ task 0: 687.42 against 779.11 with the renewal skipped. task 1: 15,376.00 against 15,244.00 with the entry skipped, a movement of 132.00 |
| self-sufficient baseline giving a definite number different from gold | ✔ 4.22 vs 4.14; 1,052.00 vs 687.42; 117.76 vs 131.51; 14,500.00 vs 15,376.00 |
| 4-6 factors, 2 `parameter`, 2 `method`, 2 multi-source, 2 cross-difficulty per computation | ✔ 4 / 5 / 4 / 5, counts unchanged |
| every ladder at least three tiers stated in full in its rule | ✘ three tiers everywhere and every tier now substantively in the rule; **CG-13** is the residue — five fall-throughs are narrower in the rule than in the ladder |
| every factor bears weight against an honest baseline | ✔ all eighteen substitutions re-run; every one moves the scored value, and every `baseline` is what `baseline.rule` states for its input |
| a genuine near-miss per computation | ✔ for three of four; ✘ for the restoring add-on — **F-12** unchanged, still an observation |
| instantiation-stage gates re-run once on the final form | ✔ re-run by the coordinator after the rework and cited above; interpreted under `history_depth` |

**The difficulty does not close**, on one charter-scope item. Every defect that round 8 could demonstrate against a task world is closed: CG-3/F-1 and F-11, the two that put a second defensible answer on a scored parameter, are closed in the two legitimate directions — the rule reworded to the reading the world is scored on, and the world rebuilt to be legal — and CG-1, CG-1a, CG-4, F-2, F-3, F-9, F-10 and F-13 are closed in substance. What remains is **CG-13**, which no task instantiates, which was in the artifacts before this rework, and which this auditor did not raise in round 8.

---

## revision_10

Re-audit round 10, by the auditor of revisions 8 and 9, in the same session. **Revisions 1-9 above are untouched**, including the round-8 blind text and the round-9 comparison. Pre-append sha256 of this file: `ebfbdaa4681649904c00a5dbc63070d97a91fd43ecbc36a250e9ce11cff62e2f` (1912 lines). Narrow round: **CG-13 was the only open RED**, and this round verifies it, tests for regression, and tests for anything new the repair introduced.

### inputs_and_movement

| artifact | revision_9 sha256 | revision_10 sha256 | moved? |
| --- | --- | --- | --- |
| `cd.extended.yaml` | `1a01b8ab9834474275425b160f75ee50727930d248afcff719cdcc095bf37fc4` | `460015ed17069989da7ade604b7a87c29ddebf90c791c149d5d506bf985a5683` | **yes** |
| `task_tools.py` | `7fd301983c9fd6de17f3ece522baed38ff73ec078d2c349b9afaac2fc45a7398` | unchanged | no |
| `blueprint/products/cd.yaml` | `7a14550e7c6bc9cfc2f59401c8032dd5371b4809ce2874ec58315695dc044aa8` | unchanged | no |
| masked view `0.json` | `5d0d55b782…b971b2d5` | unchanged | no |
| masked view `1.json` | `a85e728c38…7964e2006` | unchanged | no |
| `tasks/0.json` | `dc1dbe69f9…9be59661` | `5493269e4560953ab7a1a10a11ab6278dff4a028b1ce949d8ef383adcae4fff2` | rationale only |
| `tasks/1.json` | `0dc71414e2…5083784bb` | `a2ea96de5ec8c844b88ec40f3f5bb7587b9669cef42748ecabd39dc0cca4ca96` | rationale only |

### the prose-only claim, tested rather than accepted

- **Both masked views are byte-identical** to round 9, so no seeded row moved in either world. The round-9 reading of both worlds stands.
- **Every `compute` expression in all four policies is character-for-character what revision_9 recorded**, across all 68 bindings, and every `params` block is unchanged.
- **Every one of the 18 `factors[].ladder` entries is character-for-character unchanged**, `when` and `value`/`method` alike, as is every `baseline` binding, every `effect` label, every `decides` and every `cross_difficulty`. All 18 tier-2 `when` values were and remain `otherwise`.
- **Every gold argument and every `computations` figure is unchanged** — re-derived independently below.
- The base section of `cd.extended.yaml` is still verbatim identical to `blueprint/products/cd.yaml` on all ten keys.
- What did change: **six fall-through clauses inside four `rule` strings**, and the `compute_basis` quotations and `overwrite.replaced_by` texts that carry those sentences. Every one of those links was re-checked: all `compute_basis` values are verbatim substrings of their `rule`, `compute_basis` keys match the binding list exactly, every `overwrite.replaced_by` is verbatim in the rule and every `superseded_clause` verbatim in its base rule, and both `prerequisite.policy_source` sentences are still verbatim in their own rule and still absent from the depended-on rule. Both `baseline.rule` blocks decompose into sentences that are all still verbatim in the rule, with `baseline.params` unchanged.

**The prose-only claim holds.**

### CG-13 — CLOSED

*What changed, clause by clause.* Six fall-throughs were rewritten from a named negative situation to an explicit residual plus a gloss naming the variables the residual ignores:

| policy | ladder | round-9 fall-through | round-10 fall-through |
| --- | --- | --- | --- |
| overdue_term_renewal_rate | `relationship_figure_grade` | "an owner who holds no active checking account of a qualifying tier earns nothing" | "**every other owner** earns nothing, whatever checking account they hold and however many deposits were posted to it" |
| omitted_withdrawal_entry | `entry_days_measure` | "where the owner holds no active savings or money market account, the days are the days the tier publishes" | "**in every other case**, whatever savings or money market account the owner holds and whatever it holds in it, the days are the days the tier publishes" |
| term_restoring_add_on | `lost_principal_measure` | "where the owner has no auto loan at the bank that is not past due, it is …" | "**in every other case**, whatever loans the owner has and however often principal was taken out, it is …" |
| term_restoring_add_on | `restored_interest_span` | "where the owner holds no active checking account of a qualifying tier, no interest is added" | "**in every other case**, whatever checking account the owner holds and however often principal was taken out, no interest is added" |
| term_restoring_add_on | `restoration_rate_grade` | "an owner holding no active card earns it at …" | "**every other owner**, whatever card they hold and whatever they have charged to it, earns it at …" |
| term_restoring_add_on | `restoration_allowance_grade` | "where the owner holds no active savings or money market account, nothing is added" | "**in every other case**, whatever savings or money market account the owner holds and however many terms the certificate has run through, nothing is added" |

*Is the sixth genuinely a member of the defect class?* **Yes.** `lost_principal_measure` was not in this auditor's round-9 list of five. Its tiers are "auto loan not past due **and** principal taken out more than once" and "auto loan not past due **and** principal taken out only once", so its old third tier, "where the owner has **no** auto loan at the bank that is not past due", left uncovered the cell **active auto loan with zero early partial withdrawals in the twelve months** — a cell the rule reached no verdict on while `compute[lost_principal]`'s final `else` decided it as `withdrawn_principal_year - credits_back_year`. That is exactly the shape of the other five. Revision_9 §CG-13 excluded it on the ground that the cell is business-vacuous (with no withdrawal there is no loss to restore); that was a judgement call about severity, not about membership, and the reworker is right to have repaired it. **This auditor's round-9 enumeration of five was one short.**

*Is any of the six a widening that swallows a tier above?* **No, and this was tested, not reasoned.** "Every other owner" and "in every other case" are residual by construction: they are defined by exclusion from the tiers above, so they cannot overlap them. The trailing gloss ("whatever card they hold and whatever they have charged to it") states which variables the residual is indifferent to; it does not add an independent condition that could reach back over tier 0 or tier 1. And the tier-0 and tier-1 clauses of all six ladders are **textually unchanged** from revision_9, so whatever disjointness they had they still have.

*The exhaustiveness sweep — this auditor's own, not the reworker's.* Round 8's ladder check tested pairwise disjointness and not exhaustiveness, which is how CG-13 survived seven revisions; no gate script tests it either. This round it was built from scratch. For each of the **18 ladders** across the four policies, the tier-0, tier-1 and tier-2 predicates were transcribed **from the rule's own clauses** — the residual tiers transcribed as residual, the positively-worded ones (`entry_principal_measure`, `added_days_grade`, `assembled_rate_rounding`) transcribed as written and **not** assumed to be complements — together with the branch the `compute` expression takes, and the whole variable space was enumerated. Domains include every checking tier and every card tier plus "no account", every certificate variant's own `relationship_qualifying_checking_tiers`, and boundary values on both sides of every threshold.

```
relationship_figure_grade      cells=168   overlap=0   gap=0   rule!=compute=0
jumbo_figure_grade             cells=24    overlap=0   gap=0   rule!=compute=2   (CG-2)
carried_principal_measure      cells=8     overlap=0   gap=0   rule!=compute=0
assembled_rate_rounding        cells=6     overlap=0   gap=0   rule!=compute=0
penalty_basis_measure          cells=8     overlap=0   gap=0   rule!=compute=0
charged_rate_grade             cells=84    overlap=0   gap=0   rule!=compute=0
charged_days_measure           cells=28    overlap=0   gap=0   rule!=compute=0
charged_share_grade            cells=18    overlap=0   gap=0   rule!=compute=0
charged_penalty_rounding       cells=10    overlap=0   gap=0   rule!=compute=2   (CG-2)
entry_principal_measure        cells=8     overlap=0   gap=0   rule!=compute=0
entry_rate_grade               cells=12    overlap=0   gap=0   rule!=compute=0
entry_days_measure             cells=10    overlap=0   gap=0   rule!=compute=0
added_days_grade               cells=8     overlap=0   gap=0   rule!=compute=0
lost_principal_measure         cells=12    overlap=0   gap=0   rule!=compute=0
restored_interest_span         cells=126   overlap=0   gap=0   rule!=compute=0
restoration_rate_grade         cells=28    overlap=0   gap=0   rule!=compute=0
restoration_allowance_grade    cells=14    overlap=0   gap=0   rule!=compute=0
restoring_deposit_rounding     cells=6     overlap=0   gap=0   rule!=compute=0
```

**578 cells, 0 gaps, 0 overlaps.** Exhaustiveness and disjointness hold **together**, which is the trade the coordinator asked to be tested for: the repair bought exhaustiveness without spending disjointness. No narrow fall-through wording survives in any of the four policies.

The seven ladders of the family — the six above plus `entry_principal_measure`, repaired in round 9 by CG-4 — now each pair an `otherwise` branch in `factors` with a rule clause that is its true complement. Two of the seven state that complement positively rather than as a residual (`entry_principal_measure`: "where the owner holds no active card"; and outside the family `added_days_grade`: "where the entry is booked within thirty days"), and the sweep confirms both are genuinely complete: their tier-1 clauses already cover the rest of the space, so no rewrite was owed and none was made.

*The worked instance re-derived.* Revision_9's demonstration was an owner of an **18-Month Bump-Up Certificate** holding an **active Secured Visa** with 900.00 of purchases posted in the three months before the deposit. Re-derived on the current rule: tier 0 fails (the card is neither a Cash Rewards Visa nor a Travel Rewards Visa Signature); tier 1 fails (900.00 is not "less than eight hundred dollars"); tier 2 now reads "*every other owner, whatever card they hold and whatever they have charged to it, earns it at the tier's published standard interest rate less the tier's relationship bonus points*" and **applies**, giving 3.83 − 0.15 = **3.68**. `compute[restoration_rate]`'s final `else` gives **3.68**. The rule is no longer silent where the code is not, and — the other half of revision_9's finding — the fall-through no longer misdescribes itself: it no longer reserves 3.68 for "an owner holding no active card" while handing it to a card holder.

**CG-13 is closed in substance, not renamed.**

### no new defect

- The only rule≠compute cells the sweep finds anywhere are the **four that are CG-2**, this auditor's standing round-8 observation, unchanged: `jumbo_figure_grade` tier 0 says "*whose owner **holds** an active savings or money market account*" while `compute[jumbo_figure]` tests `savings_balance > 0`, and `charged_penalty_rounding` tier 1 says "*the owner **holds** an active checking account whose balance is below …*" while `compute[rounded_penalty]` tests `checking_balance > 0`. An owner with an active account of exactly 0.00 lands on a different tier under each face. Neither task world contains a zero-balance active account, so no consequence can be demonstrated; it remains an observation. That the sweep re-derived CG-2 independently, and nothing else, is evidence the sweep is sensitive rather than vacuous.
- **Multi-source counts are untouched.** The requirement bites on "every tier other than the fall-through", and only fall-throughs were rewritten, so no tier that carries the multi-source burden changed. Counts remain 3 / ≥4 / 4 / ≥4 multi-source factors per computation, against a floor of 2.
- Factor structure is unchanged in every respect: 4 / 5 / 4 / 5 factors, 2 `parameter` and ≥2 `method` each, ≥2 `cross_difficulty` each, binding sets disjoint, no `decides` equal to `result`.
- No new narrow, overlapping or self-contradicting clause was introduced anywhere; the six new sentences are the only prose the sweep had not already seen, and all six pass.

### nothing regressed

Re-derived independently on the two worlds, and compared afterwards with the artifacts:

| quantity | revision_9 | revision_10 recomputation | GT now |
| --- | --- | --- | --- |
| T0 `new_interest_rate` / `new_apy` | 4.14 / 4.22 | 4.14 / 4.22 | 4.14 / 4.22 |
| T0 `withdrawal_amount` / `penalty_amount` / `penalty_days` / `rate_applied` | 103,054.59 / 687.42 / 68 / 3.99 | identical | identical |
| T0 renewal factor baselines, whole baseline | 4.17 / 4.09 / 4.19 / 4.13, 4.22 | identical | identical |
| T0 penalty factor baselines, whole baseline | 689.45 / 713.26 / 909.82 / 763.80 / 687.41, 1,052.00 | identical | identical |
| T0 edge skipped | 779.11 | 779.11 | 779.11 |
| T1 `entry_amount` / `entry_days` | 131.51 / 235 | 131.51 / 235 | 131.51 / 235 |
| T1 `deposit_amount` | 15,376.00 | 15,376.00 | 15,376.00 |
| T1 entry factor baselines, whole baseline | 149.88 / 134.90 / 104.65 / 127.60, 117.76 | identical | identical |
| T1 deposit factor baselines, whole baseline | 15,076.00 / 15,299.00 / 15,373.00 / 14,876.00 / 15,375.79, 14,500.00 | identical | identical |
| T1 edge skipped | 15,244.00 | 15,244.00 | 15,244.00 |

**No scored value moved, no ledger row was removed, and all eighteen factor substitutions still move their scored value.** Both problem trees, both state-form prerequisite sentences, both `owner=user` writes, both `db_closure_matches_initial_state` flags and both `charter_scope` blocks are unchanged; `task_tools.py` is byte-identical, so the uuid8s, the owners and the four unconditional tool bodies are too.

The numeric prose corrected in round 9 is intact and no stale figure returned: task 0 still carries 336.15, 4,132.63 and 220.89 and carries none of 304.23, 4,038.17 or 313.89; task 1 carries 735.41, 5,264.59, 131.51, 15,376.00, 298.34, 14,798.34 and 71,301.36 and carries none of 789.83, 130.15, 15,375.00, 54.42, 296.98 or 14,796.98.

*Two rationale factor cards updated, and true.* Task 0's `relationship_figure_grade` card and task 1's cards for `entry_days_measure`, `lost_principal_measure`, `restored_interest_span`, `restoration_rate_grade` and `restoration_allowance_grade` now describe their third tier as "every other owner / every other case, the fall-through the rule states as the complement of the two above". The sweep above is what makes that description true.

*Observations not acted on, as claimed, each confirmed:* **O-9.1** — the `penalty_basis_measure` wording and `within_months=1` are both unchanged, so the one-day boundary stands. **O-9.2** — task 1's world is byte-identical, so `interest_months_recent` is still exactly 3 against a `>= 3` threshold and two factors still share that boundary. **O-9.3** — `interest_months_recent` is still a row `COUNT` against a rule that says "in each of the three months", so CG-6 is still closed on task 1's world and open at charter scope. CG-2, CG-5, CG-7 to CG-12, F-4 to F-8 and F-12 to F-14 are likewise unchanged; none has acquired a consequence.

---

### closing_checklist (revision_10)

| item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks; `_difficulty.md` alongside | ✔ |
| old revisions traceable | ✔ revisions 1-9 preserved verbatim; this round appended as `revision_10` |
| **every comparison section carries a PASS** | ✔ **both tasks, all four relationships** |
| extended policies fully covered; scopes pairwise disjoint | ✔ {renewal, penalty} and {entry, add-on}, disjoint in policies and tools |
| task tools and GT closed; uuid8s independently generated, frozen, unreused | ✔ `3666596b`, `44cc2957`, `7001af6d`, `1e70ab4d`; `task_tools.py` byte-identical since revision_8 |
| one to three prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, no cycle; difficulty-wide DAG | ✔ one prerequisite and one `value_input` edge per task, `confirm_partial_withdrawal_44cc2957` and `confirm_term_add_on_1e70ab4d` owned by the customer, two disjoint acyclic components |
| every edge bears weight | ✔ 687.42 vs 779.11; 15,376.00 vs 15,244.00 |
| self-sufficient baseline giving a definite number different from gold | ✔ 4.22/4.14, 1,052.00/687.42, 117.76/131.51, 14,500.00/15,376.00 |
| 4-6 factors, 2 `parameter`, 2 `method`, 2 multi-source, 2 cross-difficulty per computation | ✔ 4 / 5 / 4 / 5 |
| **every ladder at least three tiers, pairwise disjoint and stated in full in its rule** | ✔ **578 cells swept, 0 gaps, 0 overlaps, 0 rule/compute disagreements beyond observation CG-2** |
| every factor bears weight against an honest baseline | ✔ eighteen substitutions re-run this round |
| a genuine near-miss per computation | ✔ for three of four. For the restoring add-on the criterion is met in form — the 900.00 card payment of 2026-06-06 is a record a careless reader would count and the rule excludes — but it flips no tier, which is **F-12**, carried as an observation and not as a red light. Stated here so the close-out does not pass over it |
| instantiation-stage gates re-run once on the final form | ✔ re-run by the coordinator after this rework; every count identical to round 9 |

## THE DIFFICULTY CLOSES.

For both tasks: **policy self-consistency PASS, the problem tree holds PASS, factors bear weight PASS, unique solution PASS.**

Across three rounds, thirteen red lights were raised and all thirteen are closed in substance: CG-1, CG-1a, CG-3/F-1, CG-4, CG-13, F-2, F-3, F-9, F-10, F-11 and F-13's false sentence at charter and task scope, and revisions 1-7's findings against the superseded generation of the artifacts. The two that put a second defensible answer on a scored parameter were closed in the two directions that actually remove the ambiguity rather than rename it — CG-3/F-1 by wording the rule to the reading the world is scored on, and F-11 by rebuilding the world to be legal under the charter it is scored against. What remains on record is a set of observations, none of which demonstrates a consequence on either task's world, and which per this skill are not grounds for rework: CG-2, CG-5 to CG-12, F-4 to F-8, F-12, F-14, O-9.1, O-9.2, O-9.3.
