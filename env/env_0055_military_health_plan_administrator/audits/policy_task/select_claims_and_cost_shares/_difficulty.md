# Policy-task audit — select_claims_and_cost_shares / charter-global

## charter_global_frozen

- Frozen: 2026-10-11T14:06Z, before any task's GT was revealed. Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- `select.extended.yaml` sha256 `26c538891092bb3ca065ac6eb52878e4f84d3c69f9ed94b78b2c19a2bea16dac`; `task_tools.py` sha256 `848574315be1b621460c2f5b479e0a0ef1c6e8acce3d8b4065e6de7198a2c639` (both match the brief).
- Read: `blueprint/blueprint.yaml`, `blueprint/products/select.yaml`, `blueprint/products/prime.yaml` (Retiree Group B variant only, to check the seeded Prime rows), `blueprint/db_schema.json` (select_claim_lines enums, select_enrollments columns), `blueprint/share_tools.py` (finder signatures, verify/transfer), the extended yaml, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (lines 200-440: semantics of SUM/LATEST/COUNT/CFIELD/XSUM/MONTHS/within_months; it carries no task GT — disclosed because it sits outside the brief's literal read list).
- Masked / not read: `tasks/0.json`, `tasks/1.json`, the difficulty `worklog.md`, the scenario `worklog.md`, `/tmp/sel_author/`, every other difficulty's tasks and audits, every other scenario. Nothing in this section is derived from a revealed GT.
- Base copy: `diff` of extended lines 1-1127 against `blueprint/products/select.yaml` differs only by one trailing blank line — verbatim.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, cache-diff INFO, traceability deferred); masked-view hashes supplied and re-verified (`0.view.json` 5f6395c6…, `1.view.json` b18626dd…). Complete.

DSL facts used throughout (from the evaluator): `SUM/COUNT/LATEST` are filtered to the target holding (`select_enrollment_id == HID`), never the sponsor family; `F()` reads the target enrollment row; `CFIELD(cat, …)` returns the first matching holding of that category for the same `customer_id`; `XSUM` reads another category's event rows owned by the customer; `within_months=w` keeps rows with `0 <= MONTHS(row_date, NOW) < w`, where `MONTHS` subtracts one when the day-of-month of NOW is smaller than the row's.

### policy_conflict_scan

Seven extended policies, one tool each:

| policy | subject | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| select_ext_card_installment_payment | select_fee_payment | pay_select_installment_by_card_fa3a0d38 (user) | amount | [] |
| select_ext_professional_line_correction | select_claim_line_post | post_select_professional_line_96ff63a5 (agent) | cost_share_amount | [] |
| select_ext_inpatient_stay_correction | select_claim_line_post | post_select_inpatient_stay_a4ca4c06 (agent) | tricare_paid_amount | professional (value_input claims_net), card (value_input fees_counted) |
| select_ext_ohi_line_reprocessing | select_claim_line_post | post_select_ohi_reprocessed_line_2895a639 (agent) | cost_share_amount | [] |
| select_ext_bank_draft_payment | select_fee_payment | authorize_select_bank_draft_0bb89bb0 (user) | amount | [] |
| select_ext_ohi_stay_reprocessing | select_claim_line_post | post_select_ohi_reprocessed_stay_ac99ca71 (agent) | tricare_paid_amount | ohi line (value_input claims_s), bank draft (value_input fees_s) |
| select_ext_cap_line_reprocessing | select_claim_line_post | post_select_cap_reprocessed_line_5ecdf694 (agent) | tricare_paid_amount | ohi stay (value_input liab_post_r) |

- Overlapping subjects are separated by the reversal record each policy selects: appeal_overturned + no inpatient days (professional), appeal_overturned + inpatient class (stay), ohi_retroactive + no inpatient days (OHI line), ohi_retroactive + inpatient class (OHI stay), catastrophic_cap_reprocessing + no inpatient days (cap line); card = quarterly/annual installments, draft = monthly installments. No two policies select the same record class, so no two reach different conclusions on the same object.
- Eligibility/time anchors: every claim policy anchors the plan year on the service (admission) date, matching base `select_agg_family_accumulators`; the window implementation deviates at the edges (finding P5).
- Cross-category reads: professional and stay read `referral` (Inpatient Mental Health Authorization); OHI stay and cap line read `prime` (enrollment, claim lines, fee ledger). Each read is declared in `cross_category`.
- Scope: by the trees, the seven policies split into two disjoint trees — {stay, professional, card} and {cap line, OHI stay, OHI line, bank draft}. With M=2 and one tree per task the claimed scopes can be mutually exclusive and jointly complete; confirmed per task against `charter_scope` only after reveal (see the task files).
- Claimed event types `select_ohi_update`, `select_tier_update`, `select_fee_charge`, `select_fee_credit`, `select_fee_refund`, `select_claim_line_reverse` have no extended policy writing them (reversals are all seeded). Observation only.

### rule_compute_equivalence

- Every `compute_basis` value is a verbatim substring of its policy's `rule` (script check, all seven: no miss). Every `baseline.rule` sentence is a sentence of the `rule` (all seven).
- Every factor ladder tier has a sentence in the rule and a branch in the `decides` binding (read pairwise; no rule-only or compute-only tier).
- Deviations found (each recorded in findings):
  - P5: rule "service dates in the plan year that contains …"; compute `win = MONTHS(anchor,NOW) - MONTHS(anchor,sd) + MONTHS(anchor,sd) % 12 + 1` with `0 <= MONTHS(row,NOW) < win`. For NOW = 2026-10-28 a row dated 2025-12-29..31 gives MONTHS = 9 < 10 and is counted in plan year 2026; the rule excludes it. Applies to professional, stay, OHI line, OHI stay, cap line.
  - P7: rule "beneficiary liability posted on the claim lines with service dates in the plan year" and base `select_agg_family_accumulators` "combines every member's net liability"; compute `SUM('select_claim_lines', …)` is restricted to the target enrollment. A second family member's lines are invisible to compute.
  - Cap-line `ded_r` carries `0 if class_r in P('deductible_exempt_service_classes')`; the quoted basis sentence ("the deductible it takes, the smaller of that amount and the tier's deductible_individual less …") states no exemption. The branch has base authority (`select_deductible`), so observation only.
  - Card/draft `received` and `carried` — see factor_ladders (one formula written as tiers); not an equivalence failure.

### action_binding_and_uuids

- Seven `(target_tool, computes)` pairs, each claimed by exactly one policy; no tool is a target of two policies.
- uuid8 tails: 96ff63a5, a4ca4c06, fa3a0d38, 2895a639, 0bb89bb0, ac99ca71, 5ecdf694 — pairwise distinct, no shared prefix or sequence, no copied stem with a changed tail. PASS.
- Docstrings: none names another tool, none carries a sequence word about tool order (the only "after" — "now figured with TRICARE paying after the other insurer" — is payer order, not call order). PASS.
- Function bodies: every tool only `ctx.find`s the source row and `ctx.create`s one new row; none refuses, errors or hints when a prerequisite is unresolved. The tools judge no prerequisite. PASS.
- Side note: neither payment tool updates `select_enrollments.fee_balance_due`; after a payment the enrollment row still shows the pre-payment balance (observation O3).

### prerequisite_graph

- `prerequisite` filled on all seven (`[]` on four). Edges: stay→professional, stay→card, OHI stay→OHI line, OHI stay→bank draft, cap line→OHI stay. All point at extended policy ids in this file, none at a base policy or self; acyclic (two trees, depth 1 and 2).
- `policy_source` verbatim in the blocked policy's own rule: 5/5 (script check).
- `form: state` on all five, no `fallback_reason` key on any. Correct pairing.
- `gate` names `claims_net`, `fees_counted`, `claims_s`, `fees_s`, `liab_post_r` all exist as bindings of the blocked policy's compute; `kind: value_input` on all five and each gate is a value binding (not an eligibility gate). PASS.
- `resolved_by` equals the depended-on policy's `target_tool` on all five; each `effect` is genuine (the write adds a row that enters the named SUM). PASS.
- `condition` vs sentence: same strength and scope on all five (stay→card: quarterly/annual installments of the admission year past due; OHI stay→draft: monthly installments of the plan year due on or before adjudication; claim edges: every reversed line of the stated class/date carries its re-adjudication). No authoring-viewpoint phrasing in `prerequisite`. PASS.

### prerequisite_sentences

| edge | sentence (own rule) | connective | waited-on state | resolving write (single reading) |
|---|---|---|---|---|
| stay → professional | "The TRICARE payment on a corrected stay is fixed only after every professional line billed for the same admission date that stands reversed carries its corrected adjudication." | only after | reversed professional line has a later corrected line on its claim | the professional-line policy is the only rule settling "the corrected adjudication of a … professional or other outpatient claim line whose earlier adjudication stands reversed" (appeal reversals). OHI line / cap line handle OHI and cap reversals, picked out by the reversal record's reason. One reading. |
| stay → card | "The TRICARE payment on a corrected stay is not fixed until the fee account shows no past-due balance on the quarterly or annual installments of the plan year that contains the admission date." | not until | no past-due balance on quarterly/annual installments of the year | the card policy is the only rule clearing "the past-due balance on the quarterly or annual installments"; the draft rule is limited to monthly installments. One reading. |
| OHI stay → OHI line | "The TRICARE payment on a stay reprocessed for other health insurance is fixed only after every outpatient line of the plan year that stands reversed for other health insurance carries its reprocessed adjudication." | only after | OHI-reversed outpatient lines carry a reprocessed line | OHI-line policy only. One reading. |
| OHI stay → draft | "The TRICARE payment on a stay reprocessed for other health insurance is not fixed until the fee account shows no past-due balance on the plan year's monthly installments." | not until | no past-due balance on monthly installments | bank-draft policy only (card is quarterly/annual). One reading. |
| cap line → OHI stay | "The TRICARE payment on a line reprocessed for the catastrophic cap is fixed only after every inpatient stay of the plan year that stands reversed for other health insurance carries its reprocessed adjudication." | only after | OHI-reversed stays carry a reprocessed stay | OHI-stay policy only (the inpatient-stay-correction policy handles appeal reversals). One reading. |

- Four-point test: each sentence joins the blocked result to the waited-on state with an ordering connective; the state is named in record words (reversed line / corrected adjudication / past-due balance); no tool name, policy id, snake_case token or row id in any sentence; scope matches `condition`. PASS on all five.
- No second wording of any dependency in the blocked rules; no depended-on rule restates the sentence. PASS.
- Undeclared cross-problem orders in extended rules: none found. Base sentences stating cross-problem order ("The corrected adjudication is posted afterwards as a new line of the same claim" in `select_claim_line_reversal`; "Lines are accumulated in adjudication order" in `select_deductible`) ground no edge, and every edge has its own extended sentence. Observation only.
- Reverse coupling (observation O5): the professional line's `stay_days` is `LATEST(post, class=inpatient_mental_health_admission, service_date=sd)`. If the corrected stay (inpatient_days = covered days) were posted first, the professional line would read covered days instead of billed days and its attending share would become 1. The declared edge excludes that order, so no second answer arises; the rule's "the billed days of the stay" does not say which row of the stay to read.

### override_declarations

Sentence-by-sentence sweep of each `base_policy_refs` entry. "follows" = extended gives the same scored quantity; "n/e" = not engaged by the policy's write; "differs" = a finding.

Claim-line policies (professional, stay, OHI line, OHI stay, cap line), refs `select_agg_family_accumulators`, `select_deductible`, `select_outpatient_cost_shares`, `select_inpatient_cost_shares`, `select_catastrophic_cap`, `select_prior_authorization_and_filing`, `select_nonparticipating_providers`, `select_ohi_coordination`, `select_cost_share_tier_ladder`:

