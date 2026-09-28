# Policy-task audit — payment_plan_servicing / charter-global

## charter_global_frozen

- Scenario: `env/env_0025_multispecialty_physician_group`; difficulty `payment_plan_servicing`; category `payplan` (Patient Payment Plans).
- Charter under audit: `tasks/payment_plan_servicing/payplan.extended.yaml` sha256 `214c7fffde287e00278eff9928b9fee0d1158cc35f7746085f087ce2adfaebf6` (matches the coordinator's brief).
- Tool module under audit: `tasks/payment_plan_servicing/task_tools.py` sha256 `a56b1dfd88d42db84e76fcb8795a87d95326695b9fa9c6d23c01f0332c5ee28c` (matches the brief).
- Freeze time of this section: 2026-09-25T00:06Z (UTC wall clock of the audit run). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the author of the artifacts.
- Revision: r1 (first audit; no earlier revision exists).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/payplan.yaml`, the class parameters of `blueprint/products/billing.yaml` (prompt_pay_*, returned_payments_before_restriction, gfe_dispute_threshold_usd, late_fee_usd, returned_payment_fee_usd, billing_msr_late_fees_12m), the extended charter, `task_tools.py`, and the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (RND / MONTHS / DAYS / within_months only).
- Masked and unread while this section was written: every `tasks/payment_plan_servicing/tasks/*.json`, `tasks/payment_plan_servicing/worklog.md`, every other audit directory. Nothing in this section derives from a revealed GT; it was frozen before either task's GT was opened.
- Entry conditions (Step 0): the brief supplies the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred until the KB is published), the masked views `audits/_coordinator/views/policy_task/payment_plan_servicing/r1/{0,1}.view.json` with sha256 `76259898…779ab8` and `9f26fe0c…283610` (both re-hashed and matching), and the charter hashes. The deferred traceability gate is a KB-stage gate and is recorded as cited, not as missing input. Entry conditions satisfied.

### policy_conflict_scan

Base section: `diff` of charter lines 5–1000 against `blueprint/products/payplan.yaml` lines 4–1000 is empty — the base copy is verbatim.

Extended policies (7) and the scope division stated in the charter header comment (lines 1001–1003):

| id | trigger | subject | target_tool / computes | claimed by |
| --- | --- | --- | --- | --- |
| payplan_ext_signing_setup_fee (A) | on_request | payplan_balance_enrolled | enroll_setup_fee_08ffaf93 / amount | task 0 |
| payplan_ext_encounter_charge_enrollment (B) | state_due | payplan_balance_enrolled | enroll_encounter_charge_372696d1 / amount | task 0 |
| payplan_ext_signing_installment (C) | on_request | payplan_agreement_signed | sign_installment_agreement_b4bb7ade / installment_amount | task 0 (root) |
| payplan_ext_add_on_charge_amount (D) | on_request | payplan_balance_enrolled | enroll_add_on_charge_102110ed / amount | task 1 |
| payplan_ext_add_on_term_extension (E) | on_request | payplan_modified | extend_plan_term_6d1d2771 / extension_months | task 1 |
| payplan_ext_add_on_fee (F) | on_request | payplan_balance_enrolled | enroll_add_on_fee_792da8e6 / amount | task 1 |
| payplan_ext_add_on_installment (G) | on_request | payplan_modified | accept_add_on_installment_27cdd630 / installment_amount | task 1 (root) |

Overlapping subjects and how they separate:
- `payplan_balance_enrolled` is written by A, B, D and F. They separate by plan status and occasion: A at signing of a proposed plan (enroll_reason setup_fee); B on a proposed plan for a later-posted charge of an already-enrolled encounter (initial_enrollment); D on an active plan at the patient's request (add_on); F on an active plan on the day of an add-on (setup_fee). Base `enroll_when_open` (proposed or active) is inherited by all four. No two of them apply to the same plan status and occasion.
- `payplan_modified` is written by E (term) and G (installment). Distinct fields; E never writes installment_amount and G never writes term_months (tool bodies confirm).
- Two extended policies override the same base clause each time: A and F both replace the base `payplan_enrollment_terms` setup-fee sentence; E and G both replace the base `payplan_add_on_and_modification` reamortize sentence. The replacements are compatible (A: fee at signing; F: fee at each add-on; E: term lengthened by the add-on; G: installment re-spread by basis over the installments left) and together give one merged reading per situation.
- Time anchors: every policy is evaluated on the handling date (NOW); B's prompt-pay window and late-posting lag anchor on the charge's posting and service dates; C and A's "signing date" is the handling date (the sign tool stamps `ctx.now()`).
- Cross-category reads: every extended policy reads only `billing` (billing_accounts fields, class parameters via CPARAM, billing_transactions via XSUM/XCOUNT/XLATEST); all read-only.
- Terminal states: C ends in status active; G ends in a new installment with modification_count +1; E ends in a longer term. No two policies drive one field to two values in the same situation.

Scopes: task 0 = {A, B, C}, task 1 = {D, E, F, G}. Pairwise disjoint and jointly complete over the seven extended policies (subject to confirming each task's `charter_scope` after the reveal).

Conflicts found: none that yields two conclusions in one situation on either task's world. Terminology and scope observations are listed under findings (O-1 … O-11).

### rule_compute_equivalence

Mechanical sweep (auditor's own script, removed afterwards): every `compute_basis` value of all seven policies is a verbatim substring of that policy's own `rule` (whitespace-normalised); every `baseline.rule` sentence is a verbatim sentence of the `rule`; every `overwrite.superseded_clause` is verbatim in the named base rule and every `replaced_by` is verbatim in the extended rule.

Per policy, rule → compute, then compute → rule:

- A (setup fee): standard fee `P('setup_fee_usd')`; autopay share (method ach/card/hsa_fsa_card ∧ zero late fees in the 12-month window) → `autopay_share`; late-fee window "less than 12 whole months" → `XCOUNT(… within_months=12 …, line_category='late_fee')`, whose `within_months` means `0 <= MONTHS(txn_date, NOW) < 12`; tenure "at least 120/60 whole months" → `MONTHS(opened_date, NOW)`; hardship "at least 50 % … through on or after the signing date" → `DAYS(NOW, through) >= 0`; size share on initial_enrollment + add_on sums (setup fee excluded); product of four shares → `scheduled_fee`; returning-plan rule (≥12: half, floor to dollar; 1–11: ×0.75, ceiling to dollar; 0: half-up to cent) → `fee_entered`. Sweep back: no binding without a rule sentence. Equivalent.
- B (encounter charge): estimate cap (Self-Pay: estimate + gfe_dispute_threshold_usd; other classes: estimate × 1.25 rounded; no estimate: full) → `counted_amount`; collections, adjustments and payments applied to the charge → `tos_collected`, `adjustments`, `all_payments`; clearing ladder on reversals in 12 months vs `returned_payments_before_restriction` → `credited_payments`; relief share (approval ≥50 / >0 and <50, through ≥ service date, no hardship adjustment on the charge) → `relief_share`; prompt-pay rate (≤ window days since posting; ach full, card/hsa_fsa_card half) → `prompt_rate`; late-posting share (≥60 / ≥30 days from service to posting) → `late_posting_share`; single rounding at the end → `result`. Equivalent except the charge selector — see O-3: the rule's filter "a charge the financial account posts, after the proposal date, for an encounter already enrolled on a proposed plan … where several such charges stand unenrolled the most recently posted one" is implemented as `XLATEST(… event_type='billing_charge_posted')` over the whole account, with no encounter, proposal-date or unenrolled filter.
- C (signing installment): plan balance (enrolled − reductions − payments); standard down payment and standard installment (baseline); down-payment ladder → `down_payment`; level installment → `level_installment`; first-phase ladder (Self-Pay ×0.80 floor; HDHP / PPO-POS ×0.90 floor; else level) → `first_phase`; autopay credit (ach 3.00 / card 1.50, both requiring paperless statements) → `autopay_credit`; returning-plan credit (≥12: 4.00; 1–11: 2.00; 0: 0.00) → `returning_credit`; min floor and rounding → `result`. The sentences "The installments of the first phase carry that amount for the first twelve months …" and "Any down payment above 0.00 is paid at signing as an extra payment of kind down_payment" carry no compute binding; neither is a scored quantity of this policy (see O-5 for the second). Equivalent.
- D (add-on amount): remaining balance; over-estimate share (HDHP / Self-Pay 0.50, other classes 0.75, of the part above the estimate) → `counted_amount`; plan-standing share (≥6 paid, none missed, all/at-least-one-not autopay, zero late fees in 12 months) → `standing_share`; deductible-exposure share (≥1000 / >0) → `deductible_share`; add-on prompt-pay rate (window ∧ card on file full, window ∧ no card half) → `addon_prompt_rate`; tenure rounding (≥120 floor dollar; ≥60 floor half dollar; else half-up cent) → `rounded_amount`. Selector "the most recently posted charge of the financial account" = `XLATEST` over the account: rule and compute agree. Equivalent.
- E (term extension): add-on entry booked on the handling date → `SUM(… enroll_reason='add_on', txn_date=NOW)`; size share amount / (6 × current installment); rounding ladder on reversals (0 up, 1 half-up, ≥2 down) → `size_months`; remaining-term, plan-history, plan-age, automatic-debit months → their bindings; room-left clamp `MX(0, MN(room, sum))`. Equivalent.
- F (add-on fee): number share on the lifetime count of add_on entries; size share on today's add_on entry; debit share on `autopay_enrolled` ∧ `card_on_file`; late-fee record share on a 24-month window; product of four shares; class rounding (HDHP floor dollar, Self-Pay floor half dollar, else half-up cent). Equivalent.
- G (re-spread installment): plan balance including releases; installments left = term_months − installments paid; basis ladder (Financial Hardship Plan: balance / tier term_months; other tier with today's add-on ≥ 0.50 × balance before it and no missed installment: current installment + (add-on + fee today) / installments left; else balance / installments left); class, debit and plan-age credits; min floor. Equivalent.

Rounding primitive (charter-wide): every "rounded half up to the cent" is implemented by `RND`, which the DSL defines as Python `round(float(x), 2)` (check_compute.py line 388), i.e. round-half-even on binary floats. See O-4.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: seven distinct tools, each claimed by exactly one policy (table above). No tool is claimed twice.
- Tool bodies (task_tools.py): each performs exactly one write (one `payplan_transactions` create plus a `remaining_balance` update, or one `payment_plans` update), checks no eligibility, computes no amount and validates no prerequisite: no body inspects plan status, ledger entries, term or any other policy's output before writing. Owners: `sign_installment_agreement_b4bb7ade` and `accept_add_on_installment_27cdd630` are `owner="user"`; the other five are `owner="agent"`.
- Docstrings: none names another tool or policy id and none carries "before", "after", "first", "then", "until" or "prior" as an ordering word (a grep over the module hits "first" nowhere; "when"/"today" hit lines 14, 18, 55, 96, 107, 129, 166, 169 and describe the entry date or the occasion). Two docstrings name the business occasion of another problem — `enroll_setup_fee_08ffaf93`: "Book the one-time setup fee … when the patient signs the installment agreement"; `enroll_add_on_fee_792da8e6`: "for an add-on accepted on the plan today" — recorded as O-9 (no ordering word, no position in a sequence).
- uuid8s: 08ffaf93, 372696d1, b4bb7ade, 102110ed, 6d1d2771, 792da8e6, 27cdd630 — seven distinct values, no shared prefix or suffix, no sequential or adjacent pattern; no evidence of batch derivation. (Reuse across other difficulties' modules cannot be checked without reading sibling directories, which is outside this audit's read domain.)
- Tool-layer effects add no procedure outside the policies: no confirmation, review or wait.

### prerequisite_graph

- Every policy carries `prerequisite`: A `[]`, B `[]`, D `[]`; C → {A, B}; E → {D}; F → {D}; G → {D, F, E}.
- Every `problem` is an extended policy id of this file; none points at a base policy or at itself.
- Graph: A→C, B→C (task 0 component); D→E, D→F, D→G, F→G, E→G (task 1 component). Acyclic (topological orders: A, B, C and D, {E, F}, G). The two components share no node.
- `policy_source` of all seven edges is verbatim in the blocked policy's own `rule` and in none of the depended-on rules (mechanical check).
- `form: state` on all seven edges; no `fallback_reason` anywhere (correct, since none is action-form).
- `resolved_by` equals the depended-on policy's `target_tool` on all seven edges.
- `kind: value_input` on all seven edges; each `gate` names a binding that exists in the blocked policy's compute: C `plan_balance` (twice), E `addon_amount`, F `addon_amount`, G `plan_balance`, `fee_today`, `installments_left`. Each resolving write moves that binding: A and B raise C's `plan_balance`; D raises E's and F's `addon_amount` (and F's `addon_count`); D raises G's `plan_balance`/`addon_today`; F raises G's `fee_today`/`plan_balance`; E raises G's `term_months` and therefore `installments_left`.
- `condition` texts: none uses authoring-viewpoint phrasing ("in this task", "at the opening", "the current world"). C←B's condition ("Every billing_charge_posted row whose encounter_number matches an encounter already enrolled on the proposed plan has a payplan_balance_enrolled entry on the plan pointing at it") matches its sentence's scope; both are broader than B's own trigger, which covers only charges posted after the proposal date (O-8).

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength and scope), then the single write that brings the state about and the derivation a reader performs.

1. C ← A — "The signed installment is fixed only after the plan balance carries the setup-fee entry the tier owes at signing." Connective "only after". State: a setup-fee entry on the plan balance (ledger row with enrollment reason setup_fee). No tool, id or snake_case token ("setup-fee" is hyphenated prose). Scope "the tier owes at signing" = condition's "whenever the tier's setup_fee_usd is above 0.00". Writes that could create such an entry: A (at signing of a proposed plan) and F (on an active plan on an add-on day). On a plan being signed the plan is proposed and carries no add-on, so only A applies. Derivation: sentence → look for the rule that books a setup fee at signing → A's rule ("When the patient signs the installment agreement of a tier whose setup_fee_usd is above 0.00, the plan balance is charged the setup fee …") → A's target tool. One reading. PASS.
2. C ← B — "The signed installment is not fixed until the plan carries an enrollment entry for every charge the financial account posted for an encounter already enrolled on it." Connective "not … until". State: an enrollment entry per charge (plan ledger lookup by charge reference). No tool/id. Scope equals the condition (O-8 on B's narrower trigger). Writes: B (initial enrollment on a proposed plan) and D (add-on on an active plan). The plan being signed is proposed → only B. Derivation: sentence → the rule that enrolls a charge posted for an already-enrolled encounter on a proposed plan → B. One reading. PASS.
3. E ← D — "The extension granted with an add-on is not fixed until the plan carries the add-on enrollment entry it is granted for." Connective "not … until". State: the add-on enrollment entry (enrollment reason add_on). One write: D. PASS.
4. F ← D — "The add-on fee is not fixed until the plan carries the add-on enrollment entry it is charged for." Same analysis. PASS.
5. G ← D — "The re-spread installment is fixed only after the plan carries the add-on enrollment entry for the charge the patient asked to add." Connective "only after". One write: D. PASS.
6. G ← F — "The re-spread installment is not worked out until the plan balance carries the add-on fee entry owed for that add-on." Connective "not … until". State: "the add-on fee entry" — the ledger shows it as a setup_fee-reason entry with no charge reference dated the add-on day; the reader links the phrase to F's rule ("booked on the plan balance as one enrollment entry of reason setup_fee on the day the add-on is enrolled"). One write: F (A never books on an active plan). PASS.
7. G ← E — "The re-spread installment is fixed only after the plan's term shows the extension months the add-on earns." Connective "only after". State: the plan's term (term_months / term_extension_months_used). One write: E. PASS.

No rule carries a second wording of any of these dependencies, a tool name or another policy's id. No depended-on rule restates the sentence. Cross-problem statements that ground no declared edge: A's rule says the setup fee is "booked when the agreement is signed" / "booked on the signing date" (the occasion, not an order against C's write, and consistent with edge 1); A's size share reads "the charges enrolled on the plan (initial enrollments and add-ons …)", which B's write changes, with no order stated between A and B (O-7). No base rule sentence grounds any edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (F = follows; O = handled differently, and whether declared).

- A (setup fee), refs charge_eligibility, add_on_and_modification, enrollment_terms, agreement_and_activation:
  - enrollment_terms "The tier's setup_fee_usd, where above 0.00, is enrolled into the plan balance at signing and spread with the rest" — O, declared (replaced by the share product and returning-plan rule). Other enrollment_terms sentences (tier range, down payment, installment, apr, autopay required, due day, counselor, hardship tier) do not govern the setup-fee amount — F.
  - charge_eligibility "A billing charge is enrolled in a payment plan at most once" — declared (setup fee is not a billing charge; at most one setup-fee entry). "Each charge is enrolled at its remaining balance" — not a charge, F. "Balance is enrolled only while the plan status is proposed or active" — F. "total enrolled … never exceeds max" — the measure counts initial_enrollment and add_on only, F.
  - add_on_and_modification — no sentence governs the setup fee, F.
  - agreement_and_activation — signing is the patient's act; the fee is booked by the agent on the signing date — F.
- B (encounter charge), refs charge_eligibility, add_on_and_modification:
  - "Each charge is enrolled at its remaining balance on the enrollment date" — O, declared (counted amount, credited payments, relief, prompt-pay, late-posting product).
  - "Only billing charges that are patient responsibility after insurance adjudication may be enrolled …", "at most once", collections, "only while … proposed or active", max enrolled — F (inherited as eligibility).
  - "While a charge is enrolled in an active or delinquent plan it receives no statements, late fees, final notice or prompt-pay discount under the financial account rules" — F: it governs the billing-side prompt-pay adjustment of an enrolled charge, not the enrolled amount; B's prompt-pay rate is part of the declared replacement of the enrolled-amount sentence (O-6).
  - add_on_and_modification — B is enrollment on a proposed plan, not an add-on — F.
- C (signing installment), refs agreement_and_activation, enrollment_terms:
  - enrollment_terms down-payment sentence — O, declared. Installment sentence — O, declared (plan balance at signing, including the setup fee and later enrollments, instead of payplan_msr_enrolled_total). The setup-fee "spread with the rest" clause — C's plan balance includes the setup fee, consistent — F.
  - agreement_and_activation: signing is the patient's own act (tool owner=user) — F; validity window — F (inherited eligibility); "Any down payment is paid at signing as an extra payment of kind down_payment" — F (C repeats it; O-5); first-due-date sentence — F (inherited, supplies the sign tool's `first_due_date`).
- D (add-on amount), refs charge_eligibility, add_on_and_modification:
  - "Each charge is enrolled at its remaining balance" — O, declared (over-estimate, standing, deductible, prompt-pay, tenure rounding).
  - add_on_and_modification eligibility sentences (add_on_allowed, never delinquent, count below add_on_max_count, minimum add-on amount, installments remaining, max balance) — F (inherited). The no-prompt-pay-discount sentence — as for B (O-6).
- E (term extension), refs add_on_and_modification, hardship_plan_terms:
  - reamortize sentence — O, declared (term lengthened by earned months).
  - "Where term_extension_allowed is true the term may be lengthened by up to term_extension_max_months in total, re-spreading the remaining balance; the installment may never fall below min_installment_usd" — F (E caps at the room left; G re-spreads).
  - "Each change … counts toward max_plan_modifications" — F (tool increments modification_count).
  - hardship_plan_terms "Its add-ons restart the term" — not named in E's `overwrite`; E would lengthen a Financial Hardship Plan's term on an add-on while the base restarts it. No task of this difficulty is on the Financial Hardship Plan, so no consequence is demonstrable (O-10).
- F (add-on fee), refs charge_eligibility, add_on_and_modification, enrollment_terms:
  - enrollment_terms setup-fee sentence — O, declared (a fee at each add-on). Charge-eligibility and add-on sentences — F.
- G (add-on installment), refs add_on_and_modification, hardship_plan_terms, agreement_and_activation:
  - reamortize/restart sentence — O, declared (basis ladder). Min installment — F. "A plan is modified only while its status is active" — F. hardship_plan_terms "Its add-ons restart the term" — G's hardship tier spreads over a fresh full term_months — F. agreement_and_activation "accepting a payment obligation is the patient's own act" — F (accept tool owner=user).

Disguised forms: no anonymous intermediate factor, no 0/1 multiplier on a base-fixed amount and no dropped branch found. No undeclared override found.

### factor_ladders

Per policy (P = parameter, M = method; XD = cross_difficulty):

| policy | factors (label, decides) | P | M | XD factors (category) | multi-source factors |
| --- | --- | --- | --- | --- | --- |
| A | autopay_share_of_setup_fee (P, autopay_share); tenure_share_of_setup_fee (P, tenure_share); hardship_share_of_setup_fee (P, hardship_share); balance_size_share_of_setup_fee (P, size_share); returning_plan_rule_for_setup_fee (M, fee_entered) | 4 | 1 | 4 (billing) | autopay (plan autopay method ∧ billing late fees); hardship (approval % ∧ approval date) |
| B | estimate_cap_on_counted_amount (P, counted_amount); payment_clearing_method (M, credited_payments); hardship_relief_share_at_enrollment (P, relief_share); prompt_pay_rate_at_enrollment (P, prompt_rate); late_posting_share_at_enrollment (P, late_posting_share) | 4 | 1 | 4 (billing) | estimate cap (account class ∧ charge estimate); relief (account approval ∧ charge service date ∧ adjustment rows); prompt-pay (plan autopay method ∧ charge posting date) |
| C | down_payment_at_signing (P, down_payment); first_phase_of_signed_installment (M, first_phase); autopay_credit_on_signed_installment (P, autopay_credit); returning_plan_credit_on_signed_installment (P, returning_credit) | 3 | 1 | 4 (billing) | down payment (approval ∧ late-fee rows); autopay credit (plan method ∧ account statement delivery) |
| D | over_estimate_share_of_add_on (P, counted_amount); plan_standing_share_of_add_on (P, standing_share); deductible_exposure_share_of_add_on (P, deductible_share); add_on_prompt_pay_rate (P, addon_prompt_rate); tenure_rounding_of_add_on (M, rounded_amount) | 4 | 1 | 5 (billing) | over-estimate (class ∧ charge estimate); standing (plan installments ∧ billing late fees); prompt-pay (charge posting ∧ card on file) |
| E | add_on_share_rounding_of_extension (M, size_months); remaining_term_months_of_extension (P, left_months); plan_history_months_of_extension (P, history_months); plan_age_months_of_extension (P, age_months); automatic_debit_months_of_extension (P, autopay_months) | 4 | 1 | 2 (billing) | automatic-debit months (plan method ∧ installments paid) |
| F | add_on_number_share_of_fee (P); add_on_size_share_of_fee (P); debit_share_of_add_on_fee (P); late_fee_record_share_of_add_on_fee (P); class_rounding_of_add_on_fee (M) | 4 | 1 | 3 (billing) | debit share (plan autopay ∧ account card on file) |
| G | re_spread_basis_after_add_on (M, spread); class_credit_on_re_spread_installment (P); debit_credit_on_re_spread_installment (P); plan_age_credit_on_re_spread_installment (P) | 3 | 1 | 2 (billing) | debit credit (plan method ∧ card on file); basis tier 2 (add-on entry ∧ plan balance ∧ missed-installment rows) |

Structure checks:
- Counts: every policy declares 4–6 factors with ≥2 P and ≥1 M. Per task: task 0 (A, B, C) and task 1 (D, E, F, G) each carry several multi-source and several cross-difficulty factors.
- `decides` is an input binding, never `result`, on all 34 factors; binding sets within each policy are pairwise disjoint (checked per policy).
- Every ladder has exactly three tiers, the fall-through counted; the tiers as stated are pairwise disjoint (threshold ladders use at-least / but-fewer-than; categorical ladders use distinct classes or methods; the down-payment ladder separates "approval above 0.00 and current" / "0.00 approved" / everything else, an expired approval falling to the third).
- No two tiers of one ladder select the same value or method as written. B's prompt-pay ladder and D's add-on prompt-pay ladder select "the account's full prompt_pay_discount_pct" / "half of it" / 0, which coincide at 0 for the four classes whose prompt_pay_discount_pct is 0.00 (Medicaid Managed Care, Medicare Part B, Medicare Advantage; see billing.yaml lines 95, 203, 257) — O-11; neither task's account is on such a class.
- Every tier's condition and value/method is stated in prose in the rule (verified against each `ladder.when` and each rule sentence above) and implemented as a branch of the `decides` binding; no tier lives only in `compute` and no rule tier is missing from `compute`.
- Every fall-through tier equals the policy's `baseline` for that input, and each factor's `baseline` binding is what `baseline.rule` states: A fee 25.00 standard (shares 1, fee entered at the cent); B remaining balance with every payment credited, no cap, no share; C standard down payment and standard installment; D remaining balance at the cent; E add-on share rounded down, no extra months, clamped; F standard add-on fee at the cent; G balance over installments left.
- `baseline.rule` of every policy is self-sufficient (a definite number follows from it and the records with no factor), every sentence of it is a sentence of the rule, and its `params` name the keys it uses.
- Label honesty: `method` factors change the algorithm — returning-plan rule (halve-and-floor / scale-and-ceiling / cent), clearing (which payments are credited), first phase (graduated schedule with share and floor / level schedule), tenure rounding and class rounding (floor to dollar / floor to half dollar / half-up cent), add-on share rounding (ceiling / half-up / floor), re-spread basis (fresh term / stack / whole re-spread). `parameter` factors select a number. Two borderline labels, neither changing any count below its bound: the estimate cap (P) selects the cap by an additive formula on Self-Pay and a multiplicative one elsewhere; the first-phase factor (M) differs between its first two tiers only by the share — O-11.
- Business reality: every condition is one a physician-group payment-plan office plausibly weighs for that quantity (automatic-debit method and a clean late-fee record for fees and credits; account tenure; hardship approvals; balance and add-on size; estimates and the good-faith-estimate threshold; returned-payment history for crediting uncleared checks/ACH; posting lag; plan age and payment history), and every fall-through is the ordinary treatment (full fee, full remaining balance, standard down payment and level installment, whole-balance re-spread). One compound part is nearly universal: on the only tiers where F applies (setup_fee_usd above 0.00: 18-Month and 24-Month, both autopay_required), "the plan pays by automatic debit" holds for every plan except one whose autopay was removed after returned debits; the dividing condition is the card on file. Same shape for A's autopay share, where the dividing condition is the debit method and the late-fee record — O-11.

### findings

No charter-global RED. Observations, each naming the tasks it bears on:

- O-1 (tasks 0, 1; both carry it): B's and D's rules each state the ordinary case as a flat definition ("The enrolled amount of such a charge is its remaining balance on the enrollment date …" / "The add-on amount of a charge is its remaining balance …") and later redefine the amount by the "worked out in this order" sentence. A, C, E, F and G label their ordinary case "standard". The ordering sentence is explicit and later, so a careful reader gets one result. No second defensible number shown.
- O-2 (task 1): terminology overlap. A's rule: "a plan carries at most one setup-fee entry, booked when the agreement is signed"; F's rule books the add-on fee "as one enrollment entry of reason setup_fee". If "setup-fee entry" were read as "any entry of reason setup_fee", A would bar F on every plan F applies to (every tier with setup_fee_usd above 0.00 already carries its signing setup-fee entry), leaving F empty everywhere. A reading that voids a whole policy is not defensible, so no second answer. Consequence checked in 1.md.
- O-3 (task 0): B's charge selector `XLATEST` over the whole account does not implement the rule's filter (posted after the proposal date, for an encounter already enrolled on a proposed plan, still unenrolled). On a world where a later unrelated charge (e.g. a late fee) posted after the encounter charge, compute and rule would pick different charges. Consequence checked in 0.md.
- O-4 (both): the DSL's `RND` is `round(float, 2)` (half-even on binary floats) while every rule says "rounded half up". They differ only on exact binary ties (e.g. 833.625). Whether any gold-path value is such a tie is checked per task.
- O-5 (task 0): C's rule and base agreement_and_activation require "Any down payment above 0.00 is paid at signing as an extra payment of kind down_payment", but this difficulty's tool module has no extra-payment write and share_tools.py has none either. A signing whose down payment is above 0.00 has no tool for that obligation. Consequence checked in 0.md.
- O-6 (tasks 0, 1): base charge_eligibility "While a charge is enrolled in an active or delinquent plan it receives no … prompt-pay discount under the financial account rules" sits beside B's and D's prompt-pay rate on the enrolled amount. It governs the billing-side adjustment, not the enrolled amount (which is declared as replaced), so no override is undeclared. Recorded because a reader could conflate the two.
- O-7 (task 0): A's balance-size share reads the plan's enrolled charges, which B's write changes, and no rule orders A against B (both are prerequisites of C; no edge between them). Parallel-edge terminal states checked in 0.md.
- O-8 (task 0): C←B's sentence and condition cover "every charge … posted for an encounter already enrolled", while B's rule covers only charges posted after the proposal date. A pre-proposal charge of an enrolled encounter left out at proposal would keep C's gate open with no policy to close it. Checked against task 0's world in 0.md.
- O-9 (tasks 0, 1): two docstrings name another problem's occasion without an ordering word (setup fee: "when the patient signs the installment agreement"; add-on fee: "for an add-on accepted on the plan today").
- O-10 (none of the M tasks): E lengthens the term on an add-on for every tier whose term_extension_allowed is true, including the Financial Hardship Plan, where base hardship_plan_terms says "Its add-ons restart the term" and G's hardship tier spreads over the tier's fresh term_months regardless of the extension. That base sentence is not in E's `overwrite`. No task is on the Financial Hardship Plan, so no consequence is demonstrable.
- O-11 (both): ladder-shape notes (prompt-pay tiers coincide at 0 on zero-discount classes; two borderline effect labels; the nearly universal "pays by automatic debit" part on the 18/24-Month tiers). None changes any count below its bound, and neither task's world sits where these bite.

## closing_checklist

Written after both reveals. Nothing above this heading was changed after any reveal: the section's sha256 was `88926a6df546ec9a470e07cb4e5a53b8156473659f7e57bc0b76ece2ce3d0868` at 2026-09-25T00:10:50Z, before the first GT read.

**The difficulty does not close.** Task 1 carries a SOURCE-CHAIN RED (`1.md` § findings, T1-R1), and Step 4 requires every task to PASS on all four relationships.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside | yes: `0.md`, `1.md`, `_difficulty.md`; revision r1, no earlier revision |
| every comparison section carries a PASS | no: task 0 PASS; task 1 SOURCE-CHAIN RED (T1-R1) |
| extended policies fully covered; scopes pairwise disjoint | yes: `charter_scope` task 0 = {B, A, C}, task 1 = {D, E, F, G}; the union is all seven policies and all seven tools |
| task tools and GT closed; uuid8 per tool independent and frozen | yes (§ action_binding_and_uuids); every gold write uses exactly one claimed tool |
| every tree: 1–3 prerequisite problems, ≥ max(n − 1, 1) value_input edges, an owner=user write, no cycle; the whole-difficulty graph a DAG | yes structurally (task 0: n = 2, 2 value_input, user write C; task 1: n = 3, 3 value_input into the root, user write G; two disjoint acyclic components). Task 1's tree is not raised from its root by the customer (T1-R1) |
| every computation: self-sufficient baseline, 4–6 factors (≥2 P, ≥1 M), per task ≥1 multi-source and ≥1 cross-difficulty, ladders of three distinct real tiers stated in the rule, every factor bearing weight, the baseline alone giving a definite number ≠ gold | yes for all seven computations (task 0: 7.00 vs 25.00, 416.81 vs 1060.00, 209.00 vs 202.32; task 1: 1802.50 vs 2230.00, 6 vs 1, 7.00 vs 25.00, 288.33 vs 227.05) |
| instantiation-stage gates re-run once on the final form | not run: the difficulty does not close, and the auditor cites the coordinator's snapshot (§ charter_global_frozen) rather than running gates |

Per-task verdicts:
- task 0: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-FACTOR PASS · SOURCE-TASK PASS → **PASS**
- task 1: SOURCE-POLICY PASS · **SOURCE-CHAIN RED** (T1-R1: the persona's ask names prerequisite D) · SOURCE-FACTOR PASS · SOURCE-TASK PASS → **SOURCE-CHAIN RED**

Charter-global observations O-1 … O-11 stand as recorded above. None is a red light on either task's world.

---

## revision_2

Re-audit, round 2. Everything above this line is revision 1 and stays as written. This revision was written at 2026-09-25T04:07Z (UTC), before either revised task JSON was opened.

### charter_global_frozen (r2)

- Charter hash is now `8bc3659dc6fa9eb67b0ac4916e8044971f1205e327cd0cf99938281e06e2b94a` (r1: `214c7fff…adfaebf6`). Tool module hash is now `a259bc5ea95a1318b00de1b91181fa408ca3a50645b93d6713a9f9a2dab4b9ff` (r1: `a56b1dfd…32c5ee28c`). Both match the coordinator's brief. Both changed, so every charter-global section below is re-derived in full; nothing is carried forward by reference.
- Method:
  - I rebuilt the r1 charter byte-exactly from this session's saved read of it (sha256 of the rebuilt copy = the r1 hash `214c7fff…`) and diffed it against the r2 charter. The diff is 230 lines, all inside `extended_policies`.
  - I re-read every changed passage in full and re-read the whole tool module.
  - The mechanical sweep (compute_basis verbatim in the rule; compute_basis keys equal to compute keys; baseline.rule sentences in the rule; overwrite clauses verbatim in base and replaced_by verbatim in the rule; prerequisite sources verbatim in the own rule and absent from the depended-on rule; resolved_by equals target_tool; gate names an existing binding; `decides` is a binding other than `result`) was run again on r2. All checks hold.
- Base section: lines 5–1003 of the r2 charter against lines 4–1002 of `blueprint/products/payplan.yaml` give an empty diff, so the base copy is verbatim.
- Unchanged inputs, re-hashed: `blueprint/products/payplan.yaml` `04e8d231…`, `billing.yaml` `76562f04…`, `share_tools.py` `a0a0f97c…`, `db_schema.json` `8c0093f9…`.
- Entry conditions: the brief supplies a gate snapshot after rework (all seven gates OK; traceability deferred to KB publication), the r2 views (`r2/0.view.json` `e5398d91…`, `r2/1.view.json` `5456335c…`, both re-hashed and matching), and both charter hashes. The entry conditions are met.
- Masked at the time of writing: the r2 `tasks/0.json` and `tasks/1.json`, the worklog (never opened), and other audit directories. Both r1 task JSONs had been read during revision 1; see the per-task contamination disclosures.

### what changed in the charter (r1 → r2)

| policy | change |
| --- | --- |
| A setup fee | "a plan carries at most one setup-fee entry" becomes "at most one signing setup-fee entry, booked when the agreement is signed; any add-on fee an active plan carries later is a separate entry" (in both the rule and `overwrite.replaced_by`) |
| B encounter charge | Trigger scope: "a charge the financial account posts, after the proposal date, for an encounter already enrolled on a proposed plan" becomes "a charge … for an encounter already enrolled on a proposed plan, and not yet on that plan". The ordinary case is relabelled "The standard enrolled amount …". The final rounding gains "(an amount exactly halfway between two cents goes to the higher cent)", and `result` becomes `RND(… + 0.000001, 2)`. The charge selector `charge_id … XLATEST(… event_type='billing_charge_posted')` is **unchanged**. |
| D add-on amount | Trigger changes from on_request to state_due. The rule changes from "a new eligible charge the patient asks to add … the most recently posted charge of the financial account being the one added" to "an active plan carries every eligible charge of the encounters enrolled on it: a charge the financial account posts for an encounter the plan enrolled at its proposal, and not yet on the plan, is added to it as an add-on …; the charge added is the most recently posted charge of that encounter, the encounter being the one whose charge the plan most recently enrolled at its proposal". The selector is re-implemented through `enrolled_encounter`. "standard add-on amount" label added. |
| E term extension | Trigger on_request → state_due. The Financial Hardship Plan is excluded ("On the Financial Hardship Plan an add-on restarts the term instead and earns no extension"), implemented as `hardship_tier` → result 0. |
| F add-on fee | Trigger on_request → state_due; "every add-on accepted" becomes "every add-on booked". |
| G re-spread installment | Opening sentence: "A re-spread of the installment of an active plan, whether the patient asks for it or it follows an add-on, changes the patient's payment obligation …". Prerequisite sentence to D: "… fixed only after the plan carries an enrollment entry for every charge the financial account posted for an encounter the plan enrolled at its proposal." Prerequisite sentence to F: "… the add-on fee entry owed for every add-on booked on the handling date." The stack tier (stack_ratio) becomes a split tier: "when an add-on is booked on the handling date and the plan shows no missed installment, the plan balance standing before that add-on is re-spread over the installments left and the add-on together with its add-on fee is spread over the tier's full term_months, the two spreads being added". stack_ratio is removed. |
| C signing installment | unchanged |
| tool module | Docstrings only: the setup-fee tool is "one-time signing setup fee … as one fee entry of the plan's ledger" (no "when the patient signs"); the add-on fee tool is "Book an add-on fee of an active payment plan …" (no "for an add-on accepted … today"); the accept tool now reads "a re-spread monthly installment". Function names, uuid8s and bodies are unchanged (re-read in full). |

### policy_conflict_scan (r2)

The seven policies, their target tools and computes are as in r1. Triggers are now A on_request, B state_due, C on_request, D state_due, E state_due, F state_due, G on_request. Scope division per the unchanged charter header: task 0 = {A, B, C}, task 1 = {D, E, F, G}. The scopes are disjoint and together complete.

Overlaps re-checked:
- `payplan_balance_enrolled`: A books at signing on a proposed plan. B books on a proposed plan for a charge of an enrolled encounter not yet on it. D books on an active plan for a charge of an encounter enrolled at proposal, not yet on it. F books on an active plan on an add-on day. B and D now share the same trigger shape and are separated only by plan status (proposed vs active). They never apply to one plan at one time.
- A's and F's clauses no longer conflict: A's dedup covers only the signing entry and explicitly calls a later add-on fee "a separate entry". This closes r1 O-2.
- E and G on the Financial Hardship Plan: E yields 0 and says "an add-on restarts the term instead". G's hardship tier spreads over the tier's fresh term_months. Base `hardship_plan_terms` says "Its add-ons restart the term". The three now agree. This closes r1 O-10.
- G's opening sentence adds a patient-requested re-spread with no add-on. That case falls to G's third tier ("in every other case the plan balance is re-spread over the installments left"), so one reading.
- Base `add_on_and_modification` still says "Where term_extension_allowed is true the term may be lengthened by up to term_extension_max_months in total, re-spreading the remaining balance" (a permissive, on-request extension; the parameter_schema says "Whether the term may be lengthened on request"). E's `overwrite` replaces only the reamortize sentence, so the on-request extension survives beside E's add-on-earned extension. No extended policy computes the months of an on-request extension. See r2 finding O-12.

No conflict yields two conclusions in one situation on the charter's face.

### rule_compute_equivalence (r2)

A and C are unchanged from r1 except A's dedup sentence (no compute binding) and stay equivalent. For the changed policies:

- B: equivalent in amount. The added parenthetical fixes "half up" at exact ties and `+ 0.000001` implements it in `result` (e.g. 833.625 now rounds to 833.63, 463.125 to 463.13). The r1 selector gap (O-3) is **still open**: the rule's filter "for an encounter already enrolled on a proposed plan, and not yet on that plan … the most recently posted one" has no implementation. `charge_id` is still the latest charge of the whole account, with no encounter and no not-yet-enrolled filter. Only the rule wording changed.
- D: the new selector is implemented. `enrolled_encounter` (the encounter of the latest initial-enrollment charge) comes from "the encounter being the one whose charge the plan most recently enrolled at its proposal". `charge_id` (the latest charge of that encounter) comes from "the charge added is the most recently posted charge of that encounter". The rule's "and not yet on the plan" is a condition on whether the obligation exists, not on which charge is chosen. If the latest charge of the encounter were already enrolled, the compute would still select it, but then no write is due. No empty promise.
- E: `hardship_tier` → 0 is quoted verbatim ("On the Financial Hardship Plan an add-on restarts the term instead and earns no extension."). Equivalent.
- F: the wording change touches no binding. Equivalent.
- G: the split tier is quoted and implemented as `RND(RND((plan_balance − addon_today − fee_today) / installments_left, 2) + RND((addon_today + fee_today) / P('term_months'), 2), 2)`. The condition is `addon_today > 0 ∧ missed_installments == 0`, from "when an add-on is booked on the handling date and the plan shows no missed installment". "The tier's full term_months" maps to `P('term_months')` (the tier parameter, not the plan's extended term). "Each spread is rounded half up" maps to the inner RNDs. Equivalent.
- Rounding primitive: outside B's result, `RND` is still Python `round` (half-even on exact binary ties) while every rule says "rounded half up" (O-4 is narrowed to the other policies; per-task gold paths are checked for ties).

### action_binding_and_uuids (r2)

Seven distinct `(target_tool, computes)` pairs, as in r1. uuid8s 08ffaf93, 372696d1, b4bb7ade, 102110ed, 6d1d2771, 792da8e6, 27cdd630 are unchanged, independent and unreused. Tool bodies are unchanged: one write each, no eligibility check, no prerequisite check, no amount computed. Owners: `sign_installment_agreement_b4bb7ade` and `accept_add_on_installment_27cdd630` are user; the rest are agent. Docstrings: a grep for before/after/first/then/until/prior finds none used as an ordering word. The two r1 occasion phrases are gone, so r1 O-9 is closed. The accept tool keeps "add_on" in its name while its docstring now covers any re-spread. That is naming only, not a second reading.

### prerequisite_graph (r2)

Unchanged in shape: A `[]`, B `[]`, C → {A, B}, D `[]`, E → {D}, F → {D}, G → {D, F, E}. Two disjoint acyclic components. All seven edges are `form: state` with no `fallback_reason`, `kind: value_input`, `resolved_by` equal to the depended-on target_tool, gates existing bindings (C plan_balance ×2, E addon_amount, F addon_amount, G plan_balance / fee_today / installments_left), and `policy_source` verbatim in the own rule and absent from the depended-on rule. The G←D condition was rewritten to "Every billing_charge_posted row of an encounter enrolled on the plan at its proposal has a payplan_balance_enrolled entry on the plan pointing at it (the later-posted ones as add_on entries)", which matches its sentence's scope. The G←F condition is now "For every add_on entry dated the handling date …", which matches "every add-on booked on the handling date". No authoring-viewpoint phrasing.

### prerequisite_sentences (r2)

- C←A, C←B, E←D, F←D: the same sentences as r1 and the same verdicts (r1 § prerequisite_sentences, items 1–4). For C←B, B's trigger now has the same scope as the sentence ("… and not yet on that plan", with no proposal-date restriction), so r1 O-8 is closed.
- G←D (new sentence): "The re-spread installment is fixed only after the plan carries an enrollment entry for every charge the financial account posted for an encounter the plan enrolled at its proposal." Connective "only after". State: an enrollment entry per charge of each encounter enrolled at proposal (plan ledger by charge reference). No tool or id. Scope equals the condition. Writes that bring it about: B works only on a proposed plan; D works on an active plan. G acts on an active plan, so only D. One reading.
- G←F (new wording): "The re-spread installment is not worked out until the plan balance carries the add-on fee entry owed for every add-on booked on the handling date." Connective "not … until". The write is F (A books only at signing). One reading.
- G←E: unchanged sentence; the write is E.
- The G←D sentence is written about encounters, not about a customer's ask. The customer is no longer the only source of that hop (bears on r1 T1-R1; verified per task).
- No rule carries a second wording, a tool name or another policy's id. No depended-on rule restates a sentence.

### override_declarations (r2)

Sentence-by-sentence conclusions are as in r1 (§ override_declarations), with these updates:
- A: the replaced_by on charge_eligibility now reads "at most one signing setup-fee entry …; any add-on fee an active plan carries later is a separate entry", which is the same text as the rule.
- B: the replaced_by carries the tie parenthetical, equal to the rule. The trigger change is not an override (the base has no sentence restricting later charges of an enrolled encounter).
- D: the base add_on_and_modification sentence "Where add_on_allowed is true, new eligible charges may be added to an active plan …" is permissive. D makes the later charges of an encounter enrolled at proposal due on an active plan. The base eligibility gates (not delinquent, count below add_on_max_count, minimum add-on amount, installments remaining, max balance) are inherited. This does not contradict "may", and the enrolled-amount sentence override is declared.
- E: the replaced_by now excludes the hardship tier. The base hardship_plan_terms "Its add-ons restart the term" is now followed (r1 O-10 closed).
- G: the replaced_by now carries the split tier, equal to the rule. Base agreement_and_activation "accepting a payment obligation is the patient's own act" is followed (owner user). The base on-request term extension is not overridden by E or G (O-12).
- No undeclared override found.

### factor_ladders (r2)

Factor sets, labels, `decides` bindings and binding disjointness are unchanged for A–F (r1 § factor_ladders).
- G's `re_spread_basis_after_add_on` (M) now reads: hardship tier (fresh full term) / "an add-on is booked on the handling date and the plan shows no missed installment" → split / otherwise → whole re-spread. The three methods are distinct algorithms. The split is a genuine installment-plan practice (a new balance scheduled over its own term alongside the existing schedule). The fall-through equals the baseline (`RND(plan_balance / installments_left, 2)`), and the rule states every tier.
- Counts: A 5 (4P/1M), B 5 (4P/1M), C 4 (3P/1M), D 5 (4P/1M), E 5 (4P/1M), F 5 (4P/1M), G 4 (3P/1M). Each task still has multi-source and cross-difficulty (billing) factors.
- r1 O-11 notes stand unchanged (prompt-pay tiers coincide at 0 on zero-discount classes; two borderline labels; the nearly universal "pays by automatic debit" part on 18/24-Month tiers).

### findings (r2)

No charter-global RED.

Status of every r1 item on the charter's face (the per-task consequences are checked in `0.md` / `1.md` revision_2):

| r1 item | reworker claim | auditor verdict (r2) |
| --- | --- | --- |
| O-1 flat definitions in B and D | changed | closed: both are labelled "standard" |
| O-2 setup-fee entry vs add-on fee entry | changed | closed: A's text now names the signing entry only and calls the add-on fee a separate entry |
| O-3 B selector | changed | **not closed**: only B's rule wording changed; `charge_id` is still `XLATEST` over the whole account without encounter or not-enrolled filter. Remains an observation (consequence checked on task 0's world). |
| O-4 RND half-even vs "half up" | changed | partly closed: B's result is nudged and its rule defines the tie. Every other `RND` in A, C, D, E, F, G is still half-even on exact binary ties while the rules say "half up". Remains an observation; gold paths are checked per task. |
| O-5 no extra-payment tool | unchanged | still an observation (no extra-payment tool in either module). |
| O-6 base no-prompt-pay-discount sentence | unchanged | still an observation, reasoning as in r1. |
| O-7 A/B order not pinned | unchanged | still an observation; commute checked on task 0's world. |
| O-8 C←B sentence broader than B's trigger | changed | closed: B's trigger now covers every not-yet-enrolled charge of an enrolled encounter. |
| O-9 docstring occasion phrases | changed | closed. |
| O-10 E on the Financial Hardship Plan | changed | closed. |
| O-11 ladder-shape notes | unchanged | still an observation. |

New in r2:
- O-12 (bears on task 1). The base on-request term extension survives beside E. Base `payplan_add_on_and_modification`: "Where term_extension_allowed is true the term may be lengthened by up to term_extension_max_months in total, re-spreading the remaining balance". E's override replaces only the reamortize sentence, and no extended policy fixes how many months an on-request extension takes. A customer who asks for a lower installment could be offered a discretionary extension of any size up to the room left. Whether this opens a second solution depends on what the customer requests; judged in `1.md` revision_2.
- O-13 (bears on task 1). D's selector has a latent edge case: when a plan enrolled several encounters on the same proposal date, "the encounter being the one whose charge the plan most recently enrolled at its proposal" ties, and `LATEST` keeps the first row among equal dates. Checked on task 1's world (single initial enrollment).

### closing_checklist (r2)

Written after both r2 reveals. The r2 charter-global section above was hashed as part of `_difficulty.md` (`9740b510…a6aff6a26`) at 2026-09-25T04:09:26Z, before any r2 GT read. Nothing derived from a revealed GT was written into it.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside, old revisions traceable | yes: `0.md`, `1.md`, `_difficulty.md`; revision 1 text untouched above each `## revision_2` |
| every comparison section carries a PASS | yes (r2): task 0 PASS, task 1 PASS |
| extended policies fully covered; scopes pairwise disjoint over the whole tree | yes: task 0 {B, A, C}, task 1 {D, E, F, G}; the union is all seven policies and all seven tools |
| task tools and GT closed; uuid8s independent and frozen | yes (unchanged since r1) |
| every tree: 1–3 prerequisite problems, ≥ max(n − 1, 1) value_input edges, an owner=user write, no cycle; the whole-difficulty graph a DAG | yes: task 0 n = 2 (2 value_input, user write C); task 1 n = 3 (3 value_input into the root, user write G); two disjoint acyclic components; each customer raises only the root |
| every computation: self-sufficient baseline, 4–6 factors (≥2 P, ≥1 M), per task ≥1 multi-source and ≥1 cross-difficulty, three distinct real tiers stated in the rule, every factor bearing weight, the baseline alone ≠ gold | yes: task 0 7.00 vs 25.00, 416.81 vs 1060.00, 209.00 vs 202.32; task 1 777.50 vs 960.00, 5 vs 0, 5.00 vs 25.00, 167.11 vs 177.05; all 33 factors bear weight |
| instantiation-stage gates re-run once on the final form | yes, by the auditor between 04:09Z and 04:12Z on 2026-09-25 (UTC) on charter `8bc3659d…` and tools `a259bc5e…`: check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks `--check` REPLAY OK (the `--check` flag disables its write-back; a before/after hash of every audited artifact is unchanged); check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK. check_traceability is deferred to KB publication, as in the brief. |

Round-1 RED status: **T1-R1 closed** (verified on the r2 persona, world and charter). No regression: task 0's r2 results equal r1's figure for figure, and its two r1 observations are closed.

Observations still open (none a red light):
- O-3: B's selector is still whole-account.
- O-4: half-even `RND` outside B.
- O-5: no extra-payment tool.
- O-6: the base no-prompt-pay-discount sentence.
- O-7: A and B are unordered (they commute on task 0).
- O-11: ladder-shape notes.
- O-12 (new): the base on-request term extension survives beside E; see task 1's T1-O3.
- O-13 (new, latent): D's encounter tie on a same-date multi-encounter proposal.

Per-task verdicts (r2):
- task 0: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-FACTOR PASS · SOURCE-TASK PASS → **PASS**
- task 1: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-FACTOR PASS · SOURCE-TASK PASS → **PASS**

**The difficulty passes the source-layer audit at revision 2.**
