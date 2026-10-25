# Policy-task audit — residency_occupancy_certification / charter-global

## charter_global_frozen
- Auditor: independent policy-task auditor (erl-task-policy-audit), round 1. Freeze time 2026-10-15T07:20Z. Written before any task JSON was opened.
- Freeze hashes (sha256 prefix): `residency.extended.yaml` 10cafa0163c6c3b1; `task_tools.py` 78a005f80118e4eb; masked views 0.json 1c9f30c0c748329e, 1.json 0cc89c3e2d68708a (match the coordinator snapshot).
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/residency.yaml, and products/hecm.yaml, payoff.yaml, jumbo.yaml for the cross-category reads), this difficulty's extended charter and task_tools.py, the two masked views, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics: `within_months` = 0 <= MONTHS(d, NOW) < n; LATEST strict `>` on date key; COUNT/LATEST scoped to the profile; CFIELD first match over the customer's holdings).
- Masked/not read before freeze: everything under tasks/residency_occupancy_certification/tasks/ (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure). No recursive grep was run over tasks/. No other scenario or sibling difficulty was read.
- Entry conditions: gate snapshot r1 supplied (all script gates green except traceability tool-name provenance and validate "required document not found", both pre-render); masked views + hashes supplied. Entry conditions met.
- Scratch evaluator: /tmp/audit_residency_occupancy_certification_0064/ (imports check_compute.build_env / substitute; deleted at the end).

### policy_conflict_scan
- Base section lines 1-1299 of the extended yaml are byte-identical to blueprint/products/residency.yaml (`diff` empty).
- 8 extended policies, 8 distinct target tools, 8 distinct `(target_tool, computes)` pairs. Two pairs share `computes` (checkin_sequence: facility vs call-in; certification_year: mailed vs phone); each replaced_by carves the other out by channel ("a contact confirmed by an accepted facility letter" / "a check-in the borrower confirms in person"; "mailed certification form" / "given by phone on a recorded call"), and the two replaced_by texts of each pair are mutually consistent.
- Prerequisite graph: two disjoint chains: reclass <- absence_start (state_gate) <- facility (value_input) <- call_in (value_input); return <- mailed (value_input) <- phone (value_input); refi_closing <- phone (state_gate). From the masked worlds the auditor derives task 0 = {call_in, facility, absence_start, reclass} and task 1 = {phone, mailed, return, refi_closing}: pairwise disjoint and jointly complete (all 8 policies). To be compared with charter_scope after reveal.
- Overlapping subjects / terminal-state conflicts: see findings C1 (absence clock vs base principal-residence and non-occupancy sentences) and C2 (certification-year crediting vs base cycle completion). Cross-category read boundaries: hecm (status, co_borrower, funding/closing dates, payout plan, scheduled payments), payoff (plan, status, statement/accepted dates, receipts/applications), jumbo (terminated_date); all reads are of fields those charters own. See C4/C6 for what those charters actually allow.

### rule_compute_equivalence
Every compute binding has a verbatim `compute_basis` sentence in its own rule; swept back sentence by sentence, every rule tier/window/limit has a binding. Checked items (all equal unless noted):
- reclass: death notice "taking the one received most recently" = LATEST(date_field=received_date); open cycle = year of due date; overdue-age/report-lag/handling-window ladders and the three "no more than" tests; "a Summit loan included" -> CFIELD hecm None -> 0. Absent death notice -> both dates = due date -> redating "otherwise" tier. EQUAL.
- absence_start: primary notice LATEST by received_date (fallback handling date, as stated); household latest admission LATEST by event_date; occupancy-end ladder; attested-date ladder ('' when neither, "an attested-occupancy date exists"); 12/24/3-month windows; four limits. EQUAL. Note (obs O8): the rule's tier 1 says "the household's latest admission" while the overwrite speaks of "another borrower's occupancy"; a primary borrower with two own notices can satisfy tier 1 with their own later admission.
- facility: letter = accepted supporting_document about the primary, most recently received; contact-before-start override; three-way numbering; schedule start, standing date, interval, allowance, offset; `//` floor + MX(1, ...) equals "fraction dropped ... never less than one" on all integer inputs. EQUAL.
- call_in: highest number (MAX, 0 when none), latest check-in date, numbering ladder, interval/allowance/cap/count-from ladders, `MX(1, MN(cap, ...))`. EQUAL.
- return: return notice most recently received; base_due paragraph; re-dating ladder incl. "no notice -> due date fixed above"; four limits. EQUAL (stay_start fallback to due date has no rule sentence but is unreachable while a profile is monitored).
- mailed: mail-channel accepted form most recently received; anniversary year / months short; cycle-key ladder; window/lag/seasoning ladders; "monitored HECM loan carries a funding date" in the result. EQUAL. Obs O3: seasoning tier 3 (no HECM -> certification_frequency_months) can never decide anything, because the result separately requires a HECM funding date.
- phone: household signature = latest recorded certification on the profile (date, year, channel); caller = primary borrower; join/refinance/call-window ladders. EQUAL.
- refi_closing: terminated date Summit-or-HECM-or-NOW; payoff case scoped to the monitored Summit loan; successor = active HECM; receipts/applications over all the borrower's payoff cases (stated so in the rule). EQUAL except obs: tier 2 "payoff receipt date" has no stated absent-receipt branch (compute falls to terminated date).

### action_binding_and_uuids
- Each target tool is claimed by exactly one policy; no docstring names another tool or carries a sequencing word about other tools ("after a certifying borrower's death" in reclassify is the business trigger).
- uuid8s 0e562024, c2b89a70, 6c7d3fa5, 948ffc7a, baa2f4ef, e8b1dc9f, 267bfb18, 33924361: no shared prefix/suffix, no sequence, no copy-with-new-tail. PASS.
- Tools only write the values given; no tool validates a prerequisite (read every body: ctx.update / ctx.create only). PASS.
- Docstring second reading: see C3 (both check-in tools say "1 for the first check-in of the absence" / "within the current absence"). Docstrings carry no other example value; no gold-shaped example found.

### prerequisite_graph
- `prerequisite` present on all 8 policies ([] on reclass, return, refi_closing). Every `problem` names an extended policy in this file; none self-referential; graph acyclic (two chains + one side edge).
- Each `policy_source` is verbatim in its own policy's rule (checked all 6). All `form: state`, no fallback_reason, consistent.
- kinds: absence<-reclass state_gate on residency_profiles.variant_name (a real gate sentence); facility<-absence value_input on `stay_start` (binding exists); call_in<-facility value_input on `top_number`; mailed<-return value_input on `due_on_file`; phone<-mailed value_input on `household_sig_year`; phone<-refi state_gate on residency_profiles.closed_date. resolved_by = the depended-on policy's target_tool in every case, and that tool's effect makes the stated condition hold. No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences
Four-point test on each edge (connective / record-visible state / no tool, id or snake_case / strength):
1. absence_start: "Monitoring of a health-care absence is not opened until the profile carries the certification plan matching the borrowers still living on the loan." not...until; state = plan on the profile; only reclassify_occupancy_plan writes variant_name. PASS.
2. facility: "A facility-confirmed contact is numbered only after the profile carries the start date of the health-care absence under monitoring." only after; state = absence start date; only open_absence_monitoring writes a non-empty absence_start_date. PASS.
3. call_in: "The borrower's own check-in is not numbered until the contact confirmed by the most recently received accepted facility letter stands on the profile as a recorded check-in." state = recorded check-in citing that letter; only record_facility_checkin cites a letter. PASS.
4. mailed: "A mailed certification's certification year is not fixed until no health-care absence on the profile remains under monitoring." The writer is record_return_home. Obs O5: close_occupancy_profile also ends monitoring, but only on a profile whose loan ended; on a profile still certifying it is ineligible, so one reading remains.
5. phone: "A phone certification's certification year is fixed only after every accepted mailed certification form on file for the profile is recorded on it." writer record_occupancy_certification. Obs O4: the sentence says "every" accepted mailed form, while the mailed policy fixes the year of only the most recently received form per handling; harmless when one form is unrecorded.
6. phone: "A certification is not taken by phone until every other occupancy profile of the borrower whose monitored loan has ended shows a closing date." writer close_occupancy_profile. PASS on its own wording; but the state it waits on is one the base charters cannot produce (C4 and task 1 T1-1).
No rule restates another problem's sentence; no cross-problem order outside these sentences; no base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against each base_policy_refs entry (follows = F, declared override = D, conflict not declared = U):
- reclass vs household_change: "open cycle's due date is unchanged" D; plan targets, death-notice gate F. vs evt_certification F. vs overdue_inspection: overdue_after_grace F, but after a re-dating the profile keeps status overdue with a due date inside (or before) the grace period (obs O2; no scored consequence in task 0 because monitoring opens next).
- absence_start vs health_absence: "absence_start_date is the facility admission date ..." D; "A borrower who leaves home for a hospital ... keeps the home as principal residence for up to health_absence_max_consecutive_months consecutive months." U (C1). Not in refs but governed by the same quantity: residency_nonoccupancy "Non-occupancy is confirmed for a health-care absence only when health_absence_max_consecutive_months calendar months have passed since the facility admission date." U (C1).
- facility / call_in vs health_absence: check-in sentence D (both replaced_by consistent); everything else F.
- return vs health_absence: "any cycle whose due date passed during the absence is due within response_grace_days of the return" D.
- mailed / phone vs evt_certification, evt_notices: certification_year sentences D; phone's submission-only recording D; "A cycle is complete when residency_msr_cycle_signatures reaches the plan's min_signatures" with the measure window "certification_year equals the calendar year of the profile's certification_due_date" U in effect (dropped branch, C2).
- refi vs closure / household_change: closed_date sentences D (both); loan_ended gate F.

### factor_ladders
| policy | factors (effect) | param/method | multi-source | cross_difficulty |
|---|---|---|---|---|
| reclass | redating_anchor (m), overdue_age_cap (p), report_lag_cap (p), settle_window (p) | 3/1 | overdue_age_cap, settle_window | settle_window: hecm |
| absence_start | vacancy_anchor (m), attest_source (m), attest_lookback_days (p), stay_notice_days (p), continuity_months (p), own_notice_days (p) | 4/2 | attest_lookback, stay_notice, continuity, own_notice | attest_lookback, continuity: hecm |
| facility | letter_numbering (m), schedule_start (m), standing_day (m), contact_interval_days (p), early_answer_days (p), first_contact_offset (p) | 3/3 | letter_numbering, contact_interval | contact_interval: hecm |
| call_in | call_numbering (m), call_cadence_days (p), call_early_days (p), missed_contact_cap (p), count_from (m) | 3/2 | call_numbering, call_cadence | call_cadence: hecm |
| return | redate_on_return (m), min_absence_length (p), due_lead_days (p), return_notice_age (p), last_contact_gap (p) | 4/1 | min_absence_length, due_lead_days | min_absence_length: hecm |
| mailed | cycle_key_rule (m), early_window_months (p), mail_lag_days (p), seasoning_months (p) | 3/1 | cycle_key_rule, early_window | early_window, seasoning: hecm; mail_lag: payoff |
| phone | join_household_cycle (m), join_window (p), refinance_age (p), call_window (p) | 3/1 | join_household_cycle, join_window | refinance_age: payoff |
| refi_closing | refi_close_anchor (m), handoff_gap (p), stale_notice_cap (p), acceptance_lead (p), quiet_months (p) | 4/1 | refi_close_anchor, handoff_gap | refi_close_anchor: hecm; handoff_gap, acceptance_lead: payoff |
- Counts are within bounds (4-6; >=2 p; >=1 m). Every ladder has 3 pairwise-disjoint tiers stated in the rule and implemented in compute; each fall-through equals the declared factor baseline; `decides` is never `result`; bindings disjoint (gate check_compute green). No two tiers of a ladder select the same value as stated. Labels honest (method tiers change the date source or numbering algorithm; parameter tiers change a number).
- Realism of tiers: C1 (vacancy_anchor tiers 1-2), C4 (refi_close_anchor / acceptance_lead degenerate on charter-consistent worlds) and C5 (conditions with no business nexus) are REDs. Weak-nexus but defensible conditions are listed as obs O1.

### findings
C1 — SOURCE-POLICY RED + SOURCE-FACTOR RED (bears on task 0). Symptom: residency_ext_absence_start_vacancy moves the absence clock to "the occupancy-end date" (household's latest admission or a co-borrower's death) and leaves two base sentences that count the same absence from the absent borrower's own departure: residency_health_absence "A borrower who leaves home for a hospital, rehabilitation center, nursing home or assisted-living facility because of physical or mental illness keeps the home as principal residence for up to health_absence_max_consecutive_months consecutive months." and residency_nonoccupancy "Non-occupancy is confirmed for a health-care absence only when health_absence_max_consecutive_months calendar months have passed since the facility admission date." Neither is named in an `overwrite`. Root cause: the declared override replaces only the absence_start_date sentence, but these two sentences govern the same 12-month limit. Realism: 24 CFR 206.27(c)(2)(iii) makes a HECM due and payable when, "for a period of longer than 12 consecutive months, a mortgagor fails to physically occupy the property because of physical or mental illness and the property is not the principal residence of at least one other mortgagor". The 12 months are the absent mortgagor's own consecutive months; a co-borrower's continued occupancy only defers the trigger while it lasts. It does not restart the count. No HECM servicer can publish vacancy_anchor tiers 1-2 (count from the household's latest admission / the date of death). Doing so defers a HUD due-and-payable event that the servicer must report. Demonstration: task 0 file.
C2 — SOURCE-POLICY RED (bears on task 1). Symptom: residency_ext_return_redating can re-date a not-yet-due open cycle to the return date (moving the due date's calendar year back), while residency_ext_mailed_form_cycle_year (cycle_key_rule tiers 1-2) and residency_ext_phone_cert_cycle_year (join_household_cycle tiers 1-2) credit the very certifications given in answer to it to a different certification year. Base residency_evt_certification still says "A cycle is complete when residency_msr_cycle_signatures reaches the plan's min_signatures", and that measure counts only "rows whose certification_year equals the calendar year of the profile's certification_due_date". Base residency_overdue_inspection still makes the profile overdue 30 days after that due date. Merged result: a cycle answered by every required signer stays open, turns the profile overdue and orders a chargeable inspection. The base sentence was not overwritten (dropped branch). Demonstration: task 1 file.
C3 — SOURCE-POLICY RED, check 3 (bears on task 0). record_facility_checkin_6c7d3fa5 and confirm_absence_checkin_948ffc7a both describe `checkin_sequence` as "the check-in number this contact carries within the current absence, an integer, 1-based (1 for the first check-in of the absence)". The charter numbers by count-on-the-profile plus one (baseline) or by scheduled-contact slot (facility tier 1) or highest-plus-missed-contacts (call-in tier 1). These give, for example, 6 for the first check-in of an absence. The docstrings state a second business rule for the same scored value. Members: both tools' `checkin_sequence` args (the "within the current absence" scope also contradicts the charter's "count of check-ins recorded on the profile", which spans earlier absences).
C4 — SOURCE-FACTOR RED (bears on task 1). residency_ext_refi_profile_closing is scoped to a monitored Summit loan "paid in full through a satisfied Borrower Voluntary Payoff". Every closing limit requires "the payoff terms carry an accepted date". Under blueprint/products/payoff.yaml a Borrower Voluntary Payoff has `acceptance_required: false`, `acceptance_signature_days: 0` ("0 where no agreement is needed") and "Borrower Voluntary Payoff and HECM-to-HECM Refinance Payoff are satisfied from terms_issued". So the BVP case never carries an accepted_date, and the override can never apply. Separately, refi_close_anchor tier 1 ("the successor loan funded on or before the loan's terminated date") selects a date different from the fall-through only when a HECM was held while the Summit first-lien loan was still open. hecm.yaml forbids that ("a borrower with an open Summit loan of any plan other than Summit Second Lien cannot also hold a HECM"). Payoff satisfaction is also "on the day payoff_msr_net_remitted first reaches the required payoff amount", which for a refinance is the successor's funding day. On every world the base charters can produce, the tiers therefore select the terminated date, the same as the fall-through. Demonstration (charter-consistent payoff rows): task 1 file.
C5 — SOURCE-FACTOR RED, class "tier condition with no business nexus to the quantity" (bears on task 1). Members (complete list): (a) mailed.mail_lag_days: the postal-lag tolerance for crediting a mailed form (10/5/0 days) is set by the plan of an unrelated satisfied payoff case. The fall-through of 0 days means an ordinary borrower's mailed form can never be credited. (b) mailed.seasoning_months: the loan-age minimum (6/9/12 months) is set by the HECM payout plan (Line of Credit vs other), which has no bearing on certification crediting. (c) phone.refinance_age: whether a spouse's phone certification joins the household signature's cycle depends on a payoff having been applied in the last 12/6 months. Joining a co-signer's open cycle is the ordinary joint-household treatment (base missing_signer_cure_days), and no servicer conditions it on a recent refinance. Obs: param keys `lag_days_refinance` / `refinance_months_h2h` are bound to the BVP tier, while the actual "HECM-to-HECM Refinance Payoff" plan falls in the "any other plan" tier (mislabel).
C6 — SOURCE-POLICY RED, class "first-match read of a non-unique record without a decoy guard" (no task world carries the decoy). Members: mailed.payoff_kind and phone.payoff_kind = CFIELD('payoff','variant_name', status='satisfied') against the rule's singular "the borrower's satisfied payoff case". A borrower can hold several satisfied payoff cases (payoff.yaml: "A requester may hold payoff cases on more than one loan"). Probe (task 1 world after the return write, form received 2026-11-23, plus one 2019 satisfied "HECM-to-HECM Refinance Payoff" case): decoy row first -> mailed result 2026; decoy row last -> 2027. Related members of the unscoped-read neighbourhood (obs, rule says so explicitly): phone.payoff_applied_day and refi.funds_received_day take the latest over all the borrower's payoff cases. phone.refinance_age can then pair one case's plan with another case's application date. Tie-break: "received most recently" / "latest" reads state no tie rule (LATEST keeps the first of equal keys).
Observations (no RED): O1 weak-nexus but defensible conditions: reclass.report_lag_cap (# absence notices -> death-report lag), reclass.settle_window (tenure payments -> handling window, longer when not paying), absence.continuity_months (tenure payments), absence.own_notice_days (recent inspection order), absence.attest_lookback_days (loan names a co-borrower, true for nearly every profile reaching tier 1), return.min_absence_length (loan age), return.return_notice_age, mailed.early_window_months, phone.call_window, refi.stale_notice_cap, refi.quiet_months, facility.first_contact_offset. O2 reclass leaves status overdue with a due date not past grace. O3 inert seasoning tier 3. O4 phone "every mailed form" vs mailed one-per-handling. O5 close also ends monitoring. O7 "facility letter" = any accepted supporting_document about the primary borrower; on plans that require marriage, trust or POA supporting documents those would be read as facility letters. O8 household latest admission may be the primary's own.

## closing_checklist
Written after both reveals (2026-10-15T07:22:52Z); nothing above this heading was changed after the reveal.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; no earlier revision exists.
- Scope: GT charter_scope task 0 = {reclass, absence_start, facility, call_in}, task 1 = {refi_closing, return, mailed, phone}. These are pairwise disjoint, jointly cover all 8 extended policies, and equal the auditor's pre-reveal derivation. Task tools are closed: 4 + 4, each used by exactly one task's gold; uuid8s independent.
- Trees: each task has 3 prerequisite problems, 2 value_input edges, an owner=user root write, and no cycle. The difficulty-wide graph is acyclic.
- Arithmetic: every expected value, baseline_result and per-factor baseline_result in both tasks equals the auditor's independent recomputation.
- NOT CLOSED: charter-wide REDs C1-C6 and per-task REDs remain (task 0: C1, C3; task 1: T1-1, T1-2, C2, C5). The instantiation gates were not re-run by this audit (the coordinator's r1 snapshot is the gate record).

task0=SOURCE-POLICY RED task1=SOURCE-TASK RED
charter=C1,C2,C3,C4,C5,C6

## revision_2

### charter_global_frozen (r2)
- Re-audit, round 2. Written 2026-10-15 between 12:12:52Z and the reveal (see the closing section below), before tasks/0.json and tasks/1.json of r2 were opened. Inputs: extended yaml 48b6ef0eaa1c669b (changed from 10cafa0163c6c3b1), task_tools.py d3216d18b8d8a889 (changed from 78a005f80118e4eb), masked views 0.json 1450db130a827983 and 1.json ef6cb33ef0a8c00f, snapshot_r2.txt (all script gates green; traceability misses are only unlock tool names; validate errors are pre-render). Both shared inputs changed, so every charter-global section is re-derived in full below; the r1 text above is left untouched.
- Contamination disclosure: the auditor holds round-1 knowledge of the r1 tasks/0.json and 1.json GT (round 1 revealed it). The task 1 tree is new, so the r1 GT does not bear on it. The task 0 regression derivation was recomputed from the r2 masked view, and its world was re-dated, so no r1 figure carries over. The coordinator's message carries only item ids and gate lines, no scored value.

### policy_conflict_scan (r2)
- Base section is still byte-identical to blueprint/products/residency.yaml. 8 extended policies: reclass, absence_start, facility, call_in, return_redating, mailed_form_standing (new; computes effective_date), cycle_completion_date (new; computes last_certified_date), return_contact_number (new; computes checkin_sequence). phone_cert_cycle_year and refi_profile_closing and their tools are gone; no rule or tool still names them or reads payoff/jumbo.
- Three policies compute checkin_sequence on three tools; each replaced_by carves out the other two by situation ("confirmed by an accepted facility letter" / "confirms in person while still in care" / "the closing contact in which the borrower confirms having come home"). The three replaced_by texts are mutually consistent.
- Graph: reclass <- absence_start (state_gate) <- facility (value_input) <- call_in (value_input); return_contact <- return (value_input) <- mailed (value_input) <- completion (value_input). Auditor-derived scopes: task 0 = {call_in, facility, absence_start, reclass}; task 1 = {completion, mailed, return, return_contact}. Disjoint and complete.

### rule_compute_equivalence (r2)
Mechanical: every compute_basis sentence is verbatim in its own rule; every prerequisite policy_source is verbatim in its own rule (script check). Manual sweep of the new and changed bindings:
- reclass: survivor limit (12/6/0 by notice promptness) and the result's "where the primary borrower has an accepted health-care absence notice" guard = `survivor_admission == '' or ...`; facility letters counted only "on a plan whose supporting_document is none" = `P('supporting_document') == 'none'`. EQUAL.
- absence_start: turned-away notice = rejected health notice about the primary, most recently received (admission, receipt, reason, sender); departure ladder; transfer window by sender = HECM co-borrower; corroboration to the latest letter's contact date; own-notice window; four limits. EQUAL.
- facility: schedule start now tests an admission falling *after* the absence start (<= facility_link_days). EQUAL.
- call_in: numbering tier 1 = admission after the absence start; late-contact grace by whether the latest check-in cites a letter. EQUAL. Obs: the factor `ladder` text of call_numbering omits "the late-contact grace taken away"; the rule prose and compute both carry it.
- return: borrower's confirmation = latest check-in dated on or after the return date; re-dating ladder; four limits plus "the due date passed during the absence". EQUAL.
- mailed_form_standing: standing ladder; pre-return / receipt-lag / crediting windows; "otherwise it stands on the signature date". EQUAL. Obs N1: tier 2 "signature date later than the date received" is not stated as exclusive of tier 1 (both can hold for a post-dated form signed before the return). Compute and the rule's "chosen as follows" order take tier 1, and no task world reaches the overlap.
- cycle_completion_date: last signature under the open cycle by latest standing date; completion ladder; three link/margin tests; "other than the last signature's standing date ... only when". EQUAL.
- return_contact_number: slot formula bounded by `[top+1, top+cap]`; interval/allowance/offset/cap ladders. EQUAL.

### action_binding_and_uuids (r2)
- 8 tools, 8 policies, one `(target_tool, computes)` each. New uuid8s 701e433e, e152f965 are unrelated to the 6 retained ones. No tool body validates a prerequisite: complete_certification_cycle computes only the base-rule next anniversary and status flip, not a scored value. No docstring names another tool or orders tools.
- C3 check: both check-in docstrings and the new confirm_return_home docstring now say only "the check-in number the confirmation is recorded under on the profile ... 1-based". The "(1 for the first check-in of the absence)" / "within the current absence" phrasing is gone. No example value in any docstring.

### prerequisite_graph / prerequisite_sentences (r2)
- All 8 policies carry `prerequisite` ([] on reclass and return_contact). Acyclic. All edges are form state, with no fallback. Gates exist as bindings (stay_start, top_number, confirm_day, monitoring_off, last_sig_day) or as the plan field. resolved_by = target_tool of the depended-on policy.
- New sentences: (a) return: "The return is not recorded until the borrower's own confirmation that the borrower is back home stands on the profile as a check-in." The writer is confirm_return_home (owner user). Obs N2: the rule's own definition ("the latest recorded check-in dated on or after the return date") would also be met by a call-in or facility check-in dated after the return. Those policies are scoped to a borrower "still in care" / a facility contact, so one reading remains for a borrower who is home. (b) mailed: "A mailed certification's standing date is fixed only after the profile shows no health-care absence under monitoring." Writer record_return_home. (c) completion: "A cycle's completion date is fixed only after every accepted certification form on file for the cycle stands on the profile as a recorded certification." Writer record_occupancy_certification. All pass the four-point test.

### override_declarations (r2)
- absence_start now names base_policy_refs health_absence, nonoccupancy and overdue_inspection. Its overwrite replaces only the absence_start_date sentence, and it now moves the start *earlier* (to the borrower's own departure), never later. The rule states that "another borrower's continued occupancy never moves it" and that the consecutive-month limit counts from the absence start date "exactly as the base rules ... provide".
  - Base health_absence "keeps the home as principal residence for up to ... 12 consecutive months" from leaving home is consistent with this: the departure is when the borrower left home.
  - Base nonoccupancy "since the facility admission date" reads the hospital admission as a facility admission (base lists "a hospital" among the facilities). No conflict remains.
- mailed_form_standing: overwrite of the signer-recording sentence (effective date only). The certification year stays the calendar year of the due date, so the base cycle-completion measure is untouched.
- cycle_completion_date: overwrite of the last_certified_date sentence. The due-date move and status flip are inherited and performed by the tool.
- return_redating: the passed-cycle sentence is overwritten; a cycle not due during the absence keeps its due date (the r1 pull-forward of a not-yet-due cycle is gone).
- return_contact / facility / call_in: check-in sentence declared three ways, consistently.
- reclass: unchanged apart from the new survivor limit. Obs O2 (status stays overdue with a re-dated due date) persists.

### factor_ladders (r2)
| policy | factors (m/p) | multi-source | cross_difficulty |
|---|---|---|---|
| reclass | 5 (1/4) | overdue_age_cap, settle_window | settle_window: hecm |
| absence_start | 4 (1/3) | departure_anchor, transfer_window_days, own_notice_days | transfer_window_days: hecm |
| facility | 6 (3/3) | letter_numbering, contact_interval_days | contact_interval_days: hecm |
| call_in | 6 (2/4) | call_numbering, call_cadence_days | call_cadence_days: hecm |
| return | 5 (1/4) | confirm_lag_days, notice_age_days | confirm_lag_days: hecm |
| mailed_form_standing | 4 (1/3) | standing_rule | none |
| cycle_completion | 4 (1/3) | return_link_days | due_margin_days: hecm |
| return_contact | 5 (1/4) | closing_interval_days | closing_interval_days: hecm |
- Bounds met; tiers pairwise disjoint as stated except obs N1; fall-through = factor baseline everywhere; no two tiers share a value.
- Realism: the C1 tiers are replaced by a departure anchor that counts from the borrower's own earlier hospital admission. This is HUD-consistent and only ever earlier than the facility admission. The C5 members were removed with their policies, and no condition reads another product's unrelated transaction type. Weak-nexus but defensible conditions remain as obs O1 (reclass.report_lag_cap now counts facility letters, settle_window, own_notice_days, cycle_completion.due_margin_days and confirm_link_days, mailed.crediting_window_days, return.notice_age_days).

### findings (r2) — status of round-1 charter REDs
- C1 CLOSED: absence clock is the borrower's own departure (task 0: 2026-01-01). It is never moved later by another borrower, consistent with 24 CFR 206.27(c)(2)(iii) and the base sentences.
- C2 CLOSED: no policy credits a certification to a year other than the due-date year, and cycle completion now exists as a scored write. On the task 1 terminal world the 2026 cycle is complete (see 1.md r2).
- C3 CLOSED: docstrings no longer state a numbering rule.
- C4 CLOSED (policy and tool removed). C5 CLOSED (all three members removed with their policies). C6 CLOSED (no payoff reads remain). O7 CLOSED (letters only on plans with supporting_document none, in every policy that reads them). O8 CLOSED (absence anchor rewritten).
- New charter-wide REDs: none. New observations: N1, N2, the call_numbering ladder-text omission, and the residual O1/O2/O3-type items above.

### closing_checklist (r2)
Written after the r2 reveal (2026-10-15T12:14:28Z); the r2 charter-global sections above were frozen before it.
- Files 0.md and 1.md each carry a revision_2 section. The r1 text is untouched (apart from the r1 timestamp-correction note recorded in r1).
- Scope: GT charter_scope equals the auditor's pre-reveal partition (task 0 = reclass, absence_start, facility, call_in; task 1 = return_contact, return, mailed_form_standing, cycle_completion). The two scopes are disjoint and cover all 8 policies. Task tools are 4 + 4, closed, with independent uuid8s.
- Trees: task 0 has 3 prerequisite problems (2 VI + 1 SG) and task 1 has 3 (3 VI). Each has a user-owned write; the difficulty-wide graph is acyclic.
- Arithmetic: every expected value, baseline_result and per-factor figure in both tasks equals the auditor's recomputation.
- Round-1 REDs: C1, C2, C3, C4, C5 and C6 are all CLOSED, and T1-1..T1-4 are closed by removal or fix. Nothing regressed in task 0. No new charter-wide RED was found.
- Open: task 1 SOURCE-CHAIN RED T1-r2-1 (persona opening names the return problem's outcome), a user_scenario-only defect. Obs N1, N2, N3 and O1/O2 are non-blocking.
- Instantiation gates: the coordinator's snapshot_r2 is the gate record; this audit did not re-run them.

VERDICT revision_2: task0=PASS task1=SOURCE-CHAIN RED charter=CLEAN

## revision_3

### entry (r3)
- Gate: `tail -1 tasks/residency_occupancy_certification/worklog.md` = "REWORK round 3: gates 7/7 green". snapshot.sh was executed (nothing else under /tmp/erl0064_coord was read) and wrote snapshot_r3.txt (2026-10-15T12:52:21Z).
- Gates: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. Traceability misses are only the unlock tool names (non-tool_name misses 0). validate_scenario INVALID: re-run via erlbench.validate.validate_scenario, all 28 errors are "required document ... not found", 8 of them this difficulty's extended policies (pre-render). No gate red counts as a RED. Side effect of that run: the error list printed other difficulties' required-document ids (names only, no content); nothing else of theirs was read.
- Hash comparison r3 vs r2: extended yaml 48b6ef0eaa1c669b (unchanged), task_tools.py d3216d18b8d8a889 (unchanged), 0.json 1450db130a827983 (unchanged), 1.json a25b8a2805b7cf9d (changed from ef6cb33ef0a8c00f).
- Per the re-derivation rule, every charter-global section of revision_2 (conflict scan, rule/compute equivalence, action binding and uuids, prerequisite graph and sentences, override declarations, factor ladders, findings) is carried forward by reference on the grounds of the two unchanged shared hashes. Task 0 per-task sections are carried forward on the unchanged 0.json hash. Only task 1 is re-judged.

### findings (r3)
- No charter-wide RED (carried from r2). Obs N1, N2, N3, O1 and O2 unchanged.

### closing_checklist (r3)
Written after the r3 reveal (2026-10-15T12:53:51Z).
- 0.md and 1.md each carry revision_3. The earlier revisions are untouched.
- Scopes are disjoint and complete; tools are 4 + 4 with independent uuid8s; both trees have 3 prerequisite problems, enough value_input edges and a user-owned write, and the graph is acyclic. Every GT figure in both tasks equals the auditor's recomputation (task 0 per r2, unchanged hash; task 1 recomputed in r3).
- All round-1 and round-2 REDs are closed (C1-C6, T1-1..T1-4, T1-r2-1). There is no regression and no new defect. The instantiation gates were re-run by snapshot.sh (r3): all green apart from the pre-render required-document errors and the unlock tool-name traceability misses.
- Non-blocking observations: N1, N2, N3, O1, O2.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### entry (r4)
- Worklog tail = "REWORK round 4: gates 7/7 green". `/tmp/erl0064_coord/snapshot.sh residency_occupancy_certification 4` was executed (nothing else under /tmp/erl0064_coord was read) and wrote snapshot_r4.txt (2026-10-15T18:15:21Z).
- Gates: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK, and TRACEABILITY is now OK. validate_scenario INVALID, carrying the same required-document class as r3 (pre-render).
- Hash comparison r4 vs r3: extended yaml 52ba47940a176357 (was 48b6ef0e…), task_tools.py 609d0dfe8f51e699 (was d3216d18…), 0.json 70a85b30de60af58 (was 1450db13…), 1.json 88b1300082e819f6 (was a25b8a28…). Everything changed, so every section is re-derived in full; nothing is carried by reference.
- Inputs read this round: render_source/residency_occupancy_certification/render_r1.md and render_source/XF_recipe.md (coordinator-supplied), the charter, the tools, the two masked views. Written before the r4 tasks/*.json were opened. Scratch evaluator in /tmp/audit_residency_occupancy_certification_0064/ (check_compute semantics).
- Self-disclosure: four of the findings below (R4-1 members return.redate_anchor_on_return and mailed.standing_rule, R4-2 member pattern, and the r2 facility.early_answer obs) concern structures that already existed in r2/r3 and that this auditor passed then. They are reported now rather than carried as passed.

### structure (r4)
- Base section still byte-identical. Same 8 policies and tools. computes changed: reclass and return now compute `response_days` (an integer). Their tools take response_days and set due = today + days via a _Calendar helper; the docstrings say exactly that.
- Graph unchanged: reclass <- absence (SG) <- facility (VI) <- call_in (VI); return_contact <- return (VI) <- mailed (VI) <- completion (VI). Acyclic. Six policy_source sentences are verbatim in their own rules. Every compute_basis quote is verbatim in its own rule (script sweep).
- Factor counts (m/p): reclass 6 (1/5), absence 4 (1/3), facility 6 (1/5), call_in 5 (2/3), return 5 (1/4), mailed 4 (1/3), completion 4 (1/3), return_contact 5 (1/4). Cross-difficulty hecm factors are present in reclass, absence, facility, call_in, return, completion and return_contact.

### render_r1 items (r4)
1. **Assembly class: CLOSED in form for all 8 policies.**
   - Additive policies (reclass, facility, call_in, return, return_contact): each states its combination once, generically, in its baseline paragraph. Examples: "the re-dating anchor plus the survivor allowance, the survivor allowance being the sum of the allowances this policy sets out"; "the scheduled contact number plus the numbers held for earlier contacts". The same paragraph defines every summand with its standard value ("Under the standard rule ... each zero days"). Each factor sentence replaces only its own quantity, and each factor moves the result on its own (solo, recomputed).
   - Gate policies (absence, mailed, completion): the gate sentence ("Every continuity / standing / completion limit is met when ...") names only quantities the baseline defines with defaults (anchor or departure date; each window zero days). Each limit factor's sentence reads alone ("The transfer window is ... days where ...").
   - Judgement on the accepted gate design: sound under the skill's tests. The skill demands removal-weight, not solo movement, and every limit factor bears weight on its task world (below). The factor documents can be written without naming another factor; only the gate sentence in the computation document lists the baseline quantities. The cost is that a factor alone never moves the result, so these documents read as "relief window, effective only when every window is met". That is a stated design choice, not a defect.
2. **Retired-clause deferral: CLOSED.**
   - mailed now keeps only "the acceptance of the form and the signer's role and channel" from base and restates the recording/year clause.
   - completion restates the due-date move in its own text and defers only "when a cycle counts as complete ... and the return of a pending or overdue profile to current", which is not retired.
   - return restates "the profile becomes current and the absence_start_date is cleared".
   - All replaced_by texts restate the out-of-scope content and say "under this policy" (no "fixed below").
3. **Negative-lag branch: CLOSED where it existed.** The four r3 ladders are rewritten or removed.
   - Each new lag reads its negative case explicitly: report lag "a notice received before that date counting as received on it"; letter lag, mailed form, return notice and closing grace similarly; completion form receipt via MX.
   - Remaining literal-only cases (obs): absence_start corroboration (contact before admission) and own-notice (receipt before admission). Both pass "no more than" in rule and compute alike, so the readings agree; neither is stated as a branch.
4. **Minors: CLOSED.** The open_absence_monitoring docstring has no effect beyond the body; the tie sentence appears once in absence_start; return's replaced_by no longer claims "within response_grace_days of ... its confirmation".

### new findings (r4)
- **R4-1 SOURCE-FACTOR RED: ladder conditions that hold of every customer reaching the write, leaving fewer than three reachable tiers or a redundant scope clause.** Complete member list:
  - (a) reclass.redating_anchor: tiers 1-2 both require "an accepted death notice is on file", which base death_notice_on_file makes true at every reclassification. The fall-through ("no accepted death notice") is unreachable, so only 2 tiers remain.
  - (b) reclass.report_allowance_days: same; the "no accepted death notice" fall-through is unreachable, so 2 tiers.
  - (c) return.redate_anchor_on_return: tier 1 "the borrower's confirmation is recorded" holds at every return write (the rule's own prerequisite sentence "The return is not recorded until the borrower's own confirmation ... stands on the profile"). Tiers 2-3 are unreachable, so 1 tier.
  - (d) call_in.count_from: tier 3 ("no check-in and no absence start date") is unreachable for a check-in made during monitoring, and tier 2's "profile carries an absence start date" part restates scope. 2 tiers.
  - (e) return_contact.count_from_anchor: the rule scopes the closing contact to "while the profile is still under monitoring", so the absence start date always exists. Tier 3 is unreachable and tier 2's start-date clause restates scope. 2 tiers.
  - (f) mailed.standing_rule: the "profile shows no health-care absence under monitoring" clause in tiers 1-2 holds at every write (the rule's own prerequisite sentence). All three tiers stay reachable through their other clauses; the clause restates scope.
  - Obs only: facility.early_answer_days tier 3 ("no accepted notice about the primary borrower") is reachable only in contrived base-producible worlds.
- **R4-2 SOURCE-FACTOR RED: two tiers of one ladder select the same outcome.** Members:
  - (a) facility.inspection_visit: tier 2 ("dated on or before the absence start date") and tier 3 ("no result recorded") both give 0.
  - (b) call_in.numbering_basis: tier 2 "the count of check-ins recorded" and tier 3 "zero where no check-in is recorded" select the same quantity on tier 3's domain (the count is zero there). The ladder has two methods.
- **R4-3 SOURCE-FACTOR RED: fall-through is not the baseline.** completion.due_window_days declares baseline `{due_window: 0}`, and the rule's standard paragraph says "the due-date window ... zero days". But the ladder's fall-through ("the profile monitors no HECM loan") is response_grace_days = 30, so no tier gives the standard value. Only member found (every other factor's fall-through equals its baseline; script check).
- **R4-4 SOURCE-POLICY RED: rule/compute mismatch on the facility-letter window (absent-record branch).** absence_start defines "A facility letter is an accepted supporting document ... received less than letter_window_months whole calendar months before the handling date", and its gate requires "a facility letter is on file". But `latest_letter_day` reads the latest accepted supporting document with no window.
  - Probe (task 0 world after reclass, both letters re-dated to contact 2024-08-20 / received 2024-09-01): the rule gives no facility letter, the limits fail and the start is 2026-01-29; the compute gives 2026-01-01.
  - Same unwindowed read in facility (`letter_contact_day`/`letter_received_day`): obs only, because without a current facility letter the policy has no contact to number. call_in late grace "cites a facility letter" does not re-test the window: obs.
- **R4-5 SOURCE-POLICY RED: floor placement admits two readings.** call_in: "The check-in number is the numbering basis plus the scheduled contacts that fell due since the count-from date, at least one." "At least one" can bind the scheduled contacts (compute: basis + MX(1, s)) or the check-in number (basis + s, floored at 1).
  - Probe (task 0 world, facility check-in #6 dated 2026-10-01, handled 2026-10-14): s = (13 - 21 - 21) // 28 = -2, so the compute gives 7 and the second reading gives 4.
  - facility ("plus one, and never less than one" inside the scheduled-number definition) and return_contact ("and never fewer than one" on the scheduled contacts) place the floor unambiguously; call_in is the only member.
- Realism (no RED): the reclass/return re-dating anchors (death-notice receipt vs date of death; borrower confirmation) and the allowances are proprietary-schedule items with plausible nexus. Weak-nexus obs O1 continues: settling period by death-notice recency, documented-return allowance, payment allowances.

### charter line (r4, pre-reveal)
charter = R4-1, R4-2, R4-3, R4-4, R4-5. Round-3 status: no RED was open at r3; the r3 items stay closed (C1 departure anchor, C2 year/completion coherence, C3 docstrings), no regression.

### closing_checklist (r4)
Written after the r4 reveal (2026-10-15T18:22:44Z); the r4 charter section above was frozen before it.
- GT matches the auditor's blind derivation item for item in both tasks: writes, scopes, closures, every expected / baseline / per-factor figure. Scopes are disjoint and complete; trees are valid (3 problems; 2 or 3 value_input edges; user-owned write; acyclic). The gates (snapshot_r4) are green apart from the pre-render required-document class.
- render_r1 items 1-4: closed across the class (see §render_r1 items (r4)). The accepted gate design for absence_start, mailed and completion is sound under the skill.
- Not closed: R4-1 (scope-restating or unreachable ladder tiers: reclass x2, return anchor, call_in count_from, return_contact count_from, mailed monitoring clause), R4-2 (coinciding tiers: facility.inspection_visit, call_in.numbering_basis), R4-3 (completion due_window fall-through != baseline), R4-4 (absence_start unwindowed letter read; probe 2026-01-01 vs rule 2026-01-29), R4-5 (call_in floor placement; probe 7 vs 4).
- Non-blocking obs: N3; literal negative lags in absence_start; facility unwindowed letter read (out of scope); facility.early_answer tier 3; O1.

VERDICT revision_4: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED charter=R4-1,R4-2,R4-3,R4-4,R4-5

## revision_5

### entry (r5)
- Worklog tail = "REWORK round 5: gates 7/7 green". snapshot.sh round 5 was executed (nothing else under /tmp/erl0064_coord read) and wrote snapshot_r5.txt (2026-10-15T20:14:24Z).
- Gates: all seven OK, including TRACEABILITY. validate_scenario INVALID: re-run via erlbench.validate, 20 errors, all "required document ... not found" (pre-render). No gate RED.
- Hash comparison r5 vs r4: extended yaml f031b01f938b5fd0 (was 52ba4794…), changed. task_tools.py 609d0dfe8f51e699, 0.json 70a85b30de60af58 and 1.json 88b1300082e819f6 are unchanged. The charter-global sections are re-derived; persona and tool checks are carried from r4 on the unchanged hashes. Scored values are recomputed because the charter changed.
- Written before the r5 tasks/*.json were opened. Base section still byte-identical.

### round-4 REDs (r5)
- **R4-1 CLOSED across the class; every listed ladder now has three reachable tiers:**
  - (a) reclass.redating_anchor: primary has an absence notice -> notice receipt; no notice and death on or after the due date -> date of death; otherwise (death before the due date) -> reclassification date. The death-notice clause is gone from the tiers; an absent death notice is a stated fallback ("the handling date stands in for both").
  - (b) report allowance: <= 30 days / 31-90 / later still.
  - (c) return anchor: confirmation more than 14 days after the notice receipt / receipt more than 7 days after the return date / return date. All reachable with a confirmation always present.
  - (d) call_in.count_from: latest check-in / notice receipt when received more than 45 days after the start / start.
  - (e) return_contact.count_from_anchor: same shape as (d).
  - (f) mailed: the "no absence under monitoring" clause is removed from the anchor tiers.
  - The r4 obs facility.early_answer is rebased on recorded check-ins (none / latest cites a document / latest cites none) and is now fully reachable.
- **R4-2 CLOSED.** inspection_visit is 2/1/0 by results within inspection_window_months. call_in numbering basis is now highest number (latest check-in cites a document) / one (no check-in) / count (latest cites none): three distinct methods, with fall-through = baseline (count).
- **R4-3 CLOSED.** completion due window is 60/45/0, fall-through 0 = baseline 0.
- **R4-4 CLOSED.** absence_start reads the latest letter only when it was received within letter_window_months (`latest_letter_day` gated by the window), matching the rule's definition. facility reads its letter through the same window (`letter_in_window`), which also closes the r4 obs.
- **R4-5 CLOSED.** call_in: "... and never fewer than one; that floor applies to the scheduled contacts before they are added to the numbering basis".

### XF / render_r1 closures re-checked (r5)
- Mechanical sweep, 8 of 8 policies:
  - every compute_basis quote, prerequisite sentence, baseline.rule and replaced_by text is verbatim in its own rule;
  - every compute binding has a basis;
  - no ladder has duplicate outcomes;
  - every value-ladder fall-through equals its factor baseline, and the method-ladder fall-throughs equal their baselines on their own domains.
- Combinations are stated once, generically (additive sum or the generic gate sentence). Baselines define every quantity with a default. No replaced_by points at "fixed below" or defers to a retired clause.
- Negative-lag branches are now stated wherever a lag is read, including absence_start ("A letter contact date or a notice receipt earlier than the facility admission date counts as zero days after it") and completion ("An anchor date before the return date, or a latest contact before the anchor date, counts as zero days after it"); both are MX-clamped in compute.
- Same-day ties: every policy reads with LATEST (3-8 sites each), and every rule carries "Where two records share the date a reading is ordered by, the one entered first is read." exactly once. LATEST keeps the first-entered row among equal keys, so the reading matches.
- Gate-policy design (absence, mailed, completion) still sound, as judged in r4.

### new findings (r5)
- No new RED.
- Obs (non-blocking): the facility inspection number now counts any occupancy inspection result within 6 months, including one dated before the absence start. This is a proprietary choice with weak nexus; on task 0 the only result (2026-04-17) falls after the start. O1 weak-nexus items and N3 persist.

### charter line (r5, pre-reveal)
charter = CLEAN.

### closing_checklist (r5)
Written after the r5 reveal (2026-10-15T20:17:00Z).
- GT matches the auditor's blind recomputation in both tasks, item for item. Scopes are disjoint and complete, and the trees are valid (3 problems; 2 or 3 value_input edges; a user-owned write in each). The graph is acyclic.
- R4-1 through R4-5 are closed across their classes. The XF recipe points and the render_r1 items still hold. Same-day tie rules are stated in all 8 policies. The snapshot_r5 gates are green apart from the pre-render required-document class.
- Open: none. Non-blocking obs: N3, O1, and the facility inspection-window nexus.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### entry (r6)
- Worklog tail = "REWORK round 6: gates 7/7 green". snapshot.sh round 6 was executed (nothing else under /tmp/erl0064_coord read) and wrote snapshot_r6.txt (2026-10-15T21:21:06Z).
- All seven gates OK, including TRACEABILITY. validate_scenario INVALID with 6 errors, all "required document ... not found" (re-run via erlbench.validate). No gate RED.
- Hash comparison r6 vs r5: extended yaml 9ed9b2776c089587 (was f031b01f…), changed. task_tools 609d0dfe…, 0.json 70a85b30… and 1.json 88b13000… are unchanged. Base section still byte-identical.
- Inputs read this round: render_source/residency_occupancy_certification/render_r2.md, the charter and the views. Written before the r6 task JSONs were opened.

### render_r2 items (r6)
1. **return_redating tier-1 receipt: CLOSED.** The compute now reads `return_received = MX(return_day, <latest receipt>)`, so the confirmation-gap test and the receipt anchor both use the receipt as the rule defines it.
   - Probe: task 1 world after the closing contact, with the return notice re-dated to return 2026-11-10 / received 2026-11-01 and the confirmation on 2026-11-20.
   - The receipt is read as 2026-11-10 (10 days <= 14), so the anchor is the return date 2026-11-10. That is the rule's reading; r5's compute would have given the confirmation date.
2. **call_in prerequisite effect text: CLOSED.** It now reads "the numbering basis is one (the opening of monitoring held as the first contact)", matching rule and compute.
3. **return contact allowance zero branch: CLOSED.** It now reads "... and zero days where only one is (the borrower's own confirmation) or none is"; the ladder's fall-through says the same.
4. **completion punctuation: CLOSED.** It now reads "... to the next closing anniversary. A cycle's completion date ...".

### same-class sweep (r6): every "received before ... counting as received on it" / "counts as zero days" clause against every compute use of that receipt
- reclass: the clamp is scoped to the report allowance only; `report_lag = MX(0, ...)`. The re-dating anchor uses the raw receipt, and the rule's death-notice definition carries no clamp. Consistent.
- absence_start: "a letter contact date or a notice receipt earlier than the facility admission date counts as zero days"; both uses are MX-clamped. Consistent.
- facility: the letter clamp is now also applied to the date itself (`letter_received_day = MX(contact, receipt)`), not only to the lag. The same-class member is closed.
- mailed: the form receipt is MX-clamped. The return notice in this rule carries no clamp sentence and is read raw. Consistent.
- completion: the form receipt is MX-clamped, and both link tests are MX-clamped as stated.
- return_contact: the return-notice clamp applies to "the return notice" (most recent) and is used only through `return_lag = MX(0, ...)`. The return-notice-number count reads each notice's receipt, as its own sentence states.
- call_in: no clamp sentence; the raw notice receipt is used as stated.
- Mechanical re-sweep of all 8 policies: quotes, prerequisite sentences, baseline.rule and replaced_by are verbatim; every binding has a basis; no duplicate tier outcome; fall-through = baseline; the tie rule appears once per policy.

### findings (r6)
- No new RED. No regression of R4-1 to R4-5 or of the render_r1 closures (re-swept). Obs unchanged: N3, O1, facility inspection-window nexus.

### charter line (r6, pre-reveal)
charter = CLEAN.

### closing_checklist (r6)
- After the reveal (2026-10-15T21:22:26Z), both tasks' GT equals the auditor's recomputation item for item. All render_r2 items are closed, the same-class sweep is clean, and nothing regressed. Gates are green apart from the pre-render required-document class.
- Open: none. Obs: N3, O1, facility inspection-window nexus.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
