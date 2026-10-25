# Policy-task audit — funding_and_disbursement_disputes / charter-global

## charter_global_frozen

- freeze time: 2026-10-13T05:51Z (written before any task's GT was read)
- auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator
- frozen inputs (hashes verified against the coordinator brief):
  - `tasks/funding_and_disbursement_disputes/funding.extended.yaml` sha256 `d2923f0cfa7c2d20f1bc049411ac21f377892e88f904984e06ea7f071d7cd67c`
  - `tasks/funding_and_disbursement_disputes/task_tools.py` sha256 `2d06c0d5472362437836df2f94e85d664a8314acb4b9593b240f1a1753f67ee2`
- read: `blueprint/blueprint.yaml`, `blueprint/products/funding.yaml` (whole), `blueprint/products/loan.yaml` and `lock.yaml` (targeted reads only: the program fee rule, the condition rules, the lock relock/float-down events and rule), the `share_tools.py` signatures, the extended charter, `task_tools.py`
- masked and unread here: every task JSON field except `frozen_time` / `user_scenario` / `initial_state` (taken from the coordinator's masked views), `worklog.md` files, any prior audit
- entry conditions (Step 0): gate snapshot supplied; masked views supplied with hashes; all gates green except `check_traceability`, which is red only on unlock-call tool names that have no published KB source yet (docs are rendered in a later step; coordinator verified 0 non-unlock misses). Accepted as out of scope. Input is complete.

Base copy: `yaml.safe_load` of the extended file's base keys (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) equals `blueprint/products/funding.yaml` key by key. The text is reformatted (line wrapping), but no content differs.

### policy_conflict_scan

Six extended policies, each with a distinct `(target_tool, computes)`:

| policy | trigger | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| funding_ext_late_funding_refund (lf) | state_due | refund_late_funding_interest_1de244fe (agent) | interest_amount | [] |
| funding_ext_per_diem_shortfall (sf) | on_request | pay_prepaid_interest_shortfall_7376ee5f (user) | interest_amount | lf (value_input, gate sf_held) |
| funding_ext_returned_wire_refund (rw) | state_due | refund_returned_wire_interest_891dcbc9 (agent) | interest_amount | [] |
| funding_ext_earlier_month_refund (em) | state_due | refund_earlier_month_interest_1e4f3041 (agent) | interest_amount | rw (value_input, gate em_prior_days) |
| funding_ext_funding_month_interest (fm) | state_due | pay_funding_month_interest_3474c980 (user) | interest_amount | [] |
| funding_ext_interest_dispute_decision (dd) | on_request | decide_prepaid_interest_dispute_44bdf39e (agent) | refund_amount | fm (value_input, gate dd_held); em (value_input, gate dd_owed_days) |

Scope triggers and how the policies divide the closings:
- lf applies only when "the disbursement date falls within the period of the closing's prepaid interest charge". em applies only when "the disbursement date falls after the last day of the charge collected at closing", and so does fm ("funds in a later month than the month its prepaid interest was collected for"). So lf is disjoint from em and fm on any one closing.
- rw needs a `funding_conditions_unmet` recall, and its lost days are clipped to the charge period. It can coexist with em, and em's prerequisite orders the two.
- sf ("priced below the per diem the note supports") and dd ("per diem overcharge or late-funding dispute") can each coexist with the others. Their prerequisite sentences fix the order.

Overlapping subjects:
- `funding_per_diem_refunded` is written by lf, rw and em, and as a side effect of dd's tool.
- `funding_per_diem_charged` is written by sf and fm.

These overlaps are on a shared ledger, not on a shared quantity. Each policy claims its own `interest_amount` / `refund_amount`. Two tools stamp the same `refund_reason`: lf's tool and em's tool both write `funding_later_than_estimated` (task_tools.py lines 68 and 219). See prerequisite_sentences for why this does not make sf's hop ambiguous.

Claimed task scopes (inferred pre-reveal from worlds and personas only, not from `charter_scope`):
- task 0 = {sf, lf}
- task 1 = {dd, fm, em, rw}

These are pairwise disjoint and jointly cover all six policies. This is consistent with check_extended's "all policies are covered across the suite with disjoint scopes". It will be re-confirmed after the reveal in each task file.

Cross-category reads:
- lock: `locked_rate`, `float_down_used`, `lock_pricing_events.new_rate/event_date`
- loan: `base_loan_amount`, `loan_amount` (sf only), `funding_fee_exempt`, the `upfront_program_fee_pct` product parameter, `loan_conditions.*`

All are declared in each policy's `cross_category`. No undeclared read was found in compute.

Terminal states: every write is an append to the ledger (or the dispute table) plus a balance update. No lifecycle transition is claimed, so there is no terminal-state conflict.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` value is a verbatim substring of its policy's `rule` (whitespace-normalised). Every compute binding has a `compute_basis` entry, and no basis entry is orphaned. All six policies pass. Every `baseline.rule` sentence is a verbatim sentence of its `rule`.

Sentence-level sweep back from rule to compute:

- **sf — empty promise (finding F-G4).** The sentence "A shortfall that comes only from funding earlier than estimated is never collected." has no implementation. When funding is earlier than estimated (disbursement < estimated_funding_date ≤ charge end), `sf_days` takes tier 2: `(DAYS(F('disbursement_date'), sf_charge_through) + 1) if (sf_refund_count == 0 and F('disbursement_date') <= sf_charge_through)`. That counts more days than were charged, so `sf_raw > 0` and compute bills exactly the early-funding shortfall that the rule (and base `post_closing_interest_shortfall_collected: false`) says is never collected.
- **lf — filter mismatch (finding F-G5).**
  - Rule tier 2 of the funds-out treatment reads off "the borrower's latest document answering a prior-to-funding condition".
  - `lf_doc_day` is `XLATEST('loan','loan_conditions','document_date', ..., event_type='loan_condition_cleared', condition_class='prior_to_funding')`. It has no filter excluding conditions Larkspur completes itself.
  - rw's rule says the verbal verification of employment is one "which Larkspur completes itself". em's and rw's compute exclude it with `!= 'verbal_verification_of_employment'`; lf's compute does not.
- **lf — scope check (observation).** The rule says "falls within the period of the charge", but `lf_refund_days` tests only `disbursement_date <= lf_charge_through`, with no lower bound. This is harmless wherever disbursement ≥ estimated date.
- **dd — extra condition (observation).** `dd_int_rate` tier 1 adds `dd_excess > 0`, which the rule does not state. Interest on a zero excess is zero, so the scored value does not move.
- **em — possible double subtraction (observation).** `em_counted` subtracts prior-refund days, funds-out days and window days without de-overlapping them, while the rule says "not counted again". In a world where a returned-wire refund's days overlap the window days, compute would subtract a day twice.
- Everything else checked has a matching rule sentence: tiers, windows, the business-day counting (`*_window_offset` / `*_ack_offset` / `*_resp_offset` formulas checked against the "counted Monday through Friday, starting with the day after …" sentences), caps, floors and rounding.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy, and the six target tools are distinct.
- uuid8 tails are `1de244fe`, `7376ee5f`, `891dcbc9`, `1e4f3041`, `3474c980` and `44bdf39e`. They share no prefix, are not sequential, and none is a re-tailed copy of another.
- Docstrings:
  - No docstring names another tool or uses an ordering word (`before`/`after`/`first` grep: no hits inside docstrings). em's "funded in a later month" describes a date, not a step order.
  - Two docstrings say more than their policy's rule:
    - rw's docstring ("a funding wire Larkspur had to recall or re-send because of its own error") is broader than its rule, which covers only recalls for an open prior-to-funding condition. Observation.
    - em's docstring says its entry is "marked as a refund for funding later than estimated", the same marking as lf. Observation.
- Tool bodies: none reads any other row to accept or refuse a call. No tool validates a prerequisite (bodies at task_tools.py lines 58-74, 106-122, 157-173, 209-225, 257-273, 304-329).
- dd's tool books its refund entry with `source_interest_entry_id=filing.get("disputed_entry_id")`. That is null when the filing names no entry, so the refund names no charge. Base `funding_per_diem_interest` says "Each refund names the charge entry it corrects." This is an observation: a tool effect, and it moves no scored value.

### prerequisite_graph

- Every policy fills in `prerequisite`. The edges are sf→lf, em→rw, dd→fm and dd→em. Every `problem` is an extended id in this file, none is a base id or a self-edge, and the graph is acyclic.
- Every edge's `policy_source` is a verbatim sentence of the blocked policy's own rule, and none appears in the depended-on policy's rule (scripted check).
- All four edges are `form: state`, `kind: value_input`, with no `fallback_reason`. This is correct, because none is action-form.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- The gate bindings `sf_held`, `em_prior_days`, `dd_held` and `dd_owed_days` exist in the blocked compute.
- **Finding F-G6 (declaration).** On the dd→em edge, the declared `effect` says "the earlier-month refund lowers the prepaid interest held **and removes its days from the owed days**", and `gate: dd_owed_days`. But `dd_owed_days` is built only from `dd_one_days`, `dd_one_from`, `dd_one_through` and `dd_scope_days`, and those read charge rows only (`event_type='funding_per_diem_charged'`). No refund row enters `dd_owed_days` in any world.
  - So the named gate binding is never moved by the resolving write. The edge carries weight only through `dd_held`, which is a different binding.
  - The other three effects are true: lf's refund days enter `sf_days` tier 1 and `sf_held`; rw's refund days enter `em_prior_days`; fm's charge enters `dd_held` and `dd_owed_days` tier 1.
- No `prerequisite` text carries authoring-viewpoint phrasing.

### prerequisite_sentences

Four-point test, one block per edge.

1. **sf→lf.** Sentence: "The per diem shortfall is fixed only after the closing's prepaid interest ledger carries the late-funding refund owed for the unfunded days that fall in the month the loan funded."
   - Ordering connective: "only after".
   - State form: a ledger row, a late-funding refund. It names no tool, policy id or row id.
   - Scope: "the unfunded days that fall in the month the loan funded" matches `condition`.
   - Writers of a `funding_later_than_estimated` refund: lf and em. em's rule restricts it to "a month before the month in which its loan funded", so it cannot produce a refund "for the unfunded days that fall in the month the loan funded". Exactly one write brings the state about.
   - Derivation: sentence → find the policy whose rule refunds prepaid interest "for days on which its loan was not yet funded, where the disbursement date falls within the period of the closing's prepaid interest charge" → lf. There is one reading.
   - PASS. The shared refund_reason stamp is recorded as an observation.
2. **em→rw.** Sentence: "The earlier-month refund is fixed only after the closing's prepaid interest ledger carries the returned-wire refund owed for the days a Larkspur-side recall cost."
   - "only after"; state form; no tool or id.
   - Only rw's rule refunds "days lost to a funding wire that Larkspur recalled". One write, one reading.
   - PASS.
3. **dd→fm.** Sentence: "A prepaid interest dispute is not decided until the closing's prepaid interest ledger carries a charge for the month in which the loan funded."
   - "not until"; state form.
   - Writers of a charge: fm and sf. sf's payment is "recorded as a prepaid interest charge for the period of the closing's latest prepaid interest charge", which is never the funding month when funding fell in a later month. fm's charge covers "the month in which the loan funded".
   - One write. PASS.
4. **dd→em.** Sentence: "A prepaid interest dispute is decided only after the closing's prepaid interest ledger carries a refund for every day of the charge collected at closing that falls before the funding month and that the borrower does not bear."
   - "only after"; state form.
   - **Observation O-G1.** The waited-on state is brought about jointly by two writes: rw (the Larkspur-side recall days) and em (the remaining earlier-month days). The declared graph routes rw only through em→rw. A reader walking from dd's sentence alone derives dd⇐{em, rw}; with em⇐rw the write order is the same (rw, em, dd), so no second order or terminal state results. This is not "two alternative writes" but a conjunction, so it is not RED.
   - "the borrower does not bear" is resolved only by reading em's and rw's rules. The sentence states it openly at the right strength.

Other ordering sentences in the extended rules: lf's and rw's "owed as soon as / once the loan has funded" (a closing state, not another problem), and em's/lf's internal day-window sentences. None states an order between problems that grounds no declared edge.

Base sentences that state a cross-problem order: `funding_authorization` "an expired lock must be relocked first". No task tree rests on it. This is an observation, per check 6.

### override_declarations

Sentence-by-sentence against `base_policy_refs`. Abbreviations used below:
- PDI = `funding_per_diem_interest`
- DR = `funding_dispute_resolution`
- WR = `funding_wire_returns`
- PDI-daily = the PDI sentence "daily_interest_amount is loan_amount times note_rate percent divided by per_diem_day_count_basis, rounded to per_diem_daily_rounding_decimals". Its formula binds the closing's own `loan_amount` / `note_rate` (holding table `closings`; event fields "total note amount being funded", "note interest rate").

**lf** (refs PDI, DR):
- The late-day refund sentence and "at the same daily amount" are both named in `overwrite`.
- Inherited and followed: "within per_diem_refund_business_days", dedup ("A charge that already carries a late-funding refund is not refunded again"), and "Each refund names the charge entry".
- Clean.

**sf** (ref PDI):
- PDI-daily is named.
- Inherited: "When funding is earlier than estimated, the shortfall is never billed after closing". The rule follows it, but compute breaks it (F-G4).
- PDI "interest_amount is daily_interest_amount times interest_days" belongs to the at-closing charge. sf's payment row records the latest charge's full period and day count at the shortfall per diem, but an amount ≠ days × per diem. Observation: ledger-row invariant, scoped to at-closing charges.

**rw** (refs PDI, DR, WR):
- `overwrite: []`.
- rw prices lost days at its own per diem ladder: the loan file's financed amount × the lock's rate, or the closing-record per diem, or the charge's daily amount.
- Under PDI-daily, the per diem of any `funding_per_diem_refunded` entry (PDI's subject includes it; the event field reads "per diem interest used: loan amount times note rate divided by the day-count basis") is the closing record's `loan_amount × note_rate / 365`.
- **Finding F-G1: undeclared override** of PDI-daily. The tell: sf and fm declared overwrites of exactly this sentence for their own per diem, and lf declared "at the same daily amount". So the author knew the sentence governs per diem figures. rw does not name it.

**em** (refs PDI, DR):
- Names "when disbursement moves into the next month, every day collected for the earlier month is refunded".
- Its `replaced_by` describes only the funds-out treatment, while the rule also strikes the re-send-window days. Observation: the replacement text understates the override, but the rule is unique.
- Its per diem ladder departs from PDI-daily without naming it. Same **F-G1**.

**fm** (ref PDI):
- Names "Interest accrues from the disbursement date." and PDI-daily. Clean.
- fm's post-closing charge for the funding month contradicts no PDI sentence.

**dd** (ref DR):
- Names only "any excess is refunded (refund_issued, refund_amount equal to the excess)".
- **Finding F-G2: undeclared override (anonymous intermediate).**
  - DR: "A per_diem_overcharge or late_funding dispute is decided by recomputing prepaid interest **under the per diem policy** from the recorded disbursement_date".
  - dd: "…decided by recomputing the prepaid interest the closing's loan owes from the recorded disbursement date…". dd then prices owed days at its own rate/amount ladders, not under PDI-daily.
  - The base sentence is rewritten without the "under the per diem policy" clause, and it is not named in `overwrite`.
  - PDI-daily itself is overwritten twice with two different replacements (sf: "The shortfall per diem is …"; fm: "The per diem of the funding-month interest is set from how the closing charge was priced: …"). So "the per diem policy" that DR points at has no unique merged meaning for a dispute recomputation.
- **Finding F-G3: undeclared override.**
  - DR: "A late_funding dispute never earns compensation beyond the interest refund."
  - dd covers "a per diem overcharge or late-funding dispute" and adds "Interest on the excess, where a rule below grants it, … is added to the refund."
  - For a `late_funding` dispute in a record-differs or late-decision tier, the two give different refund_amounts. The sentence is not named.

Which task each finding bears on:
- F-G1 and F-G2: task 1 (rw, em, dd are in its tree). The consequence is demonstrated in `1.md`.
- F-G3: no current task, because task 1's filing is `per_diem_overcharge`.
- F-G4 and F-G5: no current task (neither world has early funding or lf funds-out tier 2).

### factor_ladders

The declared counts all meet the bounds: every task has a multi-source factor, and the lock and loan cross-difficulty factors exist.

| policy | factors (effect) | param / method | cross_difficulty |
|---|---|---|---|
| lf | rate_source (P), accrual_base (P), resend_allowance (P), funds_out_rule (M), correction_window (M) | 3 / 2 | lock, loan, loan |
| sf | rate_source (P), accrual_base (P), measured_days (M), record_absorption (P) | 3 / 1 | lock, loan, loan |
| rw | rate_source (P), accrual_base (P), resend_allowance (P), recall_attribution (M), per_diem_source (M) | 3 / 2 | lock, loan, loan |
| em | rate_source (P), accrual_base (P), funds_out_rule (M), correction_window (M), per_diem_source (M) | 2 / 3 | lock, loan, loan |
| fm | rate_source (P), accrual_base (P), interest_start (M), per_diem_source (M) | 2 / 2 | lock, loan |
| dd | rate_source (P), accrual_base (P), charge_scope (M), owed_days_rule (M), excess_interest_rate (P), excess_interest_days (M) | 3 / 3 | lock, loan |

Every ladder has three tiers stated in the rule (verbatim, as checked under rule_compute_equivalence), implemented in its `decides` binding, with disjoint binding sets and `decides` ≠ `result`. Every fall-through equals its factor `baseline`, and every `baseline` is the baseline.rule statement for that input. One exception: rw (F-G9 below).

Structural findings:

- **F-G7, `*_rate_source` (all six policies): two tiers select one value.**
  - Tier 1 is "the new rate on the latest relock entry"; tier 2 is "the rate the lock currently holds".
  - Under the lock charter, a relock fee entry triggers `lock_relocked` with `map: {new_rate: locked_rate}` (lock.yaml lines 597-599), and a float-down triggers `lock_repriced` with `map: {locked_rate: new_rate, float_down_used: true}` (lines 636-638). Both tiers' values are therefore `rate_locks.locked_rate` whenever the selecting entry is the lock's latest repricing.
  - The tiers diverge only when a later repricing has superseded the relock. Tier 1 would then price at a superseded rate, which is not a treatment a lender publishes.
  - The ladder is effectively two tiers: "lock repriced after the closing record opened → the lock's current rate; otherwise → the closing's note rate".
  - In addition, the selected value is stamped on the seed as `rate_locks.locked_rate`.
- **F-G8, `*_accrual_base` (all six policies): two tiers select one value, stamped.**
  - Loan charter `loan_upfront_program_fee` (loan.yaml lines 1811-1817): "Where the program carries an upfront_program_fee_pct … loan_amount equals base_loan_amount plus base_loan_amount times upfront_program_fee_pct percent, rounded to the cent. A VA borrower with funding_fee_exempt true pays no funding fee and loan_amount equals base_loan_amount."
  - So tier 1's value ("base loan amount plus that base amount times the upfront fee percent") and tier 2's value ("the file's base loan amount") are each, by definition, `loan_files.loan_amount`. One tier, "the loan file's loan amount", has been written as two.
  - The outcome is a field on the seed, `loan_files.loan_amount`. sf's own rule even names it ("the loan file's loan amount"). Reading it and applying the ladder cannot be told apart by the score in any consistent world.
- **F-G10, `fm_interest_start`: tier 2 and the fall-through select the same value.**
  - Tier 2 is "it starts on the date that wire went out". The fall-through is "it starts on the recorded disbursement date".
  - The wire that funded the loan is by definition dated on the disbursement date: base `funding_authorization`: "The disbursement_date is the wire date". `fm_wire_count` / `fm_wire_time` filter `wire_date=F('disbursement_date')`.
  - Compute makes it literal: `… else (0 if (fm_wire_count > 0 and fm_wire_time <= P('wire_cutoff_time')) else 0)`.
  - The fall-through condition "no funding wire is on record" also holds of no funded closing (`funding_completed` is triggered by `funding_wire_sent`).
  - Effective ladder: two tiers.
- **F-G11, `dd_excess_interest_days`: fall-through unreachable.**
  - The fall-through is "otherwise, where no filing date is on record, there are none". Every customer reaching this write has a filing: dd decides "the filing", and `filed_date` is a field of every `funding_dispute_filed` row.
  - Tiers 1 and 2 (decision ≤ / > the acknowledgment deadline) are complementary and cover every such customer. The ladder has two live tiers.
- **F-G9, rw baseline is not self-sufficient.**
  - `baseline.rule` = "A closing whose wires show no Larkspur-side recall has no lost days. Each lost day is refunded at the daily amount the closing charge used. The returned-wire refund is the lost days times the per diem of the refund, rounded half up to the cent."
  - It states the lost days only for a closing *without* a recall. For any closing that has a Larkspur-side recall (the only closings rw's scope covers), baseline.rule gives no lost-day count. The factor baseline `rw_lost_days: '0'` is therefore not "what the baseline states for that input".
  - The demonstration is in `1.md`.
- **Observation O-G2, label.** The `*_per_diem_source` factors (rw, em, fm) are labelled `method`, but tiers 1 and 2 feed different inputs into one formula (amount × rate / 100 / basis) and tier 3 substitutes a recorded number. This reads as a `parameter`. It is verdict-neutral here, because the affected computations already fail on F-G7/F-G8/F-G10.
- **Observation O-G3, `fm_interest_start` tier 1 premise.** Tier 1 rests on a wire "released after the closing method's wire cutoff time". Base `funding_authorization` says a request is "wired that day by wire_cutoff_time; a later request is wired the next business day". So the tier-1 world is one the base charter says does not arise.

Surviving factors per policy after F-G7, F-G8, F-G10 and F-G11 (structure only; weight is per task):

| policy | survivors | count | parameter | method | verdict |
|---|---|---|---|---|---|
| lf | resend_allowance (P), funds_out_rule (M), correction_window (M) | 3 | 1 | 2 | below 4 and below 2 |
| sf | measured_days (M), record_absorption (P) | 2 | 1 | 1 | fails |
| rw | resend_allowance (P), recall_attribution (M), per_diem_source (M) | 3 | 1 | 2 | fails |
| em | funds_out_rule (M), correction_window (M), per_diem_source (M) | 3 | 0 | 3 | fails |
| fm | per_diem_source (M) | 1 | 0 | 1 | fails |
| dd | charge_scope (M), owed_days_rule (M), excess_interest_rate (P) | 3 | 1 | 2 | fails |

Cross-difficulty factors surviving: `lf_funds_out_rule` (loan), `sf_record_absorption` (loan), `rw_recall_attribution` (loan) and `em_funds_out_rule` (loan). Whether each one's tier is actually decided by the other product's rows in a given world is a per-task question.

### findings

| id | class | summary | bears on |
|---|---|---|---|
| F-G1 | SOURCE-POLICY RED (undeclared override) | rw and em price refunded days at their own per diem ladder; base PDI-daily, not named in their `overwrite`, fixes a refund's per diem as the closing's `loan_amount × note_rate / basis` | task 1 (rw, em) — demonstrated in 1.md |
| F-G2 | SOURCE-POLICY RED (undeclared override, anonymous intermediate) | DR "recomputing prepaid interest under the per diem policy" is rewritten by dd without the clause and not named; dd's owed per diem departs from the per diem policy | task 1 (dd) — demonstrated in 1.md |
| F-G3 | SOURCE-POLICY RED (undeclared override) | DR "A late_funding dispute never earns compensation beyond the interest refund" vs dd's interest on the excess for late_funding disputes | no current task (task 1 is per_diem_overcharge); moves no scored value here |
| F-G4 | SOURCE-POLICY RED (rule/compute) | sf rule "A shortfall that comes only from funding earlier than estimated is never collected" has no compute; `sf_days` tier 2 bills it | no current task (task 0 funded late); moves no scored value here |
| F-G5 | SOURCE-POLICY RED (rule/compute) | lf funds-out tier 2 "the borrower's latest document" vs `lf_doc_day` with no borrower-answered filter | no current task; moves no scored value here |
| F-G6 | SOURCE-POLICY RED (prerequisite declaration) | dd→em `effect`/`gate` claims em's refund removes days from `dd_owed_days`; no refund row ever enters `dd_owed_days` | task 1; moves no scored value (the edge carries weight through `dd_held`) |
| F-G7 | SOURCE-FACTOR RED (unreal ladder: two tiers one value, stamped) | `*_rate_source` tiers 1/2 both equal `rate_locks.locked_rate` by the lock charter's trigger maps | tasks 0 and 1 — demonstrated per task |
| F-G8 | SOURCE-FACTOR RED (two tiers one value; stamp) | `*_accrual_base` tiers 1/2 both equal `loan_files.loan_amount` by the loan charter | tasks 0 and 1 — demonstrated per task |
| F-G9 | SOURCE-FACTOR RED (incoherent baseline) | rw baseline.rule gives no lost-day count for a closing with a recall | task 1 |
| F-G10 | SOURCE-FACTOR RED (two tiers one value) | `fm_interest_start` tier 2 ≡ fall-through (compute `0 … else 0`) | task 1 |
| F-G11 | SOURCE-FACTOR RED (unreal ladder) | `dd_excess_interest_days` fall-through unreachable; two live tiers | task 1 |
| O-G1 | observation | dd's second prerequisite state is produced jointly by rw and em; the declared graph routes rw only via em | task 1 |
| O-G2 | observation | `*_per_diem_source` labelled method but select a per diem figure | task 1 |
| O-G3 | observation | `fm_interest_start` tier 1 premise (wire after cutoff) contradicts base `funding_authorization` | task 1 |
| O-G4 | observation | lf and em tools both stamp `refund_reason=funding_later_than_estimated`; dd's tool books a refund naming no charge when the filing names none (base "Each refund names the charge entry it corrects") | tasks 0, 1 (no scored value) |
| O-G5 | observation | base `funding_authorization` "an expired lock must be relocked first" states a cross-problem order; no tree rests on it | none |

## closing_checklist

Written after both reveals (2026-10-13T05:56Z). The section above is pre-reveal and unchanged. Status: **the difficulty does not close.** Not all four relationships PASS.

| item | status |
|---|---|
| per-task files | `0.md` and `1.md` match tasks 0 and 1 one-to-one; first revision; each has source_derivation_frozen before source_gt_comparison |
| comparison sections all PASS | **no**: task 0 SOURCE-FACTOR RED; task 1 SOURCE-POLICY + SOURCE-FACTOR + SOURCE-TASK RED |
| coverage and scopes | 6/6 extended policies covered; scopes {lf, sf} and {rw, em, fm, dd} are disjoint and match the revealed `charter_scope` |
| task tools and uuid8s | tools closed against GT; uuid8s independent |
| task 0 tree | 1 prerequisite problem, 1 value_input, owner=user present (sf), acyclic |
| task 1 tree | 3 prerequisite problems, 3 value_input, owner=user present (fm), acyclic |
| difficulty-wide graph | DAG {sf→lf, em→rw, dd→fm, dd→em}; no cross-task cycle |
| factors | **fail**: F-G7/F-G8 in every computation, F-G9/F-G10/F-G11 in task 1, the loan-charter contradiction on task 1's evidence row, and counts below bounds in all six computations |
| baselines | every baseline gives a definite fall-back ≠ gold, except rw (F-G9) |
| instantiation gates | re-run on the final form is not performed by this auditor (artifacts unchanged since the coordinator's snapshot; extended/task_tools hashes verified) |

Observation added at reveal, about GT proof fields only:
- em `baseline_result` 402.10 is the all-factor-baseline figure. The baseline.rule-alone figure is 562.94. Both are ≠ gold.
- Task 1's closure text "the remaining days 2026-09-24..2026-09-27 are borne by the borrower" is contradicted by the gold dd refund, which returns them.

## revision_2

### charter_global_frozen (round 2)

- freeze time: 2026-10-13T15:13Z. Written before any round-2 GT was read.
- Inputs (hashes verified against the coordinator brief):
  - `funding.extended.yaml` sha256 `f4e6e842…a907` (CHANGED)
  - `task_tools.py` sha256 `c50df279…429ac9` (CHANGED)
- Both shared inputs changed, so every charter-global section below is re-derived in full. Nothing is carried forward.
- Read for this revision: base `funding.yaml` (unchanged, sha256 `5942c3cf…`); targeted reads of `loan.yaml` (VA turn times), `lock.yaml` (45-day lock confirmation days and desk cutoff) and `credit.yaml` (Hometown Heroes categories; credit_application_at_closing).
- Base copy: key-by-key equal to `blueprint/products/funding.yaml`.

### policy_conflict_scan (round 2)

Policies:
- lf: funding_ext_late_funding_refund
- sf: funding_ext_per_diem_shortfall
- rw: funding_ext_returned_wire_refund
- fm: funding_ext_funding_month_interest
- dd: funding_ext_interest_dispute_decision
- rd: funding_ext_redraw_fee_balance (new)

em (funding_ext_earlier_month_refund) is removed. The six `(target_tool, computes)` pairs are distinct.

Edges:
- sf⇐lf (gate `sf_days`)
- fm⇐rw (gate `fm_open_days`)
- dd⇐fm (gate `dd_day`)
- dd⇐rd (gate `dd_owed`)

All are state form and value_input. The graph is acyclic.

How the policies divide closings:
- lf applies only when disbursement is within the charge collected at closing. fm applies only when disbursement is after it. They are disjoint.
- rw is bounded to the charge period. Its rule hands non-lost unfunded days to "the rules for funding late", never to itself.
- The shortfall per diem overwrite (sf) and the funding-month per diem overwrite (fm) now exclude each other in so many words ("prices a per diem shortfall only and never funding-month interest" / "and never for a per diem shortfall").

`refund_reason=funding_later_than_estimated` is now stamped only by lf's tool. The two charge writers are sf (period of the charge collected at closing) and fm (from the disbursement date), which do not overlap. rd's tool is the only fee-ledger writer.

### rule_compute_equivalence (round 2)

- Mechanical: every `compute_basis` value is verbatim in its rule. Every binding has a basis, every baseline sentence is in the rule, and every factor `decides` an existing binding.
- Sentence sweep: every compute branch has a rule tier and the reverse holds, including:
  - lf's overlap de-duplication ("A day the treatment of funds that were out already takes out is not taken out again" ⇄ `lf_overlap`)
  - sf's lower bound ("a day before the first day of the charge … never counts" ⇄ `disbursement_date >= sf_chg_from`)
  - rw's "without both there are no lost days" ⇄ the `rw_first != None and rw_end_off != None` guard
  - dd's "closing fees still owed" ⇄ `dd_owed`
- Residual observations:
  - `lf_out_days` checks for *an* own-error return plus *a* wire on the estimated date, but not that the returned wire is that wire. Harmless in both worlds.
  - `sf_cutback` sums every `credit_reduced/exceeds_eligible_costs` row of the customer rather than "a credit … cut back at closing". Harmless here.

### action_binding_and_uuids (round 2)

- New tool `book_redraw_fee_balance_4ee9eceb`. Its uuid8 is independent of the other five, which are unchanged.
- No docstring names another tool, uses an ordering word, or carries an example figure (no gold value appears in any docstring).
- Rounding: every body now uses `_Money.cents` (half away from zero, which is half-up for positive amounts), matching the docstrings.
- No body reads other rows to accept or refuse a call.
- The dispute tool now takes `disputed_entry_id` and books its refund naming that charge. Base "Each refund names the charge entry it corrects" is now met, so the round-1 O-G4 half about this is closed.

### prerequisite_graph and prerequisite_sentences (round 2)

Every `policy_source` is verbatim in the blocked rule and absent from the depended-on rule. Each edge is "only after" or "not … until", in state form, with no tool name, id or snake token.

| edge | sentence (abridged) | writers of that state | effect claim checked against compute |
|---|---|---|---|
| sf⇐lf | "…ledger carries the late-funding refund owed for the unfunded days that fall in the month the loan funded" | lf only (the only `funding_later_than_estimated` stamp) | true (`sf_days` tier 1, `sf_held`) |
| fm⇐rw | "…ledger carries the returned-wire refund owed for the days a Larkspur-side return cost" | rw only | true (`fm_open_days`) |
| dd⇐fm | "…ledger carries a charge for the month in which the loan funded" | fm only (sf's charge covers the period of the charge collected at closing) | true (`dd_day` tier 1) |
| dd⇐rd | "…closing's fee ledger carries the redraw fee balance the redraw schedule leaves on the closing's latest redraw" | rd only | see R2-P2: the waited-on state is not stable under rd's own object definition |

No rule states a cross-problem order that grounds no edge. Base `funding_authorization` "relocked first" remains an observation (O-G5, unchanged base).

### override_declarations (round 2)

- **lf.**
  - OW1 restates "at the same daily amount" and adds the take-out treatments.
  - OW2 scopes DR "A late_funding dispute never earns compensation beyond the interest refund" to "Apart from the late-booking interest …". The still-in-force part is kept.
  - lf prices at the charge's daily amount, which is base.
- **sf / fm.** Both overwrite PDI-daily with mutually exclusive scopes. fm's second overwrite keeps "every day collected for the earlier month is refunded" and adds setoff.
- **rw.** Its overwrite keeps the base sentence and adds the hand-off. rw prices at the charge's daily amount, which is base.
- **dd.** It overwrites the DR recompute sentence for per diem overcharge disputes only, and keeps it for late-funding disputes.
- **rd.**
  - OW1 replaces "the redraw is charged doc_redraw_fee when the reason is the borrower's (…)" with the format ladder. The borrower-reason condition drops out of `replaced_by`, but rd's rule reasserts it ("each one a redraw whose reason was the borrower's") and base "free when Larkspur caused it" still stands. Observation.
  - OW2 replaces only the list item "doc_redraw_fee once per borrower-caused redraw".
  - **R2-P1 (SOURCE-POLICY RED, undeclared override).** The head of that same base sentence remains in force and unnamed: `funding_closing_fees` "Closing fees follow the closing method's schedule **and are charged on the Closing Disclosure**". rd books a further `doc_redraw_fee` charge on a funded closing after consummation ("booked as a further doc redraw fee charge … recovers it only by setoff"). Under the in-force base clause, no closing fee is charged off the Closing Disclosure, so the redraw fees stand at what the disclosure charged and nothing further is booked. Under rd, a balance is booked and then set off by dd. The scored rd `amount` and dd `refund_amount` differ between the two readings (demonstrated in `1.md`).

### factor_ladders (round 2)

| policy | factors (effect) | P / M | cross_difficulty |
|---|---|---|---|
| lf | resend_allowance (P), funds_out_rule (M), correction_window (M), late_booking_rate (P), late_booking_span (M) | 2/3 | — |
| sf | measured_days (M), amount_record_allowance (P), rate_record_allowance (P), credit_cover (P) | 3/1 | loan, lock, credit |
| rw | first_lost_day (M), resend_days (P), rereview_days (P), relock_days (P), last_lost_day (M) | 3/2 | loan, lock |
| fm | setoff_per_diem (P), setoff_rule (M), late_payment_charge (P), payment_channel (M) | 2/2 | loan |
| dd | charge_scope (M), standing_day_refund (P), excess_interest_rate (P), excess_interest_days (M), fee_setoff (M) | 2/3 | lock |
| rd | package_format (P), rush_addon (P), rider_addon (P), program_addenda (P), signer_sets (P), repeat_step (M) | 5/1 | loan ×3 |

- Every ladder has three tiers stated in the rule and implemented in its binding, with pairwise-distinct outcomes.
- The round-1 collapsed ladders are gone: rate_source, accrual_base, interest_start and per_diem_source.
- dd_excess_interest_days' fall-through ("decided within the acknowledgment days") is now reachable.
- Every fall-through equals its factor baseline. Every baseline.rule gives a definite figure, with the observation O2-B below.

Structural findings:

- **R2-F1 (SOURCE-FACTOR RED, mislabelled effect): `rd_repeat_step` is labelled `method`.**
  - Its tiers multiply one sum by `third_redraw_multiplier` (1.5), `second_redraw_multiplier` (1.25) or nothing (×1): `RND(rd_sum * K('third_redraw_multiplier'), 2)` / `RND(rd_sum * K('second_redraw_multiplier'), 2)` / `RND(rd_sum, 2)`.
  - That is a different number in the same formula, so it is a `parameter`.
  - rd then has 6 parameters and 0 methods, failing the "at least 1 method" bound.
- **R2-F2 (SOURCE-FACTOR RED, unreal ladder): `fm_late_payment_charge`.**
  - The tiers charge $25 / $10 / nothing by how many business days after the **disbursement date** the borrower pays interest that Larkspur never billed at closing and never set a due date for.
  - A mortgage lender's late charge is weighed against a payment's due date and grace period, not against the date the loan funded. Here the time-since-disbursement condition charges a borrower for the lender's own delay in billing.
  - No lender publishes that treatment. With R2-F2 struck, fm keeps 3 factors (1 parameter), below both bounds.
- **R2-F3 (SOURCE-FACTOR RED, unreal outcome): `dd_fee_setoff` tiers 1 and 2, together with rd's whole computation.**
  - They recover a lender redraw fee priced above the amount charged on the Closing Disclosure, after consummation, by withholding a refund owed to the borrower.
  - A lender's own fees are zero-tolerance against the Closing Disclosure. An under-collection after consummation is the lender's loss, not something it recovers by setoff.
  - So the treatment the setoff tiers apply is not one a residential mortgage lender would publish.
  - Even striking dd_fee_setoff, dd keeps 4 factors (2 P / 2 M), so dd's count still holds. The defect lands on rd's and dd's scored values via R2-P1.
- **O2-B (observation).** fm's and rd's baseline.rule mention components they do not define: fm's "less the setoff, plus any late payment charge and any payment channel charge", and rd's "plus the rush, rider, program addenda and signer set add-ons … repeat-redraw step". Read as absent, these give 2,368.09 and 0.00, both ≠ gold and both equal to the factor baselines. Unlike round-1 F-G9, the baseline is not silent on the case the policy covers, so this is not RED.
- **O2-C (observation).** `rd_package_format`: Hybrid and RON closings require E-SIGN consent before documents are drawn (base `funding_method_eligibility`, `esign_consent_required: true`). The consent clause of tiers 1 and 2 is implied by the method, so every e-closing lands on tier 1 or 2 and its variant `doc_redraw_fee` (150) never prices an e-closing redraw. This is a declared override, so it is an observation.

### findings (round 2, charter-global)

| id | class | summary | bears on |
|---|---|---|---|
| R2-P1 | SOURCE-POLICY RED (undeclared override) | base `funding_closing_fees` "…and are charged on the Closing Disclosure" is not named; rd books a post-consummation doc_redraw_fee charge | task 1 (rd, dd) |
| R2-P2 | SOURCE-POLICY RED (self-referential object / unstable prerequisite state) | rd's "redraws … are the doc redraw fee charges on the closing that no reversal names" includes rd's own booked balance row. On the post-write world the "latest redraw" is that row, the schedule leaves a further balance, and dd's waited-on state reads unmet again. rd has no "booked once" sentence. | task 1 |
| R2-F1 | SOURCE-FACTOR RED (mislabel → 0 method) | rd_repeat_step is a multiplier selector | task 1 |
| R2-F2 | SOURCE-FACTOR RED (unreal ladder → fm count 3) | fm_late_payment_charge is keyed to days since disbursement on an unbilled amount | task 1 |
| R2-F3 | SOURCE-FACTOR RED (unreal outcome) | dd_fee_setoff / rd recover a post-CD fee increase by setoff | task 1 |
| O2-A | observation | the lf refund row (5 days × 44.97 ≠ 224.92, interest included) and the sf payment row (21 days × 47.63 ≠ amount) break PDI "interest_amount is daily_interest_amount times interest_days" (at-closing scope); the fm row folds the $10 late charge and the card fee into a prepaid-interest charge, outside the closing-fee schedule (base "A fee not in the method's schedule … is reversed in full" arguably reaches them) | tasks 0 and 1, no scored value |
| O2-B, O2-C | observation | above | task 1 |
| O-G5 | observation (carried, base unchanged) | base "relocked first" | none |

### round-1 closure status

| round-1 id | status |
|---|---|
| F-G1 | closed: rw prices at the charge's daily amount; em removed |
| F-G2 | closed: dd's overwrite scoped |
| F-G3 | closed: lf OW2 |
| F-G4 | closed: sf lower bound |
| F-G5 | closed: tier removed |
| F-G6 | closed: all four effect claims verified |
| F-G7 / F-G8 | no longer apply (ladders removed; values read directly) |
| F-G9 | closed: rw baseline is explicit |
| F-G10 | no longer applies |
| F-G11 | closed |
| VVOE row | no longer applies (task 1 rebuilt; no loan_conditions) |
| O-G1 / O-G2 / O-G3 | no longer apply |
| O-G4 | closed |
| O-G5 | unchanged (base) |

### closing_checklist (round 2)

Written after the round-2 reveals.

| item | status |
|---|---|
| per-task files | carry revision_2 with freeze before reveal |
| scope | 6/6 policies covered; scopes {lf, sf} and {rw, fm, rd, dd} disjoint and matching `charter_scope` |
| uuid8s | independent; the new rd tool is independent too |
| task 0 tree | n=1, 1 value_input, user write present |
| task 1 tree | n=3, 3 value_input, user write present |
| difficulty-wide graph | acyclic |
| factor bounds | task 0 meets them; task 1 fails on rd (0 methods) and fm (3 factors, 1 parameter) after the round-2 REDs |
| gates | not re-run by this auditor; coordinator snapshot is green except pre-KB traceability |
| difficulty status | **does not close** |

task0=PASS  task1=SOURCE-POLICY RED + SOURCE-FACTOR RED + SOURCE-TASK RED
charter=R2-P1, R2-P2, R2-F1, R2-F2, R2-F3

## revision_3

### input gate (round 3)

`/tmp/erl0059_coord/gates.sh funding_and_disbursement_disputes --trace`:

| gate | result |
|---|---|
| EXTENDED | OK (extended_policies=6, cross-cat=5, tasks=2) |
| TASK TOOL CONTRACT | OK (6 tools) |
| REPLAY | OK (0.json 15/15 det; 1.json 20 acts, closure 19=19) |
| SOLVABILITY | OK |
| COMPUTE | OK (history_rows_max=13, branches_max=102) |
| GROUNDING | OK |
| SCOPE | OK |
| TRACEABILITY | NOT OK, one miss: `1.json: 'refund_redraw_fee_excess_c6a6aba4' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source` |

The only traceability miss is the unlock tool name of the new tool, so it is out of scope per the brief. Input accepted.

Views from `mkviews.py`:
- `0.view.json` sha256 `b3f66377…ad9a3d` (unchanged from round 2)
- `1.view.json` sha256 `09468b99…fd2cc` (changed)

Charter and tools:
- `funding.extended.yaml` `00e34e33…7aa2` (CHANGED)
- `task_tools.py` `953e2549…6074` (CHANGED)
- base `funding.yaml` `5942c3cf…` (unchanged; key-equal)

Both shared inputs changed, so every charter-global section is re-derived. Also read: `audits/render_source/funding_and_disbursement_disputes/render_funding_r1.md` (9 source items).

### charter_global_frozen (round 3)

Freeze time 2026-10-13, written before any round-3 GT was read.

Policies:
- lf: funding_ext_late_funding_refund
- sf: funding_ext_per_diem_shortfall
- rw: funding_ext_returned_wire_refund
- fm: funding_ext_funding_month_interest
- dd: funding_ext_interest_dispute_decision
- rd: funding_ext_redraw_fee_refund (replaces round 2's redraw fee balance)

The rd tool is `refund_redraw_fee_excess_c6a6aba4`: a `funding_fee_reversed` on the doc redraw fee charge it names.

Edges, all state form and value_input:
- sf⇐lf (sf_days)
- fm⇐rw (fm_open_days)
- fm⇐rd (fm_fee_credit)
- dd⇐fm (dd_day)

The graph is acyclic. Every `policy_source` is verbatim in its own rule and absent from the depended-on rule. Each waited-on state has exactly one writer:
- the late-funding refund stamp: lf only
- the returned-wire refund: rw only
- the `funding_fee_reversed` / `not_in_fee_schedule` row: rd only
- the charge from the disbursement date: fm only (sf's charge spans the period of the charge collected at closing)

Every `effect` claim holds against compute.

**rule ⇄ compute.**
- Mechanical: every basis is verbatim, every binding has a basis, every baseline sentence is in the rule, and every branch has a tier.
- The renderer's 9 source items, re-checked against the round-3 text:
  1. Closed. sf's and fm's overwrites now keep "Every prepaid interest entry other than a per diem shortfall payment or a funding-month interest payment, the charge collected at closing included, keeps the per diem policy's daily amount". The two siblings are worded identically and exclude each other.
  2. Closed. rd's overwrites keep the borrower-reason clause, "a redraw Larkspur caused stays free", "once per borrower-caused redraw", and "no redraw fee is ever charged or raised after closing".
  3. Closed. "the redraws the schedule counts are every doc redraw fee charge" ⇄ `rd_count`. "a doc redraw fee charge that a reversal already names is not reversed again" ⇄ `rd_rev`.
  4. Closed. The payment is recorded "with what the borrower pays as its amount" ⇄ `result`.
  5. Closed. The credit is the one applied to prepaid items on the signing date, and its cut-back is on the signing date ⇄ `sf_credit_id` / `sf_cutback`.
  6. Closed. "The filing decided is the closing's latest dispute filing still marked pending; a filing that a decision record already names is not decided again" ⇄ `dd_fid` / `dd_done`.
  7. Closed. The fee setoff was removed. The outcome sentence ("A decision with a refund above zero is issued as refund_issued …; a decision with nothing to refund is denied as correct as charged with an amount of zero") is explicit.
  8. Closed. `fm_mbf` now gives the length of the month before the first payment for every month, with a Feb 28/29 rule.
  9. Closed. `lf_src_day` checks that the returned wire is the one sent on the estimated date.
- Residual observation: rw's relock tier is anchored on `original_expiration_date`, not the expiration in force at the return. On a lock extended before the return and relocked later, the tier would count relock days for a lock that never lapsed in the span. This is not exercised in any world.

**Tools.**
- uuid8 `c6a6aba4` is independent.
- No docstring carries an ordering word or a gold figure. The only figure is the generic "0.00 when the dispute is denied".
- Rounding is half-up via `_Money`.
- No body judges a prerequisite.
- Observation (O3-A): the dispute tool books its refund row with `daily_interest_amount=0.0` and `interest_days=0`. The in-force sentence restored in sf/fm ("Every prepaid interest entry other than a per diem shortfall payment or a funding-month interest payment … keeps the per diem policy's daily amount") would give that row 86.07 on task 1. It is a tool-written terminal field, not an agent argument, so it is an observation.

**Overwrites** (sentence by sentence against base_policy_refs):
- lf, sf, rw, fm: as round 2, scoped, with still-in-force parts kept.
- dd: the overwrite of the DR recompute sentence keeps the late-funding branch "still decided by recomputing prepaid interest under the per diem policy".
- rd: OW1 and OW2 are scoped and keep the in-force parts. The rd reversal is partial (the excess above schedule) under `reversal_reason=not_in_fee_schedule`. Base `funding_closing_fees` says "A fee not in the method's schedule … is reversed in full", but that sentence concerns fee types, and rd's specific overwritten clause governs the redraw amount. Observation (O3-B): the `not_in_fee_schedule` stamp invites that reading.

**New findings.**

- **R3-P1 (SOURCE-POLICY RED, internal conflict on the late-funding branch).** dd says "a late-funding dispute is still decided by recomputing prepaid interest under the per diem policy from the recorded disbursement date". The per diem policy's late-day sentence is overwritten by lf (late days the funds-out and after-return treatments take out are not refunded; "Apart from the late-booking interest …, a late-funding dispute earns no compensation beyond the interest refund"). But dd's own excess tier for a late-funding dispute is "the late days of the disputed charge … less every day the prepaid interest refunds naming the charge return … times the charge's daily amount", which has no take-out.
  - Same situation, two answers. On a closing like task 0's after lf has booked 5 of 11 late days, dd's tier gives (11 − 5) × 44.97 = **269.82**, which refunds exactly the funds-out and window days lf excludes. The per diem policy as merged gives **0.00**.
  - No current task: task 0 has no filing, and task 1's filing is `per_diem_overcharge`. It moves no scored value in this suite.
- **R3-P2 (SOURCE-POLICY RED, non-interest filings).** dd selects "the closing's latest dispute filing still marked pending" of any type. Its excess fall-through says "otherwise the excess is zero, since a closing fee or returned-wire dispute is decided by other rules", and then "a decision with nothing to refund is denied as correct as charged".
  - So a pending `closing_fee_disputed` or `returned_wire_interest` filing is decided by dd as denied_correct_as_charged with 0.00. Base DR, not overwritten for those types, says such a dispute "reverses the fee (fee_reversed) when the fee is outside the method's schedule", and that a returned-wire interest dispute is refunded when the return was Larkspur-side.
  - The dd text itself says those filings belong to other rules. Same filing, two outcomes.
  - The same fact makes `dd_dispute_type_rule`'s fall-through a treatment no lender gives for those filings (a fee dispute denied without looking at the fee). So it is also a SOURCE-FACTOR defect of that ladder; structure is recorded here, and with that factor struck dd still has 4 factors (2 P / 2 M).
  - No current task has such a filing, so no scored value moves.

**factor_ladders (round 3).**

| policy | factors (effect) | P / M | cross_difficulty |
|---|---|---|---|
| lf | resend_allowance (P), funds_out_rule (M), correction_window (M), late_booking_rate (P), late_booking_span (M) | 2/3 | — |
| sf | measured_days (M), amount_record_allowance (P), rate_record_allowance (P), credit_cover (P) | 3/1 | loan, lock, credit |
| rw | first_lost_day (M), resend_days (P), rereview_days (P), relock_days (P), last_lost_day (M) | 3/2 | loan, lock |
| fm | setoff_per_diem (P), setoff_rule (M), payment_channel (M), card_surcharge_rate (P) | 2/2 | loan, loan |
| dd | charge_scope (M), dispute_type_rule (M), standing_day_refund (P), excess_interest_rate (P), excess_interest_days (M) | 2/3 | lock |
| rd | package_format (P), rush_addon (P), rider_addon (P), program_addenda (P), signer_set_pricing (M), repeat_fee (P) | 5/1 | loan, loan, loan |

- Every ladder has 3 tiers with distinct outcomes, stated in the rule and implemented in compute.
- Labels are honest:
  - `rd_signer_set_pricing` multiplies by sessions, or adds a per-signer fee, or leaves the price as it stands: a real method change. This closes R2-F1.
  - `rd_repeat_fee` is now an added parameter fee.
  - `fm_card_surcharge_rate` is a parameter.
- Realism:
  - `fm_card_surcharge_rate` follows real surcharge law: no card surcharge in CT, MA and ME, and a 2 % cap in CO.
  - The fm late charge is removed, which closes R2-F2.
  - The rd direction is now a refund of an over-charge applied against money the borrower owes. No post-closing charge remains, which closes R2-F3 and R2-P1.
  - The rd self-reference is gone: the redraw set counts charges only, and a reversal is not booked twice. This closes R2-P2.
- The only unreal tier is the dd fall-through in R3-P2.
- O2-B carries forward as an observation: fm's, rd's and dd's baseline.rule name components (setoff, redraw fee refunds, channel charge, add-ons, repeat fee, interest rate) without defining them, and read as absent each gives a definite figure ≠ gold.

**Round-2 closure:**

| id | status |
|---|---|
| R2-P1 | closed |
| R2-P2 | closed |
| R2-F1 | closed |
| R2-F2 | closed |
| R2-F3 | closed |
| O2-A | lf/sf rows: still observations. fm row: the late charge is gone and the channel is now declared "a payment processing charge, not a closing fee", so that part is closed. |
| O2-C | carried |
| O-G5 | carried (base) |

### closing_checklist (round 3)

- Both task files carry revision_3 with the freeze before the reveal.
- Coverage is 6/6, with scopes {lf, sf} and {rw, rd, fm, dd} disjoint and matching `charter_scope`.
- uuid8s are independent.
- Trees:
  - task 0: n = 1
  - task 1: n = 3, all value_input, user write fm
- The suite-wide graph is acyclic.
- Every computation has 4 to 6 factors with at least 2 P and 1 M. Task 0 has cross-difficulty factors on loan, lock and credit; task 1 on loan and lock. Every factor bears weight against an honest baseline.
- Gates (run this round): all OK except pre-KB traceability on the new tool's unlock name.

At reveal, R3-P2 was reclassified as policy-only and `dd_dispute_type_rule` stands (see `1.md` § revision_3).

Open charter REDs, not exercised by either task:
- **R3-P1:** dd's late-funding excess tier vs the per diem policy as overwritten by lf.
- **R3-P2:** dd's any-type filing selection decides closing-fee and returned-wire filings as denied_correct_as_charged, contrary to base DR.

The difficulty closes on both tasks but not on the charter.

task0=PASS  task1=PASS
charter=R3-P1, R3-P2

## revision_4

### input gate (round 4)

`gates.sh funding_and_disbursement_disputes --trace`:

| gate | result |
|---|---|
| EXTENDED | OK |
| TASK TOOL CONTRACT | OK |
| REPLAY | OK (0.json 15/15, 1.json 20 acts, closure 19=19) |
| SOLVABILITY | OK |
| COMPUTE | OK |
| GROUNDING | OK |
| SCOPE | OK |
| TRACEABILITY | NOT OK, one miss: "1.json: 'refund_redraw_fee_excess_c6a6aba4' (unlock_agent_discoverable_tool:tool_name) has NO verbatim source" |

The traceability miss is the unlock name of a tool that `docs/funding/` predates, so it is out of scope. Input accepted.

`mkviews.py`:
- `0.view.json` b3f66377… (unchanged)
- `1.view.json` 09468b99… (unchanged)

Charter and tools:
- `funding.extended.yaml` dce3a85f…f8a (CHANGED)
- `task_tools.py` b1cb4232…3e8b (CHANGED)

Both changed, so the charter-global section is re-derived. Base is key-equal.

### charter_global_frozen (round 4), 2026-10-13T16:06Z, before any round-4 GT was read

Mechanical checks: every basis is verbatim, every binding has a basis, every baseline sentence is in its rule, every overwrite's replaced_by is in its rule, and every edge sentence is verbatim.

Graph (all edges state form, value_input; acyclic):
- sf⇐lf (sf_days)
- fm⇐rw (fm_open_days)
- fm⇐rd (fm_fee_credit)
- dd⇐fm (dd_day)

Each waited-on state has a single writer, as in round 3.

**Round-3 REDs:**
- **R3-P1: closed.** dd now decides only "the closing's latest per diem overcharge filing still marked pending" (compute: `dd_fid … dispute_type='per_diem_overcharge'`). It adds: "A late-funding, closing-fee or returned-wire dispute is not decided under this rule: it stays under the dispute resolution policy's own rules, a late-funding dispute being decided under the per diem policy as the late-funding refund applies it." The late-funding excess tier is gone.
- **R3-P2: closed** by the same filing filter and sentence. A fee or returned-wire filing is never selected, and "where none is pending nothing is decided" ⇄ `dd_fid != None` in `result`.

**Round-3 observations:**
- O3-A closed: the dispute tool now records the disputed charge's daily amount, read from that charge row. This is a field fill, not a prerequisite check.
- O3-B closed: rd adds "a doc redraw fee is a fee the closing method's schedule carries, so the reversal in full of a fee the schedule does not carry never applies to it".
- The rw relock anchor is closed: the anchor is now "the lock's expiration before any relock, the new expiration date of its latest extension or its original expiration date where it was never extended" ⇄ `rw_ext_exp` / `rw_lock_exp`.

**dd's revised compute ⇄ rule.**

| rule | compute |
|---|---|
| standing-days ladder: after the charge → days less refunded days; within the charge → disbursement date through the end; before the charge → every day | `dd_standing` |
| refund per standing day: tier 1 "after the charge and no funding-month charge" → whole daily amount; tier 2 "that does not hold and the charge's daily amount is above the per diem the note supports" → the gap; otherwise zero | `dd_day` (note per diem = `dd_note_pd`) |
| interest-rate ladder no longer restricted by type | redundant now that scope is per diem overcharge only |

The baseline gives a definite 0.00 (all fall-throughs).

Factors: `dd_standing_days_rule` (M) replaces `dd_dispute_type_rule`. dd has 5 factors (2 P / 3 M), each with three distinct outcomes, and each realistic: an overcharge refunded only on days actually owed, at the gap to the note's per diem.

**Whole-charter sweep (round 4).**

- **Branch scope.** Every compute branch has a rule tier, and every rule tier has a branch.
- **Absent records, None, zero, dates.**
  - Every `LATEST` / `XLATEST` that can be None is guarded before comparison or arithmetic: `lf_return_day`, `lf_src_day`, `rw_start`, `rw_end_off`, `rw_relock_time`, `sf_relock_day`, `sf_credit_id`, `fm_method`, `rd_id`, `rd_booked`, `rd_consent`, `dd_fid`, `dd_filed`.
  - The charge collected at closing always exists on a funded closing (base `funding_signed` triggers `funding_per_diem_charged` on the signing date).
  - A funded closing always carries a lock: `lock_must_cover_disbursement: true` on every variant. So the lock-rate reads in sf, fm and dd are defined.
  - The only divisors are 100 and the day-count basis.
  - Month lengths: `fm_mbf` covers all twelve months, with a Feb 28/29 rule.
- **First-match reads.**
  - Observation O4-A: `dd_latest_charge` orders charges by `interest_from_date`. After a per diem shortfall payment (whose period equals the charge collected at closing), two charges share that from-date, and "the closing's latest prepaid interest charge" ties. It is reached only by dd's third scope tier and its baseline, and no world exercises it.
  - Observation O4-B: `rw_ext_exp` takes the latest extension entry without requiring it to precede the relock. An extension booked after a relock would be read as "the expiration before any relock". No world exercises it.
- **replaced_by scope.**
  - sf and fm keep "Every prepaid interest entry other than …" with sibling exclusion.
  - rd keeps the borrower-reason, Larkspur-free and once-per clauses, and "never charged or raised after closing".
  - lf keeps "same daily amount" and a scoped late-funding compensation clause.
  - rw keeps its base sentence.
  - dd keeps the late-funding branch under the per diem policy as lf applies it.
  - No undeclared override was found.
- **Docstrings.** No ordering words. No figures except the generic "0.00 when the dispute is denied". Half-up rounding throughout.
- **Realism.**
  - lf: statutory refund-interest states and escalation.
  - sf: record-error allowances and an unused-credit cover.
  - rw: Larkspur's re-send standard (re-send / re-review / relock).
  - fm: setoff and card surcharge law (CT/MA/ME none, CO capped at 2 %).
  - rd: schedule components; refund of an over-charge only.
  - dd: gap refund with interest.
  - No unreal tier was found.
- **Carried observations:**
  - O2-A, ledger rows whose amount ≠ days × daily: the lf row includes interest, the sf row is a payment, and the dd refund row has days = 0.
  - O2-B, baseline wording.
  - O2-C.
  - O-G5 (base).

Charter-global REDs: **none**.

### closing_checklist (round 4)

| item | status |
|---|---|
| task files | both carry revision_4, with the freeze before the reveal and all four relationships PASS |
| coverage | 6/6 policies; scopes {lf, sf} and {rw, rd, fm, dd} disjoint and equal to `charter_scope` |
| uuid8s | independent |
| task 0 tree | n=1, value_input, user write |
| task 1 tree | n=3, 3 value_input, user write (fm) |
| suite graph | acyclic |
| factors | every computation has 4-6 factors with ≥2 P and ≥1 M; task 0 has multi-source and cross-difficulty factors (loan, lock, credit), task 1 has them too (loan, lock); every factor bears weight against an honest baseline, and every baseline is definite and ≠ gold |
| gates (this round) | all OK except the out-of-scope pre-KB traceability unlock name |
| open REDs | none |
| observations (non-blocking) | O2-A, O2-B, O2-C, O4-A, O4-B, O-G5; the fm baseline_result proof figure is 2308.09 vs the baseline-rule figure 2368.09 |

The difficulty closes at the source layer.

task0=PASS  task1=PASS
charter=CLEAN

## revision_5

### input gate (round 5)

`gates.sh funding_and_disbursement_disputes --trace`: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 15/15, 1.json 20, closure 19=19); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; **TRACEABILITY OK** (0.json 17/0, 1.json 27/0). Every gate is green.

`mkviews.py`:
- `0.view.json` b3f66377… (unchanged)
- `1.view.json` 09468b99… (unchanged)
- `task_tools.py` b1cb4232… (unchanged)
- `funding.extended.yaml` **8c8d4481…9402** (CHANGED)

Base is key-equal. Read: `render_funding_r2.md`, `kb_audit_notes_r1.md`.

### charter_global_frozen (round 5), 2026-10-13T16:41Z, before any round-5 GT was read

Mechanical checks still hold for all six policies: bases verbatim, every binding has a basis, baseline sentences in their rules, replaced_by in rule, edges verbatim. The graph is unchanged: sf⇐lf, fm⇐rw, fm⇐rd, dd⇐fm.

**The flagged items:**

| item | status | evidence |
|---|---|---|
| Baseline sentences pointing at "a rule below" (fm / dd / rd) | **closed** | Now "The standard funding-month payment carries no setoff and no payment channel charge.", "In the standard recompute, the refund per standing day is zero.", "In the standard recompute, the excess carries no interest.", "In the standard schedule, … the rush, rider and program addenda add-ons and the repeat-redraw fee are zero." (and lf/sf/rw likewise "In the standard …"). Each baseline is now self-sufficient. O2-B is closed. |
| fm card percentage stated two ways | **closed** | The flat sentence "The card convenience percentage is card_convenience_pct." is gone. The only statement is the state ladder ⇄ `fm_card_pct`. |
| Channel charge on the shortfall | **closed** | sf: "A per diem shortfall payment carries no payment channel charge, Larkspur bearing the processing cost of a shortfall its own closing record created." fm's channel sentence is scoped "for funding-month interest". |
| Credit-cover date vs the credit charter | **closed** | "the Larkspur closing cost credit whose application at closing paid prepaid items, on whatever date the credit rules book that application, was also cut back at closing" ⇄ `sf_credit_id` / `sf_cutback` with the date filter removed. The credit charter applies credits "At consummation" (credit.yaml `credit_application_at_closing`). The KB note's "only on the disbursement date" has no basis in credit.yaml, and the old signing-date filter matched consummation anyway. Both readings give the same credit on task 0. |
| dd replaced_by vs rule scope | **reworked, but the rework drops a branch → R5-P1** | see below |

**R5-P1 (SOURCE-POLICY RED, dropped branch; charter-global; moves no scored value in either task).**
- dd's overwrite still supersedes the whole base DR clause "A per_diem_overcharge or late_funding dispute is decided by recomputing prepaid interest under the per diem policy from the recorded disbursement_date: any excess is refunded (refund_issued, refund_amount equal to the excess) and a correct charge is denied_correct_as_charged."
- Its replaced_by now reads "A per diem overcharge dispute is decided by the recompute below … Late-funding, closing-fee and returned-wire disputes remain under the base dispute rule."
- Round 4's replaced_by kept the late-funding half ("a late-funding dispute is still decided by recomputing prepaid interest under the per diem policy …"), and so did the rule. Round 5 removed it from both.
- The base dispute rule that late-funding disputes are sent back to is the very clause superseded here. No other base DR sentence and no extended rule states how a late_funding dispute is decided. lf's OW2 only caps its compensation.
- Situation: a pending `late_funding` filing.
  - Reading A (the overwrite as written): no rule in force decides it.
  - Reading B ("remain under the base dispute rule" read as reviving the superseded clause for that type): recompute under the per diem policy and refund any excess.
  - Different conclusions. This is check 1's "dropped branch".
- The renderer's round-2 item 3 was not a real conflict. Round 4 said late-funding disputes are "not decided under this rule" (dd's recompute) but "under the per diem policy as the late-funding refund applies it", which is consistent. The fix removed the in-force part instead of keeping it.
- Neither task has a late_funding filing (task 1's filing is per_diem_overcharge), so no scored value moves.

**Sweep of the changed policies (sf, fm, dd, rd baselines; lf/rw baseline wording).**
- No new branch without a rule tier.
- No None or zero-division path: `sf_credit_id` None → cutback 0.
- Observation O5-A (first-match): `sf_credit_id` takes the latest prepaid-items application by entry_date. Where two stacked credits both paid prepaid items, the rule's singular "the Larkspur closing cost credit whose application at closing paid prepaid items" does not pick one. Untriggered: task 0 has one credit.
- Docstrings: unchanged (tools hash unchanged).
- Realism: unchanged tiers; the shortfall now carries no channel charge, which is realistic.

**Carried observations:** O2-A, O2-C, O4-A, O4-B, O-G5. O2-B is closed.

Charter-global REDs open: **R5-P1**.

### closing_checklist (round 5)

| item | status |
|---|---|
| per-task relationships | both tasks PASS on all four |
| coverage, scope, uuid8s, trees, graph, factor bounds | as round 4, unchanged |
| gates | all green, TRACEABILITY included |
| open charter RED | **R5-P1**: dd's overwrite supersedes the base DR clause that decides late_funding disputes, and its replacement sends them back to "the base dispute rule" without restating it, so no in-force rule decides a late_funding filing. Untriggered by either task; moves no scored value. |
| observations | O2-A, O2-C, O4-A, O4-B, O5-A, O-G5 (non-blocking) |

task0=PASS  task1=PASS
charter=R5-P1

## revision_6

### input gate (round 6)

`gates.sh funding_and_disbursement_disputes --trace`: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 15/15, 1.json 20, closure 19=19); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 17/0, 1.json 27/0). Every gate is green.

`mkviews.py`:
- `0.view.json` b3f66377… (unchanged)
- `1.view.json` 09468b99… (unchanged)
- `task_tools.py` b1cb4232… (unchanged)
- `funding.extended.yaml` **63ab5a0a…043b** (CHANGED)

Base is key-equal. All six policies pass the mechanical checks: bases verbatim, every binding has a basis, baseline sentences in rule, replaced_by in rule, edges verbatim. The graph is unchanged.

### charter_global_frozen (round 6), 2026-10-13T16:48Z, before the round-6 reveal

**R5-P1: closed.** dd's overwrite of the base DR clause now reads:

> "A per diem overcharge dispute is decided by the recompute below, … A late-funding dispute is decided, not by that recompute, but by recomputing prepaid interest under the per diem policy as the late-funding refund applies it, from the recorded disbursement date: any excess is refunded as refund_issued with the refund amount equal to the excess, and a correct charge is denied as correct as charged. Closing-fee and returned-wire disputes remain under the base dispute rule's own sentences for them."

The same sentences are in dd's rule. Exactly one in-force rule now decides each dispute type:

| dispute type | in-force rule |
|---|---|
| per_diem_overcharge | dd's recompute; filing filter `dispute_type='per_diem_overcharge'` |
| late_funding | the per diem policy as lf applies it (lf's take-outs), with compensation capped by lf's OW2 "Apart from the late-booking interest … no compensation beyond the interest refund" |
| closing_fee_disputed | base DR "A closing_fee_disputed dispute reverses the fee (fee_reversed) when the fee is outside the method's schedule or the redraw was Larkspur-caused" (not superseded) |
| returned_wire_interest | base DR "A returned_wire_interest dispute is refunded only when the return was Larkspur-side" (not superseded) |

No sentence contradicts the replacement. A scan of every extended rule for "late-funding dispute", "dispute rule", "closing-fee" and "returned-wire dispute" finds only the dd sentences above and lf's OW2 cap, which is consistent with them. The round-5 sentence "remain under the base dispute rule" for late-funding is gone.

The closing-fee branch and rd do not conflict. rd states that "a doc redraw fee is a fee the closing method's schedule carries, so the reversal in full of a fee the schedule does not carry never applies to it". A closing-fee dispute over a borrower-caused redraw therefore meets neither base reversal condition, and rd's state-due refund returns only the part above Larkspur's schedule.

**O5-A: closed.**
- Rule: "the Larkspur closing cost credit whose application at closing paid the largest amount of prepaid items (… where two such applications paid the same amount, the later-booked one)".
- Compute: `sf_pp_max = XMAX(…credit_applied_at_closing, prepaid_items)`, then `sf_credit_id = XLATEST(… entry_amount=sf_pp_max)` by entry_date, guarded by `if sf_pp_max > 0`. XMAX returns 0.0 on an empty set (check_compute helper), so the None path is safe.
- The credit charter books one application entry per cost category filled, so each credit has at most one prepaid-items entry.
- The tie-break is real and selects uniquely.

**Sweep of the changed policies (sf, dd).**
- No branch without a rule tier.
- No unguarded None.
- No new first-match ambiguity.
- No docstring change (tool hash unchanged).
- No realism change.

**Carried observations (non-blocking):** O2-A, O2-C, O4-A, O4-B, O-G5.

Charter-global REDs open: **none**.

### closing_checklist (round 6)

| item | status |
|---|---|
| per-task relationships | both tasks PASS on all four |
| coverage, scope, uuid8s, trees, graph, factor bounds | as round 4, unchanged |
| gates | all green |
| R5-P1 | closed |
| O5-A | closed |
| open REDs | none |
| observations | O2-A, O2-C, O4-A, O4-B, O-G5 (non-blocking) |

The difficulty closes at the source layer.

task0=PASS  task1=PASS
charter=CLEAN

## revision_7

### input gate (round 7)

`gates.sh funding_and_disbursement_disputes --trace`: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 15/15, 1.json 20, closure 19=19); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 17/0, 1.json 27/0). Every gate is green.

`mkviews.py`:
- `0.view.json` b3f66377… (unchanged)
- `1.view.json` 09468b99… (unchanged)
- `task_tools.py` b1cb4232… (unchanged)
- `funding.extended.yaml` **2cc59f98…1a5f** (CHANGED)

Base is key-equal. All six policies pass the mechanical checks (bases verbatim, every binding has a basis, baseline sentences in rule, replaced_by in rule, edges verbatim).

Read: `render_funding_r3.md`.

### charter_global_frozen (round 7), 2026-10-13T16:59Z, before the reveal

**Item #3, credit-cover cut-back timing: closed.**
- Rule: "… was also cut back for exceeding the eligible costs on the date that application was booked, the cut-back booked with the credit's application at closing, by at least the remainder …; where that credit was cut back on that date by less than that remainder, …".
- Compute: `sf_app_date = XLATEST(… credit_applied_at_closing, prepaid_items, credit_award_id=sf_credit_id)`, guarded `if sf_credit_id != None`. `sf_cutback = XSUM(… credit_reduced, exceeds_eligible_costs, credit_award_id=sf_credit_id, entry_date=sf_app_date)`.
- The factor ladder wording is updated to match.
- Reductions the credit product books "before … closing" on other dates no longer count.

**Set-off pointer: closed.** fm's setoff-per-diem tier 1 now says "the rest of that day's daily amount is not set off and stays on the charge collected at closing". It no longer points at a prepaid interest dispute. This is consistent with dd, which refunds the gap on standing days under its own rule. The ladder value is unchanged.

**Renderer items #1 (combination sentences quoted by non-factor bindings) and #2 (fm/rd baselines naming components).** These are source wording, not defects.
- The quoted sentences are each policy's own rule text. They tie factor results together in compute bindings that are not factors.
- Every baseline is still self-sufficient and definite: each named component has its "standard" value stated (round 5).
- No relationship fails. Recorded as observation O7-A (KB-silence concern, for the KB audit).

**KB auditor note.** "A day the treatment of funds that were out already takes out is not taken out again" is lf's own de-duplication sentence. It is needed: without it, task 0 would subtract 09-14 twice. No defect.

**Sweep of the changed policies (sf, fm).**
- No branch without a rule tier.
- None paths are guarded (`sf_app_date`, `sf_credit_id`).
- No new first-match ambiguity: one prepaid application per credit.
- No docstring change.
- Realism: a cut-back booked with the application at consummation is exactly what the credit charter's `credit_application_at_closing` describes.

**Carried observations (non-blocking):** O2-A, O2-C, O4-A, O4-B, O-G5, O7-A.

Charter-global REDs open: **none**.

### closing_checklist (round 7)

| item | status |
|---|---|
| per-task relationships | both tasks PASS on all four |
| gates | all green |
| render item #3 (credit-cover cut-back timing) | closed |
| set-off pointer | closed |
| renderer items #1 and #2 | observation O7-A (source wording; baselines remain definite) |
| open REDs | none |

task0=PASS  task1=PASS
charter=CLEAN
