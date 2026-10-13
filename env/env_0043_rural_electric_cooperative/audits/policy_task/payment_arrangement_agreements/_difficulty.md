# Policy-task audit — payment_arrangement_agreements / charter-global

## charter_global_frozen

- Auditor: Claude (erl-task-policy-audit), independent of the instantiating agent; no answer supplied by the orchestrator was used.
- Freeze time: 2026-10-06 18:31 UTC (written before any task GT was revealed; this section contains nothing derived from a revealed GT).
- Frozen inputs (sha256, re-computed by the auditor and equal to `/tmp/orch43/views/payment_arrangement_agreements/HASHES.txt`):
  - `tasks/payment_arrangement_agreements/arrange.extended.yaml` = `f8442b77df9d7e3ca1b9752dca85ecddf76387762298f3dd05a937b5674d671a`
  - `tasks/payment_arrangement_agreements/task_tools.py` = `ddf6188a0b7a036e9e85e2e8ede85508af7538b8b3512411604b175c6fc67a77`
- Fields read for this section: `blueprint/blueprint.yaml` (difficulty scope via the brief), `blueprint/products/arrange.yaml` (base), `blueprint/products/{service,deposit,capital}.yaml` (cross-category reads only), `blueprint/db_schema.json`, `blueprint/share_tools.py` (finder signatures), the extended charter, `task_tools.py`, `erlbench/scoring.py`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to learn the semantics of `within_months`, `MONTHS`, `RND`, `CFIELD`).
- Fields masked and not read: all of `tasks/*/tasks/*.json` except the mechanically masked views (`frozen_time`, `user_scenario`, `initial_state`), `tasks/payment_arrangement_agreements/worklog.md`, the scenario-level `worklog.md`, any sibling difficulty's tasks directory, any other `env/` scenario.

### entry_conditions (Step 0)

- Gate snapshot supplied (`/tmp/orch43/snap_payment_arrangement_agreements.txt`): EXTENDED OK, TASK-TOOL-CONTRACT OK, REPLAY OK (0.json 14 acts / 1.json 17 acts, det, match), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. `check_traceability` deferred until the KB is published (stated by the brief) — recorded, not run by the auditor.
- Masked views supplied with hashes; view hashes re-computed and equal (0.view.json `36e02496…`, 1.view.json `38266713…`).
- Base copy: lines 1-806 of the extended charter are byte-identical to `blueprint/products/arrange.yaml` (diff shows only the trailing blank line 807).

### policy_conflict_scan

Six extended policies, six task tools, each `(target_tool, computes)` distinct:

| policy | subject | target_tool (owner) | computes | trigger |
| --- | --- | --- | --- | --- |
| arrange_ext_missed_installment_amount | arrange_installment_missed | book_missed_installment_8c48d67e (agent) | amount | state_due |
| arrange_ext_early_payoff_balance | arrange_balance_rebill, arrange_complete | pay_off_payment_agreement_d76d2954 (user) | payoff_amount | on_request |
| arrange_ext_installment_billed_amount | arrange_installment_bill | bill_agreement_installment_2bd16d35 (agent) | amount | state_due |
| arrange_ext_default_rebill_amount | arrange_default, arrange_balance_rebill | record_agreement_default_c78cb15c (agent) | rebill_amount | state_due |
| arrange_ext_acceptance_arranged_amount | arrange_accept | accept_payment_agreement_6d07adca (user) | arranged_amount | on_request |
| arrange_ext_balance_transfer_amount | arrange_balance_transfer | move_balance_into_agreement_3b3ea9ff (agent) | amount | state_due |

