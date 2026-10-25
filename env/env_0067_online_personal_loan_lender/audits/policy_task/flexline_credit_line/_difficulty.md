# Policy-task audit — flexline_credit_line / charter-global

## charter_global_frozen

- frozen 2026-10-16T05:05Z, before any GT field of either task was read. Built from the charter, schema, tool contracts and masked views only.
- `tasks/flexline_credit_line/line.extended.yaml` sha256 `6276d3da750c68f14633830ddfe0caea2cfc517ab14a05b9e2d3b77c47799aff`; `tasks/flexline_credit_line/task_tools.py` sha256 `472f04c3b6b16592d195f8c25e437d8edf2d2761feff30dd01771abe2199978c`.
- auditor: independent policy-task auditor.
- permitted: blueprint (line.yaml, loan.yaml fee schedule), extended charter, task_tools.py, masked views (frozen_time, user_scenario, initial_state), gate snapshot, XF_recipe.md.
- masked: every task field other than those three, worklog.md and plan.md.
- Entry conditions: the gate snapshot came with the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK pre-publication, unlock-tool-name misses only). Masked views are present and their hashes match the brief. Input is complete.
- Base copy: lines 1–1173 of the extended file are diff-identical to `blueprint/products/line.yaml` (the only diff is the trailing section comment).

Policy shorthand used in all three files:

| shorthand | policy |
|---|---|
| C | `line_ext_close_to_draws_payment` |
| R | `line_ext_returned_payment_fee` |
| D | `line_ext_draw_fee` |
| E | `line_ext_draw_fee_error_credit` |
| LD | `line_ext_largest_draw` |
| PD | `line_ext_past_due_payment` |
| LF | `line_ext_late_fee` |
| W | `line_ext_late_fee_error_waiver` |

### policy_conflict_scan

- Subjects and tools: the eight extended policies have eight distinct `(target_tool, computes)` pairs. D and LD both take a base ref of `line_evt_draws` but retire different clauses (D: the draw-fee clause and the active-status clause for fee booking; LD: the draw-limit clause for maximal draws). E and W both retire the same `line_evt_fee_waiver` clause. Each excludes the other's case by name: E "(a late or returned-payment fee charged in error is not covered by this paragraph)"; W "(a draw fee charged in error is not covered by this paragraph)".
- Eligibility / state: C's subject `line_closed_to_draws` has base mutation `{from: active, to: repayment}`, and lifecycle allows only `active → repayment, by: user`. Base rule `line_evt_draw_period_and_closure` says "A borrower may close the line at any time". Neither the base nor C says how a `frozen` line is handled → **CG-1**.
- Terminal state of C's payment vs base repayment-payment sentences → **CG-2**.
- The "missed due dates" quantity in PD, LD and LF nets out all lender-error waivers, including E's draw-fee waivers → **CG-12**.
- Cross-category reads: every loan read (status, amount_past_due, loan_transactions event/payment_type/payment_channel/principal_portion/txn_date) is declared in each policy's `cross_category.reads`. None is written.
- Scope exclusivity (as derived; charter_scope not yet compared): task 0 claims {C, R, D, E}, task 1 claims {LD, PD, LF, W}. The two are disjoint and together cover all eight policies. The prerequisite graph has two components with no cross-task edge.

### rule_compute_equivalence

- Scratch sweep (`yaml` load, whitespace-normalised substring test):
  - every `compute_basis` quote of all eight policies is a substring of its own rule (0 misses);
  - every `baseline.rule` sentence is in the rule (0 misses);
  - every `replaced_by` is restated in the rule (0 misses);
  - every factor's `decides` and `bindings` is a compute binding name.
- Sweep back, rule → compute: each tier sentence of each ladder is a branch of its `decides` binding and vice versa (eight policies, 40 factors, checked by hand). Rounding sentences match RND placement:
  - C rounds once at the end (accrued interest rounded in its own sentence);
  - R, D, LF round the figured fee and the result;
  - E and W round each component and the sum;
  - LD floors (`int`) "rounded down to the whole dollar";
  - PD rounds the paydown and the result.
- Rule / compute divergence (XF-8, negative edge): LF's `first_miss_share` compute tests `earlier_late_fees_12m - earlier_error_waivers_12m == 0` for the "no earlier missed due date" tiers. A line with lender-error waivers (for example from E) and fewer late fees gives a negative count. The compute then falls to `full_share`, while the rule ("with no earlier missed due date") gives a first-miss tier → part of **CG-12**.
- Observation (C): the accrued-interest sentence uses "the APR" while the assembly sentence defines "the APR used" first. Compute takes `F('line_apr')`. Elsewhere in this charter "the APR" always means the line's APR, so this is recorded as an observation, not a second reading.

### action_binding_and_uuids

