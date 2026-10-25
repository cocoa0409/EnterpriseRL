# Policy-task audit — private_pay_residency_billing / charter-global

## revision_1

## charter_global_frozen
- freeze: 2026-10-22T05:40Z, before any task's GT was opened; built from the charter, the schema, the tool contracts and the blueprint only. Auditor: independent policy-task auditor (erl-task-policy-audit).
- hashes: `tasks/private_pay_residency_billing/private.extended.yaml` d3a93349b4adbcc32cc41de0eebd7a269e78d0c73d945bf10d3202c647efe87c; `task_tools.py` 0315c61252bf57084edb70ed3a20424f8f2ff948055fcbbb57a401770f694785 (both match the coordinator snapshot).
- entry conditions (cited, not re-run): coordinator snapshot /tmp/erl0074_coord/snap_private_pay_residency_billing_r1.txt — check_extended, check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred to post-publication; masked views and hashes supplied. Complete.
- permitted: blueprint/*, products/*.yaml, the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the two masked views. Masked: tasks/*.json GT fields, worklog.md, plan.md, all other audits.

### policy_conflict_scan
- Base copy: every top-level key of the extended file (category … policies) equals blueprint/products/private.yaml (mechanical comparison). Seven extended policies: private_ext_late_notice_credit (credit_late_notice_days_45589810), private_ext_room_change_credit (credit_room_change_days_09a50cb9), private_ext_new_room_span (post_new_room_span_526f1e53), private_ext_additional_deposit (pay_additional_deposit_f9f00bc8, user), private_ext_conversion_credit (credit_converted_days_12618703), private_ext_resumed_recharge (post_resumed_recharge_e6f5843a), private_ext_resumption_deposit (pay_resumption_deposit_9c511f79, user).
- Scopes (from the masked views' asks and the prerequisite graph): task 0 = late-notice -> room-change -> new-room span -> additional deposit; task 1 = conversion credit -> re-charge -> resumption deposit. Pairwise disjoint, jointly complete over the seven policies.
- Overlaps found:
  - private_ext_room_change_credit vs private_ext_conversion_credit — both state_due credits on "the most recently posted room-and-board charge"; when a resident moves while another payer covers the stay, both subject states hold on the same advance and both credit the moved days; neither rule nets or excludes the other's credit (conversion nets only rate_notice_late / billing_error; room-change nets rate_notice_late, or — credited_days_rule tier 2 — counts no day for a charge carrying a payer-conversion credit). See F-06.
  - private_ext_late_notice_credit vs private_ext_new_room_span — new_room_span prices a requested move at the current schedule regardless of the agreement's notice; the late-notice policy (state_due, latest charge) then computes a further late-notice credit on that very span. See F-02.
  - private_ext_additional_deposit vs private_ext_resumption_deposit — sibling overwrites of private_deposit sentence 1, each naming both cases; scope split on "a move made while another payer source covered the stay". A resident who moved while billed privately and later converted and resumed matches both rules' scope sentences (observation O-7).
- Cross-category read boundaries: reads of medicare (coverages, ledger) and bedhold (reservations, ledger) only; no write lands outside category private (all tool bodies write private_ledger / private_agreements; events written: private_adjustment, private_room_board_charge, private_deposit_received, all `triggers: []`). The toolset available in this difficulty (7 task tools + share tools, whose only writes are verify_customer_identity and transfer_to_human_agent) contains no other product's write, so no write that another product's rules call owed can be made mid-conversation; within this product see F-02 and F-06.

### rule_compute_equivalence
- Mechanical sweep: every compute_basis quote is verbatim in its own rule (all 7); every baseline.rule sentence is in its rule; every prerequisite policy_source is in its rule. Compute bindings without a basis entry: additional_deposit (agr_tier, moved_on, iso_on), conversion_credit (agr_tier, agr_status, conv_to, notice, moved_on, iso) — plain field reads whose conditions are quoted elsewhere (observation O-3).
- Rounding: every rule says "rounded half up to the cent once, on the final figure" and every compute has a single RND on `result` (XF 10 satisfied).
- Rule/compute or rule-internal disagreements (F-04, F-13) and unstated edge/tie branches (F-03, F-14) are listed under findings.

### action_binding_and_uuids
- (target_tool, computes) pairs are unique, one policy each. uuid8s 45589810, 09a50cb9, 526f1e53, f9f00bc8, 12618703, e6f5843a, 9c511f79: distinct, no common prefix, no sequence. No factor id is a substring of a tool name (mechanical). No docstring names another tool or carries a sequencing word (the only "once" is in Returns, "the balance once the credit is posted", describing this call's own effect). No concrete example values in docstrings (formats and enumerations only). No composed multi-value arguments. Every write tool calls ctx.create and ctx.update in its own body. Imports: only `from erlbench import ToolContext, tool`.
- Tool bodies vs docstrings: F-16.

### prerequisite_graph
- Edges: late_notice -> room_change (gate pre_days), room_change -> new_room_span (new_span_days), new_room_span -> additional_deposit (dep_tier), conversion -> resumed_recharge (rc_days), resumed_recharge -> resumption_deposit (r_src). All `form: state`, `kind: value_input`, gates exist in the blocked compute, `resolved_by` = the depended-on target_tool, every `problem` an extended id, no self-edge, acyclic (two chains). `prerequisite: []` on late_notice and conversion. No authoring-viewpoint phrasing in the prerequisite fields.
- effect statements re-checked on the task worlds (task files, problem_chain): each write changes the gate binding as described.

### prerequisite_sentences
- room_change: "Before the room-change credit on a charge is fixed, that charge must carry the late-notice credit owed on it." Ordering connective "Before"; state = a late-notice credit standing on the charge (record-visible adjustment reason rate_notice_late); no tool/id; one write of this difficulty produces it under a policy rule (the late-notice policy; the other credit tools accept the enum value but no other rule posts it). Reading: sentence + the charge's adjustments + the late-notice rule -> post the late-notice credit first. Single reading.
- new_room_span: "The span for the resident's new room is not posted until the charge for the room the resident left carries its room-change credit." "not … until"; state = room_change_proration adjustment on the old-room charge; single producer (room-change policy). Single reading.
- additional_deposit: "The additional deposit is worked out only after the agreement carries the room-and-board span charged for the resident's new room." "only after"; state = a span for the new room; single producer (new_room_span). Single reading.
- resumed_recharge: "The span re-charging the days after the other payer source's coverage ended is posted only after the advance charge billed for those days carries its payer-conversion credit." Single producer (conversion policy). Single reading.
- resumption_deposit: "The resumption deposit is not worked out until the agreement carries the span re-charging the days after the other payer source's coverage ended." Single producer (resumed_recharge). Single reading.
- No depended-on rule restates the sentence; no rule states an order that grounds no edge; no base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against each base_policy_refs entry (findings only; consequences in task files).
- late_notice_credit (refs private_rate_schedule, private_evt_discharge_refund, private_evt_room_board_billing; overwrite []): follows "each charged day is priced at the rate in effect", the effective-date rule and rounding. Departs from private_rate_schedule "days billed at a new rate before it took effect are credited with reason rate_notice_late" by excluding the latest leave's days from the credited days — undeclared (F-01).
- room_change_credit (refs private_tier_placement, private_evt_discharge_refund, private_evt_room_board_billing; overwrite []): tier 1 follows "credits any advance charge for the remaining days at the old tier". Fall-through "the move starting day is the day after the move date, the move day itself staying with the room the resident left" contradicts private_tier_placement "A move the resident requests reprices from the move date" and the midnight census of private_evt_room_board_billing — undeclared (F-05).
- new_room_span (refs private_evt_room_board_billing, private_rate_schedule, private_tier_placement; overwrite []): schedule_choice tier 1 ("the move reprices without notice and the new room's schedule is the current private pay schedule") departs from private_rate_schedule "A scheduled rate takes effect for an agreement on the later of … until then the earlier scheduled rate applies" and from private_evt_room_board_billing "A month in which the tier or the rate changes is split into one span per tier and rate" — undeclared (F-02). Fall-through span start "from the day after the move date" contradicts "reprices from the move date" — undeclared (F-05).
- additional_deposit (refs private_deposit, private_evt_payments, private_tier_placement, private_agg_multi_holding): private_deposit sentence 1 declared and restated with scope (sibling exclusion present). Deposit tier under an isolation placement = the agreement's own (isolation room's) tier, against private_tier_placement "A move the center directs for infection control … does not by itself change what the resident pays" — undeclared (F-15).
- conversion_credit (refs private_payer_source_change, private_evt_discharge_refund, private_rate_schedule, private_evt_room_board_billing): both conflicting sentences declared with scope and restated. No further departure found.
- resumed_recharge (refs private_payer_source_change, private_evt_room_board_billing, private_rate_schedule, private_tier_placement): Part A resumption sentence declared with scope ("a late SNF Advance Beneficiary Notice or an upheld review moves the first re-charged day"). Tier 2 (upheld review -> day after the decision date) can move the first re-charged day before the day after the last covered date the base sentence keeps (F-11).
- resumption_deposit (refs private_deposit, private_evt_payments, private_payer_source_change, private_agg_multi_holding): both private_deposit sentences declared with scope; deposit tier under isolation as in F-15.

### factor_ladders
| policy | factor | label | tiers | multi-source | cross_difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| late_notice | notice_anchor | method | 3 | no | – | ok; negative-lag edge unstated (F-03) |
| late_notice | leave_kind | method | 3 declared, 2 reachable | no | bedhold | STRUCK: tier 2 unreachable (F-07); window wider than late days (F-08) |
| late_notice | billed_tier | parameter | 3 | yes | – | ok |
| late_notice | earlier_source | parameter | 3 | tier 2 only | – | tier 1 cross-tier value (F-09) |
| room_change | move_date_source | method | 3 | yes | – | tier 2 rule/compute mismatch (F-04); absent-request edge (F-13) |
| room_change | move_day_rule | method | 3 | no | – | tiers 1/3 constant offset (F-10); fall-through vs base (F-05) |
| room_change | come_off_tier_rule | parameter | 3 | yes | – | ok |
| room_change | come_off_schedule_rule | parameter | 3 | no | – | ok |
| room_change | credited_days_rule | method | 3 | no | – | tier 2 unreal (F-06) |
| room_change | credited_step_rule | parameter | 3 | no | – | mislabelled (F-10); tier 1 cross-tier (F-09) |
| new_room_span | span_start_rule | method | 3 | no | – | tiers 2/3 constant offset (F-10); fall-through vs base (F-05) |
| new_room_span | span_leave_rule | method | 3 declared, 2 reachable | no | bedhold | STRUCK (F-07) |
| new_room_span | priced_tier_rule | parameter | 3 | yes | – | ok |
| new_room_span | schedule_choice | parameter | 3 | tier 2 | – | tier 1 undeclared override (F-02); "a request on file" vs latest (F-13) |
| additional_deposit | deposit_days_record | parameter | 3 | no | – | ok (realism note O-2) |
| additional_deposit | deposit_tier_rule | parameter | 3 | tier 1 | – | tier 2 unreal (F-15) |
| additional_deposit | deposit_schedule_rule | parameter | 3 | no | – | ok |
| additional_deposit | insurer_benefit_rule | method | 3 | no | – | ok |
| conversion | first_converted_day_rule | method | 3 | yes | medicare | ok |
| conversion | kept_days_rule | method | 3 | tier 1 | medicare | tiers 2/3 fail shape test (F-10); tier 1 rule/compute (F-13) |
| conversion | credit_tier_rule | parameter | 3 | tier 1 | – | tier 1 condition only in ladder/compute (F-13) |
| conversion | credit_schedule_rule | parameter | 3 | no | – | ok |
| conversion | netted_days_rule | method | 3 | tier 1 | – | ok |
| conversion | netted_step_rule | method | 3 | tier 1 | – | ok |
| resumed_recharge | recharge_start_rule | method | 3 | yes | medicare | tier 2 unreal / equals fall-through (F-11) |
| resumed_recharge | recharge_leave_rule | method | 3 declared, 2 reachable | no | bedhold | STRUCK (F-07); window mismatch (F-08) |
| resumed_recharge | recharge_tier_rule | parameter | 3 | yes | medicare | ok |
| resumed_recharge | recharge_schedule_rule | parameter | 3 | no | – | tier 1 extra compute condition (F-13) |
| resumption | resumption_days_rule | parameter | 3 | tier 1 | – | ok (realism note O-2) |
| resumption | resumption_tier_rule | parameter | 3 | tier 2 | – | tier 2 unreal (F-15) |
| resumption | resumption_schedule_rule | parameter | 3 | no | – | ok |
| resumption | resumption_method_rule | method | 3 | tier 2 | – | ok |
| resumption | resumption_insurer_rule | method | 3 | no | – | zero-divisor edge (F-13) |
| resumption | resumption_held_rule | method | 3 | tier 1 | – | ok; reads account_balance (F-06 exposure) |

- Every ladder is stated in the rule (condition and outcome) and implemented in compute; decides are inputs, never `result`; binding sets disjoint; no factor binding reads another factor's binding (checked transitively; shared selections — chg_*, moved_on, iso, conv_on, span_days, std_* — are plain bindings).
- Counts after strike-outs: late_notice 3 (needs 4), new_room_span 3 (needs 4), resumed_recharge 3 (needs 4); room_change 6, additional_deposit 4, conversion 6, resumption 6. Every policy still has >= 2 parameter and >= 1 method. Task 0 loses both of its cross-difficulty factors (leave_kind, span_leave_rule); task 1 keeps four medicare ones.

### findings
Every finding below is RED (coordinator rule: any XF-class member is RED). Each names its members in full and the tasks it bears on.

F-01 SOURCE-POLICY — undeclared departure from base in the late-notice credit (XF 16, 18). Base private_rate_schedule: "days billed at a new rate before it took effect are credited with reason rate_notice_late." Extension rule: "The late-notice credit equals the late-notice days less the late-notice leave days, never below zero, times the gap …"; overwrite []. The leave days were billed at the new rate before it took effect and the base sentence credits them. Members: private_ext_late_notice_credit (result, away_days). Bears on task 0 (demonstrated there: 252.00/10166.00 vs 210.00/10208.00).

F-02 SOURCE-POLICY — undeclared override of the agreement-level rate effective date for a requested move (XF 16, 18) and a charter-internal collision. new_room_span rule: "where a room-change request on file names a date on or before the move date recorded on the agreement, the move reprices without notice and the new room's schedule is the current private pay schedule". Base private_rate_schedule: "A scheduled rate takes effect for an agreement on the later of the schedule's effective date and the rate notice delivery date plus the rate change notice days; until then the earlier scheduled rate applies"; private_evt_room_board_billing: "A month in which the tier or the rate changes is split into one span per tier and rate." (private_tier_placement's "needs no advance rate-change notice" governs the tier change, not the schedule's effective date.) Second face: private_ext_late_notice_credit, state_due on "the most recently posted room-and-board charge", computes a further credit on the extension's own span. Members: new_room_span schedule_choice tier 1; late_notice_credit's subject on a span posted by new_room_span. Bears on task 0.

F-03 SOURCE-POLICY — negative-lag edge unstated (XF 11). late_notice rule tier: "where the notice was delivered fewer than the rate change notice days before the schedule's effective date, …"; compute `DAYS(notice_date, '2026-07-01') < P('rate_change_notice_days')` is true for a notice delivered after the effective date; the rule does not say whether a notice delivered after the date counts as delivered "fewer than … days before" it. Member: late_notice notice_anchor tier 2. Bears on task 0 (notice delivered 2026-08-20; literal reading gives 0.00).

F-04 SOURCE-POLICY — rule/compute disagreement in the room-change credit (XF 9-11, A4). Rule: "where the agreement records a move date before the first day of the charge's span, the move date is the first day of the span and the whole span is moved". Compute: move_date = chg_from, but move_shift falls to 1 (tier 1 of move_day_rule needs a move date inside the span), so days moved = span − 1. Producible world: move recorded 2026-09-28, October advance posted 2026-09-25 at the old tier -> rule 31 days, compute 30. Member: room_change move_date_source tier 2 x move_day_rule fall-through. Charter-global (no task world is on this branch).

F-05 SOURCE-POLICY / SOURCE-FACTOR — fall-throughs contradict base "A move the resident requests reprices from the move date" (and the midnight census): room_change move_day_rule fall-through ("the move starting day is the day after the move date; the move day stays with the room the resident left"); new_room_span span_start_rule fall-through ("from the day after the recorded move date"). Undeclared (overwrite []), and a fall-through this operator's own published base rule rules out, so the baseline against which these factors "bear weight" is a straw man: a reader of the base sentence moves the move day without either factor's document. Bears on task 0 (both factors are scored there).

F-06 SOURCE-POLICY / SOURCE-TASK — overlapping state_due credits on one advance (conflict scan; XF 30 within the product). room_change rule: "This policy settles the room-change credit on the most recently posted room-and-board charge of an agreement, the charge billed for the room the resident left." conversion rule: "This policy settles the conversion credit on the most recently posted room-and-board charge of an agreement whose stay another payer source took over". When the move happened during the covered stay, both hold on the same charge and both credit the moved days; neither nets the other. The room-change rule even anticipates the case and keeps the double credit: credited_days_rule tier 2 "where it carries no late-notice credit but carries a payer-conversion credit, they are none, the converted days being off the charge already" — the days it says are already off are credited again in full (unreal tier outcome). The resumption deposit's held credit reads account_balance, so the extra credit moves a scored read. Members: room_change subject x conversion subject; room_change credited_days_rule tier 2; resumption_held_rule's account_balance read. Bears on task 1 (demonstrated there).

F-07 SOURCE-FACTOR — unreachable tier (XF 13; ladder floor). Tier "the resident has a bed-hold reservation whose hold was declined and which records the day the resident came back". In the bed-hold charter return_date is written only by bedhold_returned (held -> returned); bedhold_hold_declined writes end_date/end_reason and `declined` has no outgoing transition, so a declined reservation never records a return date. Members: late_notice leave_kind tier 2 (dec_start/dec_back), new_room_span span_leave_rule tier 2 (sp_dec_*), resumed_recharge recharge_leave_rule tier 2 (dec_from/dec_back). Each ladder has two real tiers; each factor is struck, leaving late_notice, new_room_span and resumed_recharge with 3 factors and task 0 with no cross-difficulty factor.

F-08 SOURCE-FACTOR — leave days taken from a wider window than the days they are subtracted from (realism, XF 27). late_notice: leave days are those "inside the charge's span" but are subtracted from the late-notice days only (a leave on 10-25..10-27 against late days 10-01..10-18 cuts a refund owed for days the resident was present: 18 x 14 = 252.00 becomes 210.00). resumed_recharge: leave days counted from "the conversion date recorded on the agreement" but subtracted from re-charge days that start at the ABN delivery date (a leave on 10-10..10-11 before an ABN delivered 10-13 cuts two re-charged days the resident was present for). Members: late_notice leave_kind (all tiers), resumed_recharge recharge_leave_rule tier 1. Task worlds sit inside the windows (no task consequence).

F-09 SOURCE-FACTOR — cross-tier rate gap and unclipped sign. late_notice earlier_source tier 1 takes "the daily rate of the most recent of those [prior-rate notice-hold] charges" whatever their tier, and room_change credited_step_rule tier 1 "the charge's daily rate less the daily rate of the most recent of those charges" likewise; after a move between tiers the gap is between two tiers' rates (e.g. a Semi LTC span at 398 against a held Private LTC rate 421 gives -23 per day), and late_notice's result is not clipped (`RND(MX(0, days) * (billed - earlier))`), so the "credit" is negative. Members: late_notice earlier_source tier 1 + result; room_change credited_step_rule tier 1. Task 0's held charges share the charge's tier (no task consequence).

F-10 SOURCE-FACTOR — label / shape failures (XF 7). move_day_rule tiers 1 and 3 select 0 and 1 in the same formula (constant offset); span_start_rule tiers 2 and 3 are `DAYS(moved_on, chg_to) + 1` and `DAYS(moved_on, chg_to)` (constant offset); kept_days_rule tiers 2 and 3 are the same medicare_ledger.day_count reversal aggregate under two filters; credited_step_rule is labelled parameter but its tiers are three algorithms (rate difference, nothing, credit amount over span days). Members: those four factors. Bears on task 0 (move_day_rule, span_start_rule, credited_step_rule scored) and task 1 (kept_days_rule).

F-11 SOURCE-FACTOR — unreal tier (XF 27). resumed_recharge recharge_start_rule tier 2: "the Part A episode ended on an upheld expedited review with a decision date recorded, they run from the day after the decision date". The Medicare charter fixes an upheld episode's last covered date as "the later of the NOMNC's last covered date and the QIO decision date" (upheld_last_covered_basis). Where the decision date is the later one, tier 2 equals the base day-after-last-covered-date (the fall-through value, two tiers one value); where it is the earlier one, tier 2 re-charges days Medicare covered. Bears on task 1's ladder (task 1 sits on tier 1).

F-12 SOURCE-POLICY — 0.00 / non-positive rows (XF 26). private_ledger.amount "always positive"; every extended rule clips to "never below zero" (late_notice not even that, F-09) and says the entry "is entered" with no zero case: late_notice (earlier_source tier 2 "there being no earlier rate to restore" gives gap 0), room_change (isolation: "no day is moved" -> 0), new_room_span, conversion, resumed_recharge ("where it carries none … no day is re-charged" -> 0-day span), additional and resumption deposits (0 owed). Members: all seven policies. No task world yields 0 on its gold path.

F-13 SOURCE-POLICY — rule/compute disagreements (XF 9-13):
  (a) conversion credit_tier_rule tier 1 — rule: "where the agreement records a room change dated after the first day of the charge's span and carries no isolation placement"; ladder and compute add "the resident's latest room-change request names a date on or before that move" (`req_on and req_on <= moved_on`). A center-directed move inside the span with no request: rule -> charge's tier, compute -> agreement's tier.
  (b) conversion kept_days_rule tier 1 — rule: "a bed-hold reservation kept for a leave during the skilled stay"; compute: CFIELD on variant 'Medicare Skilled Stay Therapeutic Leave Bed Hold' only, first match (a Medicare Skilled Stay Hospital Leave Bed Hold, or a second therapeutic reservation, is missed).
  (c) new_room_span schedule_choice tier 1 — rule: "where a room-change request on file names a date on or before …"; compute: the latest request only.
  (d) resumed_recharge recharge_schedule_rule tier 1 — compute adds `conv_on >= '2026-07-01'`, absent from the rule.
  (e) room_change move_date fall-through with no request on file (isolation moves): "the requested date on the resident's latest room-change request" names a record that does not exist; compute `req_date` None -> DAYS(None, …) undefined; the baseline gives no definite number.
  (f) resumption_insurer_rule tier 2 — "that payment divided by the days of that charge less the days credited on it": zero/negative divisor when all days are credited, unstated; compute falls to 0.
  (g) conversion kept-days reversal sums (`XSUM … service_month=chg_month`) run across every Medicare episode of the resident though the rule reads "the resident's Part A episode".
  No task world is on these branches.

F-14 SOURCE-POLICY — tie and second-record rules unstated (XF 11, 12). "The most recently posted room-and-board charge" is LATEST by entry_date, and a split month posts two spans the same day (private_evt_room_board_billing): members late_notice chg_*, room_change chg_*, new_room_span chg_*, additional_deposit span_tier, conversion chg_id, resumed_recharge adv_id, resumption sp_id/r_sp_from/r_last_post. Latest booked bed-hold days by entry_date (payer_reserved and resident_private rows of one leave are booked together): late_notice lv_*, new_room_span sp_lv_*, resumed_recharge bh_*. "The episode whose coverage has ended and which is not yet closed" as CFIELD first match, while the Medicare charter keeps ended episodes open while a secondary share is followed up: conversion pa_start/pa_cov, resumed_recharge last_cov/qio_on/end_rsn/pa_start. Month-window conventions ("within the last three/six/twelve months") unstated: additional_deposit rp_12/lc_12/ins_3/ins_sum_3, resumption rp_12/ach_*/ins_3/disp_3. Task worlds hold no tie on these reads.

F-15 SOURCE-FACTOR / SOURCE-POLICY — deposit tier under an isolation placement (XF 27). additional_deposit deposit_tier_rule tier 2 "where the agreement carries an isolation placement, it is the agreement's own tier"; resumption_tier_rule tier 2 likewise. private_room_change writes variant_name = the room moved into, so for a center-directed move into a private room the deposit is figured at the private rate while the resident is billed at the isolation billing tier — against private_tier_placement "does not by itself change what the resident pays" (undeclared) and against what an operator would publish.

F-16 SOURCE-POLICY — tool bodies do not enforce their docstrings (coordinator requirement; XF 19). All seven tools document `amount` as "a positive amount to 2 decimal places, rounded half up to the cent" (two also `daily_rate` "to 2 decimal places"); bodies use Python `round(float(x), 2)` (round(2.675, 2) = 2.67, half-up 2.68), accept negative amounts (a negative credit raises the balance), and store date/month strings unvalidated. Members: credit_late_notice_days_45589810, credit_room_change_days_09a50cb9, post_new_room_span_526f1e53, pay_additional_deposit_f9f00bc8, credit_converted_days_12618703, post_resumed_recharge_e6f5843a, pay_resumption_deposit_9c511f79. Task gold amounts carry no sub-cent part (no task consequence).

Observations (no consequence demonstrated):
- O-1 Base private_tier_placement "Only an open, active agreement changes tier", while resumed_recharge tier 1 and the additional-deposit scope sentence presuppose a tier change dated inside a payer-converted period (task 1's seed: move 2026-10-05 during Part A). Producible only if recorded after the reversion with a back-dated move date.
- O-2 Deposit-days ladders: 45 days after one late charge in 12 months, 60 on certified funds, 15 for four ACH payments in six months regardless of open past-due months — aggressive but not shown unreal; no federal cap applies to private-pay deposits (42 CFR 483.15(a)(3) bars third-party guarantees, which these rules do not require).
- O-3 Compute bindings without compute_basis entries (listed above).
- O-4 The word "time" appears in pay_resumption_deposit's docstring ("for a time"); XF 23's substring rule targets imports and the gate is green.
- O-5 resumed_recharge tier 1 "was delivered after that day": "that day" may be the ABN's first non-covered day (compute) or the last covered date.
- O-6 Bed-hold charges are posted on the booking date though the bed-hold charter bills them "on the statement day of the following month".
- O-7 Sibling deposit scopes can both match one history (move while private, later conversion and resumption).

- timestamp correction (appended): the freeze clock value above was an estimate; this section was written between 2026-10-22T05:19:33Z (directory created) and 2026-10-22T05:23:28Z (first GT read). Nothing in the sections above derives from a revealed GT.

## post_reveal (written after both tasks' comparisons)
- Both tasks' GT write sequences, arguments, closures and factor-sensitivity figures equal the blind derivations figure for figure (0.md, 1.md source_gt_comparison). The REDs are therefore not derivation disagreements: they are charter defects (F-01..F-16) and, per task, second defensible answers the charter leaves open (task 0: F-01, F-02, F-03; task 1: F-06), factors struck or mislabelled (task 0: F-05, F-07, F-10; task 1: F-07, F-10, F-11) and a seed row missing that another charter would have produced (task 1: T1-S1).
- Per-task assignment of charter findings: F-01, F-02, F-03, F-05 -> task 0; F-06, F-11 -> task 1; F-07, F-10 -> both; F-04, F-08, F-09, F-12, F-13, F-14, F-15, F-16 -> charter only (no task world on the branch).

## closing_checklist
Not reached: Step 4 is written only when every task passes all four relationships; both tasks are RED. Files: 0.md, 1.md, _difficulty.md (one per task plus this file); no earlier revision exists. Gates were not re-run (auditor does not run gates; snapshot cited above).

VERDICT revision_1: task0=RED F-01,F-02,F-03,F-05,F-07,F-10 task1=RED F-06,T1-S1,F-07,F-10,F-11 charter=F-01,F-02,F-03,F-04,F-05,F-06,F-07,F-08,F-09,F-10,F-11,F-12,F-13,F-14,F-15,F-16

## revision_2

## charter_global_frozen (revision_2)
- written before any round-2 GT field was opened (task files' revision_2 frozen sections written first). Re-derived in full: private.extended.yaml ab98737d07b940569f45d8c35c2cd41e93f9cd0e1d9c323480dd04fe7407d828 and task_tools.py d432b7ac5c6638c2d647d59a77e40e75af4aaee376b6ce87c169e68609f888bc both changed since revision_1.
- entry conditions: the round-2 snapshot was run by the auditor as instructed (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 2`, 2026-10-22T07:37:40): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; traceability deferred. Views: task0 c5897ff8…7bc3 (unchanged), task1 f4c6648d…b218.
- method: rule text read in full; compute evaluated with the framework DSL (check_compute.build_env/eval_compute) on scratch copies in /tmp/erl0074_audit_r2 for T1 (task worlds), skip-edge runs and decoy probes; T2 argued per factor over the worlds the charters can produce.

### mechanical sweeps
Base copy verbatim; every compute_basis quote verbatim in its rule; every baseline.rule sentence in its rule; every compute binding has a basis entry; every superseded clause verbatim in its base policy and every replaced_by verbatim in its rule; prerequisite sources verbatim, gates exist (resumption gate now r_tier); no factor id inside a tool name; uuid8s unchanged and distinct; docstrings carry formats only, no sequencing words; every write tool creates/updates in its own body; imports erlbench and decimal only; helpers are a class with static methods.

### status of revision_1 findings
- F-01 CLOSED (late-notice overwrite of private_rate_schedule declared and scoped).
- F-02 CLOSED in the rule (new_room_span overwrite of "until then the earlier scheduled rate applies" declared; late-notice rule excludes the requested-move span) — but the compute's exclusion is broken: N-02.
- F-03 CLOSED ("or on or after that date").
- F-04 CLOSED (move date before the span -> first day, days counted inclusive).
- F-05 CLOSED for the day-after fall-throughs; the same class persists in the requested-date standard method: N-03.
- F-06 CLOSED (room-change credit not posted on an agreement recording a conversion) — the closing test is over-broad: N-01.
- F-07 CLOSED (dead tier removed); its replacement tier is the tier above written twice: N-04.
- F-08 CLOSED for new_room_span and resumed_recharge (leave clipped to the span start / first re-charged day); late_notice tier 3 window still mismatched: N-11.
- F-09 CLOSED (same-tier notice-hold charges; result clipped at zero).
- F-10 CLOSED for move_day_rule (removed), span_start_rule (no constant-offset pair), credited_step_rule (replaced by netting_rule, method); kept_days_rule: N-04.
- F-11 CLOSED (tier 2 = expedited review pending, nothing re-charged — the Medicare charter's own rule).
- F-12 CLOSED (every rule: no entry / nothing paid when zero; tools refuse non-positive amounts).
- F-13 (a)-(g) CLOSED (rule and compute agree on each named case).
- F-14 CLOSED for charge/booking ties, episode choice and month windows (rule wording matches the DSL's LATEST order and MONTHS window); residual second-record reads: N-10.
- F-15 CLOSED (isolation -> isolation billing tier in both deposits).
- F-16 CLOSED (Decimal ROUND_HALF_UP to the cent, non-positive amounts and malformed dates/months refused).
- T1-S1 CLOSED (reservation, notice and election for the 2026-10-03 leave; persona aligned).

### policy_conflict_scan (revision_2)
- room_change vs conversion: no longer overlap (exclusion on a recorded conversion). Additional vs resumption deposit: split by the same record test, jointly complete. late_notice vs new_room_span: separated in the rule (N-02 in compute). Scopes of tasks 0 and 1 unchanged, disjoint and complete. Toolset holds no other product's write.

### factor_ladders (revision_2)
| policy | factors (label) | struck / defect |
| --- | --- | --- |
| late_notice | notice_anchor (m), leave_kind (m, bedhold), billed_tier (p), earlier_source (p) | leave_kind struck (N-04); 3 survive |
| room_change | move_date_source (m), come_off_tier_rule (p), come_off_schedule_rule (p), netting_rule (m) | move_date_source baseline N-03; netting_rule reads move_date_source's output (N-08) |
| new_room_span | span_start_rule (m), span_leave_rule (m, bedhold), priced_tier_rule (p), schedule_choice (p) | span_leave_rule struck (N-04); span_start_rule baseline N-03; 3 survive |
| additional_deposit | deposit_days_record (p), deposit_tier_rule (p), deposit_schedule_rule (p), insurer_benefit_rule (m), deposit_held_rule (m), secured_holds_rule (m, bedhold) | insurer_benefit_rule fails T2 (N-09); held/holds unreal (N-07) |
| conversion | first_converted_day_rule (m, medicare), hospital_lead_in_rule (m, medicare), kept_days_rule (m), credit_tier_rule (p), credit_schedule_rule (p), netting_choice_rule (m) | kept_days_rule struck (N-04); netting reads lead-in/first-converted outputs (N-08); first-match reads (N-10); 5 survive |
| resumed_recharge | recharge_start_rule (m, medicare), recharge_leave_rule (m, bedhold), recharge_tier_rule (p, medicare), recharge_schedule_rule (p) | recharge_leave_rule struck (N-04); 3 survive |
| resumption_deposit | resumption_days_rule (p), resumption_tier_rule (p), resumption_schedule_rule (p), resumption_insurer_rule (m), resumption_held_rule (m), resumption_holds_rule (m, bedhold) | resumption_insurer_rule struck (N-04); held/holds unreal (N-07); 5 survive |
- T2 (some producible world moves the result with every other factor at baseline): passes for every factor except additional_deposit.insurer_benefit_rule (N-09). The late-notice factors pass through a world whose span begins before 2026-07-01 and was billed at the new rate (the base rule's own late-notice case); netting through a late credit starting before the first converted day; resumption insurer through a deposit disposed of after a conversion longer than the disposition days.
- Labels honest; tiers distinct in outcome except N-04; every tier stated in the rule and implemented in compute (except the N-02 exclusion and N-10(a)).

### findings (revision_2) — all RED (any XF member is RED); members listed in full
N-01 SOURCE-POLICY/SOURCE-FACTOR (XF 13, 27; from F-06's fix). room_change rule: "on an agreement that records one [a conversion], no room-change credit is posted"; its overwrite: "the payer-conversion credit taking the moved days off at the tier the charge was posted for". converted_to persists after a reversion (schema: "payer source that took over the stay at the last conversion"; task 1's agreement is active with converted_to medicare_part_a). On any such agreement a later move while billed privately is never credited, so the new-room span (which waits on that credit) is never posted, and no conversion credit applies to an advance no other payer covered: the month stays billed at the old tier and the overwrite's framing claim is false there. Members: room_change exclusion (rule + `result = 0 if conv_rec`), its overwrite's replaced_by, new_room_span (blocked through its prerequisite). Charter only.
N-02 SOURCE-POLICY (check 2). late_notice rule: a span "whose first day is the move date recorded on the agreement and whose tier is the agreement's own … is owed no late-notice credit". Compute: `req_on = LATEST('private_ledger','requested_date', date_field='created_at', request_type='room_change_request')` reads a table without those fields (always None), and `excl` adds a request condition the rule does not state; the exclusion never fires. Task 0 after its step 3: rule -> no credit; compute -> 150.00. Member: late_notice req_on/excl.
N-03 SOURCE-POLICY/SOURCE-FACTOR (XF 16, 18; F-05 class; the move_date_source part was present in revision_1 and not reported then). Standard method "the move date is the requested date on the resident's latest room-change request, or the move date recorded on the agreement where no request is on file" (room_change) and "the new room's span days run from the requested date … or from the move date recorded" (new_room_span) vs base private_tier_placement "A move the resident requests reprices from the move date"; undeclared; the fall-throughs date repricing from a day that is not the move date, and the factors' demonstrated weight is against that straw baseline. Members: room_change move_date_source fall-through/baseline; new_room_span span_start_rule fall-through/baseline. Bears on task 0.
N-04 SOURCE-FACTOR (one tier written as two). On the other tier's whole domain the first tier's method returns that tier's value: leave_kind T1 "those booked days" vs T2 "the booked days less the reversed days" (reversed = 0 on T1); span_leave_rule T1/T2 (same); recharge_leave_rule T1/T2 (same); kept_days_rule T1 "leave-of-absence days … less those booked days" vs T3 "the leave-of-absence days" (no booked days on T3); resumption_insurer_rule T1 "payment / days of that charge" vs T2 "payment / (days less days credited)" (credited = 0 on T1; present in revision_1, not reported then). Each ladder has two real tiers; all five struck: late_notice, new_room_span and resumed_recharge fall to 3 factors (< 4).
N-05 (task 1 seed; see 1.md). N-06 (task 1 seed; see 1.md).
N-07 SOURCE-FACTOR (realism, XF 27; resumption_held_rule present in revision_1, not reported then). Both deposits subtract from the deposit credit the agreement's whole open balance (not-yet-due advance balances and spans posted the same day included) and open or even unbooked bed-hold charges, so the top-up collects current receivables a second time: after those receivables are paid in the ordinary course the deposit exceeds the deposit days the same rule sets (task 0: 64.5 vs 45 days; task 1: 73.3 vs 45). Members: additional_deposit deposit_held_rule T1, secured_holds_rule T1-T2; resumption_held_rule T1, resumption_holds_rule T1-T2.
N-08 SOURCE-FACTOR (XF 1, transitive). room_change netting_rule tiers count "that credit's days on or after the move date" (move_date, decided by move_date_source); conversion netting_choice_rule tiers count days "on or after the first credited day" (first_cr, decided by hospital_lead_in_rule and first_converted_day_rule). Members: those two factors. Task 0: move_date_source's T1 figure 11360.00 carries a netting shift of 10 -> 13 days; task 1: hospital_lead_in_rule's 13080.00 carries 1 -> 0 netted days.
N-09 SOURCE-FACTOR (XF 6, T2). additional_deposit insurer_benefit_rule: with every other factor at baseline the result is MX(0, 30 x (admission-tier rate at the admission schedule - benefit) - deposit balance); the additional deposit applies only to agreements with no recorded conversion, which never dispose of their deposit, so the deposit balance is at least 30 x that rate and the benefit can only lower a figure already 0. No producible world moves it. Bears on task 0.
N-10 SOURCE-POLICY/SOURCE-FACTOR (XF 12, decoy / second record). (a) conversion lead-in: rule "the resident's private-pay hospital bed hold that began on the admission date was declined"; compute `hd_dec = CFIELD(... status='declined')` compares only the first declined hospital hold on file — probe (task 1 world plus an older declined hospital hold listed first): rule 13501.00, compute 13080.00. (b) conversion kept days: "a returned bed-hold reservation … the first such one on file" — an earlier episode's returned skilled-stay hold listed first displaces this month's (probe: task 1 world with the 10-03 hold elected and a 2025-12 returned hold listed first: kept 1, credit 13065.00; this month's hold alone: kept 0, 13501.00) — the selection keeps an LOA night held under the bed hold on the agreement too. (c) insurer payments: "the insurer's most recent payment" (additional ins_amt/ins_chg; resumption ins_amt/ins_chg) with no rule for two payment rows of one date, which base payment posting (one row per charge paid) produces for any remittance spanning two charges.
N-11 SOURCE-POLICY (F-08 residual). late_notice leave days count "booked days that fall before the day the agreement's rate notice had run the rate change notice days", while in tier 3 (notice ran before the schedule date) the late-notice days run to the schedule's effective date; resident-private bed-hold days between the two stay inside the credit although the declared overwrite says the credit "leaves out the days the resident spent away on a resident-private bed hold". Member: late_notice leave_kind tier windows x notice_anchor tier 3.

Observations (revision_2): O-8 lead-in days are entered under payer_conversion_credit while the tool's enum describes that reason as days another payer covers; O-9 the resumption deposit covers every later deposit on an agreement that ever recorded a conversion (naming only); O-10 the leave clipping in new_room_span / resumed_recharge combines two factor outputs inside the assembly sentence (stated once, order fixed); O-11 task 1's insurer share is past grace every month, yet only one late charge was assessed (base fixes no assessment day); O-12 resumed_recharge tier 2 needs a reversion recorded while a review is pending to be reached.

## post_reveal (revision_2)
- Both tasks' GT writes, closures and factor-sensitivity figures equal the blind derivations figure for figure (0.md, 1.md revision_2 comparisons). REDs are charter/seed defects, not derivation disagreements. Task assignment: task 0 — N-02, N-03, N-04, N-07, N-08, N-09; task 1 — N-04, N-05, N-06, N-07, N-08; charter only — N-01, N-10, N-11. task 0's design_rationale T2 world for insurer_benefit_rule (a deposit partly applied at an earlier disposition) is not producible on an agreement the additional deposit applies to.

## closing_checklist (revision_2)
Not reached: both tasks RED. Files 0.md, 1.md, _difficulty.md carry revision_1 untouched and revision_2 appended. Gates: round-2 snapshot cited above (7/7 OK).

VERDICT revision_2: task0=RED N-02,N-03,N-04,N-07,N-08,N-09 task1=RED N-04,N-05,N-06,N-07,N-08 charter=N-01,N-02,N-03,N-04,N-05,N-06,N-07,N-08,N-09,N-10,N-11

## revision_3

## charter_global_frozen (revision_3)
- written before any round-3 GT field was opened (task files' revision_3 frozen sections first). Re-derived in full: private.extended.yaml 0216091314cfd4c74ad95788e2d24d437a4f6bdfc823eb6c3b4129571b5dfba7 changed; task_tools.py d432b7ac5c6638c2d647d59a77e40e75af4aaee376b6ce87c169e68609f888bc unchanged (tool-contract sections of revision_2 carried forward on that hash).
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 3`, 2026-10-22T10:29:13): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 533fa344…4de6, task1 a4829fe0…0c23.
- contamination_disclosure: earlier rounds' GT read after their freezes; worklog.md "REWORK round 3" section read now (permitted by the coordinator; no gold figure).
- method: rule text read in full; DSL evaluation of every compute on scratch copies (/tmp/erl0074_audit_r2/r3.py, p3.py) for T1, skip-edge runs and decoy probes; T2 argued per factor.

### mechanical sweeps (revision_3)
Base verbatim; all compute_basis quotes verbatim in their rules; every compute binding quoted; baseline sentences in rules; superseded clauses verbatim in base and replaced_by verbatim in rules (room_change and new_room_span carry one identical sibling sentence retiring "A move the resident requests reprices from the move date", naming both cases); prerequisite sources verbatim, gates exist; no factor id in a tool name; every policy 4-6 factors.

### status of revision_2 findings
- N-01 CLOSED (conversion scope only for a move dated before the recorded conversion date; later moves are ordinary).
- N-02 CLOSED (exclusion reads private_requests; rule and compute agree; DSL: no late-notice credit on task 0's new span after its step 3).
- N-03 CLOSED as stated (standard = recorded move date; the requested-date tier declared by overwrite) — the declared tier rests on an unrecorded fact: P-01.
- N-04 CLOSED (leave ladders: booked days / private hold in force / none; kept days removed; resumption insurer ladder = additional deposit's) — the booked-days tier ignores reversals: P-03.
- N-05, N-06 CLOSED (task 1 seed; see 1.md).
- N-07 CLOSED (held credit and secured bed-hold factors removed; deposit at face).
- N-08 CLOSED (netting anchors are plain records) — the anchors can open a wider window than the credited days: P-04.
- N-09 CLOSED (with any recurring ancillary service the all-baseline figure is positive, so every deposit factor, the insurer included, moves alone).
- N-10 CLOSED ((a) exact hospital-hold read; (b) removed with kept days; (c) tie rule stated for insurer payments).
- N-11 CLOSED (leave window = the day the new rate took effect for the agreement, the later of schedule date and notice + notice days).

### policy_conflict_scan (revision_3)
room_change vs conversion: the conversion scope sentence hands the moved days from the payer-conversion credit's first day to that credit, but makes the room-change credit depend on that credit's presence (P-02). Additional vs resumption deposit: one shared scope sentence, disjoint by the recorded-conversion test. Task scopes unchanged, disjoint, complete. No other product's write in the toolset; ancillary charges bill in arrears on the 4th, none owed mid-conversation.

### factor_ladders (revision_3)
late_notice: notice_anchor (m), leave_kind (m, bedhold), billed_tier (p), earlier_source (p). room_change: move_date_source (m), come_off_tier_rule (p), come_off_schedule_rule (p), netting_rule (m). new_room_span: span_start_rule (m), span_leave_rule (m, bedhold), priced_tier_rule (p), schedule_choice (p). additional_deposit: deposit_days_record (p), deposit_tier_rule (p), deposit_schedule_rule (p), insurer_benefit_rule (m), recurring_allowance_rule (m, ancillary), item_allowance_rule (m, ancillary). conversion: first_converted_day_rule (m, medicare), hospital_lead_in_rule (m, medicare), credit_tier_rule (p), credit_schedule_rule (p), netted_days_rule (m), netted_step_rule (m). resumed_recharge: recharge_start_rule (m, medicare), recharge_leave_rule (m, bedhold), recharge_tier_rule (p, medicare), recharge_schedule_rule (p). resumption: resumption_days_rule (p), resumption_tier_rule (p), resumption_schedule_rule (p), resumption_insurer_rule (m), r_recurring_allowance_rule (m, ancillary), r_item_allowance_rule (m, ancillary).
- Every ladder 3 tiers, stated in the rule and implemented; no tier reads another factor's output (netting anchors and leave windows read recorded dates); labels honest; shape test passes pairwise (new pairs: leave booked count vs days held so far; recurring 3-month total/3 vs latest service month vs price schedule; item total/3 vs latest item; netted days late-notice vs billing-error vs all credits; netted step rate gap vs credits/credit days vs credits/span days). No tier repeats another tier's method on its domain.
- T1 on both task worlds: every factor moves (0.md, 1.md). T2: holds for every factor (late-notice factors through a span billed at the new rate before 2026-07-01; deposit factors through any resident with a recurring ancillary service; conversion netting factors through a charge with a late-notice credit).

### findings (revision_3) — all RED; members listed in full
P-01 SOURCE-POLICY/SOURCE-FACTOR (XF 13, 27). The declared requested-date tier asserts a fact no record holds: "where the resident's latest room-change request names a date on or before the move date recorded on the agreement and inside the span …, the new room was set aside for the resident from that requested date". The records hold a request date and a move date and nothing about the room's availability; in a producible world where the request date precedes the move because the room was not ready (this scenario's own round-1 task-0 story), the rule moves the old room's credit and the premium new room's charge to the requested date — billing the new room for nights it could not be occupied. Members: room_change move_date_source tier 1 and the shared overwrite sentence (room_change, new_room_span); new_room_span span days (from the credit's first day) and schedule_choice tier 1; late_notice exclusion's request-date branch; the room_change and new_room_span leave/netting windows that start at the request date.
P-02 SOURCE-POLICY (check 6: undeclared cross-problem order). room_change rule: "… the room-change credit takes off only the moved days before the first day the payer-conversion credit on the charge covers, and none while the charge carries no payer-conversion credit". The room-change credit's value waits on the conversion credit, but its `prerequisite` declares only the late-notice edge. Two orders on a producible world (move recorded 2026-10-03 while private, Part A from 10-05, private billing resumed 10-11, October advance at the old tier): room-change first -> nothing posted (zero, no entry) and, absent a revisit, the old room keeps 10-03..10-04; conversion credit first -> room-change credit 2 days at the come-off rate. Member: room_change in-conversion clause.
P-03 SOURCE-POLICY (XF 12, reversed record). Leave tier 1 reads the booking's day_count and ignores bedhold_day_reversed rows against it (returned_earlier, billing_error …), so days the resident was present count as days away. Probe (task 0 world, one booked day reversed): late-notice credit stays 210.00 (should be (18-2) x 14 = 224.00), new-room span stays 11336.00 (should be 27 x 436 = 11772.00). Members: late_notice leave_kind tier 1 (lv_booked), new_room_span span_leave_rule tier 1 (lv_booked), resumed_recharge recharge_leave_rule tier 1 (bh_priv).
P-04 SOURCE-POLICY (XF 12, window). Netted days are counted from a wider anchor than the credited days: room_change nets late-notice days "on or after the earlier of the move date recorded on the agreement and the date the resident's latest room-change request names" while the moved days start at the move date — a stale latest request (dated before the span; move recorded 10-06) gives move date 10-06 but nets from the request date: probe 10138.00 against 10208.00 (15 netted days instead of the 10 inside the move). conversion nets late-notice days from "the later of the qualifying hospital admission date … and the first day of the charge's span" while the credited days start at the coverage start where no lead-in tier applies (admission inside the span with neither a declined private hold nor resident-private booked days, e.g. a payer-reserved hold), netting days the credit never gave back. Members: room_change net_from; conversion nd_anchor.
P-05 SOURCE-FACTOR (dishonest standard). conversion standard method: "the netted days are all the days of the credits already posted against the charge" and "the netted per-day amount is the total of the credits already posted against the charge divided by the days of the charge's span" — together they net cr_days x cr_amt / span_days, a fraction of the earlier credits no business would net (a 15.00 one-day credit on a 31-day span nets 0.48). netted_step_rule's demonstrated weight (task 1: 13077.10) is against that figure. Member: conversion netted_step_rule fall-through/baseline (with netted_days_rule's standard).
P-06 SOURCE-FACTOR (XF 27; method misstates its own purpose). "The recurring-service allowance … secure[s] one month of the ancillary charges"; tier 1 "where at least three recurring charges were posted … within the last three months, it is their total divided by three" counts charges, not months: three services started in one month (cable 42.00, telephone 29.00, oxygen concentrator 185.00, one statement) give 85.33 for a 256.00 month; two services over two months (four charges) give 4/3 of a month. Members: additional_deposit recurring_allowance_rule tier 1; resumption r_recurring_allowance_rule tier 1.
P-07 SOURCE-POLICY (check 7; stale proof text). Prerequisite `effect` of additional_deposit and of resumption_deposit: "… and the balance owed set against the deposit includes the span" — neither compute reads the balance owed since round 3; the effect claims a change the write does not make. Members: additional_deposit.prerequisite[0].effect; resumption_deposit.prerequisite[0].effect.

Observations (revision_3): O-13 the two residents' ancillary histories are identical row for row (dates, amounts, request timestamps) though they live at different centers; O-14 the room-change, new-room-span and conversion computes return non-zero on worlds where their subject no longer holds (e.g. task 0 after its chain: room-change compute 12644.00 on the new span) — the rules' subject sentences exclude those worlds, the computes do not test them; O-15 recurring tier 1 on both task worlds averages in July's prorated cable (21.68), giving 64.23 against a 71.00 month.

## post_reveal (revision_3)
- Both tasks' GT writes, closures and factor figures equal the blind derivations. P-07's member list extended by the reveal: tasks/0.json prerequisite_closure edge additional_deposit <- new_room_span `flips_to_true_by` ("from 2026-10-06" — gold's span starts 2026-10-03 — and "the balance owed includes the span"). Task assignment: task 0 — P-07; task 1 — P-05, P-07; charter — P-01..P-07.

## closing_checklist (revision_3)
Not reached: both tasks RED. Revisions 1-2 untouched; revision_3 appended in 0.md, 1.md, _difficulty.md. Gates: round-3 snapshot 7/7 OK.

VERDICT revision_3: task0=RED P-07 task1=RED P-05,P-07 charter=P-01,P-02,P-03,P-04,P-05,P-06,P-07

## revision_4

## charter_global_frozen (revision_4)
- written before any round-4 GT field was opened (task files' revision_4 frozen sections first). Re-derived in full: private.extended.yaml 1f495b5ea1d7a53d0cade363fd9c54756fae68c908e4eec74ea9ce11d413c262 changed; task_tools.py d432b7ac5c6638c2d647d59a77e40e75af4aaee376b6ce87c169e68609f888bc unchanged (tool-contract conclusions of revision_2 carried forward on that hash).
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 4`, 2026-10-22T15:19:15): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 300a85d6…7f76.
- contamination_disclosure: earlier rounds' GT; worklog.md "REWORK round 4" read now with permission.
- method: rule text read in full; DSL evaluation (/tmp/erl0074_audit_r2/r4.py) for T1, skip-edge runs and decoys; T2 argued per factor; mechanical sweeps including a duplicate-sentence scan.

### mechanical sweeps (revision_4)
Base verbatim; compute_basis quotes, baseline sentences, superseded clauses, replaced_by texts and prerequisite sources all verbatim; every binding quoted; gates exist (room-change gate renamed ln_net); no factor id in a tool name; 4-6 factors per policy. Duplicate sentences: three in private_ext_conversion_credit's rule (Q-02).

### status of revision_3 findings
- P-01 CLOSED (requested-date tier now: a requested move into a higher-priced tier made before the date asked for reprices from that date — record test only; persona aligned).
- P-02 CLOSED (conversion scope is a record test on the recorded conversion date and status; the room-change credit no longer depends on the conversion credit's presence) — its new outcome depends on when the move is processed: Q-03.
- P-03 CLOSED (booked days less reversed days in all four leave/lead-in reads; DSL probe now subtracts).
- P-04 CLOSED as to window equality on the task worlds — achieved by restating the shared selection outside its factor: Q-04.
- P-05 CLOSED (standard netting anchor = standard credited window; standard per-day = the charge's daily rate).
- P-06 CLOSED for start-ups within the window — cancelled services now pass tier 1: Q-01.
- P-07 CLOSED for both deposit edges — the room-change edge's effect is stale: Q-05.

### factor_ladders (revision_4)
Unchanged factor lists except conversion (netted_days_rule now decides the netting anchor with four tiers). Every ladder stated in its rule and implemented; T1 moves every factor on both task worlds (task files); T2 holds for every factor (late-notice factors through a span billed at the new rate before 2026-07-01; deposits through any resident with a recurring ancillary service; conversion netting through a late-notice credit straddling the credited window). Shape test passes pairwise.

### findings (revision_4) — all RED; members listed in full
Q-01 SOURCE-POLICY/SOURCE-FACTOR (XF 13, 27). Recurring-service allowance tier 1: "where recurring charges were posted … within the last three months and every recurring service among them was also charged before those three months, the services having run through the whole period, it is the total of those charges divided by three". The record test passes for a service cancelled inside the window (charged through the month of cancellation, base ancillary_evt_recurring), so the stated premise is false and the allowance — said to "secure one month of the ancillary charges the center bills … in arrears" — secures a service that no longer runs; a reader who takes the premise as part of the condition finds neither tier 1 nor tier 2 and falls to the standard price-schedule month. Task 0 (cable cancelled 2026-08-18): 57.00 as tested vs 71.00 by the premise reading (deposit 1429.00 vs 1443.00); one forward month of services is 29.00. Members: additional_deposit recurring_allowance_rule tier 1; resumption_deposit r_recurring_allowance_rule tier 1.
Q-02 SOURCE-POLICY (rule self-contradiction). private_ext_conversion_credit's rule states "The netted days are the days of the late-notice credit on the charge, running consecutively from its first credited day, that fall on or after the netting anchor; the netted amount of the other credits is, for each room-change or billing-error credit on the charge, … times its amount divided by its days" and also, unprefixed and twice, "The netted days are the days of the credits already posted against the charge, each credit's days running consecutively from its first credited day, that fall on or after the netting anchor." On an advance carrying a late-notice and a billing-error (or room-change) credit, the second definition puts the other credits' days into the netted days (netted at the netted per-day amount) on top of their own netted amount — a second, double-netting reading. The rule also repeats "Under this policy the Part A coverage episode read …" and "On an agreement still billed to the other payer source that records a move …". Member: conversion rule (netted-days definitions).
Q-03 SOURCE-POLICY/SOURCE-FACTOR (XF 27; from P-02's fix). room_change: on an agreement whose recorded conversion date falls after the move date, "the room-change credit takes off only the moved days before that conversion date while the agreement is still billed to the other payer source, and none once the agreement is active again, the advance's days before the other payer source took over then staying at the tier the advance was posted for"; new_room_span: none "on an agreement … that is active again"; resumed_recharge tier rule restates it. The charge for the days between a move and the other payer's start thus depends on whether the office processes the move before or after the reversion: world — move to a semi-private room 2026-10-03 while private, Part A from 10-05 to 10-10, private billing resumed 10-11, October advance at the private tier: processed while converted, 10-03..10-04 come off the private charge and a new-room span bills them at the semi-private rate; processed after the reversion, both stay at the private rate. Same facts, two bills; a resident who moved to cut costs pays the dearer room for nights in the cheaper one. Members: room_change conversion-scope clause (days_moved / conv_back), new_room_span conv_back exclusion, conversion lead-in trim (trim_on/g_trim, "still billed" condition), resumed_recharge tier tier 1 framing.
Q-04 SOURCE-FACTOR (XF 1-2: a shared selection restated as a copy). The first moved day (room_change) and the first credited day (conversion) are decided by factors (move_date_source; first_converted_day_rule + hospital_lead_in_rule) and decided a second time from the same records under another name (room_change `net_from`, a plain binding; conversion `nd_anchor`, the netted_days_rule factor with its own g_* re-reads). Substituting either factor's baseline leaves the copy unchanged, so each single-factor figure mixes two windows: task 0 move_date_source 10236.00 (days from 10-06, netting from 10-08); task 1 netted_days_rule 13080.00 (credit from 10-02, netting anchored at 10-11, nothing netted). Members: room_change move_date_source / net_from; conversion first_converted_day_rule, hospital_lead_in_rule / netted_days_rule (nd_anchor, g_* bindings).
Q-05 SOURCE-POLICY (check 7; stale proof text). room_change prerequisite `effect`: "its days on or after the earlier of the move date recorded on the agreement and the date the resident's latest room-change request names are netted at its amount divided by its days" — the rule now nets from the first moved day (the requested date when the move reprices from it, which is the later of the two) and nets billing-error credits too. Member: room_change.prerequisite[0].effect (task-closure members added at reveal, if any).

## post_reveal (revision_4)
- Both tasks' GT equals the blind derivations figure for figure; task closures carry no stale text (Q-05 stays a charter member only). Task assignment: task 0 — Q-01, Q-04; task 1 — Q-04; charter — Q-01..Q-05.

## closing_checklist (revision_4)
Not reached: both tasks RED. Revisions 1-3 untouched; revision_4 appended. Gates: round-4 snapshot 7/7 OK.

VERDICT revision_4: task0=RED Q-01,Q-04 task1=RED Q-04 charter=Q-01,Q-02,Q-03,Q-04,Q-05

## revision_5

## charter_global_frozen (revision_5)
- written before any round-5 GT field was opened. private.extended.yaml 751f009f78f68334f21729c9478a4756431f785a1e292765e7b7a381ea7f0bbb changed (re-derived in full); task_tools.py d432b7ac5c6638c2d647d59a77e40e75af4aaee376b6ce87c169e68609f888bc unchanged (tool-contract conclusions carried forward).
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 5`, 2026-10-22T17:35:29): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 46c3f795…bca1e.
- contamination_disclosure: earlier rounds' GT; worklog "REWORK round 5" read with permission. Coordinator rounding ruling applied (half up = RND(x + 1e-9, 2); residue not RED).

### mechanical sweeps (revision_5)
Base verbatim; all quotes verbatim; every binding quoted; overwrites verbatim; prerequisites verbatim with existing gates; no factor id in a tool name; no duplicate sentence in any rule; 4-6 factors per policy; every half-up result computed as RND(x + 1e-9, 2).

### status of revision_4 findings
- Q-01 CLOSED (tier 1 also needs every service charged in the latest service month; a stopped service falls to tier 2, the latest month).
- Q-02 CLOSED (conversion rule rebuilt; one definition of netted days; no duplicates).
- Q-03 CLOSED (the conversion-month scope is decided by the recorded conversion date against the move date and the advance's span, the same whatever the status; a tier change recorded while payer_converted is not producible under base "Only an open, active agreement changes tier", so a move inside the covered period is recorded on reversion and falls in scope either way).
- Q-04 CLOSED (no copies: netting windows are stated once, generically, in the assembly — room-change netted days from the move date, conversion netted days from the first credited day; the netting factors select only which credits and the per-day amount; single-factor figures now move both windows together).
- Q-05 CLOSED (room-change prerequisite effect restated).

### factor_ladders (revision_5)
Changes: conversion — held_hospital_days_rule (m, bedhold) and unheld_hospital_days_rule (m, bedhold) replace the lead-in and netting-anchor factors; netted_step_rule kept. Every ladder stated and implemented; shape test passes; T1 moves every factor on both worlds; T2 holds for every factor. Decoys on new reads: the stay's bed hold is read exactly (private-pay hospital reservation whose leave began on the qualifying admission date); booked days net of reversals; the latest-service-month test counts each service in that month.

### findings (revision_5) — all RED; members listed in full
R-01 SOURCE-FACTOR (one quantity split into two complementary factors; ladder not weighed for the quantity). The conversion credit's credited days add "the held hospital days and the unheld hospital days". The bed-hold charter opens one reservation per leave, so the qualifying stay's hospital window is always either declined (unheld = the window), held from the departure (held = the window) or held from a late election (unheld = days before it, held = the rest): in every producible world the two add up to the window, and both are given back at the same conversion credit rate. How the bed was kept therefore never changes the credit — it decides only which of two summands carries the days. The business quantity is the hospital window (the days the resident was out of the census or charged under the bed hold); the two ladders divide it on a condition the conversion credit does not weigh. Task 1: held 2 + unheld 1 = 3 = the window 2026-10-02..10-04; declined or on-time it would still be 3. Members: conversion held_hospital_days_rule, unheld_hospital_days_rule.
R-02 SOURCE-POLICY (XF 13; stale framing). resumed_recharge tier rule: "… the re-charge tier is the agreement's own tier, the advance's days before the other payer source took over having stayed at the tier the advance was posted for" — the conversion rule now "takes off the cheaper-room difference for the moved days before that payer took over" (room_change overwrite says the same), so those days did not stay at the advance's tier when the move was to a cheaper room. Two rules give two accounts of the same days. Member: resumed_recharge tier-rule framing clause.
Observation O-16: task 0 posts its October bed-hold charge at booking (8b7280d7…, 2026-10-18) while task 1's October bookings carry no charge row (the reworker removed one as premature); the bed-hold charter bills on the following month's statement day and does not fix the posting day, so both are producible; no scored read uses either.

## post_reveal (revision_5)
- Both tasks' GT equals the blind derivations figure for figure. Task assignment: task 0 — none; task 1 — R-01; charter — R-01, R-02.

## closing_checklist (revision_5)
Not reached: task 1 RED and charter not clean. Revisions 1-4 untouched; revision_5 appended. Gates: round-5 snapshot 7/7 OK.

VERDICT revision_5: task0=PASS task1=RED R-01 charter=R-01,R-02

## revision_6

## charter_global_frozen (revision_6)
- written before any round-6 GT field was opened. private.extended.yaml 0131a11c1c4fe2209a99747ae6d64f2cf44cca2bed36fa8fc091071824e73df6 (changed: conversion-credit and re-charge rules re-derived in full; the other five policies' rules textually equal to round 5, their computes re-run); task_tools.py d432b7ac…88bc unchanged.
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 6`, 2026-10-22T17:46:50): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 c0329260…31e9.
- contamination_disclosure: earlier rounds' GT; worklog "REWORK round 6" read with permission. Rounding ruling applied.

### mechanical sweeps (revision_6)
All quotes, baselines, overwrites and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy; half-up results as RND(x + 1e-9, 2). The phrase "stayed at the tier" no longer appears anywhere in the charter.

### status of revision_5 findings
- R-01 CLOSED (one hospital_days_rule decides the first hospital day — departure on the stay's bed hold / qualifying inpatient admission / none; the sixth factor moved_day_rate_rule prices the moved days, stated once in the assembly).
- R-02 CLOSED (re-charge tier framing now says the payer-conversion credit gave the advance back; consistent with the conversion and room-change rules).

### factor_ladders (revision_6)
conversion: first_converted_day_rule (m, medicare), hospital_days_rule (m, bedhold), moved_day_rate_rule (p), credit_tier_rule (p), credit_schedule_rule (p), netted_step_rule (m). Every ladder stated and implemented; the moved days and netted days are generic assembly sentences reading the first credited day; shape test passes; T1/T2 hold. Decoys on the new reads: the stay's bed hold keyed on its return date (finding S-01); the moved-day rate compares current-schedule rates of the posted and agreement tiers (dearer move -> none, probe consistent with the rule).

### findings (revision_6) — RED; members listed in full
S-01 SOURCE-POLICY/SOURCE-FACTOR (XF 12, absent/declined record; realism). conversion rule: "the stay's bed hold is the resident's private-pay hospital bed-hold reservation whose return date is that episode's Part A coverage start date"; hospital_days_rule tier 2 applies "where no such bed hold is on file", starting the hospital days at the qualifying inpatient admission. A declined (or released / expired) hospital hold never records a return date in the bed-hold charter, so for a declined hold the departure the reservation does record is ignored and the days from departure to the inpatient admission (observation nights, away at midnight, bed not held — not chargeable under the base midnight census) stay billed privately. Probe on a task-1 copy (departure 10-01 into observation, inpatient admission 10-02, coverage from 10-05; move moved out of the span): hold returned on 10-05 -> hospital days from 10-01, 4 days, credit 13471.00; same stay with the hold declined -> hospital days from 10-02, 3 days, credit 13088.00 — the 10-01 night away is charged though the bed was not held. Members: conversion "stay's bed hold" definition (hs_dep keyed on return_date) and hospital_days_rule tiers 1-2.

## post_reveal (revision_6)
- Both tasks' GT equals the blind derivations figure for figure. Task assignment: task 0 — none; task 1 — none; charter — S-01.

## closing_checklist (revision_6)
Not reached: the charter carries S-01. Revisions 1-5 untouched; revision_6 appended. Gates: round-6 snapshot 7/7 OK.

VERDICT revision_6: task0=PASS task1=PASS charter=S-01

## revision_7

## charter_global_frozen (revision_7)
- written before any round-7 GT field was opened. private.extended.yaml 7eb9cbe525e89e40c0931b4d0abdaa470c1eae169fd55502867e9aa67f029043 (changed: conversion rule's departure read and hospital_days_rule tier 1 re-derived; the other six policies' rules unchanged, computes re-run); task_tools.py d432b7ac…88bc unchanged.
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 7`, 2026-10-22T18:11:05): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 c0329260…31e9.
- contamination_disclosure: earlier rounds' GT; worklog "REWORK round 7" read with permission. Rounding ruling applied.

### mechanical sweeps (revision_7)
All quotes, baselines, overwrites and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy.

### status of revision_6 findings
- S-01 CLOSED as stated: the departure is read from any hospital reservation whatever its status (exact key on the qualifying admission date first); DSL probe (declined hold, departure 10-01 into observation, admission 10-02): hospital days from 10-01, credit 13471.00 — the same as for a returned hold. The fallback read keeps a first-match-per-status selection: T-01.

### findings (revision_7) — RED; members listed in full
T-01 SOURCE-POLICY (XF 12, second record). Where no reservation began on the qualifying admission date, the departure is "the latest leave start falling inside the charge's span and before that admission date among the reservation returned on the Part A coverage start date and the first reservation on file in each of the declined, returned, released and expired statuses". A resident with an earlier hospitalization has an older reservation of the same status on file; when it is listed first it displaces the stay's own reservation (its leave start lies outside the span and is discarded), no departure is found, and the hospital days fall back to the inpatient admission — the S-01 outcome by another route. Probe on a task-1 copy (stay's hold declined, departure 10-01 into observation, admission 10-02; an older declined hospital hold of 2026-03-02 listed first): 13088.00 instead of 13471.00, the 10-01 night away charged though the bed was not held. Members: conversion hs_dec, hs_ret, hs_rel, hs_exp (CFIELD first match per status) and the rule's "first reservation on file in each of the … statuses".

## post_reveal (revision_7)
- written after the reveal (2026-10-22T18:12:06Z): both tasks' GT equals the blind derivations figure for figure. Task assignment: task 0 — none; task 1 — none; charter — T-01.

## closing_checklist (revision_7)
Not reached: the charter carries T-01. Revisions 1-6 untouched; revision_7 appended. Gates: round-7 snapshot 7/7 OK.

VERDICT revision_7: task0=PASS task1=PASS charter=T-01

## revision_8

## charter_global_frozen (revision_8)
- written before any round-8 GT field was opened. private.extended.yaml 4e17064eb9b84ea278ef722c94211c853e5c8269c27a0d5a44fc785d64c4edf5 (changed: conversion-credit overwrite, scope count, departure read and out-of-scope compute; room-change scope sentence — re-derived; other rules unchanged, computes re-run); task_tools.py d432b7ac…88bc unchanged.
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 8`, 2026-10-22T22:04:22): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 c0329260…31e9.
- contamination_disclosure: earlier rounds' GT; worklog "REWORK round 8" read with permission. Rounding ruling applied.

### mechanical sweeps (revision_8)
All quotes, baselines, overwrites (verbatim superseded clauses; replaced_by verbatim in rules) and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy.

### status of revision_7 findings
- T-01 CLOSED inside the new scope: the first-match-per-status reads are gone; within the scope (at most one hospital reservation, counted so that a hidden second one breaks the count) the departure is that reservation's leave start. The out-of-scope fallback introduced by the same route: U-01.

### findings (revision_8) — RED; members listed in full
U-01 SOURCE-POLICY/SOURCE-FACTOR (XF 31 out-of-scope restatement; realism). Out of scope the overwrite restates base: "the advance billed for days on or after the conversion date is credited with reason payer_conversion_credit at the daily rate of that charge", and the compute reads the recorded conversion date: `base_cr = (days from MX(conv_on, chg_from) through chg_to) x chg_rate`. On an agreement that is active again the recorded conversion date is, by the schema, "the first day billed privately again after a reversion", so the fallback credits the resumed private days and leaves the days the other payer covered (and the hospital days) billed privately — the opposite of base's intent (the date the other payer took over); the re-charge then charges the resumed days again. The scope is left by ordinary records: any second reservation of one kind and status (e.g. two home visits, two hospitalizations) breaks the count. Probe on a task-1 copy with a June therapeutic hold (returned, with its transfer notice) added: out of scope, credit 9156.00 (21 days 10-11..10-31 at 436) instead of 13088.00 — the Part A days 10-05..10-10 and hospital days 10-02..10-04 stay on the resident's private bill. Members: conversion overwrite of private_payer_source_change (out-of-scope clause) and `base_cr`; the scope count (any bed-hold kind) that routes ordinary residents there.

## post_reveal (revision_8)
- written after the reveal (2026-10-22T22:05:31Z): both tasks' GT equals the blind derivations figure for figure. Task assignment: task 0 — none; task 1 — none; charter — U-01.

## closing_checklist (revision_8)
Not reached: the charter carries U-01. Revisions 1-7 untouched; revision_8 appended. Gates: round-8 snapshot 7/7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=U-01

## revision_9

## charter_global_frozen (revision_9)
- written before any round-9 GT field was opened. private.extended.yaml db8baf78629019d2fff99697f3e963474acd3076c4f6fafb9f5930b812ac1e4c (changed: conversion-credit overwrite out-of-scope date, departure keys and scope; re-derived; other policies unchanged, computes re-run); task_tools.py d432b7ac…88bc unchanged.
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 9`, 2026-10-22T22:10:43): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK; views task0 c3cc05d2…b6dd, task1 c0329260…31e9.
- contamination_disclosure: earlier rounds' GT; worklog "REWORK round 9" read with permission. Rounding ruling applied.

### mechanical sweeps (revision_9)
All quotes, baselines, overwrites and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy.

### status of revision_8 findings
- U-01 CLOSED. The out-of-scope credit now dates the restated base clause from the first day another payer source took over (the Part A coverage start on an agreement active again after Part A), never the resumption date. DSL probes on task-1 copies: a second (June) therapeutic hold on file now stays in scope (the exact key finds the stay) — 13088.00, and the out-of-scope figure on that copy would be 11772.00 (27 days from the Part A start), not 9156.00; the stacked round-7 world (stay's hold declined with an observation departure and an older declined hospital hold listed first) is out of scope and takes the base restatement (11772.00, days on/after the Part A start) — the base clause computed exactly, as the scope route intends; in scope the same stay without the older hold gives 13471.00.

### decoys on the changed reads (revision_9)
Exact keys (leave start = qualifying admission; return date = coverage start) across the three hospital kinds, any status; the count fallback breaks on a hidden second reservation of a kind and status (its notice names an uncounted reservation); absent hospital reservation -> inpatient admission. Out-of-scope date follows the first-converted-day records. T1 moves every factor on both worlds; T2 holds for every factor (in-scope worlds).

### findings (revision_9)
None. All XF recipe points re-checked on all seven policies: factor independence and assembly (netting and moved-day windows are stated once in the assembly; no factor tier reads another factor's output), rule = compute (sweeps above; DSL evaluation), overwrites declared and scoped with sibling sentences naming both cases, tool contracts (unchanged hash; half-up, positivity and format checks in the bodies), realism (base-consistent bed-hold, Medicare ABN/NOMNC/QIO and late-notice treatments; company-set deposit schedules), DSL routes (scoped coarse record test with exact out-of-scope restatement). Observations carried: O-2 (deposit-day ladders), O-13/O-16 (seed style notes).

## post_reveal (revision_9)
- written after the reveal (2026-10-22T22:11:48Z): both tasks' GT equals the blind derivations figure for figure. Task assignment: none.

## closing_checklist (revision_9)
- Files: 0.md, 1.md and _difficulty.md, one per task plus this file; revisions 1-8 untouched, revision_9 appended; every comparison section of revision_9 carries PASS.
- Coverage and scopes: the seven extended policies are claimed exactly once — task 0: late_notice, room_change, new_room_span, additional_deposit; task 1: conversion, resumed_recharge, resumption_deposit; scopes (whole trees) pairwise disjoint; seven task tools, each target of one policy; uuid8s 45589810, 09a50cb9, 526f1e53, f9f00bc8, 12618703, e6f5843a, 9c511f79 distinct and unchanged since round 1.
- Trees: task 0 three prerequisite problems with three value_input edges; task 1 two with two value_input edges; each root is an owner=user deposit payment; no cycle; the difficulty's prerequisite edges form two disjoint chains.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors with >= 2 parameter and >= 1 method; every ladder of three tiers stated in its rule, distinct in outcome; task 0 multi-source billed_tier / move_date_source and cross-difficulty bedhold / ancillary factors; task 1 multi-source first_converted_day_rule and cross-difficulty medicare / bedhold / ancillary factors; every factor moves its task's scored value (T1) and has a producible single-factor world (T2); each all-baseline figure is definite and differs from gold.
- Gates re-run on the final form: round-9 snapshot — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (traceability deferred to post-publication).

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

## charter_global_frozen (revision_10)
- private.extended.yaml 55d67b2713d366432810450d394f35dab8653857861a1264de6e7f5b52a147cc (rule and ladder wording changed in five policies; no compute changed — DSL re-run reproduces every scored, baseline and sensitivity figure); task_tools.py d432b7ac…88bc unchanged.
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 10`, 2026-10-23T06:22:18): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK.
- contamination_disclosure: earlier rounds' GT; audits/render_source/private_pay_residency_billing/render_r1.md and worklog "REWORK round 10" read with permission.
- Audit-miss disclosure: render_r1 findings 1-7 were present in the charter my revision_9 cleared (rule/compute divergences on worlds outside the two task worlds); revision_9's "None" findings line was wrong for them.

### mechanical sweeps (revision_10)
All quotes, baselines, overwrites (verbatim, replaced_by in rules) and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy.

### status of render_r1 findings (each checked against the compute)
1. late-notice exclusion — CLOSED: the rule now requires a recorded move date for both branches ("where a move date is recorded on the agreement, whose first day is that recorded move date or the date named by the resident's latest room-change request"), as `excl` does.
2. "the move date" in the conversion carve-out — CLOSED: room-change rule, its replaced_by and the new-room span's sibling exclusion all say "after the move date recorded on the agreement" (compute: last_room_change_date). Class swept: the remaining unqualified "the move date" in the room-change rule (credit entry, days moved, netted days) are the factor's move date, which is what ln_net / days_moved read; the conversion rule has a single (recorded) move date.
3. conversion netted window — CLOSED: "on or after the first credited day and on or before the last converted day" = nd/oth's [first_cr, stop_on). Class swept: re-charge and converted-days stops ("through the day before a move …") and the new-room span ("through the last of them") agree with their computes.
4. re-charge schedule tier 2 — CLOSED (rule and ladder: notice recorded and not run by the recorded conversion date -> preceding) = s_cur. Class swept over every schedule ladder: room-change come-off, new-room schedule_choice, conversion credit_schedule_rule, additional deposit_schedule_rule, resumption_schedule_rule — each rule tier equals its compute branch.
5. leave vs booking — CLOSED in late-notice, new-room span and re-charge (rules and ladders: "the latest booking of resident-private bed-hold days (the one whose first booked day is latest …)") = XLATEST by from_date. The conversion's hospital read is reservation-level by design (leave start), consistent with its compute.
6. where the unreversed days sit — CLOSED: new-room span and re-charge now say "the remaining days counted in a row from the first booked day" (late-notice already did) = leave_in from lv_start.
7. come-off standard schedule — CLOSED: adds "and that date falls on or after the current schedule's effective date" = co_notice_in. Class swept (conversion, new-room span, re-charge, deposits carry the effective-date condition).

### findings (revision_10)
None. Every changed sentence agrees with its compute on the task worlds and on the divergent worlds render_r1 names; the probes of revisions 7-9 reproduce (in-scope stacked world 13471.00; out-of-scope restatement 11772.00; second therapeutic hold stays in scope 13088.00).

## closing_checklist (revision_10)
- Files: 0.md, 1.md, _difficulty.md; revisions 1-9 untouched, revision_10 appended; both comparison sections of revision_10 PASS.
- Coverage, scopes, uuid8s, trees and factor structure as listed in revision_9's closing checklist (no compute, world or tool changed since).
- Gates re-run on the final form: round-10 snapshot 7/7 OK (traceability deferred to post-publication).

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

## charter_global_frozen (revision_11)
- private.extended.yaml 24ea66b9dc5b65d87972c4cfdba6766ef000c791a29185c78316d7bb904eafaa (recurring-allowance tier-2 wording in both deposits; no compute changed); task_tools.py d432b7ac…88bc unchanged; views task0 2de792fe289d3dbeb4d6f95766fbb3849ca87e4c8f81bccd72ef620861d560d2, task1 8799de2e9a6445c285127d02c3c9fdd971d94163d69abc58f3c48cd74f888ef9 (cross-product seed rows).
- entry conditions: snapshot run by the auditor (`/tmp/erl0074_coord/snapshot.sh private_pay_residency_billing 11`, 2026-10-23T06:57:32): [check_extended] EXTENDED OK; [check_task_tools] TASK TOOL CONTRACT OK; [replay_tasks --check] REPLAY OK; [check_solvability] SOLVABILITY OK; [check_compute] COMPUTE OK; [check_grounding] GROUNDING OK; [check_cross_fire] SCOPE OK.
- contamination_disclosure: earlier rounds' GT; _kb_verdict.md (S1, S2), worklog "REWORK round 11" and the published docs/bedhold, docs/ancillary read with permission.
- Audit-miss disclosure: S1 (task 0's bed-hold charge priced at 436.00 where the published hospital-stay charge gives 421.00) was in every revision since round 1; my checks priced it against the bed-hold charter's base rule, not the published hospital-stay charge.

### S1 — every seeded cross-product row against the published docs
- bedhold, task 0: hospital-stay charge 8b7280d7… now 1263.00 = 3 x 421.00 — hs_rate (agreement signed 2025-07-30, notice 2026-08-20 delivered after 2026-07-01: current schedule only from 2026-10-19, so 10-15..10-17 are prior-schedule days), hs_base (no day before the transfer notice of 10-15 22:40), hs_diet (leave 10-15..10-17 = 3 days < 4: no credit), hs_ext (0 + 3 days < 15: 100 %), hs_iso (no isolation), hs_after/hs_ret (returned 10-18, after the entry): CLOSED; reservation charge_balance 1263.00 matches. Booking 05b70530… (10-15..10-17, departure counted, return day not), notice and on-time election (10-16 11:45, within 24 h of the notice) consistent.
- bedhold, task 1: hospital hold e369d50b… (emergency departure 10-02 06:50, notice 11:20, election 10-03 14:10 — after the window, hold from the election day), booking 8f2d8dc5… 10-03..10-04, returned 10-05; therapeutic hold 280b64fc… (notice 09:30 before the 10:15 departure, on-time election), booking fafbb3a6… 10-17..10-18; no charge rows — the published charges post only when the representative signs, so unsigned bookings are a producible state; balances 0.00 consistent.
- ancillary, both tasks: recurring starts dated on the first charged day (task 0 telephone and cable 2026-04-01; task 1 telephone and cable 2026-02-01, oxygen 2026-08-12 -> 20/31 x 185.00 = 119.35), cancellations charged through the month requested (task 0 cable through August, task 1 cable through July), statements on the 4th, prices from the private-pay schedule (telephone 29.00, cable 42.00, oxygen 185.00, haircut 22.00, manicure 15.00, two guest lunches 2 x 9.50 = 19.00), every optional item against a prior request, every charge paid by one matching payment. Consistent.
- medicare, task 1: episode 73f4a696… (3 inpatient midnights 10-02..10-05, coverage 10-05, days 10-05..10-10 booked, NOMNC 10-08 with 2 days' lead, coverage_ended skilled_need_ended, SNF ABN 10-14 for care from 10-11, option 2) — consistent (unchanged since revision_6).
- No private compute reads a bed-hold charge or balance; no scored figure moves.

### S2 — CLOSED
Both deposits' recurring tier 2 now reads "the total of all the recurring charges billed for the latest service month (the service month of the recurring charge posted latest, the charge posted first deciding where two share that posting date)", ladders likewise = rc_ms (sum over the month). Class swept: the remaining tie parentheticals (latest booking, insurer's most recent payment, latest item charge) each select a single entry by design and their rules speak of a single entry.

### mechanical sweeps (revision_11)
All quotes, baselines, overwrites and prerequisites verbatim; every binding quoted; no duplicate sentence; no factor id in a tool name; 4-6 factors per policy.

### findings (revision_11)
None.

## closing_checklist (revision_11)
- Files: 0.md, 1.md, _difficulty.md; revisions 1-10 untouched, revision_11 appended; both comparison sections PASS.
- Coverage, scopes, uuid8s, trees and factor structure unchanged since revision_9's checklist (no compute, tool or private seed row changed).
- Gates re-run on the final form: round-11 snapshot 7/7 OK (traceability deferred to post-publication).

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