- agg_family_accumulators: "Deductibles and the catastrophic cap are family accumulators … a line's deductible is limited both by the patient's own remaining individual deductible and by the family's remaining family deductible, and once the family deductible is met no member owes any further deductible" — **differs** in professional, OHI line, cap line (only the individual remainder; family remainder dropped; compute cannot see other members) → P4. "The family catastrophic total combines every member's net liability …" — rule wording unscoped, compute single-enrollment → P7. "Amounts accumulate to the calendar plan year of the service date" — follows in prose, compute window over-includes late-December rows → P5. "Prime cost shares … never count" — declared overwrite in OHI stay and cap line; follows elsewhere.
- select_deductible: plan year / exempt classes / inpatient deductible only where `inpatient_deductible_applies` (false on all tiers; stay tools post 0) — follows. "the smaller of … the patient's remaining individual deductible … and the family's remaining family deductible" — **differs** (P4). "A denied line applies nothing" — n/e. "Lines are accumulated in adjudication order; a line adjudicated later … does not reopen deductibles already met" — follows (each policy reads the plan year as posted at its own handling time).
- select_outpatient_cost_shares: network percent / fixed copay / non-network percent / copay ≤ remaining / rounding — follows. "(durable medical equipment always carries network_dme_cost_share_pct)" — **differs** in professional, OHI line, cap line: on fixed_copayment tiers compute reads `P('network_copay_durable_medical_equipment')`, a parameter that does not exist (→ None, no definite value) → P3. "Network preventive care carries network_copay_preventive_care and no deductible" — **differs** on percent_of_allowed tiers: compute charges `network_outpatient_cost_share_pct` of the amount (Retiree Group A: 20 %) where base gives network_copay_preventive_care (0.00) → P2. "The provider's network status is the one in the provider record on the service date" — extended reads it from the reversed line; in both worlds the line value equals the provider record (observation O4).
- select_inpatient_cost_shares: stay-level pricing and the four bases — follows (percent applied to the amount net of OHI, which `select_ohi_coordination` mandates). Non-network per_diem_with_minimum uses `inpatient_network_minimum_charge` (base gives no non-network minimum) — observation. "Separately billed professional services during the stay are outpatient lines" — follows (professional policy).
- select_catastrophic_cap: "Once the family's catastrophic total … reaches catastrophic_cap_family, every later line … carries no deductible and no cost share, and a line that crosses the cap is cut …" — follows in stay, OHI stay, cap line; **differs** in professional and OHI line, whose rules fix liability as "the deductible applied plus the cost share" with no cap and `overwrite: []` → P1. "Point-of-service charges, Prime cost shares … never count" — declared overwrite in OHI stay and cap line. Cap-line `replaced_by` keeps the POS / premium-based / balance-billing exclusions. OHI-stay `replaced_by` drops the premium-based and balance-billing exclusions from that clause; the balance-billing one survives through `select_nonparticipating_providers`, and premium-based costs are left unaddressed for that policy (observation O6; no premium rows in either world).
- select_prior_authorization_and_filing: authorization clause — declared overwrite in OHI line, OHI stay, cap line; followed by the stay (covered days from the authorization); n/e for the professional specialty line. Timely filing / no-eligibility — n/e on record.
- select_nonparticipating_providers — n/e (no balance bill is scored). select_ohi_coordination — follows. select_cost_share_tier_ladder — follows (the OHI-line deductible ladder hard-codes Group A constants that equal the tier parameter on every reachable input).

Fee policies (card, draft), refs `select_agg_family_accumulators`, `select_catastrophic_cap`, `select_fee_payment_and_nonpayment`, `select_enrollment_fee_schedule`:

- fee_schedule: "The family owes annual_fee_individual while exactly one member is enrolled in Select and annual_fee_family while two or more are." Card follows (its extra conjunct "its fee account carries installment charges" holds for every payer). Draft **differs**: "Where the enrollment's fee arrangement is individual because exactly one family member is enrolled and its fee account carries payments … that individual annual fee; … otherwise it is the family fee, twice the individual annual fee." For an individual arrangement with no payment yet posted, base gives annual_fee_individual and extended gives twice it. `overwrite: []` → P6. Quarter/twelfth installment arithmetic — follows.
- fee_payment_and_nonpayment: monthly methods vs card/check for quarterly/annual — follows (card policy scoped to quarterly/annual, draft = EFT to monthly). "A payment is applied to the oldest unpaid installment first" — followed in the amount; the payment row is tied to the latest installment, while the base event grain is "one payment applied to one installment charge" (observation O2). Grace/disenrollment sentences — n/e for these writes, but see observation O1.
- agg_family_accumulators / catastrophic_cap — n/e for a fee payment write.

### factor_ladders

Distinctness test: a tier is degenerate when the value another tier of the ladder selects, evaluated over every input of the degenerate tier's domain, equals the degenerate tier's value — one tier written as two. Clamp tiers (a floor or cap that selects a value the other formula would not give) count as distinct.

| policy | factor | label | declared tiers | live / distinct tiers | structural verdict |
|---|---|---|---|---|---|
| card | card_fee_level | parameter | individual∧charges / fee_exempt / else family | 3 distinct; conjunct "its fee account carries installment charges" holds of every payer (the write is recorded against an existing charge); fee_exempt tier unreachable (exempt tiers carry no charges) | RED F1 (padded conjunct) |
| card | card_installment_share | parameter | quarterly / monthly / else annual | monthly tier outside the policy's own scope ("quarterly or annual installments") and outside base payment methods (no card_single for monthly) → 2 live | RED F2 |
| card | card_already_received | parameter | ≥owed→owed / some→posted / else 0 | whole ladder = `min(posted, owed)`; tier 3 (0) = tier 2's value at posted = 0 | RED F3 |
| card | card_application_order | method | shortfall / excess / else 0 | compute `carried: earlier_excess if earlier_excess < 0 else (earlier_excess if earlier_excess > 0 else 0)` ≡ `earlier_excess` in every branch; one algorithm, so the method label is also false | RED F3, F4 |
| prof | outpatient_other_insurance | parameter | OHI∧paid≥allowed→0 / OHI∧0<paid<allowed→allowed−paid / else allowed | 3 distinct (clamp) | pass |
| prof | attending_share | parameter (xd referral) | partial auth→auth/billed / stay∧no auth→0 / else 1 | 3 distinct | pass |
| prof | outpatient_deductible_met | parameter | reversals→posted−reversed / none→0 / else posted | whole ladder = `posted − reversed` | RED F3 |
| prof | outpatient_deductible_taken | parameter | exempt→0 / some met→min(amt, ind−met)⁺ / else min(amt, ind) | tier 3 = tier 2 at met = 0 → 2 distinct | RED F3 |
| prof | outpatient_cost_share_basis | method | non-network % / network fixed copay / network % | 3 distinct algorithms | pass |
| stay | stay_covered_days | parameter (xd referral) | partial auth→auth days / needs auth∧none→0 / else billed | 3 distinct | pass |
| stay | stay_payable_allowed | parameter | MH∧0<cov<billed→allowed·cov/billed / cov=0→0 / else allowed | tier 2 = tier 1's formula at cov = 0 → 2 distinct | RED F3 |
| stay | stay_other_insurance | parameter | OHI∧paid∧cov<billed→paid·cov/billed / OHI∧paid∧all covered→paid / else 0 | tier 2 = tier 1's formula at cov = billed → 2 distinct | RED F3 |
| stay | stay_countable_fees | method | tied by coverage start / untied by posting date / else none | tier 3 = either counting method on an empty set; fall-through "count no fee" (0) is not the declared baseline `posted_paid` | RED F3, F5 |
| stay | stay_fees_added | parameter | count∧bearing∧credits→basis−credits / count∧bearing→basis / else 0 | tier 2 = tier 1 at credits = 0 → 2 distinct | RED F3 |
| stay | stay_claims_counted | parameter | reversals→posted−reversed / none→0 / else posted | whole ladder = `posted − reversed` | RED F3 |
| OHI line | ohi_line_other_insurer | parameter | 3 (clamp) | 3 distinct | pass |
| OHI line | ohi_line_deductible_amount | parameter | GroupB∧lines on record→tier P / GroupA E1-E4→50 / else 150 | conjunct "the plan year's lines are on record" holds of every caller (the reversed line's own post is a plan-year line); on every reachable input each tier returns the tier's own `deductible_individual`; the declared baseline 150 is not what `baseline.rule` ("the tier's deductible_individual") gives a Group B enrollee | RED F1, F6 |
| OHI line | ohi_line_deductible_met | parameter | as prof | whole ladder = `posted − reversed` | RED F3 |
| OHI line | ohi_line_deductible_taken | parameter | as prof | 2 distinct | RED F3 |
| OHI line | ohi_line_cost_share_basis | method | 3 algorithms | 3 distinct | pass |
| draft | draft_fee_schedule_group | parameter | GroupB∧charges→tier P / exempt→0 / else 198 | conjunct "fee account carries installment charges" holds of every drafter; on reachable inputs every tier = the tier's own `annual_fee_individual`; fall-through = Group A schedule constant | RED F1, F6 |
| draft | draft_fee_level | parameter | individual∧payments→ind / exempt→0 / else 2×ind | conjunct "its fee account carries payments": no fee schedule weighs payment history when choosing individual vs family; conflicts with base (P6) | RED F1 |
| draft | draft_installment_share | parameter | monthly / quarterly / else annual | quarterly and annual tiers are outside the policy's own scope ("the monthly installments") → 1 live | RED F2 |
| draft | draft_already_received | parameter | as card | = `min(posted, owed)` | RED F3 |
| draft | draft_application_order | method | as card | ≡ `earlier_d`; one algorithm | RED F3, F4 |
| OHI stay | ohi_stay_other_insurer | parameter | 3 (clamp) | 3 distinct | pass |
| OHI stay | ohi_stay_prime_carryover | parameter (xd prime) | change∧Prime cs→cs+fees / change∧fees credited→cs only / else 0 | tiers 1 and 2 overlap as stated (cost shares on record and fees credited); in compute tier 2 is reached only when `pr_cs_post_s == 0`, so it returns `pr_cs_net_s = 0` = the fall-through | RED F3, F7 |
| OHI stay | ohi_stay_prime_pos_exclusion | parameter (xd prime) | POS→post−rev−pos / none→0 / else post−rev | whole ladder = `post − rev − pos` | RED F3 |
| OHI stay | ohi_stay_select_claims | parameter | as stay_claims_counted | = `posted − reversed` | RED F3 |
| OHI stay | ohi_stay_prime_fee_placement | method (xd prime) | as stay_countable_fees | tier 3 degenerate; fall-through (0) ≠ baseline `pr_fees_post_s` | RED F3, F5 |
| OHI stay | ohi_stay_select_fees | parameter | as stay_fees_added | 2 distinct | RED F3 |
| cap line | cap_line_other_insurer | parameter | 3 (clamp) | 3 distinct | pass |
| cap line | cap_line_stage | parameter | reached→0 / room<uncapped→room / else uncapped | 3 distinct (clamp); base `select_catastrophic_cap` states the same three cases | pass |
| cap line | cap_line_prime_carryover | parameter (xd prime) | as OHI stay | overlap as stated; tier 2 = fall-through in compute | RED F3, F7 |
| cap line | cap_line_prime_fee_placement | method (xd prime) | as OHI stay | tier 3 degenerate; fall-through ≠ baseline `pr_fees_post_r` | RED F3, F5 |
| cap line | cap_line_select_fees | parameter | as stay_fees_added | 2 distinct | RED F3 |

Surviving factors per computation, against 4–6 total, ≥2 parameter, ≥1 method:

| computation | declared (P/M) | surviving | surviving P/M | bounds |
|---|---|---|---|---|
| card | 4 (3/1) | 0 | 0/0 | RED |
| professional | 5 (4/1) | other_insurance, attending_share, cost_share_basis | 2/1 | RED (3 < 4) |
| stay | 6 (5/1) | stay_covered_days | 1/0 | RED |
| OHI line | 5 (4/1) | other_insurer, cost_share_basis | 1/1 | RED |
| draft | 5 (4/1) | 0 | 0/0 | RED |
| OHI stay | 6 (5/1) | other_insurer | 1/0 | RED |
| cap line | 5 (4/1) | other_insurer, stage | 2/0 | RED (no method) |

Multi-source surviving factors: the three OHI-paid factors (enrollment `ohi_on_file` ∧ claim-line `ohi_paid_amount`), attending_share and stay_covered_days (claim line ∧ referral row). Cross-difficulty surviving factors: attending_share and stay_covered_days (referral) only. All three `prime` factors fail structurally.

Baselines (charter-level):
- card `baseline.rule`: "The latest installment is owed at the family fee, annual_fee_family. The card payment is the latest installment owed, rounded to the cent." Two readings: the installment owed is annual_fee_family itself (396.00 on a Retiree Group A world; the declared bindings) or the latest (quarterly) installment priced at the family fee (99.00). Not definite → F8.
- draft `baseline.rule`: "The latest monthly installment is owed at the family fee of the Group A retiree schedule, group_a_retiree_annual_fee_individual doubled. The bank draft is that installment owed …" Two readings: 396.00 (declared bindings) or a monthly installment at that fee, 33.00. It also prices every enrollee, Group B included, on the Group A retiree schedule, which base `select_enrollment_fee_schedule` never does → F8.
- The professional, stay, OHI line, OHI stay and cap line baselines are self-sufficient and definite; the OHI-line factor baseline contradicts its own `baseline.rule` (F6).

### findings

Charter-global findings. Each names the tasks it can bear on; the task files carry the per-world demonstration. Consequences below are shown on a stated situation (the policy-level demonstration the core table asks for).

- **P1 — SOURCE-POLICY RED (undeclared override: dropped catastrophic-cap branch).** Base `select_catastrophic_cap`: "Once the family's catastrophic total for the plan year (select_msr_family_catastrophic_ytd) reaches catastrophic_cap_family, every later line of that plan year carries no deductible and no cost share, and a line that crosses the cap is cut to the amount still remaining under it." Professional rule: "The beneficiary liability on the corrected outpatient line is the deductible applied plus the cost share, rounded to the cent"; the OHI-line rule says the same. Neither policy overwrites that base sentence, and neither compute has a cap. Situation: family total already at cap, corrected line 100 allowed → base liability 0.00, extended 100 × pct + deductible. Affects: `select_ext_professional_line_correction` (rule, compute), `select_ext_ohi_line_reprocessing` (rule, compute). Bears on: task 0 (professional), task 1 (OHI line).
- **P2 — SOURCE-POLICY RED (dropped branch: network preventive care).** Base `select_outpatient_cost_shares`: "Network preventive care carries network_copay_preventive_care and no deductible." Professional / OHI-line / cap-line `cs_*` on a percent_of_allowed tier: `RND((amount − ded) * network_outpatient_cost_share_pct / 100, 2)`. Situation: Retiree Group A network preventive line, 200 allowed → base 0.00, extended 40.00. Bears on: neither task's scored line (specialty / ambulatory surgery).
- **P3 — SOURCE-POLICY RED (dropped branch: DME).** Base: "durable medical equipment always carries network_dme_cost_share_pct". Same three computes, fixed_copayment tier, DME line: `P('network_copay_durable_medical_equipment')` → None, so there is no definite value where base gives 10 % / 20 %. Bears on: neither task.
- **P4 — SOURCE-POLICY RED (dropped branch: family deductible).** Base `select_deductible`: "… the patient's remaining individual deductible (deductible_individual less select_msr_individual_deductible_ytd) and the family's remaining family deductible (deductible_family less select_msr_family_deductible_ytd)." Professional / OHI line / cap line use the individual remainder only. Situation: two-member family whose family deductible is met → base 0.00 deductible, extended up to the individual remainder. Bears on: neither task (both families have one Select member).
- **P5 — SOURCE-POLICY RED (rule/compute: plan-year window).** Rule "service dates in the plan year that contains the admission date"; compute window counts a 2025-12-29 row as plan year 2026 at NOW = 2026-10-28. Bears on: neither task (no claim line or fee row falls in the over-included days; checked in the task files).
- **P6 — SOURCE-POLICY RED (undeclared override: draft fee level).** See override_declarations. Situation: Group B single retiree, first monthly installment charged and unpaid → base 49.59 owed, extended 99.18. Bears on: task 1 only in principle; on its world `n_paid_d = 3`, so there is no consequence.
- **P7 — observation (family scope).** Compute reads one enrollment where base measures span the sponsor family. With single-member families in both worlds, no consequence can be shown.
- **F1 — SOURCE-FACTOR RED (condition holds of every customer who reaches the write / no business weighs it).** card_fee_level ("its fee account carries installment charges"), draft_fee_schedule_group (same), ohi_line_deductible_amount ("the plan year's lines are on record"): each conjunct is true for every caller of that write, because the write is recorded against an existing charge or reprocesses an existing plan-year line. draft_fee_level ("its fee account carries payments"): no fee schedule chooses individual vs family by payment history. Each was written to make the factor look multi-source.
- **F2 — SOURCE-FACTOR RED (tiers outside the policy's own scope).** card_installment_share's monthly tier (scope "quarterly or annual installments"; base gives no card_single for monthly); draft_installment_share's quarterly and annual tiers (scope "the monthly installments"). Live tiers: 2 and 1.
- **F3 — SOURCE-FACTOR RED (one tier written as two or three).** See table: card/draft already_received (= min), card/draft application_order (≡ earlier excess), all four deductible_met / claims_counted / select_claims ladders (= posted − reversed), prime_pos_exclusion (= post − rev − pos), deductible_taken (tier 3 = tier 2 at met = 0), payable_allowed, stay_other_insurance, the three fees_added/select_fees ladders, the three fee-placement ladders (empty-set tier), and the two prime_carryover ladders (tier 2 = fall-through).
- **F4 — SOURCE-FACTOR RED (mislabelled method).** card_application_order and draft_application_order are labelled `method`, but every tier runs the same arithmetic (`installment − received − earlier_excess`). With them struck, the card and draft computations have no method factor.
- **F5 — SOURCE-FACTOR RED (fall-through ≠ baseline).** stay_countable_fees, ohi_stay_prime_fee_placement, cap_line_prime_fee_placement: the fall-through is "count no fee" (0) but the declared `baseline` is `posted_paid` / `pr_fees_post_*` (all payments by posting date), which is a tier of no ladder.
- **F6 — SOURCE-FACTOR RED (dishonest baseline).** ohi_line_deductible_amount: declared baseline `K('group_a_deductible_individual')` = 150; `baseline.rule` says "the tier's deductible_individual", which on a Group B world is 183 — the scored tier value. Draft_fee_schedule_group's fall-through prices a Group B enrollee on the Group A retiree schedule (198), a treatment base `select_enrollment_fee_schedule` never gives. Demonstrated on task 1.
- **F7 — SOURCE-FACTOR RED (tiers overlap as stated).** prime_carryover (OHI stay, cap line): "where … Prime cost shares of the plan year are on record, the Prime cost shares and the Prime enrollment fees … are added; where … the Prime fees of the plan year were credited back, only the Prime cost shares are added". A customer with Prime cost shares and credited Prime fees meets both tiers; prose gives no precedence (compute takes tier 1). No credits in task 1's world, so no second answer there.
- **F8 — SOURCE-FACTOR RED (baseline.rule not definite / straw man).** Card and draft baselines, see Baselines above.
- Observations: O1 — both worlds hold an installment short of its charge more than `nonpayment_grace_days` past its due date while the enrollment is `active` (base lifecycle: the system disenrolls at the paid-through date); no agent policy acts on it and the record status governs. O2 — payment tied to the latest installment versus the base grain "one payment applied to one installment charge". O3 — `fee_balance_due` is not maintained by the payment tools (and is a stamp of the payment outcome — demonstrated per task). O4 — network status read from the reversed line instead of the provider record. O5 — reverse coupling of professional line and stay. O6 — OHI-stay `replaced_by` leaves premium-based plan costs unaddressed. O7 — fixed-copayment tiers have no `network_copay_*` for lab_and_xray / home_health_visit / applied_behavior_analysis / skilled_nursing_facility (a base gap, inherited by `P('network_copay_' + class)`). O8 — the OHI-line, OHI-stay and cap-line policies pick "the most recent" reversal of their class; with two such reversals open, repeated application keeps selecting the same one, so the second can never be reached (not the case in either world). O9 — `bank draft` posting is treated as received on authorization; ordinary for phone EFT, so not ruled a real-world wait.

## closing_checklist

Written 2026-10-11, after both tasks were revealed and compared. Everything above this heading was frozen before any reveal (sha256 f3da86ef… at reveal time) and has not been edited since, apart from replacing this placeholder.

The difficulty **does not pass** the source-layer audit; the four-way PASS condition is not met.

- Audit files: `0.md`, `1.md` and this file, one per task plus the charter file; first round, no older revision. Every comparison section carries a verdict, and not every one is PASS.
- Coverage and scope: the seven extended policies split {stay, professional, card} (task 0) and {cap line, OHI stay, OHI line, draft} (task 1) — pairwise disjoint over whole trees and jointly complete. Seven tools, each claimed once, uuid8s independent. PASS.
- Trees: task 0 has 2 prerequisite problems and 2 value_input edges; task 1 has 3 and 3. Each has an owner=user problem (card; draft). Both are acyclic, and the difficulty-wide graph is acyclic. Every edge is unmet at the opening and bears weight. PASS (SOURCE-CHAIN PASS on both tasks).
- Computations / factors: **fail.** Every declared factor moves its scored value on its world, and every all-baseline figure is definite and differs from gold. But structurally (F1–F8) no computation keeps 4 sound factors with 2 parameter and 1 method. Task 1 has no sound cross-difficulty factor. Both tasks carry a `fee_balance_due` stamp equal to the scored payment.
- Policy self-consistency: **fail** at charter level (P1–P6 demonstrated on stated situations). Neither task's scored values are moved by these on its own world.
- Unique solution: task 0 **fails** on `prior_authorization_id` of the professional line (`""` vs gold `57ec9939…`); task 1 passes.
- Gate re-run on the final form: not performed by this auditor (Step 0 rule — the gates are cited from the brief: all green, traceability deferred). The artifacts are unchanged since the snapshot (hashes re-verified at freeze).

Per-task verdict lines:

- task 0: SOURCE-POLICY RED (charter P1–P5; no task-value consequence) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (stamp fee_balance_due = 34.0; F1–F5, F8; bounds fail on card/professional/stay) | SOURCE-TASK RED (professional-line `prior_authorization_id`: "" vs 57ec9939…)
- task 1: SOURCE-POLICY RED (charter P1–P6; no task-value consequence) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (stamp fee_balance_due = 27.6; F6 demonstrated on ohi_line_deductible_amount; no sound cross-difficulty factor; F1–F8 bounds fail) | SOURCE-TASK PASS

---

## revision_2

### charter_global_frozen (round 2)

- Frozen 2026-10-11T22:32Z, before either round-2 task file was opened. Auditor: same independent auditor; round-1 text above is left untouched.
- Shared inputs moved, so every charter-global section is re-derived in full:
  - `select.extended.yaml` 26c53889… → **0aebbf68b8a4b4ef9527e4550bbac5b9cd1ad04f4f10926275a37999e66f3e41**
  - `task_tools.py` 84857431… → **39e04e8226e647ef906b44ed703be43eabc4c83c1dfdf7b9a6eb86299b0195d3**
  - Both match the coordinator brief. The views also changed (0: 0d60ddfe…, 1: dc6822f5…; both re-verified).
- Base copy: lines 1-1127 still match `blueprint/products/select.yaml` verbatim (trailing blank line only).
- Not read before this freeze: `tasks/*.json`, the difficulty `worklog.md`, `/tmp/sel_author/`. Scratch scripts: `/tmp/erl55_audit_select/r2/`.
- Entry conditions: the round-2 gate snapshot is supplied in the brief (all OK, traceability deferred). Complete.

### policy_conflict_scan (round 2)

- Same seven policies, tools and owners.
- New scoping:
  - Every claim policy is now limited to "an enrollee who is the only member of the sponsor family enrolled in Select".
  - The card policy covers quarterly/annual installments of an enrollee who elected single card or check.
  - The draft policy covers an enrollee who elected allotment, EFT or recurring card, at any frequency.
- The card and draft scopes are disjoint by elected method. The claim policies are still separated by reversal reason and line class. No two policies reach different conclusions on one object.
- New declared overwrites:
  - Card and draft: the fee-schedule sentence, replaced by a ladder — catastrophic cap reached → fee 0; family → family fee; else individual.
  - Professional and stay: Prime carryover (agg_family_accumulators, catastrophic_cap).
  - OHI line: Prime carryover added to its earlier authorization overwrite.
- Observation N6: the card/draft overwrites define "the family's catastrophic total" without Prime amounts, while the five claim policies credit Prime carryover into "the family catastrophic total" of their own lines. Each definition is explicit and scoped, so there is no unresolved reading. In a Prime-to-Select year the fee policies can keep billing a family whose claims are already at cap.

### rule_compute_equivalence (round 2)

- `compute_basis` ⊂ rule and `baseline.rule` ⊂ rule for all seven policies (script check, no miss).
- **N1 — SOURCE-POLICY RED (rule/compute, new).** The OHI-line and cap-line rules state attending-share tier 1 as "Where the reprocessed line's service date is the admission date of an inpatient mental health stay and an Inpatient Mental Health Authorization starting that day was approved … for fewer days than it was requested for …". Compute: `att_o: auth_days_o / req_days_o if (auth_ok_o and req_days_o > auth_days_o) else …` (likewise `att_r`). The `mh_stay_o > 0` / `mh_stay_r > 0` test is applied only in tier 2.
  - Situation: an approved IMH authorization starting on the line's date for 7 of 8 requested days, with no inpatient mental health stay posted that day. Rule → share 1; compute → 7/8.
  - Bears on task 1 only if no stay is on record; there one is (see 1.md).
- P5 (window) residual: compute unchanged. Demonstrable on a stated situation; no consequence in either round-2 world (both NOW dates are the 31st, so no prior-December row is over-included).
- P4/P7: closed by scope. The policies now state the single-member scope, so the family remainder can never bind and the compute's single-enrollment sums equal the family sums.
- The cap-line rule now states the exemption inside the deductible sentence (round-1 observation closed).

### action_binding_and_uuids (round 2)

- Seven distinct `(target_tool, computes)` claims; uuid8s unchanged and independent.
- Docstrings carry no sequence words (only "then shows on the Explanation of Benefits", an effect).
- Tool bodies only find and create; none checks a prerequisite. PASS.
- Changes:
  - The professional-line docstring now says `prior_authorization_id` is given "only when the line's service class needs prior authorization; pass "" otherwise", aligned with the new rule sentence.
  - The payment tools now write payment rows with an empty coverage period.
  - `fee_balance_due` is still not maintained by the tools (O3 unchanged).

### prerequisite_graph (round 2)

- Same five state-form value_input edges. `policy_source` is verbatim in the blocked rule, gates exist, `resolved_by` matches the target tools, acyclic.
- The stay→card and OHI-stay→draft sentences changed wording ("…whose coverage period has begun"; the OHI-stay sentence no longer says "monthly"); `condition` was updated to match. PASS.
- **N5 — observation (new).** The fee policies are now scoped by elected method, while the blocked sentences are scoped by frequency (stay: "quarterly or annual installments") or not at all (OHI stay: "the plan year's installments"). For a quarterly allotment payer, the stay's waited-on state is cleared by the draft policy, not the declared `resolved_by` card. For a check payer, the OHI stay's waited-on state is cleared by the card policy, not the declared draft. A reader resolves the hop from the elected method on the record, so there is one reading per world. The declared `resolved_by` holds only for some worlds. Both round-2 worlds match the declared edges (task 0 check → card; task 1 allotment → draft).

### prerequisite_sentences (round 2)

Four-point test re-run on all five sentences. PASS.
- Ordering connectives: "only after" / "not until".
- Record-state objects: reversed lines carrying a re-adjudication; no past-due balance on begun installments.
- No tool, id or snake_case token. No second wording; the depended-on rules do not restate the sentences.
- Single-reading derivation per world as in round 1, subject to N5.

### override_declarations (round 2)

Sentence sweep re-run:

| round-1 item | round-2 status |
|---|---|
| P1 (cap missing in professional / OHI line) | closed — both carry the cap with base-consistent wording |
| P2 (network preventive) | closed — no deductible; `network_copay_preventive_care` on every tier |
| P3 (DME) | closed — `network_dme_cost_share_pct` for network DME |
| P4 (family deductible) | closed by single-member scope |
| P6 (draft fee level vs base) | closed — the base sentence is now declared superseded; the payments conjunct is gone; merged semantics unique |
| O6 (OHI-stay `replaced_by` dropping premium-based costs) | closed — every `replaced_by` keeps the POS / premium-based / balance-billing exclusion |

- New overwrites are named sentence by sentence, with a unique merge. The cap-reached fee exemption is a real TRICARE treatment (enrollment fees stop once the catastrophic cap is met).
- Undeclared deviation found: none, beyond N1 (a rule/compute mismatch, not an override).

### factor_ladders (round 2)

Same distinctness test as round 1. Live/distinct tiers are per stated ladder.

| policy | factor | label | verdict |
|---|---|---|---|
| card | card_fee_level | P | **RED N2**: fall-through `annual_fee_individual` ≠ declared baseline `annual_fee_family` (tier 2). A single-member customer on the fall-through is moved by the baseline alone. |
| card | card_installment_owed | M | pass (first-installment month proration / quarter / whole annual — three algorithms, all reachable for card/check payers) |
| card | card_due_charges | M | **RED F3**: tier 2 "count every charge" = tier 1's "count only begun charges" on its domain (every charge begun); tier 3 "count no charge" = either on an empty account → one method. The declared baseline is tier 2, not the fall-through. |
| card | card_already_received | P | pass (now a clamp: `left_c` can be negative, so tier 3's 0 ≠ tier 2's formula) |
| prof | outpatient_other_insurance | P | pass |
| prof | attending_share (xd referral) | P | pass |
| prof | outpatient_deductible_met | P | **RED F3** (= posted − reversed, unchanged) |
| prof | outpatient_deductible_taken | P | pass (exempt/preventive → 0; remainder < amount → remainder⁺; else whole amount — clamp, distinct) |
| prof | outpatient_cost_share_basis | M | pass (four algorithms) |
| stay | stay_covered_days (xd referral) | P | pass |
| stay | stay_payable_allowed | M | **RED F3**: tier 2 (no covered day → 0) = tier 1's per-day pricing at 0 days (cov = 0 arises only for MH stays without authorization) |
| stay | stay_other_insurance | P | pass (clamp) |
| stay | stay_claims_counted | P | **RED F3** (= posted − reversed) |
| stay | stay_fees_counted | M | **RED N3**: tiers pick a number — begun plan-year charges / payments left / 0 — i.e. `min(chg_py, max(0, left_py))`; a clamp labelled method |
| stay | stay_cap_stage | P | pass (clamp) |
| OHI line | ohi_line_other_insurer | P | pass |
| OHI line | ohi_line_attending_share (xd referral) | P | pass structurally (prose tiers distinct); compute defect N1 |
| OHI line | ohi_line_deductible_met | P | **RED F3** |
| OHI line | ohi_line_deductible_taken | P | pass |
| OHI line | ohi_line_cost_share_basis | M | pass |
| draft | draft_fee_level | P | **RED N2** (as card) |
| draft | draft_frequency_in_force | P | **RED N4 (F3)**: tier 1 "the charged frequency" and tier 2 "that frequency" (= the charged one) select the same value; compute `charged_freq_d if (…≠ elected) else (charged_freq_d if charged_freq_d else elected)` |
| draft | draft_installment_owed | M | pass (four algorithms) |
| draft | draft_due_charges | M | **RED F3** (as card) |
| draft | draft_already_received | P | pass (clamp) |
| OHI stay | ohi_stay_other_insurer | P | pass |
| OHI stay | ohi_stay_inpatient_basis | M | pass (four base bases; tier chosen by the tier parameter for the line's network relationship — observation N8: it restates base `select_inpatient_cost_shares` as a factor) |
| OHI stay | ohi_stay_select_claims | P | **RED F3** |
| OHI stay | ohi_stay_select_fees | M | **RED N3** |
| OHI stay | ohi_stay_prime_carryover (xd prime) | P | pass (cap / Prime amount / 0 distinct; observation N7: the "credit the cap" tier is inert downstream, since any credit ≥ cap leaves no room either way) |
| OHI stay | ohi_stay_cap_stage | P | pass |
| cap | cap_line_other_insurer | P | pass |
| cap | cap_line_attending_share (xd referral) | P | pass structurally; compute defect N1 |
| cap | cap_line_select_fees | M | **RED N3** |
| cap | cap_line_prime_carryover (xd prime) | P | pass (N7) |
| cap | cap_line_stage | P | pass |

Surviving factors per computation:

| computation | declared (P/M) | surviving | P/M | bounds |
|---|---|---|---|---|
| card | 4 (2/2) | installment_owed, already_received | 1/1 | **RED** |
| professional | 5 (4/1) | other_insurance, attending_share, deductible_taken, cost_share_basis | 3/1 | pass |
| stay | 6 (4/2) | covered_days, other_insurance, cap_stage | 3/0 | **RED** |
| OHI line | 5 (4/1) | other_insurer, attending_share, deductible_taken, cost_share_basis | 3/1 | pass |
| draft | 5 (3/2) | installment_owed, already_received | 1/1 | **RED** |
| OHI stay | 6 (4/2) | other_insurer, inpatient_basis, prime_carryover, cap_stage | 3/1 | pass |
| cap line | 5 (4/1) | other_insurer, attending_share, prime_carryover, stage | 4/0 | **RED** (no method) |

Baselines: all seven `baseline.rule` texts now give one definite number. The card and draft baselines are "the whole annual family fee plus the excess of the other charges over payments" (F8 closed).

### findings (round 2, charter-global)

Status of round-1 items:
- Closed: P1, P2, P3, P4, P6, P7, F1, F2, F6, F7, F8, O5, O6.
- F4: closed for the application-order factors (removed), but reappears as N3 on the new fee-counting factors.
- F5: closed for the fee-placement factors (removed), but reappears as N2 on fee_level.
- F3: partly closed.
  - Still open: the four net-of-reversals ladders, stay_payable_allowed, card/draft_due_charges.
  - New: draft_frequency_in_force (N4).
- P5 residual RED: no consequence in either world.
- Unchanged observations: O2 (payment tied to latest begun installment vs base grain), O3, O4, O7, O8, O9. O1 closed (no installment past grace in either world).

New:
- **N1 — SOURCE-POLICY RED** (attending-share compute omits the MH-stay condition in tier 1; OHI line, cap line).
- **N2 — SOURCE-FACTOR RED** (fee_level fall-through ≠ baseline; card, draft).
- **N3 — SOURCE-FACTOR RED** (clamp labelled method; stay_fees_counted, ohi_stay_select_fees, cap_line_select_fees).
- **N4 — SOURCE-FACTOR RED** (draft_frequency_in_force tiers 1 = 2).
- Observations: N5, N6, N7, N8.

### closing_checklist (round 2, written after both round-2 reveals)

All round-2 sections above this heading were frozen before the reveal (sha256 29bddd3f… at reveal time).

The difficulty **still does not pass** the source-layer audit.

- Files: round-1 text preserved; `## revision_2` appended to `_difficulty.md`, `0.md` and `1.md`. Every round-2 comparison carries a verdict.
- Every scored value of both tasks matches the auditor's blind recomputation: task 0 29.50 / 215.00 / 5,732.00 with `prior_authorization_id ""`; task 1 27.60 / 243.50 / 4,727.89 / 437.50. So do all 42 factor figures and the 7 baseline totals.
- Coverage and scope: seven policies, two disjoint trees, jointly complete; tools and uuid8s sound. PASS.
- Trees: 2 and 3 prerequisite problems, all value_input, each with a user-owned write, all unmet at the opening and load-bearing, acyclic. PASS.
- Policy self-consistency: most round-1 policy findings are closed. Open: **N1** (new: attending-share compute in the OHI line and cap line lacks the MH-stay condition the rule states) and the **P5** window residual. Neither moves either task's values.
- Factors: **fail** on four of seven computations.
  - card and draft: N2 fall-through ≠ baseline, demonstrated as decoration on both worlds; F3 due_charges; N4 frequency_in_force.
  - stay (task 0) and cap line: no method factor, because the fee-count factors are clamps labelled method (N3) and payable_allowed is degenerate (F3).
  - The four net-of-reversals ladders remain one formula (F3).
  - The professional line, OHI line and OHI stay meet the bounds.
- Unique solution: both tasks PASS (T0-1 closed).
- Gates: cited from the round-2 brief (all OK, traceability deferred); not re-run by the auditor. Artifact hashes re-verified at freeze.

Per-task verdict lines (round 2):

- task 0: SOURCE-POLICY RED (charter residual P5; no consequence on task 0) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (card_fee_level N2 decoration on this world; card 2 and stay 3P/0M sound factors) | SOURCE-TASK PASS
- task 1: SOURCE-POLICY RED (charter N1 new + P5 residual; no consequence on task 1) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (draft_fee_level N2 decoration on this world; draft 2 and cap line 4P/0M sound factors) | SOURCE-TASK PASS

---

## revision_3

### charter_global_frozen (round 3)

- Frozen 2026-10-12T02:36Z, before either round-3 task JSON was opened. Rounds 1–2 above are untouched.
- `select.extended.yaml` changed (0aebbf68… → **56dde7d64215e992e841b7e9995b66c291fd0552b8e5dee1d412568f1a66ef8c**), so every charter section is re-derived in full.
- `task_tools.py` is unchanged (39e04e82…), so § action_binding_and_uuids is carried forward from revision_2 on that hash. One exception: the professional and OHI-line policies now target `tricare_paid_amount`, which their tools already take as an argument, so the one-claim-per-pair check still holds (seven distinct pairs).
- Views re-verified: 0 = 543674ca…, 1 = 6dad5d87…. The base copy is still verbatim.
- Not read before this freeze: `tasks/*.json`, the difficulty `worklog.md`, `/tmp/sel_author/`. Scripts: `/tmp/erl55_audit_select/r3/`.
- Entry conditions: the round-3 gate snapshot is in the brief (all OK, traceability deferred). Complete.

### policy_conflict_scan (round 3)

- Seven policies, same tools.
- The five claim policies now compute `tricare_paid_amount`; the professional line and OHI line previously computed `cost_share_amount`.
- Every policy gains the scope device "whose Select enrollment took effect in the plan year that contains the adjudication (payment) date … for any other enrollee this policy settles nothing". The compute agrees: `scope_* = MONTHS(anchor, effective)//12 == MONTHS(anchor, NOW)//12`, and `result` is None out of scope.
- New declared overwrite on all five claim policies: base `select_ohi_coordination`'s "TRICARE pays no more than the allowed amount less the other insurer's payment and the beneficiary liability", replaced by the secondary-payer ladder (nonparticipating: lesser of the primary payment and the limiting charge less OHI less liability; participating: allowed less OHI less liability; otherwise primary). Named sentence by sentence; the merge is unique. This is the real TRICARE "lesser of" rule for TRICARE as second payer.
- No two policies reach different conclusions on one object. N6 (fee policies' catastrophic total without Prime vs claim policies' total with Prime) stays an observation.

### rule_compute_equivalence (round 3)

- `compute_basis` ⊂ rule and `baseline.rule` ⊂ rule for all seven (script check).
- **N1 closed**: `att_o` and `att_r` now test `mh_stay_* > 0` in tier 1, as the rules state.
- **P5, Select side: closed by the scope device** (coordinator decision). Every Select claim, deductible and fee sum is now unwindowed over the enrollment, which by scope took effect in NOW's year, so "the plan year's lines" equals "the enrollment's lines" inside the scope.
- **P5, Prime side: residual RED.** The Prime carryover still uses `XSUM(..., within_months=win, date_field='service_date')` with `win = MONTHS(anchor,NOW)%12 + 1` and the evaluator's day-of-month rule.
  - The Prime enrollment ended inside the plan year, but it began in an earlier year, so its rows are not limited by the Select scope device.
  - Situation inside the scope: Prime line dated 2025-12-30, Select effective 2026-03-20, NOW 2026-10-28. `MONTHS('2025-12-30','2026-10-28') = 9 < 10`, so compute counts the line, while the rule ("the Prime cost shares of the plan year") excludes it.
  - The coordinator's condition (rule and compute agree inside the scope) is therefore not met for the Prime reads.
  - Applies to all five claim policies. No such row in either world.
- The payer-coordination prose and compute match term for term, including the attending-share multiplier on outpatient lines and covered-day proration of billed and allowed amounts on stays.

### prerequisite_graph / prerequisite_sentences (round 3)

- Five state-form value_input edges, same pairs. Gates are now `claims_s` (stay → professional), `fees_counted`, `claims_s`, `fees_s`, `claims_r`; all exist in compute.
- `policy_source` is verbatim in the blocked rules; `resolved_by` matches the target tools; acyclic. Four-point test passes on all five.
- The stay→card sentence is now "…no past-due balance on the installments of the plan year whose coverage period has begun" (no frequency). N5 therefore applies to both fee edges. The resolver is chosen by the elected payment method on the record (card/check → card policy; allotment/EFT/recurring card → draft policy), giving one reading per world. Observation only.
- **O11 (new observation):** for an enrollment that has ended, the ledger keeps the full charge of the period containing the end date. "No past-due balance" holds only under the card/draft policy's proration of that period ("from the start of the period through the month containing the last day of coverage"), not on the raw charge rows. The card rule states the proration explicitly, so the hop still resolves one way.

### override_declarations (round 3)

- Sweep re-run: the round-2 closures hold; no regression found.
- New overwrites: `select_ohi_coordination` on all five claim policies — declared, merge unique.
- The ended-enrollment proration in card/draft agrees with base `select_fee_proration_and_exit` (the month containing the disenrollment date is never credited; no credit is due on unpaid months).
- No undeclared deviation found.

### factor_ladders (round 3)

| policy | factors (label) | structural verdict |
|---|---|---|
| card | fee_level (P), installment_owed (M), counted_charges (M), already_received (P) | all pass. fee_level is now cap → 0 / individual / else family, fall-through = baseline = family (**N2 closed**). counted_charges: ended / active / awaiting activation, three distinct row rules (**F3 closed**); baseline first-only = fall-through. → 2P/2M |
| professional | other_insurance (P), attending_share (P, xd referral), deductible_taken (P), cost_share_basis (M), payer_coordination (M) | all pass; deductible_met removed (**F3 closed**). → 3P/2M |
| stay | covered_days (P, xd referral), inpatient_basis (M), fees_counted (P), prime_carryover (P, xd prime), cap_stage (P), payer_coordination (M) | all pass. fees_counted is now labelled parameter (**N3 closed**); payable_allowed and claims_counted removed (**F3 closed**). → 4P/2M |
| OHI line | other_insurer (P), attending_share (P, xd), deductible_taken (P), cost_share_basis (M), payer_coordination (M) | all pass → 3P/2M |
| draft | fee_level (P), frequency_in_force (P), installment_period (P), counted_charges (M), already_received (P) | **frequency_in_force RED (F3/N4, unchanged)**: tier 1 "the charged frequency" and tier 2 "that frequency" (= charged) select the same value, as the reworker concedes; compute `charged_freq_d if (… != elected) else (charged_freq_d if charged_freq_d else elected)`. The other four pass; installment_period maps the frequency in force to 12/3/1 months with baseline 1 = fall-through. → surviving 3P/1M (bounds met) |
| OHI stay | covered_days (P, xd), inpatient_basis (M), select_fees (P), prime_carryover (P, xd prime), cap_stage (P), payer_coordination (M) | all pass → 4P/2M |
| cap line | attending_share (P, xd), select_fees (P), prime_carryover (P, xd), stage (P), payer_coordination (M) | all pass; select_fees relabelled (**N3 closed**); now has a method → 4P/1M |

- Every factor's fall-through equals its declared baseline. Every `baseline.rule` gives a definite number.
- Bounds (4–6 factors, ≥2 parameter, ≥1 method) are met by every computation after striking draft_frequency_in_force.
- Multi-source: the OHI factors, covered days, attending shares, payer coordination (OHI flag ∧ claim line ∧ provider status). Cross-difficulty: referral (attending/covered days) and prime (carryover) in both trees.

### findings (round 3, charter-global)

- Closed: N1, N2, N3, the F3 fillers (except below), P5 Select side (scope device).
- **Open — SOURCE-FACTOR RED:** draft_frequency_in_force (N4/F3), one value written as two tiers. With it struck the draft still meets the bounds, but it is an unreal ladder declared as a factor.
- **Open — SOURCE-POLICY RED (residual):** P5 Prime side, as above. No consequence in either world (checked per task).
- Observations: N5, N6, N7 (inert cap-credit tier, unchanged), N8 (inpatient basis restates base), O2, O3, O4, O7, O8, O9, O11 (new).

### closing_checklist (round 3, after both round-3 reveals)

Round-3 frozen sections above were on disk before the reveal (sha256 9d5f894a…).

The difficulty **does not pass yet**. What remains is narrow: one unreal ladder, one seed row that contradicts its own charter, and the P5 residual on the Prime side.

- Every scored value of both tasks matches the blind recomputation: task 0 11.50 / 840.00 (liability 200.00, deductible 0.00, auth "") / 5,817.53 (liability 1,382.47, 10 days); task 1 128.77 / 841.50 / 4,489.57 / 542.50. So do all 36 factor figures and 7 baseline totals. (Correction to revision_2, whose text is left as written: there were 36 factor figures there too, not 42.)
- Scope and coverage: two disjoint trees covering all seven policies; tools and uuid8s unchanged and sound. PASS.
- Trees: 2 and 3 prerequisite problems, all value_input, each with a user-owned write, all unmet at the opening and load-bearing, acyclic. PASS.
- Policy: N1, P1–P4, P6, P7 and the Select side of P5 are closed, and no regression was found. The new `select_ohi_coordination` overwrite is declared with a unique merge. Residual: **P5-Prime** — the Prime carryover reads stay month-windowed, and a prior-December Prime line can be counted inside the scope (no consequence in either world).
- Factors:
  - Every computation meets 4–6 / ≥2P / ≥1M with every factor bearing weight against an honest, fall-through baseline.
  - Remaining REDs: draft_frequency_in_force (one value as two tiers) and the task-0 Prime POS seed row (300.00 where its charter gives 450.00; no scored effect).
- Unique solution: both tasks PASS.
- Gates: cited from the round-3 brief (all OK, traceability deferred); not re-run by the auditor.

Per-task verdict lines (round 3):

- task 0: SOURCE-POLICY RED (charter residual P5-Prime only; no consequence on task 0) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (Prime POS seed row `d86c7fa8…` cost_share 300.00 vs charter 450.00; no scored effect) | SOURCE-TASK PASS
- task 1: SOURCE-POLICY RED (charter residual P5-Prime only; no consequence on task 1) | SOURCE-CHAIN PASS | SOURCE-FACTOR RED (draft_frequency_in_force tiers 1 = 2; bounds still met without it) | SOURCE-TASK PASS

---

## revision_4

### charter_global_frozen (round 4)

- Frozen 2026-10-12T03:42Z, before either round-4 task JSON was opened.
- `select.extended.yaml` 56dde7d6… → **8b7451fafdc86404530c7e560dc8636d607ac60ab6ca72183778875442a8018f** (changed), so every charter section is re-derived. A copy is kept at `/tmp/erl55_audit_select/r4/ext_r4.yaml` for later diffs.
- `task_tools.py` 39e04e82… unchanged → § action_binding_and_uuids carried forward on that hash.
- Views: 0 → 5445c715… (changed); 1 → 6dad5d87… (unchanged since round 3). The base copy is still verbatim.
- Not read before this freeze: tasks JSON, the worklog, `/tmp/sel_author/`.

### what changed (charter)

1. The Prime carryover in all five claim policies and their `replaced_by` texts is restated as a "carryover span … from the day after the date in the December before the plan year that bears the adjudication date's day of month through the adjudication date". The Prime compute is unchanged.
2. Card and draft: a calendar-month correction for the first-installment row (its coverage start is the mid-month effective date) in the current-period charge sums (`latest_amt`, `cur_amt_d`, `charged_freq_d`, `after_end*`).
3. Draft: the frequency in force becomes a plain rule (charged frequency of the current year / quarter / month, else elected), no longer a factor. New method factor `draft_latest_installment` (ended → end-period charges; current-period charge exists → that period's charges; else first installment). The card rule now defines its latest installment as "the charges made for coverage periods starting in the installment period that contains the payment date … on or before that date".

### rule_compute_equivalence and override_declarations (round 4)

- `compute_basis` ⊂ rule and `baseline.rule` ⊂ rule for all seven (script check).
- **Prime carryover span: rule ≡ compute.** I checked the evaluator algebra. For a prior-December row, `MONTHS(row, NOW) = month(NOW) − [day(NOW) < day(row)]`, which is `< month(NOW)` exactly when day(row) > day(NOW) — the stated span. Rows after NOW and rows before that December are excluded both ways.
- **P5-Prime NOT closed; it has moved to an undeclared override — SOURCE-POLICY RED.**
  - Base `select_agg_family_accumulators` keeps, un-superseded: "Amounts accumulate to the calendar plan year of the service date (the admission date for inpatient stays), never of the posting date." Only its "Prime cost shares … never count toward the Select family totals" sentence is overwritten.
  - The new span credits Prime cost shares and fees with prior-year December service or coverage dates into this year's family catastrophic total.
  - Situation (inside the scope device): Select effective 2026-03-20 after a Prime plan change; Prime line dated 2025-12-30 with 40.00 cost share; adjudication 2026-10-28.
    - Extended: the span runs 2025-12-29 → 2026-10-28, so the 40.00 is credited to 2026.
    - Base: the line accumulates to plan year 2025 and is not in the 2026 total.
  - The span's start also moves with the day of month of the call, which no plan-year accumulator does. The reworker flags the same gap.
  - No consequence in either world: both adjudication dates are the 31st, so the span starts January 1.
- **C1 — SOURCE-POLICY RED (new in this round's review; the card wording has carried it since round 3): card policy, enrollment ended in an installment period before the payment date's.**
  - The rule's latest installment is "the charges made for coverage periods starting in the installment period that contains the payment date". The installment owed is the proration of "the installment period that contains its last day of coverage". The earlier charges are "the charges counted other than the latest installment".
  - If the enrollment ended in an earlier quarter, the latest installment is a void charge that is not among the counted charges. The rule then subtracts nothing for it, while compute subtracts it: `left_c = paid_c − (charged_due − latest_amt)`.
  - Situation (`/tmp/erl55_audit_select/r4/card_hypo.py`, task-0 enrollment with end date moved to 2026-08-15 and the 5.00 October payment removed): counted charges 115.50 (first 16.50, Q2 49.50, Q3 49.50), payments 115.50, void Q4 49.50, owed = Q3 proration 33.00.
    - Rule: earlier counted charges 115.50 → nothing left → card **33.00**.
    - Compute: left 49.50 → received 33.00 → card **0.00**.
  - The draft policy avoids this: its latest installment for an ended enrollment is the end-period charges.
  - No consequence in task 0: the enrollment ended 2026-10-20, in the payment quarter.
- Other overwrites unchanged and declared. No other regression.

### prerequisite graph / sentences (round 4)

- Unchanged from revision_3: five state-form value_input edges, sentences verbatim, four-point test PASS. N5 and O11 observations stand.

### factor_ladders (round 4)

| policy | change | verdict |
|---|---|---|
| card, professional, stay, OHI line, OHI stay, cap line | factor sets unchanged from revision_3 | pass (as revision_3) |
| draft | frequency_in_force removed (now a plain rule — **F3/N4 closed**); new `draft_latest_installment` (M) | pass. Three distinct row rules; baseline = fall-through (first installment). Observation N9: the fall-through ("otherwise the enrollment's first installment") is a sensible answer only where the first installment is the only charge (awaiting activation, or a retroactive effective date). For an active enrollment with later charges but none for the current period it would point at the first installment rather than the most recent one. That state is not reachable under advance billing, so no red. Draft: 3P/2M |

All seven computations meet 4–6 / ≥2P / ≥1M, with every fall-through equal to its baseline.

### findings (round 4, charter-global)

- Closed: draft_frequency_in_force (F3/N4). Task-0 Prime POS seed row (now 450.00, matching the Prime formula).
- **Open — SOURCE-POLICY RED:** P5-Prime, now an undeclared conflict with base's calendar-plan-year accumulation sentence (no task consequence).
- **Open — SOURCE-POLICY RED (new):** C1, card rule vs compute for an enrollment that ended before the payment date's installment period (no task consequence).
- Observations: N5, N6, N7, N8, N9 (new), O2, O3, O4, O7, O8, O9, O11.

### closing_checklist (round 4, after both reveals)

- Every scored value of both tasks matches the blind recomputation.
- Trees: PASS on both tasks.
- Factors: PASS on both tasks — every computation is within bounds, every factor sound, every factor bears weight against a fall-through baseline, and no cross-difficulty seed row contradicts its charter.
- Unique solution: PASS on both tasks.
- The difficulty **still does not pass**, on two charter-level policy REDs, neither of which moves any scored value in either world:
  1. **P5-Prime:** the "carryover span" now matches the compute, but it credits prior-December Prime amounts into the current year, against base `select_agg_family_accumulators`' un-superseded "Amounts accumulate to the calendar plan year of the service date". This is an undeclared override, and the span's start depends on the call's day of month.
  2. **C1:** the card rule and compute disagree for an enrollment that ended in an installment period before the payment date's (rule 33.00 vs compute 0.00 on the stated situation). Present since round 3; found in this round's review.
- Gates: cited from the round-4 brief (all OK, traceability deferred).

Per-task verdict lines (round 4):

- task 0: SOURCE-POLICY RED (charter P5-Prime undeclared override + C1 card ended-earlier-period mismatch; no consequence on task 0) | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY RED (charter P5-Prime undeclared override; no consequence on task 1) | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_5

### charter_global_frozen (round 5)

- Frozen 2026-10-12T05:15Z, before either round-5 task JSON was opened.
- `select.extended.yaml` 8b7451fa… → **c2472682b51c73235cb1baa1ff9e732d1e298300616e0c0f9e5bb8e559d2b69c**. I diffed it policy by policy against the kept round-4 copy (`/tmp/erl55_audit_select/r4/ext_r4.yaml` → `r5/ext_r5.yaml`, script `r5/pdiff.py`).
- `task_tools.py` 39e04e82… unchanged → § action_binding_and_uuids carried forward.
- Views changed: 0 → 0266188a…, 1 → cb1aed41… (Prime enrollments re-seeded as 2025 open-season elections effective 2026-01-01). The base copy is still verbatim.
- Not read before this freeze: tasks JSON, the worklog, `/tmp/sel_author/`.

### what changed (charter), verified by diff

1. **Five claim policies (Prime scope route).**
   - Scope sentence extended: "…and who holds no TRICARE Prime enrollment or exactly one that took effect in that same plan year…". Compute `scope_*` adds `XCOUNT('prime','prime_enrollments') == 0 or (== 1 and MONTHS(anchor, CFIELD('prime','enrollment_effective_date'))//12 == MONTHS(anchor, NOW)//12)`.
   - The carryover-span sentence is removed. Replaced by "Within this policy's scope the beneficiary's only Prime enrollment took effect in the plan year, so every Prime record belongs to that calendar plan year, and the Prime amounts are: the cost shares on the beneficiary's Prime claim lines other than point-of-service charges, less … Prime reversals, plus the Prime enrollment fees paid toward the Prime installments whose coverage period has begun (the Prime payments posted, never more than those installments…)".
   - Compute: Prime XSUMs unwindowed; `pr_amt = pr_cs + MN(pr_chg_begun, pr_paid)`; `win_*` and `pr_chg_py_*` removed. The `replaced_by` texts and cross_category reads are updated to match (enrollment_effective_date added). The prime_carryover factor bindings drop `pr_chg_py_*`; ladders and baselines are unchanged.
2. **Card.** The latest installment for an ended enrollment is now "the charges whose coverage period starts in the installment period … that contains the last day of coverage, no later than the month containing that day and no later than the payment date". Compute `latest_amt` takes the end-period sum when `ended_c` — the draft's rule.
3. No other rule sentence, compute binding, factor, ladder or baseline changed.

### verification (round 5)

- `compute_basis` ⊂ rule, `baseline.rule` ⊂ rule (script check, all seven).
- **P5-Prime closed.**
  - Inside the new scope the beneficiary has at most one Prime enrollment, effective in the adjudication year. Every Prime claim line and installment therefore carries a service or coverage date in that calendar year (on or after the effective date, on or before NOW).
  - The unwindowed XSUMs equal "the Prime cost shares / fees of the plan year". The base "Amounts accumulate to the calendar plan year of the service date" is respected, and nothing needs an overwrite beyond the declared "never count" sentences.
  - Rule ≡ compute inside the scope. The day-of-month dependence is gone.
- **C1 closed.** Re-running `/tmp/erl55_audit_select/r4/card_hypo.py` (ended 2026-08-15, payment 2026-10-31) under the new charter gives `latest_amt` 49.50 (Q3, the end period), counted 115.50, earlier counted 66.00, left 49.50, owed 33.00 → card **0.00**. The new rule gives the same 0.00. Rule ≡ compute.
- Prerequisite graph and sentences unchanged (five state-form value_input edges, four-point test PASS). Overwrites declared, merges unique. Factor structure as revision_4 (all seven computations 4–6 / ≥2P / ≥1M, fall-through = baseline).
- No regression found; no new defect found.
- Observations unchanged: N5, N6, N7, N8, N9, O2, O3, O4, O7, O8, O9, O11.

### findings (round 5, charter-global)

- Closed: P5-Prime, C1.
- Open: none at charter level.

### closing_checklist (round 5, after both reveals)

- Audit files: `_difficulty.md`, `0.md` and `1.md`, one per task plus the charter file. Revisions 1–5 are appended in order and no earlier text was rewritten (the only edits were round-time placeholders and a correction note, both recorded where they occur). Every comparison section carries a verdict, and in round 5 all are PASS.
- Coverage: all seven extended policies are covered by two pairwise-disjoint trees — task 0 {stay, professional, card}, task 1 {cap line, OHI stay, OHI line, draft}. Task tools close over GT; seven independently generated uuid8s, unchanged since round 1.
- Trees: task 0 has 2 prerequisite problems and task 1 has 3. All edges are value_input (≥ max(n−1, 1)), each tree has a user-owned write (card, bank draft), and every edge is unmet at the opening and load-bearing. The difficulty-wide graph is acyclic.
- Factors: every computation declares 4–6 sound factors (≥2 parameter, ≥1 method), every factor's fall-through equals its baseline, and every factor bears weight on its world. Each task has multi-source factors and cross-difficulty factors (referral and prime) on seeded rows that agree with their charters. Every whole-baseline figure is definite and differs from gold.
- Policy: no open charter-level red. Remaining observations: N5, N6, N7, N8, N9, O2, O3, O4, O7, O8, O9, O11.
- Unique solution: both tasks PASS; every scored value matches the blind derivation.
- Gates: the instantiation-stage gates were re-run by the coordinator on this final form (brief: all OK, check_traceability deferred until the KB is rendered); not re-run by the auditor. The artifact hashes were re-verified at freeze.

**The difficulty passes the source-layer audit as of round 5.**

Per-task verdict lines (round 5):

- task 0: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_6

### charter_global_frozen (round 6)

- Frozen 2026-10-12T06:18Z, before either round-6 task JSON was opened.
- `select.extended.yaml` c2472682… → **f868f3d853259449762b1027f8fc52b2bae7d9d1e37f59cb0b5e5215284f3600**. Diffed policy by policy against the kept round-5 copy (`/tmp/erl55_audit_select/r6/pdiff.py`; copy at `r6/ext_r6.yaml`).
- `task_tools.py` 39e04e82… and both views (0266188a…, cb1aed41…) unchanged. § action_binding_and_uuids carried forward. The base copy is still verbatim.

### auditor's own disclosure on the renderer items

- Items (1)–(3) were present in the charter I passed in revision_5, and I did not report them. My round-5 sweep checked the changed sentences and the scored-value paths, not every rule sentence against every compute binding.
  - (1) Card/draft "earlier counted charges" vs `charged_due − latest_amt` when the latest installment is not among the counted charges.
  - (2) The fee-level catastrophic total: rule wording vs compute's begun-installment cap and fees-count flag.
  - (3) The single-member scope sentence untested in the five claim computes.
- Item (4), the product-wide reading of the prior-authorization `replaced_by`, I had accepted as a scoped overwrite.
- Revision_5's PASS on the policy relationship is withdrawn for those items. This revision re-sweeps the whole charter sentence by sentence.

### verification of the four renderer fixes

1. **Earlier counted charges — closed.**
   - Card: new rule sentence "The earlier counted charges are the charges that count other than those of the latest installment." Compute `earlier_c` = ended: counted − end-period latest; active: begun − current-period latest; awaiting activation: first installment unless it is itself the latest (`first_in_l_c`). `left_c = paid − earlier_c`.
   - Draft: the same, inside the redefined `draft_latest_installment` (it now decides `earlier_d`; baseline = fall-through "counted charges other than the first").
   - Every branch subtracts only a latest installment that is among the counted charges. Re-ran the round-4 hypothetical: still 0.00 by rule and compute.
2. **Fee-level total — closed.**
   - The rule now states, for both card and draft: "Where the enrollment's fee arrangement (fee_coverage_type) is individual … and that total … has reached catastrophic_cap_family … zero; that total is the beneficiary liability posted on the enrollment's Select claim lines less … reversals …, plus, where the tier's fees_count_toward_catastrophic_cap is true, the enrollment fees paid toward installments whose coverage period has begun (the payments posted, never more than those installments)."
   - Compute: `0 if (individual and total ≥ cap) else …`, with `total = claims + (MN(chg_begun, paid) if fees_count else 0)`. Every term is now stated.
   - The overwrite `replaced_by` texts match the rule sentences.
3. **Single-member scope — closed.** All five claim computes now test `F('fee_bearing') == True and F('fee_coverage_type') == 'individual'`, and the scope sentences say the condition is "read from the enrollee's own Select enrollment carrying the family's fee billing (fee_bearing true) under an individual fee arrangement". By base `select_enrollment_fee_schedule`, an individual fee arrangement means exactly one member is enrolled. Rule ≡ compute.
4. **Authorization overwrite — closed.** The OHI-line and cap-line `replaced_by` now read "Only for a line this policy reprocesses … within this policy's scope … gives way …; Every other Select line stays under that rule, and a line without such an authorization is denied as denied_no_authorization." The base clause survives everywhere else; the merge is unique.

- Baseline sentences reworded: "TRICARE pays as primary payer: the allowed amount less that liability" (the attending share is a factor), and the stays/cap drop "no enrollment fee and no Prime amount is added". Each `baseline.rule` is still ⊂ rule and self-sufficient; each factor's baseline equals its fall-through.

### full re-sweep (rule sentence ↔ compute), round 6

- I checked every policy: each P/F name in compute against the rule, each literal status or class, each guard, cap or floor, and each scope clause.
- One new mismatch was found, and has been present since round 2:
- **C3 — SOURCE-POLICY RED: the card computes with the elected frequency, the rule with the frequency in force.**
  - Compute: `freq_c = F('payment_frequency')` (the elected frequency) drives `per_c`, the latest-installment window and the installment owed.
  - Rule: speaks of the installments ("one quarter … for a quarterly installment, all of it for an annual one"; the latest installment is the charges of "the installment period (the calendar quarter for quarterly installments, the calendar year for annual ones)"). The inherited, un-superseded base `select_fee_payment_and_nonpayment` sentence says "A change of frequency or method takes effect from the next installment period". The draft states and computes this as its frequency-in-force rule; the card does not.
  - Situation (`/tmp/erl55_audit_select/r6/card_hypo2.py`, task-0 enrollment made active again, quarterly charges as seeded, elected frequency changed to annual for the coming year):
    - Rule (frequency in force quarterly): Q4 latest 49.50, owed 49.50, earlier counted 115.50, left 5.00 → card **44.50**.
    - Compute (elected annual): latest = all 2026 charges 165.00, owed 198.00 → card **77.50**.
  - No consequence in task 0 (elected = charged = quarterly).
- **O14 (observation, same shape as item 3 but weaker):** the card's and draft's payment-method scope ("elected payment method is a single card payment or a check" / "an allotment, an electronic funds transfer or a recurring card payment") is not tested in compute. A monthly allotment payer gets a card figure (77.50 in the hypothetical, with monthly treated as annual by `per_c`). The two policies split by method and only the card/check one is ever applied to such a payer, and neither rule carries a "settles nothing" sentence for method. I record it rather than rule it red; the coordinator may weigh it with item 3.
- **O12 (observation; the reworker flags it too):** the cap-reached fee waiver applies only to an individual arrangement. A family arrangement is charged annual_fee_family whatever its total. Base gives no waiver at all, so this is no conflict.
- **O13 (observation; flagged by the reworker):** fee-exempt tiers (all four active-duty-family tiers, fee_bearing false) now fall outside all five claim policies. Their corrected, reprocessed and cap-reprocessed lines have no extended policy.
- No other mismatch was found. Earlier observations stand (N5–N9, O2–O4, O7–O9, O11).

### findings (round 6, charter-global)

- Closed: renderer items 1–4.
- **Open — SOURCE-POLICY RED: C3** (card frequency, no task consequence).
- Observations: O12, O13, O14 (new); earlier ones unchanged.

### closing_checklist (round 6, after both reveals)

- Every scored value, gate, load-bearing figure, sensitivity and baseline total of both tasks matches the blind recomputation and is unchanged from round 5.
- Renderer items 1–4: closed (rule ≡ compute, verified branch by branch).
- New charter red **C3** (card frequency: elected vs in force; rule 44.50 vs compute 77.50 on the stated situation). It is the only open item and moves no scored value in either task.
- Observations O12–O14 are recorded for the coordinator's judgement. The difficulty does not pass on the policy relationship until C3 is closed.
- Gates: cited from the round-6 brief (all OK, traceability OK, validate_scenario VALID); not re-run by the auditor.

Per-task verdict lines (round 6):

- task 0: SOURCE-POLICY RED (charter C3 card frequency elected-vs-in-force; no consequence on task 0) | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_7

### charter_global_frozen (round 7)

- Frozen 2026-10-12T06:43Z, before either round-7 task JSON was opened.
- `select.extended.yaml` f868f3d8… → **63267be82acca3494e18054064fca76b102c9b53edc3c515c6b1b0d2ce7448b5**. Diffed against the round-6 copy (`/tmp/erl55_audit_select/r7/pdiff.py`). Only the card and draft policies changed.
- `task_tools.py` and both views unchanged. Base copy verbatim.

### verification

- **C3 closed.** The card now states and computes the frequency in force exactly as the draft does: `charged_freq_c` = annual / quarterly / monthly charge of the current year / quarter / month, else elected; `per_c` = 12 / 3 / 1. Re-ran `r6/card_hypo2.py`'s situation (`r7/hypo.py`): elected annual, charged quarterly → freq in force quarterly, latest 49.50, owed 49.50, earlier 115.50 → **44.50**, now equal to the rule's figure.
- **O14 closed.** The card scope now states and tests `fee_bearing`, method ∈ {card_single, check} and frequency in force ∈ {quarterly, annual}. The draft scope states and tests `fee_bearing` and method ∈ {allotment, electronic_funds_transfer, recurring_card}. Out of scope, `result` is None; rule ≡ compute.
- **"Ended" redefinition (reworker's sweep fix): rule ≡ compute, but it introduces a new defect.**
- **C4 — SOURCE-POLICY RED (new this round; regression from the "ended" fix).**
  - The new card and draft sentence reads: "In this policy an enrollment has ended when a last day of coverage, the disenrollment date on its record, is on record and falls before the payment date; an enrollment that has not ended and whose status is not active is taken as awaiting activation." Compute: `ended = disenrollment_date != '' and DAYS(disenrollment_date, NOW) > 0`.
  - An enrollment whose status is already `disenrolled_voluntary` (or `terminated_ineligible` / `transferred_out`) is classed as **awaiting activation** when the payment falls on, or before, its recorded last day of coverage. Base lifecycle reserves "awaiting activation" for an `applied` enrollment, and base `select_fee_proration_and_exit` owes the fee only through "the month containing the disenrollment date" ("the paid fee for every whole calendar month after the disenrollment date is credited").
  - Situations (`/tmp/erl55_audit_select/r7/hypo.py`, `r7/hypo_d.py`):
    - **Card**, task-0 enrollment (disenrolled_voluntary, last day 2026-10-20), payment on 2026-10-20: compute (= new rule) counts only the first installment as a charge → earlier 16.50, left 104.00 → card **0.00**. The same enrollment paid one day later → **11.50**. Under base, October of Q4 is owed either day.
    - **Draft**, task-1 enrollment set to disenrolled_voluntary with last day 2026-10-31, payment on 2026-10-31: compute owes the whole Q4 (148.77) → draft **128.77**. One day later it prorates to October → **29.59**. Base never owes November–December after a 10-31 disenrollment.
  - Affected: `select_ext_card_installment_payment` and `select_ext_bank_draft_payment` (the "ended" sentence; `ended_c`/`ended_d`; the awaiting-activation branches of `card_counted_charges`, `draft_counted_charges` and `draft_latest_installment`).
  - No consequence in either task world (task 0's last day 2026-10-20 is before the payment date 2026-10-31; task 1 is active with no disenrollment date).
- No other change. The five claim policies are byte-identical to round 6. Factor structure, baselines and prerequisite graph unchanged.

### findings (round 7, charter-global)

- Closed: C3, O14.
- **Open — SOURCE-POLICY RED: C4** (new; no task consequence).
- Observations unchanged: O12, O13, N5–N9, O2–O4, O7–O9, O11.

### closing_checklist (round 7, after both reveals)

- Every scored value, load-bearing figure, sensitivity and baseline total of both tasks matches the blind recomputation and is unchanged.
- C3 and O14 are closed.
- One new charter red, **C4**, came in with this round's "ended" fix. It moves no scored value in either world but makes card and draft give base-contradicting figures for a payment on or before the recorded last day of coverage of an already-disenrolled enrollment: card 0.00 vs 11.50 the next day; draft 128.77 vs 29.59.
- The difficulty does not pass on the policy relationship until C4 is closed.
- Gates: cited from the round-7 brief; not re-run by the auditor.

Per-task verdict lines (round 7):

- task 0: SOURCE-POLICY RED (charter C4 card; no consequence on task 0) | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY RED (charter C4 draft; no consequence on task 1) | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_8

### charter_global_frozen (round 8)

- Frozen 2026-10-12T07:12Z, before either round-8 task JSON was opened.
- `select.extended.yaml` 63267be8… → **9f9c1824ce802b0494f473984c7eddcbeb5ec4a3eb69939ba033426afc6d6474**. Diffed against the round-7 copy (`/tmp/erl55_audit_select/r8/pdiff.py`, copy `r8/ext_r8.yaml`).
- `task_tools.py` and both views unchanged. Base copy verbatim.

### what changed (verified by diff)

1. **Card and draft standing**: "An enrollment's standing in this policy is its lifecycle status: it has ended when its status is disenrolled_voluntary, disenrolled_nonpayment, terminated_ineligible or transferred_out, whatever the payment date, and its last day of coverage is then the disenrollment date on its record; it is active when its status is active; and it is awaiting activation when its status is applied." Plus "A rejected enrollment owes no fee and is outside this policy." Compute `ended_*` is the same status set; `scope_*` adds status ∈ {applied, active, the four ended states}.
2. **OHI line and cap line**: the prior-authorization `replaced_by` and rule sentence now read "For a line this policy reprocesses …, payability does not rest on a fresh authorization test: the reprocessed line is payable on the authorization finding of the line it replaces and carries that line's authorization reference …". The "every other Select line stays under that rule" wording is gone. The overwrite is scoped by its own subject (lines this policy reprocesses), and the base clause keeps governing every other line. The tools copy the replaced line's `prior_authorization_id`, matching "carries that line's authorization reference".
3. **All five claim policies**: new sentence "A fee-exempt enrollment carries no fee arrangement from which the family's Select membership can be read, so the fee-exempt tiers (the Active Duty Family Member tiers) are outside this policy by design." This turns O13 into a stated scope; rule ≡ compute, since `scope_*` already requires `fee_bearing`.
4. No compute other than `ended_*`/`scope_*` (card and draft) changed. No factor, ladder or baseline changed.

### verification

- **C4 closed.** Rule ≡ compute, and both agree with base lifecycle and `select_fee_proration_and_exit`. Re-ran `r8/hypo.py`, `r8/hypo_d.py` and `r8/hypo_more.py`:
  - Card, last day 2026-10-20: payment on 10-20 → **11.50**, on 10-21 → **11.50** (round 7: 0.00 vs 11.50).
  - Draft, last day 2026-10-31: payment on 10-31 → **29.59**, on 11-01 → **29.59** (round 7: 128.77 vs 29.59).
  - Card, disenrolled with last day 2026-11-15 (future): owed Oct–Nov 33.00 → 28.00, matching base (whole months after the disenrollment date are not owed).
  - Card, status applied → counts the first installment only (0.00 here). Status rejected → no result.
  - C3 re-check: 44.50, unchanged.
- Rule-sentence ↔ compute sweep re-run on the changed sentences and their bindings: no mismatch. The unchanged policies are byte-identical to round 7.
- No regression and no new defect found.
- Observations: O13 now stated as scope (closed as an observation). O12, N5–N9, O2–O4, O7–O9, O11 unchanged.

### findings (round 8, charter-global)

- Closed: C4.
- Open: none.

### closing_checklist (round 8, after both reveals)

- Process note: while writing the frozen section, unescaped backticks in a heredoc dropped two code names from item 3 ("since `scope_*` already requires `fee_bearing`"). I restored them before the reveal; that was the only edit.
- C4 closed; no open charter-level red; no regression; no new defect.
- Every scored value, load-bearing figure, sensitivity and baseline total of both tasks matches the blind recomputation and is unchanged since round 5.
- Coverage, trees, factor bounds, cross-difficulty evidence and unique solution as in the revision_5 checklist, all still holding.
- Remaining observations, none moving a scored value: O12 (no cap waiver for family arrangements, base gives none), N5–N9, O2–O4, O7–O9, O11.
- Gates: cited from the round-8 brief (all OK incl. traceability; validate_scenario VALID); not re-run by the auditor.

**The difficulty passes the source-layer audit as of round 8.**

Per-task verdict lines (round 8):

- task 0: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_9

### entry: gates run by the auditor (on the coordinator's instruction)

Run from the repo root at 2026-10-12T07:16Z, on `env/env_0055_military_health_plan_administrator/tasks/select_claims_and_cost_shares`:

| gate | result line |
|---|---|
| check_extended | EXTENDED OK (7 extended policies, 5 cross-category reads, 7 tools, 2 tasks) |
| check_task_tools | TASK TOOL CONTRACT OK (7 tools) |
| replay_tasks | REPLAY OK (0.json 18 acts / 43 closure match; 1.json 20 / 54 match) |
| check_solvability | SOLVABILITY OK |
| check_compute | COMPUTE OK (suite mean branches 143.50, steps 19.00) |
| check_grounding | GROUNDING OK |
| check_cross_fire | SCOPE OK (hard-fails 0) |
| check_traceability | TRACEABILITY OK (0.json 21 / 0 missing; 1.json 23 / 0 missing) |

- All green, so the audit proceeds.
- sha256: `select.extended.yaml` **7da5f3b38ebc443f5048cfa16c13ace6efdab2dbfb2f60ec26cdccf57199bac1** (changed since round 8); `task_tools.py` 39e04e8226e6… (unchanged); `0.view.json` 0266188a… and `1.view.json` cb1aed41… (unchanged).
- Disclosure: replay, solvability, grounding and traceability read `tasks/*.json` internally. Their printed output carries only counts and booleans, no GT value.

### charter_global_frozen (round 9)

- Frozen 2026-10-12T07:17Z, before any round-9 task-JSON field was read.
- Diff against the round-8 copy (`/tmp/erl55_audit_select/r9/pdiff.py`, copy `r9/ext_r9.yaml`): **only two sentences changed**, each in both the OHI-line and cap-line policies' rule and in their prior-authorization `replaced_by` (verbatim equal; script-checked).
  - OHI line: "For a line this policy reprocesses for other health insurance found retroactively, and only for such a line, the authorization finding of the line it replaces stands in place of a fresh authorization test: the reprocessed line is payable on that finding and carries that line's authorization reference, because only the payer order changes; every other Select line remains under the base authorization rule."
  - Cap line: the same, with "for the catastrophic cap" and "because only the family's catastrophic standing is revisited".
  - No compute, factor, baseline, prerequisite or other overwrite changed. Base copy verbatim.

### verification

- **Overwrite scope — closed.** Each `replaced_by` is a rule sentence of its own policy, names its own scope ("a line this policy reprocesses … and only for such a line"), and states that every other Select line remains under the base authorization rule. The merged semantics are unique: the reprocessed line is payable on the replaced line's finding and carries its reference (the tools copy `prior_authorization_id` from the source row); every other line is governed by base `select_prior_authorization_and_filing` and its `authorization_on_file` eligibility, unchanged.
- **O16 (observation, same declaration class, no red):** the other overwrites also supersede a base sentence with a `replaced_by` that speaks only of the policy's own write, without an explicit "every other line remains" clause:
  - Prime "never count" (agg_family_accumulators, catastrophic_cap) in the five claim policies;
  - `select_ohi_coordination` in the five;
  - `select_enrollment_fee_schedule` in card and draft.
  For each, the base quantity for every other write is still fixed by an un-superseded base formula or measure, so no second reading arises:
  - `select_msr_family_catastrophic_ytd` excludes Prime;
  - the base `select_ohi_coordination` formula is `tricare_paid_amount: max(0, allowed_amount - ohi_paid_amount - cost_share_amount)`;
  - the base fee-schedule formula is `annual_fee: annual_fee_family if fee_coverage_type == "family" else annual_fee_individual`.
  The authorization clause differed because its only other carrier is the eligibility condition with the identical sentence. Recorded in case the renderer applies the same reading to these.
- **Regression:** none. Recomputation on both worlds is unchanged; the card, draft, scope and standing re-checks of rounds 6–8 stand (no compute changed).
- Open charter-level reds: none.

### closing_checklist (round 9, after both reveals)

- Gates: all eight green on the final form, run by the auditor at 07:16Z (table above).
- The overwrite-scope change is genuine. Both prior-authorization `replaced_by` texts are rule sentences naming their own scope and keeping the base rule for every other Select line.
- No regression: every scored value, load-bearing figure, sensitivity and baseline total of both tasks is unchanged and matches the blind recomputation.
- No open charter-level red. New observation O16 (other overwrites of the same declaration class, each still pinned by an un-superseded base formula or measure).

**The difficulty passes the source-layer audit as of round 9.**

Per-task verdict lines (round 9):

- task 0: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS

---

## revision_10

### entry: gates run by the auditor (on the coordinator's instruction)

Run from the repo root at 2026-10-12T07:38Z on `env/env_0055_military_health_plan_administrator/tasks/select_claims_and_cost_shares`: check_extended **EXTENDED OK** · check_task_tools **TASK TOOL CONTRACT OK** (7 tools) · replay_tasks **REPLAY OK** (0.json 18 acts, 43/43 closure; 1.json 20 acts, 54/54) · check_solvability **SOLVABILITY OK** · check_compute **COMPUTE OK** · check_grounding **GROUNDING OK** · check_cross_fire **SCOPE OK** (hard-fails 0) · check_traceability **TRACEABILITY OK**. All green.

sha256:

| file | hash | vs round 9 |
|---|---|---|
| `select.extended.yaml` | 7da5f3b38ebc443f5048cfa16c13ace6efdab2dbfb2f60ec26cdccf57199bac1 | byte-identical (cmp) |
| `task_tools.py` | **283e0d0017ca18e68941dd4bbee44f3e9739816a2a3a92800f3b395da3d46571** | changed |
| `0.view.json` | 0266188a… | unchanged |
| `1.view.json` | cb1aed41… | unchanged |

I checked each task JSON's `frozen_time`, `user_scenario` and `initial_state` against its view, reading only those three keys: equal for both tasks, so the views stand and no rebuild was needed.

### charter_global_frozen (round 10)

- Frozen 2026-10-12T07:38Z, before any round-10 GT field was read.
- The charter is unchanged, so § prerequisite graph/sentences, override declarations, factor ladders and rule ↔ compute are carried forward from revision_9 on the identical hash.
- § action_binding_and_uuids is re-derived because the tool module changed.

### action_binding_and_uuids — tool contracts vs effects (all 7 tools)

- **Card (`pay_select_installment_by_card_fa3a0d38`) and bank draft (`authorize_select_bank_draft_0bb89bb0`).**
  - Docstrings now: "…tied to the installment charge named here, and the enrollment's recorded fee balance (fee_balance_due) falls by the amount paid [drafted], never below 0.00."
  - Bodies: after creating the payment row, `ctx.update("select_enrollments", enr_id, fee_balance_due=max-0(balance − amount))` on the enrollment that owns the named charge.
  - **Contract and effect now agree (O3 closed).**
  - Neither body refuses, errors or hints on any prerequisite; no ordering words; no other tool named.
- **Five claim tools.** Bodies unchanged; each docstring's stated effect (one new paid line on the same claim, with the listed copied fields and the given deductible / liability / TRICARE payment; deductible 0 on the stay and cap tools) matches the body.
  - Unchanged minor gap (O17): the OHI-line, OHI-stay and cap-line bodies also copy the replaced line's `prior_authorization_id`, which their docstrings do not list among the repeated fields. The policy rules state it ("carries that line's authorization reference"), so no reading changes.
- uuid8 tails unchanged and independent.
- **Effect on scoring and near-misses.**
  - No compute reads `fee_balance_due`; every computation reads the ledger.
  - Recomputation on both worlds is unchanged: 11.50 / 840.00 / 5,817.53; 128.77 / 841.50 / 4,489.57 / 542.50; load-bearing and all-baseline figures identical.
  - Opening balances 94.00 (task 0) and 178.36 (task 1) are still not the scored payments; they include the void Q1-2027 charge / the billed-ahead Jan-2027 charge. After the gold payment the balance reads 82.50 and 49.59, which are not scored values either.
  - The field still does not hand over a scored value.
- **O18 (observation, new):** the floor at 0.00 departs from base account semantics ("a negative value is a credit owed to the beneficiary") when a payment exceeds the recorded balance. It is not reached in either world, since both payments are below the balance.
- **O3a (observation):** `fee_balance_due` is the gross account balance (charges, including billed-ahead or void ones, less payments). It is not the "past-due balance" the prerequisite sentences and fee policies define from begun or counted charges. A reader must take the gate state from the ledger, as the rules say.

### findings (round 10)

- Closed: O3 (tool contract vs effect).
- Open reds: none.
- New observations: O17 (unchanged detail), O18, O3a.

### closing_checklist (round 10, after both reveals)

- Gates: all eight green on the final form, run by the auditor at 07:38Z.
- The change is genuine: the card and bank-draft tools now reduce `fee_balance_due` exactly as their docstrings say. The other five tool contracts match their effects (O17 detail aside).
- No scored value, load-bearing figure, sensitivity or baseline total moved.
- `fee_balance_due` hands over no scored value before or after the payment.
- No open red. Observations O3a, O17 and O18 are recorded.

**The difficulty passes the source-layer audit as of round 10.**

Per-task verdict lines (round 10):

- task 0: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
- task 1: SOURCE-POLICY PASS | SOURCE-CHAIN PASS | SOURCE-FACTOR PASS | SOURCE-TASK PASS