- Overlapping subjects: `arrange_balance_rebill` is the subject of both the payoff and the default policy, but each is reached by a different transition (`rebill_reason` early_payoff vs default) and a different tool; no shared trigger. No two extended policies govern the same quantity.
- Time anchors: every extended policy is evaluated on "the day ... is recorded" = the tool's `ctx.now()` date; windows use the evaluator's `within_months` ("0 <= MONTHS(d, NOW) < k", i.e. dates after the same day k months earlier). Consistent across the charter.
- Cross-category read boundaries — **conflict found** (finding D-F2): the default policy sets the held security deposit, its accrued interest and the payable capital credits against the defaulted balance of a service account that is still open, which the deposit charter and the capital charter both forbid (quoted under findings). The transfer policy's capital hold-back ("to be paid as a bill credit against the past due") and the payoff policy's application of capital/deposit bill credits do not contradict a quoted sentence of those charters; recorded as observations (D-O8).
- Scope: task 0's tree covers {missed, payoff}; task 1's tree covers {installment, default, acceptance, transfer}. The two sets are disjoint and jointly cover all six extended policies (scope fields themselves are masked; this is the auditor's own derivation, to be compared at reveal).

### rule_compute_equivalence

Swept sentence by sentence, every `compute_basis` quotation checked mechanically against its own `rule` (whitespace-normalised substring) and every binding read against the rule:

- All `compute_basis` quotations are verbatim in their rule except payoff `capital_status: "where the member's capital credit account is active"` — the rule reads "where the member's capital credit account in the patron class of the service account's rate schedule is active"; the meaning is present (observation D-O6).
- All `baseline.rule` sentences are verbatim sentences of their policy's `rule` (all six).
- **Rounding mode — every policy (finding D-F1).** Each rule ends "rounded half up to the cent once at the end"; every `result` binding is `RND(...)`, and the evaluator defines `RND` as `lambda x, n=2: round(float(x), n)` (`check_compute.py` build_env), i.e. Python's round-half-to-even on a binary float. On an exact tie the two differ by a cent (e.g. 50.575 → rule 50.58, compute 50.57). Scoring is an exact DB-hash match (`erlbench/scoring.py`: `match = predicted == target`; tools store `round(float(amount), 2)`), so a one-cent difference fails the task. Consequence is demonstrated per task (task 0 hits a tie; task 1 does not).
- Invented sentinels (observation D-O4): transfer `acceptance_day: F('accepted_date') or '9999-12-31'` (no rule sentence says what the acceptance day is when none is recorded); missed `certificate_received: ... or NOW` (an unexpired `medical_certificate_expires` with no certificate row is silently put on the "received within 30 days" tier).
- Transfer `fees_since_notice` (observation D-O2): rule "Service fees billed since an outstanding disconnect notice are held back"; compute sums only `service_fee` lines of the latest billing period and only when the latest bill post-dates the notice. A fee billed after the notice on an earlier period, or a fee billed after the notice when the latest bill predates it, is held back by the rule and not by compute. No consequence in either task world (task 1: the only post-notice fee is the 2026-10-06 field collection fee of the latest period, both readings 35.00).
- Transfer `left_out` (observation D-O3): "otherwise the lines of the latest billing period ... are left out" — compute sums usage, fee, late and program lines but no `service_bill_credit` lines; tier precedence when an account is both under notice and `disconnected_nonpay` is fixed by compute order only. No consequence in task 1 (latest farm-home period has no credit lines; status disconnect_pending).
- Every factor's ladder tiers are sentences of the rule and branches of its `decides` binding, and every branch of each `decides` binding is a tier the rule states (checked for all 24 factors). No tier lives only in compute.

### action_binding_and_uuids

- Each `(target_tool, computes)` claimed by exactly one policy (table above).
- No tool body checks a business precondition; every body is an unconditional `ctx.create` / `ctx.update` (read in full). No tool refuses, errors or hints when a prerequisite is unresolved.
- Docstrings name no other tool and state no position in a sequence. Two phrasings noted (observation D-O10): `move_balance_into_agreement_3b3ea9ff` "a member's newly accepted payment arrangement" (describes the object's state, which is also the transfer's prerequisite state); every docstring's "Afterwards ..." describes the call's own effect, not an order among tools.
- uuid8s: 8c48d67e, d76d2954, 2bd16d35, c78cb15c, 6d07adca, 3b3ea9ff — pairwise distinct, no shared prefix/suffix, no sequential pattern, none present in `blueprint/share_tools.py`. PASS.

### prerequisite_graph

Edges (all `form: state`, no `fallback_reason` needed):

| id | blocked policy | problem | kind | gate | resolved_by = problem's target_tool |
| --- | --- | --- | --- | --- | --- |
| E1 | early_payoff_balance | missed_installment_amount | value_input | missed_month (compute binding exists) | book_missed_installment_8c48d67e ✓ |
| E2 | default_rebill_amount | installment_billed_amount | value_input | billed_out (exists) | bill_agreement_installment_2bd16d35 ✓ |
| E3 | acceptance_arranged_amount | default_rebill_amount | state_gate | arrangements.status (record field) | record_agreement_default_c78cb15c ✓ |
| E4 | balance_transfer_amount | acceptance_arranged_amount | value_input | acceptance_day (exists) | accept_payment_agreement_6d07adca ✓ |

- `prerequisite` filled on all six (`[]` on missed and installment). Every `problem` is an extended policy id of this file, none self-referencing; graph is two chains (missed ← payoff; installment ← default ← acceptance ← transfer) — acyclic.
- Each `policy_source` is verbatim in the blocked policy's own rule (mechanical check) and absent from the depended-on rule.
- `condition` vs sentence strength: E1, E2, E4 equal scope. E3 equal scope ("every other agreement ... whose missed installments have reached the default count").
- `effect` claims: E1, E2, E4 — the depended-on write changes the named binding (verified per task). E3's effect adds "the portfolio default history the tier allows (prior_defaults_allowed) is read on current records" — `arrange_agg_member_history` applies its eligibility to `arrange_offer` only, not to acceptance; the clause over-claims a gate the charter does not apply to acceptance (observation D-O7). No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Four-point test, per edge:

- E1 "The balance billed back on an early payoff is fixed only after every installment of the agreement whose grace period has ended unpaid carries a missed-installment entry on the agreement's ledger." — connective "only after"; waited-on state = a missed-installment entry on the agreement's ledger (record-visible, no performer/tool); no tool, id or snake_case; scope = every grace-ended unpaid installment. Only one write of this difficulty creates an `arrange_installment_missed` row: `book_missed_installment_8c48d67e` (missed policy, whose rule describes recording a miss). Single reading. PASS.
- E2 "The balance billed back at a default is not fixed until the installment due on every bill already issued for the service account carries its installment-billed entry on the agreement's ledger." — "not ... until"; state = installment-billed entry; only `bill_agreement_installment_2bd16d35` creates `arrange_installment_bill` rows (installment policy: "its next installment is billed on each bill issued"). PASS.
- E3 "The arranged amount recorded on an acceptance is fixed only once every other agreement of the member whose missed installments have reached the default count shows defaulted status." — "only once"; state = defaulted status; only `record_agreement_default_c78cb15c` sets `status=defaulted` (default policy: "When the missed installments ... reach missed_installments_before_default, the agreement defaults"). PASS.
- E4 "The amount moved into an agreement is not fixed until the agreement shows the member's acceptance, with its accepted date and acceptance method recorded." — "not ... until"; state = accepted date and method recorded; only `accept_payment_agreement_6d07adca` sets them. PASS.
- Second wordings / undeclared orders (observations, no demonstrable second answer in either task):
  - D-O5: the transfer rule also opens "Once an agreement is accepted, the past-due balance it covers is moved off the service account into the agreement" — an action-form restatement of the E4 dependency alongside its state-form sentence.
  - D-O9: the default rule's first sentence "When the missed installments of an agreement reach missed_installments_before_default, the agreement defaults" states that the default waits on missed-installment entries (written by the missed policy) and grounds no declared edge. In neither task are both writes pending (task 0: one miss on a two-miss tier, no default; task 1: the miss is seeded), so no two orders can be exhibited.
  - Base sentences stating cross-problem order (e.g. arrange_evt_acceptance "On acceptance the arranged amount is moved off ...") ground no edge; E4 rests on its extended sentence. Observation only.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- missed ← arrange_evt_default: sentence 1 (when an installment counts as missed) replaced and declared. Sentences 2-5 (default trigger, rebill, disconnect on default, never reinstated) govern other quantities; followed.
- payoff ← arrange_evt_completion: sentence 2 (early payoff bills back "the unbilled balance") replaced and declared; the extended amount is unbilled less net credits. Sentence 1 (completion when last installment billed and balance zero) and 3 (no hold after completion) followed. arrange_evt_default / arrange_evt_termination: the unbilled-balance definition is consistent; followed. Consequence noted as observation D-O8: after a payoff the tool closes `arranged_balance` to 0 while the ledger (transfer − installments − rebill) keeps a residual equal to the net credits applied, against the base account definition "out = installments billed and the unbilled remainder billed back at payoff" — a consequence of the declared override, not a second answer.
- installment ← arrange_evt_installments: "A payment above the bill due is applied under extra_payment_application" replaced and declared. "Each installment is computed under installment_rounding_rule" and "the last installment being whatever remains" are followed by the "installment scheduled" sentence; the reduction below the scheduled amount derives from the declared replacement. No undeclared override (observation D-O11 only).
- default ← arrange_evt_default: "the unbilled arranged balance is billed back at once ... due default_rebill_due_days" replaced and declared; other sentences followed. arrange_evt_completion / arrange_evt_termination: followed.
- acceptance ← arrange_evt_terms: the arranged-amount sentence and the pledge-toward-down-payment clause both replaced and declared. Down-payment sentence 1 (pct, minimum, cap) is consumed through the offer's stated `down_payment_amount`; followed. ← arrange_evt_acceptance: window, method, down-payment-posted gate inherited and not weakened.
- transfer ← arrange_evt_acceptance: "On acceptance the arranged amount is moved off the service account's past-due balance" replaced and declared; other sentences followed.
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped base branch found beyond the declared replacements. No authoring note calls base's output a "wrong value".
- Cross-charter: the overwrite mechanism declares only arrange base sentences; the deposit/capital conflict of D-F2 cannot be declared here and stands as a conflict.

### factor_ladders

Per policy (label as declared → auditor's assessment; MS = every non-fall-through tier a conjunction over distinct records; XD = reads another difficulty):

**missed_installment_amount** (6 factors; baseline: usage lines only, share 1, payments as posted, 1-month pledges, no pledge credit, no allowance — all six fall-throughs equal the baseline):
- current_lines_by_late_record — method → honest (changes the line set). 3 tiers distinct. MS no. XD service.
- medical_protection_share — parameter (0.5/0.75/1) → honest. MS yes (service_accounts.medical_certificate_expires × service_certificates.received_date). XD service.
- payment_crediting_by_record — method → honest (channel filter / net of returns / as posted). MS no (tier 1 single). XD service.
- pledge_lookback_by_circumstance — **method → mislabelled**: `pledge_months` evaluates to the integer 3/2/1 and is fed unchanged into the same `XSUM(..., within_months=pledge_months)`; only a window length differs (finding D-F3).
- pledge_credit_by_agency_record — parameter (1.0/0.5/0) → honest. MS yes (pledge rows × agency-payment rows). XD service.
- shortfall_allowance_by_standing — parameter (20/10/0) → honest. MS yes (ledger missed entries × capital account). XD capital.
- Counts as declared: 3 parameter / 3 method; honest: 4 parameter / 2 method (bounds still met).

**early_payoff_balance** (4 factors; baseline: nothing covered first, latest period's credits, no credit applied; fall-throughs equal baseline):
- arrears_covered_first — method → honest (max(notice, missed) / missed / none). MS yes (ledger × service_accounts). XD service.
- credit_bills_by_circumstance — **method → mislabelled**: `credit_bills` is the integer 3/2/1 selecting how many identical per-period sums are added (finding D-F3). MS no (certificate expiry and notice date are fields of the same service_accounts row).
- capital_credit_share — parameter (1.0/0.5/0) → honest. MS no (one capital row). XD capital.
- deposit_interest_share — parameter (1.0/0.5/0) → honest. MS no (one deposit row). XD deposit.
- Counts as declared: 2 parameter / 2 method; honest: 3 parameter / 1 method. If a mislabelled factor is struck rather than relabelled, this computation keeps 3 factors (< 4).

**installment_billed_amount** (4 factors; fall-throughs equal baseline):
- previous_bill_requirement — method → honest (line set). MS yes (ledger missed × late-charge rows). XD service.
- credit_toward_previous_bill — method → honest. MS no. XD service.
- pledge_by_agency — parameter (1.0/0.5/0) → honest. MS no. XD service.
- uncleared_funds_share — parameter (0.5/0.75/1) → honest. MS yes (latest payment row × return rows). XD service.
- 2 parameter / 2 method. Only service is read across difficulties.

**default_rebill_amount** (4 factors; fall-throughs equal baseline):
- deposit_principal_set / deposit_interest_set / capital_credits_set — parameter (share of held amount / accrued interest / payable: 1, 0.5, 0) → honest labels. MS no (each one row). XD deposit / deposit / capital. Their tier-1 and tier-2 outcomes conflict with the deposit and capital charters (finding D-F2).
- latest_bill_covered_first — method → honest (line set). MS yes (late-charge rows × return rows). XD service.
- 3 parameter / 1 method.

**acceptance_arranged_amount** (6 factors; fall-throughs equal baseline):
- late_charges_out_of_arrears — method → **mislabelled** (12-month sum / 3-month sum / none: a window length) (finding D-F3; weakest of the three because the fall-through is "none").
- pledge_toward_down_payment — parameter (1.0/0.5/0) → honest. Conditions: tier parameter × pledge age.
- charge_settled_first — method → honest (latest late charge / latest fee / none: different record). MS partly (tier 2 is a conjunction).
- deposit_owed_set_aside — method → label honest (whole required / required ÷ count / 0). **Tier 2's outcome "one installment of it, the required amount divided by its installment count" is not an installment the scenario's deposit charter ever bills** for tiers with `first_installment_pct` 50 (deposit charter formula `first_installment: round(required_amount * first_installment_pct / 100, 2)`, `later_installment: round((required_amount - first_installment) / max(installment_count - 1, 1), 2)`; every deposit tier read here has `installment_count: 3`, `first_installment_pct: 50`) — finding D-F4b.
- excess_credit_by_record — parameter → honest. MS yes (late rows × return rows).
- check_payment_scale — parameter → honest. MS yes (latest payment × count of check payments).
- Declared 3 parameter / 3 method; honest 4 / 2.

**balance_transfer_amount** (4 factors; fall-throughs equal baseline):
- latest_bill_left_out — method → honest. MS no (tier 2 single condition).
- pledge_held_back_by_agency — parameter (whole / 0.5 / 0) → honest.
- fees_held_back_since_notice — parameter (1.0/0.5/0) → honest. MS yes (fee lines × late-charge rows).
- capital_payable_held_back — parameter → honest. XD capital.
- 3 parameter / 1 method.

No ladder has two tiers selecting the same value or method; every ladder has exactly three pairwise-disjoint tiers stated in full in the rule. No tier condition holds of every customer reaching the write. Realism notes that demonstrate no consequence are kept as observations (D-O8).

### findings

- **D-F1 — SOURCE-POLICY RED (rule/compute: rounding mode).** Symptom: rule "rounded half up to the cent once at the end" (all six policies) vs `RND = round(float(x), 2)` (half-to-even on binary floats). Evidence: `check_compute.py` build_env `"RND": lambda x, n=2: round(float(x), n)`; `round(50.574999…, 2) = 50.57` while half-up of the exact 50.575 is 50.58. Consequence: demonstrated in `0.md` (task 0 missed amount and, through E1, the payoff). Bears on: task 0 (tie present), task 1 (no tie at any scored value — no consequence).
- **D-F2 — SOURCE-POLICY RED (cross-category conflict, undeclarable).** Default rule: "where the deposit is held and was paid in full at least deposit_settled_months calendar months before the default date, its whole held amount is set against the balance ... its whole accrued interest is set against the balance ... where that account is active and carries retired credits still payable, the whole payable balance is set against the balance". Deposit charter `deposit_evt_application`: "A deposit is never applied to an account that is still open and active merely because a bill is past due; collection follows the Electric Service charter." Capital charter `capital_agg_member_payout`: "An unpaid balance on an open, active service account is never offset; it is collected under the Electric Service charter." Same situation (a default on an open account), opposite conclusions. Consequence demonstrated in `1.md`. Bears on: task 1.
- **D-F3 — SOURCE-FACTOR RED (mislabelled effect).** pledge_lookback_by_circumstance (missed), credit_bills_by_circumstance (payoff), late_charges_out_of_arrears (acceptance) are labelled `method` but their tiers only substitute a window length / period count into an identical expression. Bears on: task 0 (two factors; the payoff computation keeps 1 honest `method` and 3 honest `parameter`, or 3 factors if struck) and task 1 (one factor; bounds still met).
- **D-F4 — SOURCE-FACTOR RED (cross-difficulty evidence vs that product's charter)**, two parts whose demonstration is per task: (a) the deposit charter pays deposit interest "on the bill of interest_payout_month" (1 for every tier) — see `0.md` for the September deposit-interest credit the payoff's deposit factor rests on; (b) acceptance tier 2's "required amount divided by its installment count" is not the deposit charter's installment — see `1.md`.
- Observations D-O1..D-O11 (no demonstrated second answer): D-O1 baseline sentences kept in the rule beside the ladders that refine them (e.g. payoff "No credit standing on the service account is applied to the payoff." followed by tiers that apply capital/deposit credits) — read as default-then-refinement; D-O2 transfer fees_since_notice scope; D-O3 transfer left_out credit lines / precedence; D-O4 sentinels; D-O5 second wording of E4; D-O6 payoff `capital_status` quotation not verbatim; D-O7 E3 effect over-claims prior_defaults_allowed; D-O8 realism: the payoff applies capital-retirement and deposit-interest bill credits that have already reduced the service bill, and leaves a ledger residual after closing the balance to zero; the transfer holds back payable capital credits that the capital charter pays on its own schedule; D-O9 default trigger states an undeclared order on missed entries; D-O10 docstring phrasing; D-O11 installment rounding-rule sentence followed.

## closing_checklist

Written 2026-10-06 18:36 UTC, after both reveals. Nothing above this heading was changed after the reveal (sha256 of this file at freeze: `0ee6464c…`).

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; first revision, no older revisions. **Not every comparison carries a PASS.**
- Coverage and scope: the six extended policies are covered; GT `charter_scope` = task 0 {missed, payoff}, task 1 {installment, default, acceptance, transfer} — equal to the blind derivation, pairwise disjoint over the whole trees. uuid8s independent and frozen. PASS.
- Problem trees: task 0 n = 1, 1 value_input, user write (payoff) — PASS. Task 1 n = 3, declared 2 value_input but only 1 bears weight as a value (`1.md` T1-F3), user write (acceptance) named by the customer in the opening request (`1.md` T1-F2) — FAIL. Difficulty-wide graph acyclic — PASS.
- Factors: every computation has a self-sufficient baseline, 4–6 declared factors, 3-tier ladders stated in the rule, distinct tier outcomes, and every factor moves its scored value against its baseline; all-baseline numbers differ from gold. FAIL on: mislabelled `method` factors (D-F3; task 0 payoff drops to 1 honest method / 3 factors if struck); cross-difficulty evidence vs its own charter (D-F4: task 0 September deposit-interest credit; task 1 deposit installment 120 vs 180/90/90).
- Policy self-consistency: FAIL on D-F1 (rounding; task 0 GT 50.57/134.45 vs rule 50.58/134.46) and D-F2 (deposit/capital set against an open account's default; task 1 69.10 vs 135.68).
- Instantiation gates on the final form: the charter, tool module and task files are unchanged since the orchestrator's snapshot (charter `f8442b77…`, tools `ddf6188a…`; tasks `d9ccddd2…`, `5b9e2a7e…` read at reveal); the auditor did not re-run them (Step 0: gates are supplied, not run by the auditor). `check_traceability` remains deferred.

**Difficulty result: does not pass the source-layer audit.** Per task: task 0 — SOURCE-POLICY RED, SOURCE-FACTOR RED (problem tree PASS); task 1 — SOURCE-POLICY RED, SOURCE-CHAIN RED, SOURCE-FACTOR RED.

## revision_2

### charter_global_frozen (revision_2)

- Auditor: Claude (erl-task-policy-audit), same auditor as round 1; written before any round-2 task GT was read. Freeze time: 2026-10-06 19:55 UTC.
- Inputs changed since round 1, so every charter-global section is re-derived in full: `arrange.extended.yaml` `f8442b77…` → `959e3bfc4a7bcf6e7c89f11f470e144971d283e834e5ee3dd7a0d3349b6ea8c1`; `task_tools.py` `ddf6188a…` → `ad03c99dbfd39685e7df12fac941566a7e079381d560a2f24edfdd4c1efb0572` (both equal to `/tmp/orch43/views/payment_arrangement_agreements_r2/HASHES.txt`). Base copy still byte-identical to `blueprint/products/arrange.yaml`. Blueprint files unchanged (mtime 11:15–11:20 UTC, before round 1).
- Entry conditions: round-2 gate snapshot `/tmp/orch43/snap_payment_arrangement_agreements_r2.txt` — EXTENDED, TASK-TOOL-CONTRACT, REPLAY (0.json 14 acts, 1.json 17 acts, match), SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability still deferred. Masked views r2 re-hashed: 0.view `40394846…`, 1.view `e87a152d…` — equal.
- Masked and not read: `tasks/*.json` GT fields, `tasks/payment_arrangement_agreements/worklog.md` (modified 19:29 — not opened), scenario worklog, sibling difficulties, other scenarios. The reworker's claims were received by item id only; no claim text was used as evidence.
- Round-1 text above is untouched.

### policy_conflict_scan (revision_2)

- Six policies, six tools, `(target_tool, computes)` unchanged and distinct; subjects unchanged.
- Cross-category boundaries: the default rule now reads "A security deposit is never applied and capital credits still payable are never offset at a default, because the service account stays open." and no longer reads the deposit charter, so it agrees with deposit `deposit_evt_application` and capital `capital_agg_member_payout`. It now applies the latest bill's capital-retirement and billing-correction credits and a carried credit balance — none contradicts a quoted sentence of another charter (realism: D-O8 family, below). The transfer no longer caps at a past-due measure; it is the arranged amount less hold-backs.
- **Newly found (present since round 1, not identified then): seeded capital-retirement evidence contradicts the capital charter's payout timing** — `capital_evt_general_retirement`: general retirements "are paid with the bills and check run of general_retirement_payment_month of the resolution year", `general_retirement_payment_month: 12` for every class, resolutions approved 2024-11-19, 2025-11-18, 2026-11-17; `active_member_disbursement: bill_credit`, `minimum_bill_credit_amount: 1.0`. An active member therefore receives capital-retirement bill credits only on December bills and carries no payable above 1.00 between payouts. Per-task demonstration in `0.md` / `1.md` revision_2 (R2-F1).
- Scope: task 0 {missed, payoff}; task 1 {installment, default, acceptance, transfer} (auditor's derivation; unchanged).

### rule_compute_equivalence (revision_2)

- Mechanical check: every `compute_basis` quotation verbatim in its rule (all six; round-1 D-O6 quotation now verbatim); every `baseline.rule` sentence in its rule; `compute_basis` has no entry for the binding `unbilled` in payoff and default (observation R2-O1; the sentence "The unbilled balance is the amount moved into the agreement less every installment billed and every amount already billed back" is quoted under `transfers_in` / `moved_in`).
- **Rounding (D-F1):** every `result` is now `int(MX(0, …) * 100 + 0.5 + 0.000001) / 100` — half up for the non-negative values these results are clamped to; the 50.575 case evaluates to 50.58. Closed. Intermediate `RND` remains only in the acceptance's `deposit_first_installment` / later installment, mirroring the deposit charter's own `round(…, 2)`; no rule sentence states another rounding there.
- Sentinels (D-O4): `acceptance_day` removed; missed `certificate_received … or '0000-01-01'` now sends "unexpired certificate, no certificate row" to tier 2, which the rule now states ("an unexpired medical certificate but no certificate received within those days"). Closed. Acceptance `pledge_date or NOW` with `pledge_amount or 0` yields no credit when no pledge exists — consistent.
- Transfer (D-O2, D-O3): the hold-back scope is now stated in the rule ("the charges concerned being those billed for the latest billing period where that bill was issued after the notice") and implemented as such; `left_out` removed. Closed.
- Payoff: credit window is now a month window over `charge_date` (`within_months=credit_months`), rule "the bill credits posted to the service account in the month ending on the payoff day" / "in the credit_months_notice months" / "credit_months_medical months" — equivalent.
- Default: every tier sentence present and implemented (bill credits by record; carried credit balance "(the service account's balance less that bill's charges and plus its credits, where below zero)" = `MX(0, 0 - (account_balance - latest_charges + latest_credits))`; capital standing; correction share).

### action_binding_and_uuids (revision_2)

- uuid8s unchanged (8c48d67e, d76d2954, 2bd16d35, c78cb15c, 6d07adca, 3b3ea9ff), independent, not in share_tools.py. Bodies still unconditional creates/updates; no `if`/`raise` in any tool body. D-O10: "newly accepted" removed from the transfer docstring ("a member's accepted payment arrangement"). PASS.

### prerequisite_graph and prerequisite_sentences (revision_2)

- Same four edges, all state form; all `policy_source` verbatim in the blocked rule and absent from the depended-on rule; all `resolved_by` = depended-on target tool. Acyclic.
- E4 changed: `gate: arranged_recorded` (binding exists), effect "arranged_recorded becomes the arranged amount the member committed to on acceptance instead of the amount stated on the offer". The transfer `result` now subtracts hold-backs from `arranged_recorded` with no cap, so the acceptance's value enters the scored number directly.
- E3 effect now "the arranged amount itself reads nothing from the other agreement" — D-O7 closed.
- D-O5: the transfer rule's action-form "Once an agreement is accepted …" sentence is gone. Closed.
- D-O9 (changed, not closed): the default rule now opens "An agreement whose missed-installment entries number at least missed_installments_before_default is in default" — a state-form statement that the default waits on missed-installment entries, still grounding no declared edge. No task has both writes pending (task 1's miss is seeded); observation.

### override_declarations (revision_2)

- missed, installment, acceptance: overwrites unchanged and verbatim; acceptance's deposit set-aside sentence rewritten (below) without touching a base sentence.
- payoff: same declared overwrite (arrange_evt_completion early-payoff clause). 
- default: overwrite `replaced_by` now "The balance billed back at the default is the unbilled balance less the credits applied to it, never below zero, rounded half up to the cent once at the end, and it is due default_rebill_due_days after the default date." — verbatim in rule; base sentence verbatim in base. Followed otherwise.
- transfer: `replaced_by` "The amount moved into the agreement is the arranged amount recorded on acceptance less what is held back from it …" — verbatim; base acceptance sentence verbatim. No undeclared override found.

### factor_ladders (revision_2)

| policy | factors (label → assessment) | parameter / method (honest) |
| --- | --- | --- |
| missed | current_lines (method ✓), medical_share (param ✓), payment_crediting (method ✓), pledge_lookback (now param ✓), pledge_credit (param ✓), shortfall (param ✓, XD capital) | 4 / 2 |
| payoff | arrears_covered_first (method ✓), credit_window (now param ✓: 12 / 10 / 1 months), capital_credit_share (param ✓, XD capital), deposit_interest_share (param ✓, XD deposit) | 3 / 1 |
| installment | unchanged: 2 method ✓, 2 param ✓ | 2 / 2 |
| default | bill_credits_by_record (method ✓: capital+correction / capital / none), carried_credit_share (param ✓), capital_credit_standing (param ✓, XD capital), correction_credit_share (param — **dead tier**, see R2-F2) | 3 / 1 |
| acceptance | late_charges_out (now param ✓), pledge (param ✓), charge_settled_first (method ✓), deposit_owed_set_aside (method ✓; tier outcomes now the deposit tier's own first / later installment), excess_credit (param ✓), check_scale (param ✓) | 4 / 2 |
| transfer | charges_held_by_record (method ✓: fees+late / fees / none; MS notice × bill date × returns), charge_hold_by_late_record (param ✓), pledge_held_back (param ✓), capital_payable_held_back (param ✓, XD capital) | 3 / 1 |

- D-F3 closed: the three window/count factors are now labelled `parameter`; every computation keeps ≥ 1 honest `method` and ≥ 2 `parameter`, 4–6 factors.
- D-F4b closed: deposit set-aside tiers now "its first installment as the deposit tier bills it (first_installment_pct percent of the required amount)" / "its next later installment as the deposit tier bills it (the required amount less that first installment, divided by one less than its installment count)" — the deposit charter's `first_installment` / `later_installment` formulas.
- All fall-throughs equal their baselines; no two tiers of a ladder share an outcome as stated.
- **R2-F2 — SOURCE-FACTOR RED (new; dead tier).** Default `correction_credit_share`: tier 1 "in full where no returned payment was posted in the twelve months ending on the default date". But correction credits enter the result only through `bill_credits_by_record` tier 1, whose condition includes "a returned payment was posted in the twelve months ending on that date" (`bill_credits_applied = latest_capital_credits * … + latest_correction_credits * correction_share if (default_late_3m >= 1 and default_returns_12m >= 1) else …`). Whenever a correction credit is applied, `default_returns_12m >= 1`, so `correction_share` is 0.5 or 0; the "in full" tier can never reach a scored value in any world. The ladder has two live outcomes, below the three-tier minimum. Bears on task 1.
- Realism (D-O8 family, observation R2-O2): the default now applies credits already posted on the latest service bill (capital retirement, billing correction) and a carried credit balance to the defaulted arrangement balance, and applies more of them to the member with a late charge and a returned payment than to one with a late charge only (and none to a member with no late charge).

### findings (revision_2, charter-global)

- D-F1 closed. D-F2 closed. D-F3 closed. D-F4b closed (charter part). D-F4a: see `0.md` revision_2 (timing fixed, amount still contradicts the deposit charter — R2-F3).
- R2-F1 (new finding, pre-existing since round 1): capital-retirement seed evidence vs capital charter timing — bears on tasks 0 and 1.
- R2-F2 (new, introduced by the rework): dead tier in default `correction_credit_share` — bears on task 1.
- Observations: R2-O1 (`unbilled` basis key), R2-O2 (default credit realism), D-O9 (changed, still observation), D-O1 / D-O8 / D-O11 left as is and still hold.

### closing_checklist (revision_2)

Written 2026-10-06 19:57 UTC, after both round-2 reveals; nothing above this heading in revision_2 was changed after the reveal (revision_2 freeze sha256 of this file `496b4f0b…`).

- Files: `0.md`, `1.md` each carry round 1 and revision_2; round-1 text untouched.
- Round-1 REDs: D-F1/T0-F1 closed; D-F2/T1-F1 closed; D-F3/T0-F2/T1-F4 closed; D-F4b/T1-F5 closed; T1-F2 closed; T1-F3 closed; D-F4a/T0-F3 **partly closed** (timing fixed, amount 7.35 vs charter 4.55 → R2-F3).
- Changed observations verified: D-O2, D-O3, D-O4, D-O5, D-O6, D-O7, D-O10, T1-O1, T1-O2 closed; T1-O4 now explained by the stated hold-backs; D-O9 reworded but still an undeclared state dependency (observation). Left-as-is items (D-O1, D-O8/T0-O2, D-O11, T0-O1, T0-O3, T1-O3, T1-O5, T1-O6) still hold as observations.
- Regressions: none in the scored solutions — blind revision_2 derivations equal GT on every write, argument, owner, order and factor-sensitivity figure in both tasks. New defect introduced by the rework: R2-F2 (dead tier in default correction_credit_share). New finding not caused by the rework and missed in round 1: R2-F1 (capital-retirement seed rows vs capital charter timing; the 22.40 row in task 1 is new in round 2).
- Coverage/scope disjoint and complete (GT charter_scope equals the derivation); uuid8s frozen; trees: task 0 n = 1 (1 value_input, user payoff), task 1 n = 3 (2 weight-bearing value_input, user acceptance), acyclic.
- Gates: orchestrator's round-2 snapshot on the current hashes is all green; not re-run by the auditor.

**Difficulty result (revision_2): does not yet pass.** Task 0 — SOURCE-FACTOR RED (R2-F1, R2-F3); task 1 — SOURCE-FACTOR RED (R2-F1, R2-F2). Policy self-consistency, problem tree and unique solution PASS for both tasks.

## revision_3

### charter_global_frozen (revision_3)

- Auditor: Claude (erl-task-policy-audit), same auditor; written before any round-3 task GT was read.
- Inputs: `arrange.extended.yaml` `959e3bfc…` → `e2de1c1f12b1cacc580b512fe86ec3c90dd5fcafe67fe532a9d06a986ac1e257` (changed → charter-global sections re-derived in full below); `task_tools.py` `ad03c99dbfd39685e7df12fac941566a7e079381d560a2f24edfdd4c1efb0572` (unchanged since revision_2 → §action_binding_and_uuids (revision_2) carried forward by reference on that hash). Both equal to `/tmp/orch43/views/payment_arrangement_agreements_r3/HASHES.txt`. Base copy byte-identical to the blueprint; blueprint products, schema and share tools unchanged (same sha256 as revision_2).
- Entry conditions: round-3 snapshot `/tmp/orch43/snap_payment_arrangement_agreements_r3.txt` all OK (REPLAY 0.json 14 acts, 1.json 15 acts, match); views r3 re-hashed equal (0.view `81febf84…`, 1.view `f5872024…`).
- Masked and not read: `tasks/*.json` GT, both worklogs, sibling difficulties, other scenarios. Reworker claims received by item id only.

### policy_conflict_scan (revision_3)

- Six policies / six tools unchanged in binding. Cross-category reads now: missed {service, capital}; payoff {service, capital, deposit}; installment, default, acceptance, transfer {service} only. No extended rule now sets a deposit or payable capital credit against an open account; default keeps "A security deposit is never applied and capital credits still payable are never offset at a default, because the service account stays open." No conflict with a quoted sentence of the deposit, capital or service charters found.
- Rule-level divergence (observation R3-O1): acceptance tier "where the service account carries an outstanding disconnect notice and no returned payment was posted in the twelve months ending on the acceptance day, every payment posted to the service account in the month ending on the acceptance day counts" toward "the down payment paid", while base `arrange_evt_acceptance` defines the down payment as having "posted ... on or after the offered_date". A payment of that month dated before the offer would count under the extended tier and not under base; the extended sentence governs the excess reckoning, not the base posting gate, and no overwrite names the base sentence. Consequence only where a pre-offer payment falls in that month — not in task 1's world (both farm payments in the month are dated 2026-10-05 and 2026-10-06, offer 2026-10-05).

### rule_compute_equivalence (revision_3)

- Mechanical: every `compute_basis` quotation verbatim; no compute binding lacks a `compute_basis` entry and none is extra (R2-O1 closed); every `baseline.rule` sentence in its rule; every overwrite verbatim on both sides; all results half-up `int(… * 100 + 0.5 + 0.000001) / 100`.
- Payoff: `credit_months_medical` 10 → 11; otherwise as revision_2.
- Default (rewritten factors): "Which credits standing on the service account are applied follows the account's payment record" → `credits_applied` three branches (correction + carried / correction / none) ✓; carried credit and its returns share ✓; correction share by 12-month returns ✓; new "They count further according to when the corrected line was billed: in full where it was billed on or before the day the balance was moved into the agreement …; at correction_share_after_transfer … where it was billed after that day" → `correction_source` (the correction credit's `source_reference_id`), `corrected_line_date`, `transfer_date` (ledger transfer entry) ✓.
- Acceptance: deposit set-aside removed; new `down_payment_by_standing` = month payments / month payments less checks / latest payment on or after the offer ✓; check scaling now keyed to "the latest payment posted to the service account" in both rule and compute ✓.
- Transfer: capital hold-back removed; new `pledge_hold_by_age` (hold days / lookback / none) multiplies the agency share ✓.

### prerequisite_graph and prerequisite_sentences (revision_3)

- Unchanged four edges, verbatim sentences, resolved_by = depended-on target tool, gates exist (E3 a record field), acyclic, none restated in the depended-on rule. E2/E4 effects as revision_2. D-O9 unchanged (observation).

### override_declarations (revision_3)

- Overwrites identical to revision_2 and verbatim. Beyond R3-O1 no base sentence is handled differently without declaration.

### factor_ladders (revision_3)

| policy | factors | param / method (honest) | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- |
| missed | unchanged (6) | 4 / 2 | medical, pledge credit, shortfall | service, capital |
| payoff | unchanged (4) | 3 / 1 | arrears_covered_first | service, capital, deposit |
| installment | unchanged (4) | 2 / 2 | previous_bill_requirement, uncleared | service |
| default | bill_credits_by_record (method: correction + carried / correction / none), carried_credit_share (1 / 0.5 / 0), correction_timing_by_transfer (1 / 0.5 / 0), correction_credit_share (1 / 0.5 / 0) | 3 / 1 | bill_credits (late × returns), correction_timing (credit row × corrected line × ledger transfer), carried (balance/lines × returns) | service |
| acceptance | late_charges_out (param), pledge (param), charge_settled_first (method), down_payment_by_standing (method: month payments / non-check month payments / latest payment), excess_credit (param), check_scale (param) | 4 / 2 | excess_credit, check_scale, down_payment_by_standing (notice × returns) | service |
| transfer | charges_held_by_record (method), charge_hold_by_late_record (param), pledge_held_back_by_agency (param), pledge_hold_by_age (param: 1 / 0.5 / 0) | 3 / 1 | charges_held_by_record | service |

- **R2-F2 closed:** correction credits are now applied in `bill_credits_by_record` tiers 1 and 2; tier 2 requires "no returned payment ... in those twelve months", so `correction_credit_share`'s "in full" tier is reachable. Carried credit is applied only under tier 1 (a return in 12 months) but `carried_credit_share` distinguishes returns in 3 months, so its "in full" tier (return 4–12 months back) is reachable too. No dead tier found in any ladder.
- Every ladder: three disjoint tiers stated in the rule, distinct outcomes, fall-through = baseline.
- Realism observations: R3-O3 — `correction_timing_by_transfer` tier 2 applies half of a correction for a line billed after the transfer, although the rule's own reason for tier 1 ("its overbilled amount having been moved in with the arrears") implies such an overbilling never entered the agreement; R2-O2 (credits applied to a defaulted balance, more for a worse record) left as is and still holds.

### findings (revision_3, charter-global)

- R2-F2 closed. R2-O1 closed. No new charter-global RED.
- Observations: R3-O1 (acceptance down payment window vs base "on or after the offered_date", no consequence in task 1), R3-O3 (correction timing realism), D-O9, R2-O2, and the carried-over D-O1 / D-O8 / D-O11.

### closing_checklist (revision_3)

Written 2026-10-06 20:35 UTC after both round-3 reveals; nothing above this heading in revision_3 was changed after the reveal.

- Per-task files `0.md`, `1.md` carry round 1, revision_2 and revision_3; older revisions untouched; both revision_3 comparisons carry **PASS**.
- Round-2 REDs: R2-F1 (task 0; task 1 (a), (b)) closed; R2-F2 closed; R2-F3 closed. R2-O1 closed. No new RED; no regression — blind revision_3 derivations equal GT on every write, argument, owner, order, tree figure and factor-sensitivity figure.
- Coverage: six extended policies covered; scopes {missed, payoff} / {installment, default, acceptance, transfer} disjoint over whole trees; uuid8s independent and frozen (tools unchanged since revision_2).
- Trees: task 0 n = 1, 1 value_input, user payoff; task 1 n = 3, 2 weight-bearing value_input + 1 state_gate, user acceptance; customer raises only the root in both; acyclic difficulty-wide.
- Factors: every computation 4–6 factors with ≥ 2 parameter and ≥ 1 honest method, three-tier ladders stated in the rule with distinct reachable outcomes, fall-through = baseline, every factor moves its scored value, all-baseline ≠ gold; each task has multi-source factors and cross-difficulty factors on seeded rows consistent with their charters (task 0: service, capital, deposit; task 1: service).
- Gates: orchestrator's round-3 snapshot on the current hashes all green; not re-run by the auditor; traceability deferred.

**Difficulty result (revision_3): passes the source-layer audit.** Task 0 PASS; task 1 PASS. Open observations (not grounds for rework): R3-O1, R3-O2, R3-O3, R2-O2, D-O1, D-O8, D-O9, D-O11 and the per-task carried observations.