- Tool suffixes: `close_line_to_draws_7539d675`, `assess_returned_payment_fee_0fd8e99d`, `assess_draw_fee_4f046c6c`, `credit_draw_fee_error_e1e6ecd0`, `post_line_draw_ce97e56d`, `pay_past_due_amount_8ea5bc66`, `assess_late_fee_ba469c06`, `waive_fee_charged_in_error_c67a36f8`. All eight uuid8s are distinct, share no prefix or tail pattern, and show no sequence. Each is used by exactly one policy.
- Docstrings:
  - none names another tool or carries a sequencing word relative to other actions (grep for before/after/first/then/until/prior/once/later hits only "after the payment/credit/waiver" in return-value descriptions and "once it reaches 0.00" describing the tool's own effect);
  - no concrete example values;
  - each claimed effect matches its body. In particular, `pay_past_due_amount` lowers `minimum_payment_due` and moves `next_due_date` one month once past due reaches 0, and `post_line_draw` "no draw fee is booked by this action" matches its body.
- No body checks a status, a freeze, a past-due amount or a prerequisite.
- Runtime (XF-13): `from erlbench import ToolContext, tool` is the only import. Date maths sit in the `_DueDates` static method. Every write tool calls `ctx.create`/`ctx.update`. frozen_time formats are `2026-10-16 11:20:00 MST` and `2026-10-16 14:05:00 CDT`.
- XF-10: no factor id is a substring of any tool name (scripted check).

### prerequisite_graph

| blocked | problem | kind | gate (exists in compute) | form | resolved_by = target_tool | acyclic |
|---|---|---|---|---|---|---|
| C | R | value_input | conversion_balance ✓ | state | ✓ | ✓ |
| C | D | value_input | conversion_balance ✓ | state | ✓ | ✓ |
| C | E | value_input | conversion_balance ✓ | state | ✓ | ✓ |
| D | E | value_input | back_billing_relief ✓ | state | ✓ | ✓ |
| LD | PD | value_input | draw_balance ✓ | state | ✓ | ✓ |
| PD | LF | value_input | missed_date_late_fee ✓ | state | ✓ | ✓ |
| LF | W | value_input | first_miss_share ✓ | state | ✓ | ✓ |

- R, E and W have `prerequisite: []`. Every `policy_source` is verbatim in its own blocked rule (scripted). No `fallback_reason` is needed (all state form). No authoring-viewpoint wording.
- Observations: three conditions differ in strength from their sentences, with no consequence on either task world:
  - LF←W condition "a line_payment_posted entry of at least the minimum payment" is single-entry; the sentence "had posted in full" is cumulative. They diverge on task 1, where the 2026-08-28 minimum 487.02 was paid by two entries.
  - C←E and D←E conditions require `waiver_reason lender_error`; the sentences say "a fee-waiver entry".
  - PD←LF condition is limited to "the due date in next_due_date"; the sentence covers "every due date".

### prerequisite_sentences

All seven sentences pass the four-point test:
- each has an ordering connective ("only after", "not until", "Before", "not … until");
- each names its state in table words: returned-payment fee entry, draw-fee entry, fee-waiver entry, amount past due 0.00, late-fee entry, fee-waiver entry for a Larkspur error;
- no tool, policy id, snake_case token or row id appears;
- each has closed scope (every / each / any draw …).

For each state there is exactly one write of this difficulty that brings it about:
- returned-fee entry → R;
- draw-fee entry → D;
- fee-waiver entry on an extra draw-fee entry → E (W is scoped to late fees);
- amount past due 0.00 → PD (the only payment write);
- late-fee entry → LF;
- lender-error waiver on a late fee → W (E is scoped to draw fees).

No depended-on rule restates the sentence that waits on it, and no rule states a cross-problem order outside these edges. The derivation sentence + records + depended-on rule → resolving action is written out per task in `0.md`/`1.md` § problem_chain.

### override_declarations

Sentence-by-sentence over every `base_policy_refs` entry:

- **C** (refs `line_evt_draw_period_and_closure`, `line_evt_interest_and_annual_fee`, `line_evt_payments_and_fees`). The declared overwrite retires "When the draw period ends the line moves to repayment and the balance is repaid in level payments over the tier's repayment period at the APR in force." That sentence governs draw-period end, a case C does not handle, and the `replaced_by` restates it unchanged for that case, so it retires a clause that never conflicted (XF-4). The sentences that do govern C's quantity are left in force and undeclared:
  - `line_evt_payments_and_fees` "in repayment it is the level repayment payment plus any amount past due";
  - variant parameter `repayment_payment_method` "level payment amortizing the balance … at the APR in force, recalculated when the APR changes";
  - event `line_closed_to_draws` field "minimum_payment_due: Level repayment-period payment.";
  - `line_evt_interest_and_annual_fee` "while AutoPay is active the APR is lowered by the tier's AutoPay discount" — C's `return_addon` tier 2 adds that discount back while AutoPay stays active.

  Together these are **CG-2**. The other sentences of the three refs are followed: interest at statement closing, the annual fee, payment allocation, the late-fee grace.
- **R**: the declared overwrite of the returned-fee sentence is scoped to the most recent return. The base trigger maps the fee's `txn_date` to the return date, while R dates the fee on booking; the overwrite's "added to the outstanding balance on the date it is booked" covers this. Other sentences are followed.
- **D**: two declared overwrites, the draw-fee sentence (scoped to the most recent draw) and the active-status clause for fee booking. The base `formula.draw_fee` is likewise superseded. OK.
- **E** and **W**: the sibling overwrite of the error-waiver clause is properly cross-excluded. "A fee may be waived once" is followed. The base event `line_fee_waived` ("A … fee is waived", amount "Amount waived") is departed from in amount → see **CG-6** (realism; the overwrite does declare that the error is "put right with the credit this paragraph sets").
- **LD**: the declared overwrite of the draw-limit sentence is scoped to maximal draws. "Draws are allowed only while the line is in active status" and the verified-account eligibility are inherited and followed.
- **PD**: `overwrite: []`. No base sentence fixes the amount of a voluntary payment, so there is no undeclared override in the narrow sense. The realism of its cure amount is **CG-9**.
- **LF**: the declared universal replacement of the flat late fee (and of `formula.late_fee`'s cap, now "unpaid minimum payment") is OK.

### factor_ladders

Per policy (label counts are as declared): factors, `parameter`, `method`, cross_difficulty. Every ladder has 3 stated tiers, disjoint as written, fall-through = baseline, every tier stated in the rule and implemented in compute. Bindings are disjoint within each policy. No factor reads another factor's binding (XF-1, checked transitively; plain bindings `conversion_balance`, `latest_return_amount`, `drawn_amount`, `extra_fee_amount`, `draw_balance` and similar are read by several factors and are not factors).

| policy | factors | param | method | cross | multi-source factors |
|---|---|---|---|---|---|
| C | 6 | 4 | 2 | affordability_extension, relationship_reduction | affordability, relationship, return_addon (tier 2), payment method, accrued interest |
| R | 4 | 3 | 1 | loan_relationship_credit | first_return_share, loan_relationship_credit, standing_credit |
| D | 5 | 4 | 1 | personal_loan_fee_credit | seasoned_fee_rate, personal_loan_fee_credit, back_billing_relief |
| E | 5 | 4 | 1 | personal_loan_goodwill | service_recovery_amount, extra_entry_rebate, personal_loan_goodwill |
| LD | 5 | 4 | 1 | delinquency_reserve | delinquency_reserve, interest_cushion_method |
| PD | 5 | 4 | 1 | personal_loan_allowance | personal_loan_allowance, current_minimum_treatment |
| LF | 5 | 4 | 1 | loan_repayment_credit | first_miss_share, unpaid_minimum_figuring |
| W | 5 | 4 | 1 | loan_principal_goodwill | interest_reversal_method, error_service_recovery |

Structural failures (the realism classes CG-3 … CG-11 are in findings):
- **CG-3** — E's, W's and LD's only `method` factor is mislabelled (period-length change), so each has 0 honest methods.
- **XF-9 pairwise**: R `returned_fee_figuring` tier 1 equals tier 3 (15.00) for R01/R09 returns of 600.00–999.99; LF tier 1 never equals tier 3 below 250. These are partial overlaps only, so they are observations.
- **Counts after the striking tests** (factors struck by CG-3/4/5/7/8/9/10/11 are not counted):
  - C: 3 survive (conversion_term_band, affordability_extension, repayment_method_by_use), below 4.
  - R: 2 survive (first_return_share, returned_fee_figuring).
  - D: 2 survive (draw_size_points, frequent_drawer_figuring).
    - `seasoned_fee_rate` is struck by CG-11; `personal_loan_fee_credit` and `back_billing_relief` by CG-5.
  - E: 0 survive.
  - LD: 0 survive.
  - PD: 0 survive.
  - LF: 2 survive (first_miss_share, unpaid_minimum_figuring).
  - W: 0 survive.

  Every policy is below the 4–6 bound, so the factor relationship fails charter-wide.

### xf_recipe_sweep

Every XF point, on every extended policy:

| XF | result |
|---|---|
| 1 independence | clean on all eight |
| 2 assembly once, order fixed | clean (C, R, D, E, LD, PD, LF, W each have one assembly sentence with order) |
| 3 factor-only quantities | clean; no "as another policy figures it" |
| 4 overwrite hygiene | **RED** C (retires a non-conflicting clause; real conflicts undeclared → CG-2); others clean |
| 5 compute_basis verbatim | clean (scripted) |
| 6 rounding | clean |
| 7 docstrings | clean |
| 8 edge branches | ties stated (R, D, E, W); absent records handled (`or F('open_date')`, `or 0`); window boundary near-misses seeded. **RED** LF negative missed-date count (CG-12). Entries vs periods: "missed due dates" counted as late-fee rows net of every lender-error waiver (CG-12) |
| 9 method tiers change shape | **RED** E, W, LD (CG-3); others clean |
| 10 factor id ⊄ tool name | clean |
| 11 cross-record pairing | not used |
| 12 realism | **RED** CG-4 … CG-11 (members listed in findings) |
| 13 runtime | clean |
| 14 proof text | after reveal (per-task source_gt_comparison) |

### findings

Each finding lists the tasks it bears on. Their files demonstrate the consequence.

**CG-1 SOURCE-POLICY RED — the charter does not say whether a frozen line can be closed to draws (task 0).**
- Symptom: C can be read as allowed today on a frozen line, or as blocked until the line is unfrozen.
- Root cause: base rule `line_evt_draw_period_and_closure` "A borrower may close the line at any time: … with a balance it is closed to new draws and moves to repayment at once". Lifecycle `{from: active, to: repayment, by: user}` and event `line_closed_to_draws` `mutation: {transition: {from: active, to: repayment}}` give no `frozen` source state for a borrower's close. `frozen → repayment` exists only `by: system` (draw period ends). C's rule does not address status.
- Evidence: line.extended.yaml lines 13–27, 489–497, 1103–1108.
- Consequence: on task 0 (line frozen for the 2026-10-08 return, not unfreezable before 2026-10-19) one reading gives C = 141.96 written today and the other gives no write (refuse/come back). See `0.md`.
- Affected: base lifecycle/event vs base rule; C's rule.

**CG-2 SOURCE-POLICY RED — C departs from in-force base repayment-payment sentences without declaring it, and its declared overwrite retires a clause that never conflicted (task 0).**
- Evidence: § override_declarations, C.
- Consequence: with every other factor as derived, the base level-payment reading gives 118.61 against C's 141.96 on task 0.
- Affected: C `overwrite`, base `line_evt_payments_and_fees`, variant `repayment_payment_method`, event `line_closed_to_draws`.

**CG-3 SOURCE-FACTOR RED — mislabelled method factors (XF-9) (tasks 0, 1).**
- E `interest_putback_method`: fee×APR/36500×days vs fee×APR/1200 vs 0.
- W `interest_reversal_method`: the same.
- LD `interest_cushion_method`: balance×APR/1200 vs balance×APR/36500×days vs 0.
- Each tier is the same formula, amount × APR × period, with period = actual days/365, one twelfth of a year, or zero. Only the period length differs, so these are parameter ladders.
- Consequence: E, W and LD each have no honest `method` factor (required ≥ 1).

**CG-4 SOURCE-FACTOR RED (realism) — AutoPay enrolment selects quantities it has no bearing on (tasks 0, 1).**
- AutoPay is a payment-debit arrangement. No US lender settles how much interest it refunds, whether unbilled interest is capitalised, how much cushion it holds back, how much of a back-billed fee it relieves, or how much a borrower must pay to cure delinquency by whether the borrower's payments are debited automatically.
- Members (every one):
  - C `accrued_interest_treatment` tiers 1/2;
  - D `back_billing_relief` tiers 1/2;
  - R `standing_credit` tiers 1/2;
  - E `autopay_courtesy_amount` (whole ladder);
  - W `interest_reversal_method` tiers 1/2;
  - LD `interest_cushion_method` tiers 1/2;
  - PD `missed_date_paydown_share` tier 2 ("AutoPay off");
  - PD `current_minimum_treatment` (all tiers).
- Not a member: C `return_addon` tier 2. Withdrawing the AutoPay discount after a returned payment is a real practice; observation only.

**CG-5 SOURCE-FACTOR RED (realism) — schedules of small credits taken off fees, or goodwill/rebate add-ons on error refunds, keyed to behaviour on other products or to unrelated counts (tasks 0, 1).**
- US lenders publish fees as fixed amounts or percent formulas in the credit agreement. They deliver relationship benefits as APR discounts or whole-fee waivers. They do not publish menus of $0.25–$3.00 deductions from a late, returned-payment or draw fee keyed to personal-loan principal, loan AutoPay counts or line payment counts. They do not publish fixed "service-recovery", "goodwill", "courtesy" and percentage "rebate" increments stacked on the refund of a fee they charged in error.
- Members (every one):
  - R `loan_relationship_credit`, `standing_credit`;
  - D `personal_loan_fee_credit`, `back_billing_relief`;
  - LF `loan_repayment_credit`, `payment_history_credit`, `unused_courtesy_credit` (a credit for not having used a courtesy waiver);
  - E `service_recovery_amount`, `autopay_courtesy_amount`, `personal_loan_goodwill`, `extra_entry_rebate`;
  - W `error_service_recovery`, `loan_principal_goodwill`, `courtesy_tier_rebate`, `payment_courtesy`.

**CG-6 SOURCE-POLICY RED (realism) — error credits booked as one fee-waiver entry larger than the fee it is tied to (tasks 0, 1).**
- Base event `line_fee_waived`: "A draw, annual, late or returned-payment fee is waived", amount "Amount waived". Base: "A fee may be waived once".
- E and W book a `line_fee_waived` row with `related_txn_id` = the fee and an amount above it: 41.51 against 30.00 (task 0); 39.27 against 25.00 (task 1).
- A lender refunds the fee and the interest it charged on it. Anything else is a separate credit, not a waiver of that fee.

**CG-7 SOURCE-FACTOR RED (realism and self-consistency) — C sizes the repayment payment at a rate the line does not charge (task 0).**
- `return_addon` and `relationship_reduction` change "the APR used for the repayment payment". The close tool leaves `line_apr` unchanged, so interest keeps accruing at `line_apr`.
- The rule's "level payment that repays the balance over that number of months" is then false. Task 0: a level payment at 24.49 (118.61) on 2641.60 leaves 13.91 unpaid after 30 months at 24.74.
- No lender computes an amortising payment at a rate other than the contract APR.

**CG-8 SOURCE-FACTOR RED (realism) — C `accrued_interest_treatment` charges unbilled interest twice or makes a one-off amount recurring (task 0).**
- Tier 1 folds interest accrued since the last closing into the amount amortised. Base `line_evt_interest_and_annual_fee` still charges that cycle's interest at the next statement closing.
- Tier 2 adds the accrued interest "once" to a payment that the closing records as `minimum_payment_due`, "the monthly payment the borrower owes from now on" (close tool docstring). The one-off amount is therefore owed every month.
- Task 0 takes tier 1 (40.55 folded in).

**CG-9 SOURCE-FACTOR RED (realism) — PD's cure amount (task 1).**
- PD requires the borrower to pay down the balance to a share of the credit limit, plus the not-yet-due current minimum, to "bring the line back into good standing".
- A US lender cures a missed payment with the amount past due (plus the late fee). Base: minimum "plus any amount past due"; freeze lifted "once the amount past due is 0.00".
- All five PD factors act on the invented "good-standing paydown". Task 1: 829.79 against the cure of 248.14.

**CG-10 SOURCE-FACTOR RED (realism) — LD withholds available credit through per-draw holdbacks no open-end lender publishes (task 1).**
- Members: `interest_cushion_method`, `delinquency_reserve`, `returned_payment_reserve`, `single_draw_share`, `draw_period_taper`.
- The base defines available credit as "credit limit minus outstanding balance". A lender that wants to restrict availability lowers the limit through `line_evt_limit_changes` or freezes draws through `line_evt_freeze`. It does not apply hidden cushions, reserves, age shares and draw-period tapers to each draw request.
- Task 1: 841 against available 2,222.

**CG-11 SOURCE-FACTOR RED (realism) — D `seasoned_fee_rate` raises the draw fee for seasoned lines on some tiers (charter-wide, not on task 0's Standard tier).**
- `rate_seasoned_clean` 1.75 and `rate_seasoned_late` 2.25 replace the tier's percent for every line open 24 months or more.
- On FlexLine Preferred (1.0%) a seasoned line with no late fee pays 1.75%, more than a new line. On Plus (2.0%) a seasoned late line pays 2.25%.
- The "clean seasoned" tier is a penalty there. No lender prices loyalty that way.

**CG-12 SOURCE-POLICY RED — "missed due dates" net of every lender-error waiver (PD, LD, LF; charter-wide, not reached on either task world).**
- The rule counts missed due dates as "the late fees on the line in the last 12 months less the fee waivers for a Larkspur error in those 12 months". E's draw-fee corrections are also lender-error waivers. A draw-fee correction therefore erases a missed due date.
- On a line with no late fee, the count goes negative. LF's compute (`== 0`) then gives `full_share` where the rule's "no earlier missed due date" gives a first-miss share.
- Demonstration on task 0's post-E world (0 late fees, 1 lender-error waiver), were a late fee to come due there: compute share 1.00; rule share 0.80 (no earlier missed due date, line age 32 < 36 → `first_miss_share_new`).

## closing_checklist

Written after both reveals (2026-10-16T04:57–04:58Z). The charter-global section above was frozen before either reveal and is unchanged.

- Per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. This is the first revision (no older revisions). **Neither comparison carries a PASS.**
- Coverage and scope: `charter_scope` task 0 = {E, D, R, C}, task 1 = {W, LF, PD, LD}. This matches the derived scopes; they are disjoint and together cover all eight extended policies. `required_documents` equal the scopes. The eight task tools are closed and each uuid8 is independent. **Holds.**
- Problem trees: task 0 has 3 prerequisite problems, 4 value_input edges and owner=user root C. Task 1 has 3 prerequisite problems, 3 value_input edges and owner=user PD. Both are acyclic, with no cross-task edge. **Holds structurally.** The proof text of task 1 is RED (F-1d).
- Factors: label counts are within bounds and every factor bears weight on its world, with fall-backs ≠ gold (all 44 substitution figures match `computations`). **Fails**:
  - CG-3 leaves E, W and LD with no honest method;
  - the realism classes CG-4, CG-5, CG-7, CG-8, CG-9, CG-10 and CG-11 strike enough factors to put every policy below 4;
  - CG-12 is a rule/compute divergence.
- Policy self-consistency: **fails** — CG-1, CG-2, CG-6, CG-12.
- Unique solution: task 0 **fails** (F-0a frozen-line reading, F-0b level-payment reading). Task 1 holds apart from its factors.
- Gates were not re-run: no final form exists, because the difficulty does not pass.

The difficulty does not pass the source-layer audit.

VERDICT revision_1: task0=RED SOURCE-POLICY+SOURCE-TASK+SOURCE-FACTOR task1=RED SOURCE-FACTOR+SOURCE-CHAIN charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11,CG-12

## revision_2

### charter_global_frozen (revision_2)

- frozen 2026-10-16T07:55Z, before any revision-2 GT field was read.
- `line.extended.yaml` sha256 `9e45e14b…3f553a0` and `task_tools.py` sha256 `7b726c89…8d5b40f` are both changed from r1, so every section below is re-derived in full.
- Rework gate: the last line of `worklog.md` is `REWORK round 2: gates 7/7 green`.
- Gate snapshot (`/tmp/erl0067_coord/snapshot.sh flexline_credit_line 2`, 2026-10-16T07:23:38):
  - EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK;
  - TRACEABILITY NOT OK, 4 misses per task, all `unlock_*_discoverable_tool:tool_name` (expected pre-publication; verified by running the checker, see contamination disclosure in `0.md`/`1.md`).
  - Views r2/task_0 `7c6887e0…`, r2/task_1 `2fe5d7e5…`.
- Base copy (lines 1–1173): diff-identical to `blueprint/products/line.yaml`.
- Policies:

| shorthand | policy | tool | owner |
|---|---|---|---|
| C | close_to_draws_payment | `close_line_to_draws_7539d675` | user |
| LF | late_fee | `assess_late_fee_ba469c06` | agent |
| LR | limit_review | `apply_limit_review_5d0a2d8e` | agent |
| W2 | workout_fee_relief | `grant_workout_fee_relief_903cc630` | agent |
| R2 | returned_payment_fee | `assess_returned_payment_fee_0fd8e99d` | agent |
| DF | backbilled_draw_fee | `assess_draw_fee_4f046c6c` | agent |
| LI | limit_increase | `authorize_limit_increase_21546d5b` | user |
| RR | returned_fee_relief | `grant_returned_fee_relief_6fbb0f32` | agent |

### policy_conflict_scan (r2)

- Eight distinct `(target_tool, computes)` pairs.
- Sibling overwrites:
  - W2 and RR retire the same courtesy-count sentence with an identical `replaced_by` that names both no-request reliefs, each "under its own paragraph". W2 also retires the request-window sentence for workout relief only; RR keeps the window. Consistent.
  - DF retires the draw-fee sentence (scoped to the most recent draw posted without a fee) and the active-status clause for fee booking.
- LR adds a lender-initiated decrease with `overwrite: []`. The base event `line_limit_changed` reads "after an approved increase or a requested decrease", and LR records its review as a `request_type decrease` request. No base rule sentence is contradicted and no scored value depends on it (observation O-r2a).
- Scope (derived): task 0 {C, LF, LR, W2}, task 1 {LI, R2, DF, RR}. Disjoint, together covering all 8, no cross-task edge.

### rule_compute_equivalence (r2)

- Scripted: every `compute_basis` quote, `baseline.rule` sentence, `replaced_by` and `policy_source` is in its own rule. Every compute binding has a basis. Every factor `decides`/binding exists.
- Hand sweep of every ladder tier ↔ branch: consistent.
- Rounding:
  - C states "rounded to the cent once, at the end" and also "one spread_payment_count-th of it, rounded to the cent". The two rounding sentences coexist and compute follows both (observation).
  - LR rounds down to the step and up for the floor; LI rounds down to the step; DF rounds the figured fee and the result.

### action_binding_and_uuids (r2)

- uuid8s `7539d675`, `ba469c06`, `5d0a2d8e`, `903cc630`, `0fd8e99d`, `4f046c6c`, `21546d5b`, `6fbb0f32`: distinct, no shared prefix or sequence.
- Docstrings: no example values, no other tool names, no sequencing words; claimed effects match the bodies.
- No body checks status, freeze, past due, request status or a prerequisite.
- Runtime: the only import is erlbench; no datetime/random/uuid.
- XF-10: no factor id is a substring of any tool name.

### prerequisite_graph (r2)

| blocked | problem | kind | gate | form |
|---|---|---|---|---|
| C | LF | value_input | past_due_mode ✓ | state |
| C | LR | value_input | payment_method_code ✓ | state |
| C | W2 | value_input | conversion_balance ✓ | state |
| W2 | LF | **state_gate** | `line_transactions.installment_due_date` ✗ (not an eligibility gate of W2) | state |
| LI | R2 | value_input | returned_fee_share ✓ | state |
| LI | DF | **state_gate** | `line_transactions.related_txn_id` ✗ (not an eligibility gate of LI) | state |
| LI | RR | value_input | usage_balance ✓ | state |
| RR | R2 | value_input | relieved_fee ✓ | state |

- The graph is acyclic and every `policy_source` is verbatim in its rule.
- The two `state_gate` edges name a column, not an eligibility gate. Their effect texts describe value effects ("the late fees counted and chosen from …"; "the outstanding balance the usage share reads is complete"). Check 7 fails for both → **R2-N4**. On each task's world these same edges are the ones that do not bear weight (`0.md` F-0r2c, `1.md` F-1r2a).
- The other conditions now restate their sentences (round-1 O-0c / O-1b are closed).

### prerequisite_sentences (r2)

- All eight sentences pass the four-point test (connective; record-visible state; no tool/id/token; scope).
- Exactly one write per state, except **C's "carries a courtesy fee-waiver entry dated on or after its oldest unpaid due date"**. Both W2 (`grant_workout_fee_relief`) and RR (`grant_returned_fee_relief`) book `line_fee_waived` with basis courtesy dated the day granted. RR applies whenever the line's most recent return has a fee and a recorded replacement payment, which can coexist with a past-due line.
- On such a world the hop from C's sentence has two candidate writes. RR's relief satisfies the sentence, and W2's write becomes optional or doubles relief within a single courtesy allowance → **R2-N2 SOURCE-POLICY RED**.
- No rule states an undeclared cross-problem order.

### override_declarations (r2)

- **C:** retires "in repayment it is the level repayment payment plus any amount past due." with a scoped restatement. Still in force and departed from, undeclared: the base variant parameter `repayment_payment_method` (all six tiers: "level payment amortizing the balance at the start of repayment over the repayment period at the APR in force, recalculated when the APR changes") and the event `line_closed_to_draws` field "minimum_payment_due: Level repayment-period payment." → **R2-CG-2** (round-1 CG-2 partly closed).
  - C's rule "A borrower may close an active line to new draws, including a line that is past due but not frozen" agrees with the lifecycle → CG-1 closed.
- **LF:** the flat-fee sentence is retired, scoped to unpaid-at-booking dates and restated for late payers. OK.
- **LR:** see O-r2a.
- **W2 / RR:** as in § policy_conflict_scan.
- **R2:** the flat returned-fee sentence is retired for the most recent return. OK.
- **DF:** OK.
- **LI:** retires the increase-conditions sentence (on-time run → no 30-day-late payment; amount set by the paragraph). The other base sentences (active, seasoning, decrease rules, decline) are inherited. OK.

### factor_ladders (r2)

| policy | factors | param | method | honest methods | struck (realism) | survivors | cross |
|---|---|---|---|---|---|---|---|
| C | 6 | 4 | 2 | 1 (`past_due_treatment` is a multiplier) | — (spread tier R2-CG-8) | 6 | affordability_extension |
| LF | 5 | 4 | 1 | 1 | same_month_loan_share (R2-N1) | 4 | (struck) |
| LR | 5 | 4 | 1 | 1 | — | 5 | personal_loan_cut |
| W2 | 4 | 3 | 1 | **0** (`relief_fee_choice` substitutes a fee) | — | 3 + 0 methods | none |
| R2 | 5 | 4 | 1 | 1 | — | 5 | shared_return_event |
| DF | 5 | 4 | 1 | 1 | draw_size_points, recent_use_points (R2-N3) | **3** | none |
| LI | 5 | 4 | 1 | 1 | — | 5 | combined_exposure_scale |
| RR | 5 | 4 | 1 | 1 | — | 5 | bank_event_relief_basis |

- Every ladder has 3 tiers, fall-through = baseline, and every tier is in the rule.
- XF-1 independence: clean (transitive read lists checked).
- XF-9 pairwise:
  - RR basis tier 2 (min(fee, 15)) equals tier 3 whenever the line fee ≤ 15. It is distinct only above, as on task 1 (16.35). Observation.
  - R2 tier 1 equals tier 3 for R01/R09 returns of 600–999.99. Observation.

### xf_recipe_sweep (r2), every point on every policy

| XF | result |
|---|---|
| 1 | clean |
| 2 | clean (each policy has one ordered assembly sentence) |
| 3 | clean |
| 4 | **RED** C (undeclared departures from `repayment_payment_method` and the event field, R2-CG-2); others clean |
| 5 | clean (scripted) |
| 6 | clean (C's double rounding stated in rule; observation) |
| 7 | clean |
| 8 | ties stated (LF latest payment, W2 largest/most recent, R2/RR latest return, DF latest draw); absent-record branches present (`or F('open_date')`, `or 0`, `!= None`); **RED** C spread tier (entries vs periods: a ⅓ share "over the first 3 payments" recorded as one recurring payment, R2-CG-8) |
| 9 | **RED** C `past_due_treatment`, W2 `relief_fee_choice` (R2-CG-3) |
| 10 | clean |
| 11 | not used |
| 12 | **RED** LF `same_month_loan_share` (R2-N1); DF `draw_size_points` and `recent_use_points` (R2-N3); C spread (R2-CG-8). Tenure shares, shared-event share and late-booking shares were judged and accepted (observation O-r2b) |
| 13 | clean |
| 14 | after reveal |

### round-1 RED status (verified against the r2 charter, not the claims file)

| id | status | basis |
|---|---|---|
| CG-1 | **closed** | C rule addresses past-due-not-frozen; task 0 line active at 28 dpd < 30 |
| CG-2 | **partly open → R2-CG-2** | payments_and_fees sentence declared; variant `repayment_payment_method` and event field still undeclared; task 0: 103.26 vs 144.54 |
| CG-3 | **open → R2-CG-3** | E/W/LD removed, but new members: C `past_due_treatment` (multiplier), W2 `relief_fee_choice` (substituted fee) |
| CG-4 | **closed** | no compute reads AutoPay (scripted) |
| CG-5 | **closed** | no fixed-dollar credits or goodwill add-ons remain. The new realism defect R2-N1 is a different class |
| CG-6 | **closed** | W2 and RR are ≤ the fee they are booked against |
| CG-7 | **closed** | C uses `line_apr` only |
| CG-8 | **reopened → R2-CG-8** | accrued interest removed; new member: C spread tier folds a three-payment share into the recurring recorded payment |
| CG-9 | **closed** | PD removed |
| CG-10 | **closed** | LD removed |
| CG-11 | **closed** | DF tenure only subtracts points; no seasoned rate raises a fee |
| CG-12 | **closed** | all counts are plain counts of one event type |

### findings (r2)

**R2-CG-2 SOURCE-POLICY RED — residual undeclared override (task 0).**
- `repayment_payment_method` (variants, all tiers) and the `line_closed_to_draws` field "Level repayment-period payment." still state a level payment for closings. C's overwrite names neither.
- Task 0: that reading gives 103.26 against C's 144.54.

**R2-CG-3 SOURCE-FACTOR RED — mislabelled method factors (task 0).**
- C `past_due_treatment`: the part added is past due × 0 / RND(× ⅓) / × 1, a multiplier on one quantity.
- W2 `relief_fee_choice`: the relief is chosen_fee × shares in every tier; the tiers only choose which fee is substituted.
- Result: W2 has no honest method factor.

**R2-CG-8 SOURCE-FACTOR RED (realism and self-consistency) — limited-term amount recorded as the recurring payment (task 0).**
- C's spread tier adds ⅓ of the past due "over the first spread_payment_count payments". The repayment payment is recorded once as `minimum_payment_due`, which the close tool calls "the monthly payment the borrower owes from now on".
- Either the ⅓ is owed every month (33 × 11.74 = 387.42 against 35.21 on task 0), or, under base "Balances and the minimum payment are refreshed after every line" and the base payment allocation, the first payment clears the whole past due. In both cases the stated three-payment spread does not exist.

**R2-N1 SOURCE-FACTOR RED (realism) — LF `same_month_loan_share` (task 0).**
- A personal-loan late fee within 31 or 62 days of the line due date multiplies the line's late fee by 0.75 or 0.90.
- No lender cuts a penalty fee because the borrower is also delinquent on another product. Delinquency elsewhere raises risk treatment; it does not discount it.
- Task 0 takes tier 1: 5.08 against 6.77.

**R2-N2 SOURCE-POLICY RED — C's courtesy-waiver sentence has two resolving writes, W2 and RR (charter-wide).**
- See § prerequisite_sentences.
- Not reached on task 0's world: no payment is recorded against the 2026-02-25 return.

**R2-N3 SOURCE-FACTOR RED (realism) — DF surcharges only the draw Larkspur forgot to bill (charter-wide).**
- `draw_size_points` (+0.25/+0.50) and `recent_use_points` (+0.25/+0.50) raise the percent above the tier's draw fee percent for the most recent draw posted without its fee. The `replaced_by` keeps "every other draw" at the tier percent.
- The disclosed fee is the same for every draw. Billing a missed fee above it is a post-hoc fee raise for the lender's own error.
- Example: a 2400 draw on an 8000 Plus line, fewer than 6 draws in 12 months, booked in the same month: 3.00% × 2400 = 72.00 against the 48.00 every on-time draw carries.
- Not reached on task 1 (35.89 < 48.00), but both factors are taken there.

**R2-N4 SOURCE-POLICY RED — two `state_gate` edges name no eligibility gate (tasks 0, 1).**
- The edges W2←LF and LI←DF fail check 7.
- On each task world they are the edges that do not bear weight (task-file findings).

Observations:
- O-r2a: LR's lender-initiated decrease against the base `line_limit_changed` meaning; no scored consequence.
- O-r2b: tenure shares (LF, R2, W2, LR, DF), the R2 shared-event share and the late-booking/back-billing shares were judged as practices a US lender plausibly publishes.
- O-r2c: W2's trigger "when the borrower closes a line to new draws" against C waiting on W2. Read as "in connection with the closing request"; C's sentence fixes the order.

### closing_checklist (revision_2)

Written after the revision-2 reveal (07:33:25Z). The charter-global r2 section above was written at 07:33:19Z by mtime; its "frozen 07:55Z" label was an estimate (see `0.md`).

- Per-task files carry revision_2 frozen sections and comparisons. Neither comparison is PASS.
- Scope: `charter_scope` task 0 {LF, W2, LR, C}, task 1 {R2, DF, RR, LI}. This matches the derivation; disjoint and complete. Tools closed. uuid8s independent. **Holds.**
- Trees:
  - task 0: n = 3, 3 value_input edges into C, user root;
  - task 1: n = 3, 3 value_input edges (LI←R2, LI←RR, RR←R2), user root;
  - both acyclic.
  - **One decorative edge per task** (W2←LF, LI←DF), each labelled `state_gate` with a non-eligibility gate.
- Factors: every factor bears weight and every fall-back ≠ gold (all 44 sensitivity figures match, except two DF counterfactuals that differ by half-even rounding). **Fails**:
  - W2 has no honest method (R2-CG-3);
  - DF falls below 4 after R2-N3;
  - realism REDs R2-N1 and R2-N3, and the R2-CG-8 spread tier.
- Policy: **fails** (R2-CG-2, R2-N2, R2-N4).
- Round-1 REDs: CG-1, CG-4, CG-5, CG-6, CG-7, CG-9, CG-10, CG-11 and CG-12 are verified closed. CG-2 persists in part as R2-CG-2. CG-3 and CG-8 persist in new members as R2-CG-3 and R2-CG-8.
- Gate snapshot r2: 7/7 OK, with traceability unlock-name misses only. No new gate RED.

The difficulty does not pass the source-layer audit at revision 2.

VERDICT revision_2: task0=RED SOURCE-POLICY+SOURCE-TASK+SOURCE-CHAIN+SOURCE-FACTOR task1=RED SOURCE-POLICY+SOURCE-CHAIN+SOURCE-FACTOR charter=R2-CG-2,R2-CG-3,R2-CG-8,R2-N1,R2-N2,R2-N3,R2-N4

## revision_3

### charter_global_frozen (revision_3)

- Written before any r3 GT field was read (mtime precedes the reveal time recorded in the closing checklist).
- Hashes: `line.extended.yaml` `8118796e…685c46b8` and `task_tools.py` `0b2cd9bd…c81a5e278`. Both changed, so every section is re-derived.
- Gate snapshot (`/tmp/erl0067_coord/snapshot.sh flexline_credit_line 3`, 2026-10-16T15:18:48):
  - EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK;
  - TRACEABILITY NOT OK. Per the coordinator's instruction the checker was not run separately, so the miss lines were not inspected. The coordinator expects unlock-tool-name misses only pre-publication.
- Views: r3/task_0 `7c6887e0…` (unchanged world), r3/task_1 `c121de3f…`.
- Base copy diff-identical to the blueprint.

### sections (r3)

- **policy_conflict_scan:**
  - 8 distinct `(tool, computes)` pairs.
  - W2/RR sibling overwrites name each other's no-request relief.
  - LR now declares the lender-initiated decrease against the base request sentence (O-r2a closed).
  - Scopes derived: task 0 {C, LF, LR, W2}, task 1 {LI, R2, DF, RR}.
- **rule_compute_equivalence:**
  - Scripted: all `compute_basis` quotes, baseline sentences, `replaced_by` and `policy_source` texts are verbatim in their rules; every compute binding has a basis.
  - Hand sweep of all 40 ladders: tier ↔ branch consistent.
  - Every rule now states "an exact half cent to the even cent", matching the DSL RND (O-1r2b closed). Task 0's W2 10.125 → 10.12 exercises it.
- **action_binding_and_uuids:**
  - The eight uuid8s are unchanged and independent.
  - The docstrings changed only in wording: W2 is now "one late fee". No example values, no other tool names, no sequencing words. Bodies are unchanged and check nothing.
  - Runtime: erlbench is the only import.
- **prerequisite_graph:** 8 edges, all `value_input` with gates that exist in compute (C←LF late_term_cut, C←LR payment_method_code, C←W2 conversion_balance, W2←LF relief_way, LI←R2 returned_fee_share, LI←DF recent_draw_charges, LI←RR usage_balance, RR←R2 relieved_fee). The graph is acyclic and the conditions restate their sentences. R2-N4 closed.
- **prerequisite_sentences:** four-point test passes on all 8. C's waiver sentence now reads "a courtesy fee-waiver entry against one of its late fees". RR books only against returned-payment fees ("replacement relief on the returned-payment fee of that return"), so every state now has exactly one producing write. R2-N2 closed.
- **override_declarations:**
  - C now carries two overwrites: the payments sentence, and the draw-period sentence. The draw-period `replaced_by` names "the tier's repayment payment method and the closing record's level repayment-period payment" and replaces both for borrower closings. A closing sets `draw_period_end_date` (event field), so the draw-period sentence does govern closings. R2-CG-2 is closed, and the round-1 remark that this sentence "never conflicted" is withdrawn.
  - LF, R2, DF and LI `replaced_by` texts now name the parameter or record they depart from.
  - No undeclared departure found.
- **factor_ladders / xf_recipe_sweep:**

| policy | factors | param | method (honest) | cross | notes |
|---|---|---|---|---|---|
| C | 6 | 5 | 1 (method by use) | affordability | spread and multiplier removed; late-history term cut added |
| LF | 5 | 4 | 1 | — | balance-tier share replaces the loan share (balance-tiered late fees are an established US card practice) |
| LR | 5 | 4 | 1 | personal_loan_cut | |
| W2 | 4 | 3 | 1: `relief_figuring` = max(0, fee − 5) / amount past due (only when below the fee, i.e. a cap) / whole fee — subtract, cap, identity | — | R2-CG-3 closed |
| R2 | 5 | 4 | 1 | shared_return_event | |
| DF | 5 | 4 | 1 | — | all points are reductions; never above the tier percent (R2-N3 closed) |
| LI | 5 | 4 | 1 | combined_exposure_scale | draw-intensity share added |
| RR | 5 | 4 | 1 | bank_event_relief_basis | |

- XF-1 independence is clean, checked transitively. XF-9 pairwise:
  - W2 tiers never coincide;
  - RR basis tier 2 equals tier 3 when the fee is ≤ 15 (observation, as before);
  - R2 tier 1 equals tier 3 for R01/R09 returns of 600–999.99 (observation).
- XF-12 realism, every class judged across all eight policies at once:
  - (a) AutoPay conditions: none.
  - (b) Fixed-dollar credits or goodwill add-ons: none.
  - (c) Fees cheaper for worse behaviour: none. LF is lower on a smaller balance, a longer tenure and a cleaner history; DF is lower on a cleaner record and a longer tenure; R2 is lower on a first return and a shared bank event.
  - (d) Back-billing above the disclosed fee: none.
  - (e) Recurring payment carrying a limited-term amount: none. C states one fixed amount owed every month.
  - (f) Credits above the fee booked against: none. W2 ≤ fee by its own cap; RR ≤ fee.
  - (g) Lender-delay discounts (R2 late booking, DF back-billing) and tenure shares: accepted as plausible published practice.
  - (h) Lowest-confidence realism call, observation only: R2 tier 2's percentage-of-returned-amount fee, which can exceed the disclosed flat fee (30.00 on task 1, against 15.00). US NSF fees are usually flat and often capped by state law. I judged it the same way in r1 and r2, and record it explicitly here so the class is complete.
- Every other XF point is clean.

### round-2 RED status (verified against the r3 charter)

| id | status |
|---|---|
| R2-CG-2 | closed (see override_declarations) |
| R2-CG-3 | closed (C has one honest method; W2's `relief_figuring` changes shape) |
| R2-CG-8 | closed (no add-on; the fixed recurring amount is stated) |
| R2-N1 | closed (loan share removed) |
| R2-N2 | closed |
| R2-N3 | closed |
| R2-N4 | closed (both edges are value_input and bear weight on their worlds: W2 10.12 vs 12.66; LI 8800 vs 8900) |

Round-1 REDs closed in r2 remain closed: no AutoPay reads, no frozen-line case, no undeclared overwrites, and no PD/LD/E/W policy.

### findings (r3)

No new SOURCE-POLICY or SOURCE-FACTOR RED found at the charter level.

Observations:
- O-r3a: R2 tier 2 percentage NSF fee (above).
- O-r3b: two knife-edge seeds in task 1 (5194.80/5200 and 6397.20/6400). They are legitimate near-misses.
- O-r3c: C both adds workout months for lateness and cuts months for late history. On task 0 the +6 and −6 offset each other; both directions are defensible business choices.

### closing_checklist (revision_3)

Written after the r3 reveal (2026-10-16T15:23:19Z).

- Per-task files carry r3 frozen sections and comparisons, both **PASS**. Older revisions are untouched.
- Coverage and scope: `charter_scope` task 0 {LF, W2, LR, C}, task 1 {R2, DF, RR, LI}. They equal the derived scopes and `required_documents`, are disjoint, and cover all 8 policies. Tools are closed and the uuid8s are independent.
- Trees: each has 3 prerequisite problems, all edges value_input and weight-bearing, a user-owned root, and no cycle. There are no cross-task edges.
- Factors:
  - every computation has 4–6 factors, at least 2 parameters and at least 1 honest method;
  - each task has a multi-source and a cross-difficulty factor;
  - every ladder has 3 tiers stated in its rule;
  - every factor bears weight against an honest baseline;
  - every fall-back ≠ gold (all 44 figures match GT).
- Realism: no open RED. Observations O-r3a/b/c are recorded.
- Gates on the final form: snapshot r3 shows 7 gates OK and TRACEABILITY NOT OK. The miss lines were not inspected, per the coordinator's instruction; they are expected to be unlock tool names only pre-publication.
- Round-1 and round-2 REDs: all verified closed.

The difficulty passes the source-layer audit at revision 3.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### charter_global_frozen (revision_4)

- Written before any r4 GT field was read (mtime precedes the reveal time in the closing checklist).
- Gate: the last line of `worklog.md` is `REWORK round 4: gates 7/7 green`.
- Snapshot (`snapshot.sh flexline_credit_line 4`, 2026-10-17T02:36:21): all eight gates OK, including **TRACEABILITY OK**.
- Views: r4/task_0 `7c6887e0…` and r4/task_1 `c121de3f…`, both identical to r3, so the worlds did not move.
- Sources:
  - `line.extended.yaml` sha256 `45031e0626d8f261099d34c1c03adae412e2990d6ac136057547658fef6e9fd1` (changed);
  - `task_tools.py` `0b2cd9bd…c81a5e278` (unchanged since r3);
  - base copy diff-identical to the blueprint.
- Inputs this round:
  - KB audit `audits/policy_kb/flexline_credit_line/1.md`, last line `src=src-1,src-2,src-3`, and their sections in `0.md`/`1.md`;
  - renderer notes `audits/render_source/flexline_credit_line/render_r1.md` (two edge cases);
  - `rework_r4_claims.md`.
- Re-derivation scope: the charter-global sections below are re-checked in full on the new yaml. The worlds and tools are unchanged, so the per-task computations are recomputed against every moved clause (see the task files).
- contamination_disclosure: the r3 GT values are known to me from the r3 reveal. Revision 4 is therefore a re-verification, not a blind derivation.

### downstream items, verified against the r4 charter

**src-1 (C `min_term_months` floor inert at baseline in the assembly sentence) — closed, whole class swept.**
- The floor now sits in the two factor sentences that take months off: "the trim never takes the term below min_term_months" and "the cut never takes the term below min_term_months". The assembly sentence now fixes the order, "the months added before the months taken off", and no longer names the floor. The baseline does not mention it.
- Compute: `term_after_trim = MX(12, band + affordability + workout − trim)`, then `conversion_term = MX(12, term_after_trim − late_cut)`.
  - Because the additive part is always ≥ 18, the per-step floors equal a single floor at the end, and trim-then-cut equals cut-then-trim. The stated order is the only one that matters (add before subtract), and compute follows it.
- Class sweep: a clamp that binds only after a factor moves the value and that sits in an assembly or computation sentence. All eight assembly sentences checked:
  - LF ("held to no more than the unpaid part"), LR (balance and minimum floors, cap at the prior limit), R2 (minimum-due cap), DF (raised to the minimum draw fee) and LI (held to the request and tier max) all bind at baseline.
  - DF's "less every point reduction above, never below 0.00" can never bind: the maximum reduction is 1.00 point, which does not exceed any fee-charging tier's percent (the smallest is Preferred at 1.0). The published computation doc `back_billed_fee_amount_97bdd274` does not carry it. Observation O-r4b.
  - W2 and RR have no clamp in their assembly sentences.
  - No remaining member.

**src-2 (LI←RR declared state form, but the sentence named the action) — closed, whole class swept.**
- The sentence is now "The approved limit is fixed only after the returned-payment fee of a return that has a replacement payment recorded against it carries a courtesy fee-waiver entry." That is a record state in table words. The only producing write is RR (W2 books only against late fees). The condition now requires `waiver_reason courtesy`, matching the sentence.
- Class sweep of the other seven `policy_source` sentences: each names a record state ("carries its late-fee entry", "carries a credit-limit review decided on or after …", "carries a courtesy fee-waiver entry against one of its late fees", "shows its returned-payment fee entry", "carries a draw-fee entry", "carries its returned-payment fee entry"). None names an action.
- **Relation to revision 3:** my r3 § prerequisite_sentences passed the old LI←RR sentence ("… replacement relief … is booked") as state form. That pass was wrong; the KB audit's src-2 was correct.

**src-3 (retired base clauses live in force only inside extended hubs) — no policy defect.**
- Every `replaced_by` restates the retired clause for every out-of-scope case, which is exactly what XF-4 requires. Checked: C ×2, LF, LR, W2 ×2, R2, DF ×2, RR. LI replaces the increase conditions for every increase request, which is its whole scope.
- A base document showing the clause as retired is therefore faithful. Nothing to close at the source layer.

**render-relief-zero-waiver — closed, class swept.**
- RR's `relief_basis_way` now keys on `loan_fee_waiver_count ≥ 1` (an existence test, XCOUNT of `loan_fee_waived` related to the same-day loan fee), as the rule says ("already carries a personal-loan fee waiver"). The new binding sits inside `bank_event_relief_basis`'s bindings.
- Class sweep (existence in the rule vs amount in the compute): C affordability (EXISTS), R2 shared event (XCOUNT), LR loan cut (EXISTS), W2 relief way (counts), RR's `relieved_fee > 0 and replaced_amount > 0` gate (a booked 0.00 fee gives relief 0.00 either way, so the value is the same). No remaining member.

**render-review-raise — closed, class swept.**
- LR `result = MN(review_limit_now, MX(stepped, balance_floor, tier_min))`. The rule, assembly and baseline now say "never above the credit limit before the review".
- Observation O-r4a: on an over-limit line the baseline sentence's two "never" clauses (≥ balance and ≤ prior limit) cannot both hold. The assembly sentence resolves this (cap last). Not reachable on either task world (task 0 balance 2600.21 < 3300).
- Class sweep (stated bound vs compute), every policy: LI "never below the current credit limit" is now enforced by `MX(current_limit, …)`. The others were all already enforced: LF, R2, W2 (≤ fee: tiers ≤ fee and shares ≤ 1), RR (≤ fee), DF (≥ minimum fee × share), C (≥ 12), LR (≥ tier minimum).

### charter sections (r4)

- **policy_conflict_scan:** unchanged from r3. Scopes are disjoint and complete.
- **rule_compute_equivalence:** scripted sweep. Every `compute_basis` quote, baseline sentence, `replaced_by` and `policy_source` is verbatim in its rule. Every binding has a basis. Every factor binding exists.
- **action_binding_and_uuids:** tools unchanged since r3, so carried forward by hash.
- **prerequisite_graph:** 8 value_input/state edges, all gates exist, acyclic.
- **override_declarations:** as r3, plus no new departures.
- **factor_ladders:** counts unchanged (C 6, LF 5, LR 5, W2 4, R2 5, DF 5, LI 5, RR 5). Each has an honest method.
- **xf_recipe_sweep:** all 14 points clean. XF-14 is checked after the reveal.
- Realism classes (a)–(h) as in r3: no member. O-r3a (R2's percentage NSF fee) stands as an observation.

### findings (r4)

No open RED. Observations: O-r4a (over-limit baseline clauses), O-r4b (DF floor that can never bind).

### closing_checklist (revision_4)

Written after the r4 reveal (2026-10-17T02:39:54Z).

- Both task files carry r4 sections with **PASS**. Older revisions are untouched.
- Scope, trees, factors and realism are as in r3 § closing_checklist, all re-verified on the r4 yaml.
- Downstream items closed with their classes: src-1, src-2, render-relief-zero-waiver, render-review-raise. src-3 is not a source defect.
- Gates on the final form: snapshot r4 shows all eight OK, traceability included.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global (revision_5)

- Gate: last worklog line is `REWORK round 5: gates 7/7 green`. Snapshot r5 (2026-10-17T20:51:40): all eight gates OK.
- `line.extended.yaml` (`45031e0626d8f261…`) and `task_tools.py` (`0b2cd9bdfe20e668…`) are byte-identical to r4, so every charter-global section of revision_4 (and through it r3) is carried forward by hash.
- This was a seed-only rework. Both worlds were re-simulated: views r5/task_0 `57af5ae6…` and r5/task_1 `cc56126f…`.

### seed items verified (rows checked against the owning product's published rules in `docs/loan` and the line charter)

| item | check | status |
|---|---|---|
| src-4a | task 0 loan late fee 18.64 = 5% × 426.95 × 0.90 (first-late: 11 net installments) × 0.97 (tenure 30 months); no AutoPay or term-extension share; FlexLine pay-cycle case 3 | closed |
| src-4b | installment 426.95 = level payment at base 16.24%; daily-interest re-simulation matches every split and principal 6387.95 | closed |
| src-4c | `autopay_enrolled` false, every payment online, current = base rate; no enrollment record expected | closed |
| src-5a | task 1 loan returned fee 12.75 = 15.00 × 0.85 (12 installments − 1 return = 11); no AutoPay share; bank-event case 3 (no FlexLine fee on the date) | closed |
| src-5b | installment 421.26 = level at base 11.99%; re-simulation matches, principal 9601.14 | closed |
| src-5c | origination fee 478.40 = 2.99% (Grade B); net proceeds and both disbursements follow | closed |
| src-5d | loan never on AutoPay; online payments only; no account-change records needed | closed |
| own-history | late fees flat 25.00 under LF's paid-late clause (task 0: 2025-08-01, 2026-04-03; task 1: 2026-02-28); task 0 returned fees 6.38 and 8.31 re-priced by R2's paragraph on their dates; courtesy waiver 6.38 in full | closed |

Class sweep, every seeded row of every product in both worlds (line, loan, bank accounts, limit request):
- No row remains that its owning rules would not produce.
- Line draw fees are at tier percent.
- Interest rows were re-simulated end to end by the reworker. Ledger sums equal `outstanding_balance` in both worlds (2597.01, 6368.63).

### per-task (cited)

- Both tasks were re-derived in full from the new views before the reveal (`0.md`/`1.md` § revision_5).
- Every prerequisite is unmet at the opening, and every edge and factor bears weight.
- The gold matches in every value and every factor sensitivity.

### closing_checklist (revision_5)

- Both task files carry r5 sections, both **PASS**. Older revisions are untouched.
- The charter structure is unchanged from r4 (CLEAN).
- Seeds are consistent with the owning rules.
- All 8 gates are OK on the final form.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN
