# Policy-task audit — domain_renewals_and_transfers / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-22, auditor = independent erl-task-policy-audit agent (not the instantiator). Written before any task GT was revealed; nothing below derives from a revealed GT field.
- Hashes (sha256, re-verified by the auditor): `domain.extended.yaml` fe8893a6dd23540e754a97874f97542f6b8395c230262382ff049e9074edfde7; `task_tools.py` cfdb5331d2fc85dfe0b13720d052daa60ddef642719b856922f806554cb6ee24; views 0.view 050bef7f…ba04, 1.view af6bc5ae…baba (both match the brief).
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/domain.yaml (base copy compared key by key with the extended file's base section: all 10 keys identical), products/account|hosting|email|ssl.yaml (parameters and multi-holding rules only, for cross-category pricing checks), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (build_env/eval_compute semantics: COUNT/SUM/LATEST scoped to the holding, `within_months` = 0 <= MONTHS(row, NOW) < n, MONTHS counts a month only once its day is reached, CFIELD/CPARAM = first matching row).
- Masked / unread until both derivations were frozen: tasks/*.json, plan.md, worklog.md, every evaluation_criteria / computations / closure / rationale / required_documents field. No recursive grep touched the tasks directory.
- Entry conditions (Step 0): gate snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r1.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views and hashes supplied. check_traceability deferred by the coordinator (not run). Entry conditions met.

### policy_conflict_scan
Eight extended policies (P1..P8):
- P1 `domain_ext_lapsed_registry_year` (grace renewal ≥ 2025-12-01, tool bill_grace_renewal_b28bd74d, agent)
- P2 `domain_ext_auto_renew_overbilling` (correction refund of the latest auto-renew line billed < 2025-12-01, refund_auto_renew_overbilling_9a8c47ae, agent)
- P3 `domain_ext_grace_line_overbilling` (same for the latest grace line, refund_grace_renewal_overbilling_eac8310e, agent)
- P4 `domain_ext_maximum_term_extension` (max-term extension of an active domain not restored that day, pay_domain_term_extension_84339760, user)
- P5 `domain_ext_redemption_restore_price` (restore ≥ 2025-12-01, bill_redemption_restore_c1eb5c46, agent)
- P6 `domain_ext_transfer_line_overbilling` (correction of the transfer-in line, refund_transfer_in_overbilling_a01c5ca4, agent)
- P7 `domain_ext_restore_line_overbilling` (correction of the latest restore line, refund_restore_overbilling_617b9b9c, agent)
- P8 `domain_ext_restore_day_extension` (max-term extension on a restore day, pay_restore_extension_years_823e7992, user)

Overlaps found: (a) the "stays under the rule that governs it, which bills the TLD's renewal_price per year plus the icann_fee_per_year per year" tails of P1/P4/P8 (and P5's restore tail) describe sibling extended cases and historical charge dates with a price that contradicts P1, P4, P5, P8 and the correction prices of P2, P3, P7 — finding C1/C2; (b) the correction gates of P1 and P5 quantify more broadly than their resolvers reach — C3; (c) P4/P8 split extensions by "restore charge dated the day of the order" — exclusive and exhaustive for active domains billed ≥ 2025-12-01; (d) refund destination, rollback and window departures of P2/P3/P6/P7 are declared (C5/C6 list the gaps). Triggers: every tool writes only domain_charges/domain_holdings; base triggers that leave the category (account_credit_apply / account_credit_refund) fire only on account_credit payment or destination, which no tool writes — trigger rule (XF 20) holds. Cross-category reads (hosting, account, email, ssl) are read-only and declared in each `cross_category`.
Scope partition (derived, to be compared after reveal): task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6, P7, P8}; pairwise disjoint and jointly covering all eight policies.

### rule_compute_equivalence
- Mechanical sweep (`/tmp/audit_domain_renewals_and_transfers_0076/sweep.py`): every `compute_basis` quote of every policy is verbatim in its rule; every baseline.rule sentence is verbatim in the rule; every compute binding has a basis.
- Rounding: `int(x*100+0.5)/100` half-up placements match "rounded half up to the cent" in each component sentence; final `RND` follows the stated order sentence in P1, P2, P3, P4, P5, P6, P7, P8. Order sentences (credits floored at zero, then fees, then make-good) match compute.
- Windows: "less than 12 / 24 whole months … a month counting only once its day of the month is reached" == `within_months` / `MONTHS(...) < n`; late-fee / early-restore day counts == `DAYS` with inclusive `<=`.
- Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa (checked per policy).
- Departures: P4 extension-years formula vs its own "greatest whole number" sentence (C4); first-match certificate read vs the rule's OV/EV-first ordering (C7); zero-amount branches with no rule tier (C8).

### action_binding_and_uuids
- Eight `(target_tool, computes)` pairs, each claimed by exactly one policy. uuid8s b28bd74d, 84339760, 9a8c47ae, eac8310e, a01c5ca4, 617b9b9c, c1eb5c46, 823e7992 — no shared prefix/suffix, no sequence; read as independently generated.
- Tool bodies check no policy condition (only positive amount / years ≥ 1 / row exists), each write calls ctx.create/ctx.update in its own body, half-up helper is a pure static method, no composite string args, no concrete example values in docstrings, no factor id is a substring of a tool name (swept).
- Docstrings carry no before/after/first/then; `pay_restore_extension_years_823e7992` says "on the day it is restored" (observation O3).

### prerequisite_graph
- Every policy has `prerequisite` (P2, P3, P6, P7 = []). Edges: P1→P2 (value_input, late_fee), P1→P3 (state_gate), P4→P1 (value_input, ext_years), P5→P7 (value_input, restore_fee), P5→P6 (state_gate), P8→P5 (value_input, rx_years). All `problem` ids are extended policies of this file, no self edge, graph acyclic (two disjoint trees).
- All six `policy_source` texts verbatim in the blocked policy's own rule (swept); all `form: state`, no fallback_reason; `resolved_by` = the depended-on policy's target_tool; value_input gates name real compute bindings (late_fee, ext_years, restore_fee, rx_years). Conditions mirror the sentences (no strengthening); the breadth mismatch between those sentences and the resolvers is C3.

### prerequisite_sentences
- E1 (P1←P2) "The late reactivation fee … is fixed only after every over-billing on the domain's most recent auto-renew charge stands as a correction refund against that charge." — "only after"; record-visible state (refund line against the charge); no tool/id. Single writer: P2's refund. Derivation: sentence → look for a policy whose rule books a correction refund against an auto-renew charge → P2.
- E2 (P1←P3) "A grace-period renewal is not billed until every grace-period renewal charge already on the domain that was billed above the price its charge date set carries its correction refund." — "not … until"; state; single writer P3.
- E3 (P4←P1) "A maximum-term extension is priced only after the domain's status reads active, its extension years being counted from the expiry date the domain then carries." — state; for a domain in grace only P1's write sets active (P5's restore needs redemption and a restored-today domain is outside P4's scope).
- E4 (P8←P5) "Restore-day years are priced only after the domain's status reads active again and a restore charge dated the day of the order stands on it …" — state; single writer P5.
- E5 (P5←P7), E6 (P5←P6) — same shape as E1/E2; single writers P7/P6.
- No rule restates another problem's sentence, names a tool or a policy id; no undeclared cross-problem order sentence found. Breadth defect: C3.

### override_declarations
Sentence-by-sentence against `base_policy_refs` (findings only; consequences in task files):
- P1: retires domain_renewal_pricing S1 (real conflict: late fee) and S-tier/bulk (real: reseller-only discount), domain_grace_renewal "It is billed at…" (real), domain_auto_renew "An auto-renew charge may be attempted only while… active or on_hold" (no conflict — C5). Tail omits grace renewals billed before 2025-12-01 and misdescribes sibling cases (C1, C5). Inherited and followed: min years, new expiry from current expiry, max-years refusal, grace window, DNS parking, bulk exclusion of grace lines.
- P2: retires domain_refunds full-amount (real), auto-renew window (real), rollback (real), destination (real), new-registration refund window (no conflict — C5); does not retire "a TLD whose window is 0 never refunds that charge type" (C6) nor any pricing sentence fixing what an auto-renew line cost (C2).
- P3: as P2 for grace lines (C5, C6, C2).
- P4: retires domain_renewal_pricing S1 and tier/bulk (real), domain_grace_renewal eligibility S1 and window S2 (no conflict with an active-domain extension — C5); "ordered for one domain at a time" sits beside an un-retired domain_agg_bulk_renewal (O6).
- P5: retires domain_redemption_restore pricing sentence (real); tail fixes the price of every other restore (C2 vs P7).
- P6: retires full-amount (real), transfer refunded only on cancellation (real), destination (real), new-registration window (no conflict — C5), domain_purchase_pricing "while transfers, bundled lines and the ICANN fee are never discounted" (real for its scope, but nothing restated for bundled lines / ICANN / other transfers — C5); does not retire "An inbound transfer is billed once at the TLD's transfer_in_price plus one icann_fee_per_year" (C2).
- P7: retires full-amount, both "restore charge is never refund(ed|able)" sentences, destination (real), new-registration window (no conflict — C5).
- P8: retires domain_renewal_pricing S1 and tier/bulk (real); tail as C1.

### factor_ladders
| policy | factors (effect, cross_difficulty) | param / method | multi-source | notes |
|---|---|---|---|---|
| P1 | hosting_rate (P, hosting), reseller_pct (P, account), mailbox_part (M, email), certificate_part (P, ssl), autorenew_part (P), late_fee (M) | 4 / 2 | hosting_rate (status ∧ term), autorenew_part (setting ∧ decline count), late_fee | all tiers in rule; all ladders ≥3 distinct outcomes |
| P2 | hosting_rate (P), reseller_pct (P), mailbox_credit (M), certificate_credit (P), funding_saver (P) | 4 / 1 | hosting (opened ∧ status ∧ term) | funding_saver fall-through unreachable in scope — C9 |
| P3 | as P2 (payment_credit) | 4 / 1 | hosting | payment_credit — C9 |
| P4 | hosting_rate, reseller_pct, mailbox (M), certificate, term_step (M), winback | 4 / 2 | hosting | all tiers reachable in scope |
| P5 | fee_courtesy (M), hosting_rate, mailbox (M), certificate, lapse, notice_makegood | 4 / 2 | hosting, lapse, courtesy | makegood is ICANN ERRP-based (real) |
| P6 | companion (P), mailbox (M), certificate (P), payment_credit (P) | 3 / 1 | companion | payment_credit — C9 → 3 surviving factors |
| P7 | hosting_rate (P), mailbox (M), certificate (P), payment_credit (P) | 3 / 1 | hosting | payment_credit — C9 → 3 surviving factors |
| P8 | hosting_rate, mailbox (M), certificate, lapse, term_step (M), retention | 4 / 2 | hosting | term_step, retention — C9 |
Method shape test (XF 6): mailbox (per-seat × count vs flat vs none), term_step (per-year × years vs flat vs none), late_fee (waived vs flat vs per-day capped), fee_courtesy (waived vs min(restore_fee, early fee) vs restore_fee) each add an input or an operation — honest `method` labels. Factor independence (XF 1): no factor binding reads another factor's binding (term_span recomputes the month count from fields; line_years / ext_years are plain bindings). Cross-difficulty reads: hosting, account, email, ssl (per policy as tabled).

### findings
Each finding: verdict — symptom — root cause — evidence — demonstrated consequence — artifact/location. Task demonstrations live in 0.md / 1.md.

**C1 — SOURCE-POLICY RED (overwrite tails misprice sibling extended cases).** Symptom: the out-of-scope restatements in P1, P4 and P8 state that the cases their siblings govern "stay under the rule that governs it, which bills the TLD's renewal_price per year plus the icann_fee_per_year per year". Evidence: P1 OW#1/#3 replaced_by and rule S1: "every manual renewal, extension order, restore and auto-renew charge stays under the rule that governs it, which bills the TLD's renewal_price per year plus the icann_fee_per_year per year…"; P4 OW#1/#3/#4 and rule S1: "every grace-period renewal, restore, restore-day extension and auto-renew charge stays under the rule that governs it, which bills the TLD's renewal_price per year plus the icann_fee_per_year per year…"; P8 OW#1 and rule S1: "every grace-period renewal, restore, maximum-term extension of a domain not restored that day and auto-renew charge stays under the rule that governs it, which bills…renewal_price per year plus the icann_fee_per_year per year". Against: P1 (grace price = component − credits + ICANN + late fee), P4/P8 (extension price with hosting rate and credits), P5 (restore fee + restored-year component − credits − make-good). Consequence: for each sibling write two readings exist — the sibling's own formula or the tail's "renewal_price per year plus ICANN" — with different amounts (task 0: P1, P4; task 1: P5, P8; figures in the task files). Artifact: P1/P4/P8 `overwrite[*].replaced_by` and the first sentence of each rule. Bears on tasks 0 and 1.

**C2 — SOURCE-POLICY RED (undeclared override: correction policies redefine the price past charge dates set).** Symptom: P2, P3, P6, P7 declare a line "over-billed" relative to "the price its charge date set", which each defines by its own ladder (hosting rate, reseller discount, mailbox/certificate/payment credits), for charges billed before 2025-12-01. The pricing sentences in force for those charges say otherwise and are not retired for them: base domain_purchase_pricing "An inbound transfer is billed once at the TLD's transfer_in_price plus one icann_fee_per_year." (in force; P6 retires only the no-discount clause); P5 tail "every other restore stays under the rule that governs it, which bills the restore_fee plus restore_includes_renewal_years at the renewal_price plus the icann_fee_per_year for each of those years" (vs P7); P1/P4/P8 tails "…auto-renew charge stays under the rule that governs it, which bills the TLD's renewal_price per year plus the icann_fee_per_year per year" (vs P2), P4/P8 tails "every grace-period renewal …" (vs P3); domain_auto_renew "Each attempt renews auto_renew_term_years at the price set by domain_renewal_pricing" (not retired). Root cause: no overwrite names the pricing sentence that fixed what those historical lines cost. Consequence: whether a correction refund is owed at all, and its amount, has two or three readings (task 0: P2, P3 and through E1 P1's late fee; task 1: P6, P7 and through E5 P5's restore fee). Artifact: P2/P3/P6/P7 overwrite lists and rules.

**C3 — SOURCE-POLICY RED (gate sentences broader than their resolvers).** E2: "every grace-period renewal charge already on the domain that was billed above the price its charge date set carries its correction refund" and E1: "every over-billing on the domain's most recent auto-renew charge"; E5/E6 the same for restore and transfer lines. The resolvers correct only "the domain's most recent … charge, where it was billed before 1 December 2025, less than 24 whole months before the day of the correction and paid by card or PayPal", and "nothing is refunded" / no price is defined outside that scope. Demonstration (producible world): a .com domain in grace whose most recent grace line was over-billed 25 months ago (or paid from account credit, or an older over-billed grace line behind a newer one): P3 gives no correction, the E2 state can never hold, so P1 "is not billed" ever and the customer's renewal has no solution; alternatively the reader takes "over-billed" as undefined outside P3's scope and bills — two conclusions in one situation. Same for P5 via E6 (transfer line 24+ months old) and E5. Artifact: P1/P5 rule gate sentences, P2/P3/P6/P7 scope sentences. No task world hits it (both task worlds' lines are in scope; task 1's transfer line is at 23 whole months).

**C4 — SOURCE-POLICY RED (P4 extension-years counting contradicts its own maximum).** P4: "A maximum-term extension renews the greatest whole number of years that keeps the new expiry date no more than max_registration_years after the day of the order" vs "The extension years are counted as max_registration_years times 12, less the whole months from the day of the order to the expiry date…, divided by 12 and rounded down" (compute `(120 - MONTHS(NOW, expiry)) // 12`), and inherited base "A renewal is refused if its new expiry date would lie more than max_registration_years after today's date." World: active .com, order 2026-10-22, expiry 2028-11-01 → whole months 24 → formula 8 years → new expiry 2036-11-01, 10 days beyond 2036-10-22; the first sentence gives 7 years (2035-11-01). Two answers (7 vs 8 years, different amount). Artifact: P4 rule sentences 2–3 and compute ext_years/term_span. P8 carries the same pair; within P8's scope the whole-month count is always 9–11, so it is an observation there. No task world hits it.

**C5 — SOURCE-POLICY RED (XF 15: overwrites that retire nothing real / omit in-force content).** Members, all in one pass: (a) retiring clauses that do not conflict: P1 OW#3 (domain_auto_renew status sentence), P2 OW#5, P3 OW#5, P6 OW#5, P7 OW#5 (new-registration refund window), P4 OW#3 and OW#4 (grace-renewal status and window sentences). (b) replaced_by not restating still-in-force content: P1 OW#2, P4 OW#2, P8 OW#2 retire "The renewal_price component of every renewal line is reduced by the domain_renewal_discount_pct … a manual multi-domain order may instead receive the bulk discount…" and restate only their own component, while their tails say out-of-scope renewals bill "renewal_price per year plus the icann_fee_per_year per year" — for a reseller's ordinary manual or auto-renew line this contradicts the un-retired domain_agg_bulk_renewal ("When the customer's account tier also grants a domain_renewal_discount_pct … the single higher of the two percentages applies") and the account charter meaning of domain_renewal_discount_pct ("Percent off the renewal_price component of manual domain renewals and auto-renew charges"): Gold reseller, one-year .com manual renewal = 17.98×0.92 → 16.54 + 0.20 = 16.74 vs 18.18. P6 OW#3 retires "while transfers, bundled lines and the ICANN fee are never discounted" with a replaced_by about correction refunds, leaving bundled lines, the ICANN fee and out-of-scope transfers without their no-discount sentence. P1 OW#1/#4 retire the grace-renewal price sentences wholesale and no tail restates them for grace renewals billed before 2025-12-01. Artifact: the listed overwrite entries.

**C6 — SOURCE-POLICY RED (XF 17: undeclared departure from a zero-window sentence).** Base domain_refunds: "Each window adds whole calendar days to the charge date…; a TLD whose window is 0 never refunds that charge type." P2 and P3 retire only the auto-renew and renewal window sentences and then refund auto-renew / grace lines "at any time while the charge was billed less than 24 whole months before the day of the correction" for every TLD, including .ca, .co, .io whose auto_renew_refund_days and renewal_refund_days are 0. World: .io domain, over-billed auto-renew line 3 months old → base: never refunded; P2: correction refund. Artifact: P2/P3 overwrite lists. No task world hits it (.com, .net).

**C7 — SOURCE-POLICY RED (XF 10: first-match certificate read vs rule ordering).** All eight policies read the certificate tier with `CPARAM('ssl','validation_level', domain_id=HID, status='active')` (and P2/P3/P6/P7 a separate `CFIELD(... 'opened_date' ...)`), i.e. the first matching row. The rules say "certificate_credit_validated where an active … OV or EV product covers this domain, certificate_credit_dv where the active subscription covering it is on a DV product". The ssl charter allows several live subscriptions on one name ("several subscriptions may cover the same name"). World: an active DV and an active OV subscription both with domain_id = this domain, DV row first → compute takes the DV tier, rule takes the OV tier (e.g. P1 credit 0.50 vs 1.00). Artifact: cert_level/cert_open bindings of P1–P8. No task world hits it (one certificate each).

**C8 — SOURCE-POLICY RED (XF 22: zero-amount writes).** P1, P4, P5, P8 floor `component − credits` at zero and the mailbox credit (mailbox_credit_per_seat × seats, up to 300 seats) is uncapped; on an ICANN-free TLD the amount reaches 0.00 with no rule tier for it, while the schema says charges are positive and every billing tool rejects amount ≤ 0. World: .io domain in grace, annual hosting (year price 49.98), M365 with 200 seats (credit 50.00), late fee waived → P1 = 0.00 → the grace renewal cannot be booked, and P4's prerequisite (status active) can never be brought about. Similar for P5 (.io, fee waived, 200 seats, make-good). Artifact: P1/P4/P5/P8 result bindings and mailbox ladders; tool bodies. No task world hits it. (Zero extension years in P4/P8 are refused by the inherited min_renewal_years sentence — observation O7.)

**C9 — SOURCE-FACTOR RED (ladders whose fall-through no in-scope customer can reach).** (a) Payment credits: P2 `charge_funding_saver`, P3 `grace_line_payment_credit`, P6 `transfer_line_payment_credit`, P7 `restore_line_payment_credit` — each policy's scope requires the line to be "paid by card or PayPal" and returns 0 otherwise, so the fall-through "nothing where it was paid any other way" (= the factor baseline) is never applied to any customer who reaches the write; only two live tiers. (b) P8 `restore_day_retention` — P8's scope requires "a restore charge dated the day of the order", so "two or more / exactly one restore charge … less than 24 whole months" always counts at least that charge; the fall-through/baseline is unreachable (also an invented count ladder, XF 18). (c) P8 `restore_day_term_step` — within P8's scope the restored expiry is always 9–11 whole months ahead (grace 25–30 days plus at most 30 redemption days, plus one restored year), so the restore-day years are always 9 on the order: only the "5 or more" tier is live; "3 or 4" and the baseline are unreachable. Consequence: these factors' baselines are treatments no in-scope customer receives (straw-man baselines); struck from the count, P6 and P7 keep 3 factors each (below the floor of 4), P2/P3/P8 keep 4. Per-task effect in 0.md / 1.md.

**Observations (not grounds for rework).**
- O1 Realism: the same credit family (mailbox 0.25/seat or 0.75 flat, certificate 1.00/0.50, card/PayPal saver 0.40/0.20, lapse/auto-renew credit, win-back 2.00/1.00) recurs in all eight policies; plausible as a Harborline bundle/autopay schedule, not demonstrated unreal. The "per-year price = transfer_in_price for a 1-month hosting plan" reuses a price column as a companion rate — plausible as a company schedule, not demonstrated unreal. ICANN fee 0.20 and the post-expiry-notice make-good (ERRP 5-day notice) are real.
- O2 Base event trigger domain_refund → domain_expiry_update (charge_type renewal/auto_renew/grace_renewal) remains in the events section while P2/P3 say a correction refund "leaves the expiry date where it stands"; the rule sentence is retired, the event mapping is not.
- O3 `pay_restore_extension_years_823e7992` docstring "on the day it is restored" ties the tool to the restore event (not an ordering word; distinguishes it from the P4 tool).
- O4 "A domain is never billed two such charges on one day" is a framing claim the LATEST tie-break relies on; true of the charter's own write paths.
- O5 The blueprint summary says the agent books renewals; P4/P8 make the extension payment the customer's own write (persona supplies that authorisation).
- O6 P4 "ordered for one domain at a time" beside un-retired domain_agg_bulk_renewal.
- O7 P4/P8 give 0 years / 0.00 when the expiry is already ≥ 109 whole months ahead; the inherited "A renewal must be for at least min_renewal_years whole years" refuses it, so no second answer.
- O8 Claimed event types domain_auth_code_issue, domain_settings_update, domain_registrant_change, domain_agp_delete, domain_transfer_out_decision are used by no extended policy.

## closing_checklist
Not reached in revision_1: both tasks carry REDs (0.md T0-R1..R4, 1.md T1-R1..R4) and the charter carries C1–C9. Facts confirmed after the reveal that the closing checklist will need: per-task files 0.md / 1.md correspond to tasks 0 / 1; scopes {P2, P3, P1, P4} and {P6, P7, P5, P8} are pairwise disjoint and jointly cover all eight extended policies; each tree has 3 prerequisite problems, 2 value_input edges, one owner=user write, no cycle, and the whole difficulty's prerequisite graph is acyclic; GT values and factor_sensitivity figures equal the auditor's independent recomputation in both tasks. Instantiation gates were not re-run by this audit (coordinator snapshot r1 cited in charter_global_frozen).

Task bearing of charter findings: C1, C2, C5, C9 → tasks 0 and 1 (demonstrated in their files); C3, C4, C6, C7, C8 → charter only (demonstrated on producible worlds above; no task world reaches them).

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9

---

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-22 before any revision_2 task GT was opened; same independent auditor. Entry: worklog tail `REWORK round 2: gates 7/7 green` confirmed; gate snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r2.txt` (run by the auditor via snapshot.sh, source not read) shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; check_traceability not run.
- Hashes: `domain.extended.yaml` baea533334b35288b1d87ce3e797c9bfee1aa178a9b058eec9982bc0ba75f51e; `task_tools.py` 928ce4fcc3129a186fe582b158ae8cd963535d18043248f963bbaabb967da618; 0.view acf91987…14d7; 1.view 503d1fda…9dac. Both shared inputs changed → every charter-global section re-derived in full below (revision_1 text kept above, untouched).
- Read: the reworked charter (base section re-compared with products/domain.yaml: identical), tools, the "REWORK round 2 claims" section of worklog.md only (lines 1–33; item ids and one-line claims), blueprint products (hosting/account parameters for price checks). Masked until freeze: tasks/*.json, plan.md, the rest of worklog.md (nothing beyond line 33 exists).

### policy_conflict_scan (revision_2)
Eight extended policies: P1 `domain_ext_lapsed_registry_year` (grace renewal ≥ 2025-12-01, bill_grace_renewal_b28bd74d); P2 `domain_ext_grace_line_price_match` (refund_grace_renewal_price_match_8c76edf7); P3 `domain_ext_manual_line_price_match` (refund_manual_renewal_price_match_6ed19e80); P4 `domain_ext_maximum_term_extension` (pay_domain_term_extension_84339760, user); P5 `domain_ext_redemption_restore_price` (bill_redemption_restore_c1eb5c46); P6 `domain_ext_transfer_line_price_match` (refund_transfer_in_price_match_5d5ebe85); P7 `domain_ext_restore_line_price_match` (refund_restore_price_match_9ee6604c); P8 `domain_ext_restore_day_extension` (pay_restore_extension_years_823e7992, user). Price matches (P2, P3, P6, P7) refund the difference between a 2022-01-01..2025-11-30 card/PayPal line and its "Domain Care price" computed with today's records; they no longer redefine what a historical line cost. Pricing tails of P1/P4/P8 now name the sibling rules. Overlaps found: refund tails of P2/P3/P6/P7 (N1), tier discount inside the Domain Care price of transfer and restore lines (N2). Trigger rule: tools write only domain_charges/domain_holdings with card / original_payment_method → no cross-category trigger fires. Derived scopes: task 0 {P1, P2, P3, P4}, task 1 {P5, P6, P7, P8}.

### rule_compute_equivalence (revision_2)
Mechanical sweep re-run (`sweep.py`): every compute_basis quote and every baseline sentence verbatim in its rule; every binding has a basis; no factor id inside a tool name. Year counting (P4/P8): `(120 − whole months − (1 if days of month differ)) // 12` with `mx_exact = MONTHS(a,b)+MONTHS(b,a)==0` — equals "greatest whole number keeping the new expiry within max_registration_years" on every input (checked: 2028-11-01 vs 2026-10-22 → 7; same-day → exact; month-end Jan 31 → Feb 28 → correct); zero years bill nothing by rule and compute. Order sentences, floors and rounding match compute in all eight. Hosting reads filter status active (one live plan per primary domain under hosting_agg_multi_holding); no first-match certificate or mailbox read remains.

### action_binding_and_uuids (revision_2)
Eight (tool, computes) pairs, one policy each; new uuid8s 8c76edf7, 6ed19e80, 5d5ebe85, 9ee6604c independent of each other and of the four kept ones. Tool bodies check only positive amount / years ≥ 1 / row existence; half-up static helper; docstrings carry no ordering words or example values (O3 "on the day it is restored" unchanged).

### prerequisite_graph (revision_2)
Edges: P1←P2 value_input lr_late_fee; P4←P1 value_input mx_years; P4←P3 state_gate; P5←P7 value_input rs_fee; P5←P6 state_gate; P8←P5 value_input rx_years. All policy_source verbatim in the blocked rule (swept); form state; resolved_by = target tools; gates are real bindings; acyclic, two disjoint trees.

### prerequisite_sentences (revision_2)
Each price-match sentence now carries exactly its resolver's scope ("most recent … charge, where it was billed from 1 January 2022 through 30 November 2025 by card or PayPal above its Domain Care price, carries its price-match refund") — single writer each. P4 "priced only after the domain's status reads active": for a grace domain only P1's write; P8 "status reads active again and a restore charge dated the day of the order": only P5's write.

### override_declarations (revision_2)
- P1: retires domain_renewal_pricing S1 (real: late fee) and domain_grace_renewal "It is billed at …" (real); tail restates tier/bulk/ICANN for every other renewal and names P4/P8 — closed. P4, P8: retire S1 only, tails name siblings — closed. P5: retires the restore price sentence and "no account-tier or bulk discount applies to any part of it" (real for its scope), tail restates both for other restores.
- P2/P3/P6/P7 each retire seven/eight domain_refunds clauses; genuine for their own line type: full-amount, destination, rollback (P2/P3), own window (P2/P3: manual-or-grace window; P2/P3 zero-window), transfer-on-cancellation (P6), restore-never (P7, both sentences). Not genuine (no conflict with the line type the policy refunds): listed in N3.

### factor_ladders (revision_2)
| policy | factors (P = parameter, M = method) | years variable within scope |
|---|---|---|
| P1 | reseller_pct P (account), hosting_credit P (hosting), plan_allowance M (hosting), volume_credit P (account), autopay_credit P, late_fee M | fixed 1 ("renews exactly one year") |
| P2 | reseller P, hosting_credit P, plan_allowance M, volume P, term_credit M | variable (pre-Dec grace lines may be multi-year) |
| P3 | as P2 | variable |
| P4 | reseller P, hosting_credit P, plan_allowance M, volume P, autopay P, term_step M | variable |
| P5 | fee_courtesy M, reseller P, hosting_credit P, plan_allowance M, volume P, notice_makegood P | fixed 1 (restore_includes_renewal_years = 1 on every TLD) |
| P6 | reseller P, hosting_credit P, plan_allowance M, volume P | fixed 1 (transfer_in_years_added = 1) |
| P7 | reseller P, hosting_credit P, plan_allowance M, volume P | fixed 1 |
| P8 | reseller P, hosting_credit P, plan_allowance M, volume P, autopay P, price_lock M | fixed 9 on every in-scope order (restored expiry is always 9–11 whole months ahead) |
All fall-throughs reachable in scope (payment, retention, win-back and restore-day term ladders removed); ladders ≥ 3 distinct outcomes; multi-source: hosting_credit (status ∧ term), price_lock (acquisition ∧ date), late_fee/courtesy; cross-difficulty: hosting, account. Realism: bundle/plan/volume/autopay credits, transfer price lock, late fee, early-restore waiver and ERRP make-good are plausible registrar schedules (O1 closed); the volume thresholds equal the Bronze/Silver deposit minimums (observation O9).

### findings (revision_2)
Round-1 items:
- **C1** pricing tails — closed (P1/P4/P8 tails name the sibling rules and restate base tier/bulk/ICANN for every other renewal). The same class persists in the refund tails — **N1** below (members missed in revision_1: the round-1 correction policies' tails had the same shape; disclosed here).
- **C2** — closed (no historical price is redefined; base pricing sentences remain true of the matched lines).
- **C3** — closed (gate sentences = resolver scope).
- **C4** — closed (verified on the counterexample and month-end inputs).
- **C5** — partly closed ((b) restatements fixed; transfer no-discount clause no longer retired); (a) persists — **N3**.
- **C6** — closed (zero-window sentence declared superseded for the price matches and restated).
- **C7** — closed. **C8** — closed (largest per-year credit sum 9.00 < smallest discounted per-year component 10.54; smallest restore ≥ 3.04; zero years bill nothing). **C9** — closed (all fall-throughs reachable).

New / persisting REDs:

**N1 — SOURCE-POLICY RED (sibling refund tails, XF 15/16).** The out-of-scope sentence of each price match — "Every other refund stays under the rule that governs it, which returns the full amount of one original charge … refunds only within the charge type's refund window … refunds an inbound transfer charge only when the transfer is cancelled, never refunds a restore charge …" (P2, P3, P6, P7 rule S2 and OW#1/#2) — covers the three sibling price matches and states for them content they contradict: P2's tail makes P3's manual-line refund a full refund inside a 5-day window (i.e. none for a 2022 line); P3's tail does the same to P2; P6's tail says a restore charge is never refunded (vs P7); P7's tail says a transfer charge is refunded only on cancellation (vs P6). No tail names its siblings. Consequence: two readings of each scored price-match refund and, through E1/E5, of P1's late fee and P5's restore fee (task files). Artifact: P2/P3/P6/P7 rule S2 + OW#1/#2. Bears on tasks 0 and 1.

**N2 — SOURCE-POLICY RED (undeclared departure, XF 17).** P6: "The Domain Care component of a inbound transfer charge is the TLD's transfer_in_price times the years the charge covered, reduced by the transfer line's reseller discount" vs in-force base domain_purchase_pricing "…while transfers, bundled lines and the ICANN fee are never discounted" (deliberately no longer retired) and the account charter meaning of domain_renewal_discount_pct ("Percent off the renewal_price component of manual domain renewals and auto-renew charges"). P7: the Domain Care component of a past restore "reduced by the restore line's reseller discount" vs P5's own tail "every other restore … with no account-tier or bulk discount on any part of it" and base "no account-tier or bulk discount applies to any part of it". Consequence: for any reseller account two Domain Care prices (with / without the tier percentage) → two refund amounts (task 1). Artifact: P6/P7 component sentences. (P5 applying the renewal discount to its own restored year is declared against the domain base; the account charter's parameter meaning still excludes restores — observation O10.)

**N3 — SOURCE-POLICY RED (XF 15 non-conflicting retirements, persisting from C5(a)).** All members: P2 OW#2 (new-registration window) and OW#7 (auto-renew window); P3 OW#2, OW#7; P6 OW#2 (new-registration), OW#5 (manual-or-grace window), OW#6 (auto-renew window), OW#7 (zero-window — transfer lines have no window); P7 OW#2, OW#6 (manual-or-grace), OW#7 (auto-renew), OW#8 (zero-window — restore lines have no window). None of these clauses governs the line type the policy price-matches; restating them in the tail does not make the retirement genuine.

**N4 — SOURCE-FACTOR RED (mislabelled method — constant multiplier, XF 6).** "plan_allowance_premium for each year" vs "the flat plan_allowance_standard once" (and P8's price lock "for each of the restore-day years" vs "once") differ in shape only through the years variable; where the policy's scope fixes that variable, both tiers are constants and the factor is a parameter. Members: lapsed_year_plan_allowance (P1, years ≡ 1), restored_year_plan_allowance (P5, ≡ 1), transfer_line_plan_allowance (P6, ≡ 1), restore_line_plan_allowance (P7, ≡ 1), restore_day_plan_allowance and restore_day_price_lock (P8, ≡ 9). Consequence: P6, P7 and P8 have no honest `method` factor (floor: 1 per computation); P1 and P5 keep late_fee / fee_courtesy. Artifact: factor `effect` labels and ladders. (Ladder text typo "the year the charge covereds" in P2/P3/P6/P7 plan_allowance ladders — observation O11.)

Observations (revision_2): O3, O5, O8 unchanged; O2 closed (corrections removed, rollback superseded only for P2/P3); O4 kept as the stated tie rule; O6/O7 closed; O9 volume-credit thresholds coincide with tier minimums (overlaps the reseller discount); O10 P5 restored-year tier discount vs account parameter meaning; O11 ladder typo; O12 duplicate bindings gl_term_span/ml_term_span/mx_term_span restate the years binding (XF 2 shared selection stated twice in compute, once in rule).

## closing_checklist (revision_2)
Not reached: N1–N4 open. Confirmed: scopes {P2, P3, P1, P4} / {P6, P7, P5, P8} disjoint and complete; each tree 3 prerequisite problems, 2 value_input, one customer write, acyclic; GT equals the independent recomputation in both tasks, factor figure by figure. Task bearing: N1 → tasks 0, 1; N2 → task 1; N3 → charter (P2/P3/P6/P7 overwrite lists); N4 → tasks 0 (P1) and 1 (P5–P8).

VERDICT revision_2: task0=RED task1=RED charter=N1,N2,N3,N4

---

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-22 before any revision_3 task GT was opened; same auditor. Entry: worklog tail `REWORK round 3: gates 7/7 green`; snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r3.txt` (run by the auditor, source not read): all 7 gates OK. check_traceability not run. Owner writes judged by `audits/render_source/owner_ruling.md`.
- Hashes: `domain.extended.yaml` f4871daf1c26f191b18fc25fa8e96ccade62e459e292e4540b4e2dd378fc8f22; `task_tools.py` 893226a28e7e8704908ec88e02e545ab3af89c756d3fdc91122f99888931e958; 0.view 05c710c3…0607; 1.view 5fce49f4…f029. Both shared inputs changed → charter-global sections re-derived; base section still identical to products/domain.yaml. Read of worklog limited to the "REWORK round 3 claims" section (lines 35–53).

### policy_conflict_scan / rule_compute_equivalence / action_binding / prerequisite graph and sentences (revision_3)
- Same eight policies, tools and edges as revision_2 (P1←P2 value_input, P4←P1 value_input, P4←P3 state_gate, P5←P7 value_input, P5←P6 state_gate, P8←P5 value_input); all policy_source verbatim; gate sentences now read "… by card or PayPal and earns Domain Care credits, carries its price-match refund", which is exactly the resolvers' scope ("nothing is refunded where those credits come to zero").
- Price matches now refund "the charge's Domain Care credits, never more than the amount billed", credits read from today's records; no reseller discount, no repricing of the matched line. Restore (P5) carries no tier discount. P4/P8 state the holder pays at Harborline's secure checkout after the agent's quote, never to the method on file; both user tools take an enum `checkout_method` (paypal / new_card), enforced in the body.
- Sweep re-run: compute_basis and baseline sentences verbatim; every binding has a basis; no factor id in a tool name; docstrings without ordering words or example values. Year counting, zero-year rule, rounding, order sentences unchanged and correct.
- Owner ruling (b): no base product-charter sentence assigns manual-renewal billing to the agent (base lifecycle names the agent only for grace→active and redemption→active, which stay agent writes), so no overwrite is required; both extension rules state the checkout act; both personas show the in-person need (task 0: the card on file was declined, pays via PayPal; task 1: card on file near its limit, pays with a card not on file). Accepted.

### override_declarations (revision_3)
P2/P3 retire full-amount, destination, manual-or-grace window, zero-window, rollback — each governs a renewal-type line; P6 retires full-amount, destination, transfer-on-cancellation; P7 full-amount, destination, both restore-never sentences. No non-conflicting retirement remains. P1/P4/P8 retire base S1 with sibling-naming tails; P5 retires the restore price sentence with its tail restating base for other restores.

### factor_ladders (revision_3)
| policy | factors | methods |
|---|---|---|
| P1 | reseller P, hosting P, plan_allowance M, volume P, autopay P, late_fee M | 2 |
| P2, P3 | hosting P, plan_allowance M, volume P, autopay P, term M | 2 |
| P4 | reseller P, hosting P, plan_allowance M, volume P, autopay P, term_step M | 2 |
| P5 | fee_courtesy M, hosting P, plan_allowance M, volume P, autopay P, notice_makegood P | 2 |
| P6, P7 | hosting P, plan_allowance M, volume P, autopay P | 1 |
| P8 | reseller P, hosting P, plan_allowance M, volume P, autopay P, price_lock P | 1 |
plan_allowance premium tier = (TLD price − registration_price) per year: two tariff inputs added → passes the XF 6 shape test where the years are fixed (recipe: "a tier PASSES if it adds … tariff parameter"); flat once; none. price_lock relabelled parameter (honest: years ≡ 9 in scope). All fall-throughs reachable in scope; multi-source hosting (status ∧ term), autopay (setting ∧ declines); cross-difficulty hosting, account. Bound check: largest per-year credit sum (.org/.io: 3.00 + 7.00 + 0.50 + 0.50 + 4.00 lock or 0.60 term) stays below the smallest discounted per-year component of that TLD (.org Platinum 16.70); smallest restore with waived fee stays positive (.us 1.98) — C8 still closed.

### findings (revision_3)
Round-2 items: **N1 closed** (every price-match tail names its three siblings as set by their own rules). **N2 closed** (no tier or transfer/restore discount in any price match; P5 restore undiscounted). **N3 closed** (only own-line clauses retired). **N4 closed** under the recipe's tariff-input rule (see table).
Sweep of every class raised in revisions 1–3 across all eight policies: C1/N1 sibling tails — clean; C2 historical repricing — clean; C3 gate breadth — clean; C4 year counting — clean; C5/N3 overwrite hygiene — clean; C6 zero-window — clean; C7 first-match reads — clean (hosting filtered active, unique by base); C8 zero amounts — clean (bounds above); C9 unreachable fall-throughs — clean; N2 discount on undiscountable lines — clean; N4 constant-multiplier methods — clean under the recipe. One new member of the XF 9 edge class:

**N5 — SOURCE-POLICY RED (XF 9: negative edge with no rule tier; XF 18 realism).** P6: "The transfer line's plan allowance is the TLD's transfer_in_price less its registration_price for each year the charge covered where the active … plan is a Harborline Business, Harborline Cloud 4 or Harborline Cloud 8 plan, the flat plan_allowance_standard once … where that active plan is a Harborline Starter, Harborline Plus or Harborline Pro plan". For .co, transfer_in_price 28.98 < registration_price 29.98, so the premium "allowance" is −1.00 per year: it reduces the credits, and a Business/Cloud customer earns less than a Starter customer. Probe (`r3/probe_co.py`, task-1 world switched to .co): Cloud 8 → allowance −1.00, refund 2.45; Starter → +0.75, refund 4.20. No rule sentence floors the allowance or gives a tier for a negative difference, and no registrar publishes a negative "allowance". Artifact: P6 plan-allowance sentence and tl_plan. No task world reaches it (.net). Every other tariff difference used (renewal − registration on all seven TLDs, renewal − transfer for the lock) is ≥ 0; the lock is 0 on .us across all tiers (observation O14, T2 holds on other TLDs).

Observations (revision_3): O3 (docstring "on the day it is restored"), O5 closed by the owner ruling, O8 unchanged; O9 closed (thresholds 250 / 5,000); O10 closed; O11 closed; O12 kept (duplicate years binding in term factors); O13 task 0 persona authorises the agent's grace renewal on the card it says was declined for the auto-renewal; O14 .us price lock zero; O15 price-match baseline is "no refund" (credits only, params []) — definite and differs from gold, accepted.
- O16 (after reveal): stale revision-2 figures/wording remain only inside the dated revision-2 history blocks of both design_rationale texts; O17 every plan_allowance ladder's value text adds "(the year is priced at the first-year registration price)", a phrase no rule sentence carries (for the price matches it reads as repricing a past line; no scored value changes) — observation.

## closing_checklist (revision_3)
- Per-task files 0.md / 1.md and this file carry revisions 1–3; both task comparisons PASS in revision_3; GT equals the independent recomputation figure for figure in both tasks.
- Scopes {P2, P3, P1, P4} / {P6, P7, P5, P8}: disjoint, covering all eight extended policies; tools closed; uuid8s independent.
- Trees: 3 prerequisite problems, 2 value_input edges, one owner=user write (accepted under the owner ruling, checkout_method entailed by each persona), acyclic; whole-difficulty graph acyclic.
- Factors: every computation 4–6 factors with ≥ 2 parameter and ≥ 1 method; multi-source and cross-difficulty (hosting, account) factors in both tasks; every factor bears weight; baselines definite and different from gold.
- Gates: re-run on the final form by the coordinator snapshot r3 (7/7 OK).
- Open: N5 (charter-only, no task world reaches it). The difficulty does not pass the source-layer audit until N5 is closed.

VERDICT revision_3: task0=PASS task1=PASS charter=N5

---

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-22 before revision_4 GT; same auditor. Entry: worklog tail `REWORK round 4: gates 7/7 green`; snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r4.txt` (run by the auditor): 7/7 OK; check_traceability not run.
- Hashes: `domain.extended.yaml` 5f172eb9d7b8bb4a157903b6cfe5b716e2d2e412ab070b3d75e8a00eef7d99f9 (changed); `task_tools.py` 893226a2…e958 (unchanged from revision_3); views 05c710c3…0607 and 5fce49f4…f029 (unchanged). Charter re-derived by full diff against the revision_3 dump (`r3/dump.txt` vs `r4/dump.txt`): the only changes are the eight plan-allowance sentences / bindings / ladders and the restore-day price lock; everything else is byte-identical, so the remaining revision_3 charter-global conclusions carry forward on that diff. Tool-module sections carry forward on the unchanged tools hash. Worklog read limited to "REWORK round 4 claims" (lines 55–61).

### changes verified
- Plan allowance (P1–P8): rule "the amount by which the TLD's [renewal|transfer_in]_price exceeds its registration_price, for each … year, … that amount being never less than plan_allowance_standard for each … year, also where the … price does not exceed the registration_price" ↔ compute `MX(K('plan_allowance_standard'), P(..) − P('registration_price')) * years` — one reading, equivalent. Ladder texts restate it; the "(the year is priced at the first-year registration price)" phrase is gone (O17 closed).
- Restore-day price lock (P8 only — the claim's "both extension policies" is inexact; P4 has no lock): "the amount by which the TLD's renewal_price exceeds its transfer_in_price … and nothing otherwise or where the renewal_price does not exceed the transfer_in_price" ↔ `MX(0, renewal − transfer) …` — equivalent.
- Mechanical sweep: compute_basis and baseline sentences verbatim; every binding based; policy_source of all six edges verbatim; no factor id in a tool name.
- Probe (`r3/probe_co.py` re-run): .co transfer line, Cloud 8 → allowance 0.75, refund 4.20; Starter → 0.75, refund 4.20 — no negative allowance and no premium-below-standard inversion. On .co transfer lines (years ≡ 1) the premium and standard tiers coincide numerically (observation O18; the tiers differ on every other TLD/line, T2 holds).

### findings (revision_4)
- **N5 closed.**
- Sweep of every class raised in revisions 1–4 across all eight policies (C1/N1 sibling tails, C2 historical repricing, C3 gate breadth, C4 year counting, C5/N3 overwrite hygiene, C6 zero-window, C7 first-match reads, C8 zero amounts — bounds re-checked with the floored allowance, the largest per-year credit sum still below the smallest discounted per-year component of its TLD and the smallest restore positive —, C9 unreachable fall-throughs, N2 discounts on undiscountable lines, N4 constant-multiplier methods, N5 negative tariff differences — the remaining subtractions (component − credits, fee + component − make-good, billed vs credits) are floored or capped by their rules; days-late / red-days / notice-lag are non-negative in scope or tiered): no member found.
- Observations unchanged: O3, O8, O12, O13, O14, O15, O16; new O18 (above). O17 closed.

## closing_checklist (revision_4)
- Per-task files carry revisions 1–4; both revision_4 comparisons PASS; GT equals the independent recomputation figure for figure in both tasks.
- Scopes {P2, P3, P1, P4} / {P6, P7, P5, P8} pairwise disjoint and jointly covering all eight extended policies; task tools closed; uuid8s independently generated and frozen.
- Each tree: 3 prerequisite problems, 2 value_input edges, one owner=user write accepted under the owner ruling (b), no cycle; the difficulty's prerequisite graph is acyclic.
- Every computation: self-sufficient baseline, 4–6 factors with ≥ 2 parameter and ≥ 1 method, ladders ≥ 3 distinct tiers stated in full in the rule; per task multi-source and cross-difficulty (hosting, account) factors; every factor bears weight; baseline numbers definite and different from gold.
- Instantiation gates re-run on the final form: snapshot r4, 7/7 OK.
- All four relationships PASS for both tasks; no open charter finding. The difficulty passes the source-layer audit.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

---

## revision_5

## charter_global_frozen (revision_5)
- Frozen 2026-10-22 before revision_5 GT; same auditor. Entry: worklog tail `REWORK round 5: gates 7/7 green`; snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r5.txt` (run by the auditor): 7/7 OK; check_traceability not run. Inputs audited: renderer findings D1–D2 in `audits/render_source/domain_renewals_and_transfers/render_r1.md`; XF_recipe points 28–29 (added during env_0076).
- Hashes: `domain.extended.yaml` 74aa45414f06c34a412593411d1d9c9d4c6169a76bda46c8452ed0501cc4fbd2 (changed); `task_tools.py` 893226a2…e958 and both views (05c710c3…0607, 5fce49f4…f029) unchanged. Full diff against the revision_4 dump: overwrites, prerequisites, factors and ladders byte-identical; changed are the eight rules' assembly / component / standard-computation sentences, the baselines, compute_basis pointers, and the rounding expressions. Base section still identical to products/domain.yaml.

### rule_compute_equivalence (revision_5)
- D2: every component now truncates `x + 0.5 + 1e-7` (cents) and every result rounds `RND(… + 1e-9)`; exhaustive check (`r5/round_check.py`: 7 renewal prices × 1–10 years × 0/3/5/8/12 %) — 0 mismatches against exact half-up (the old expression mismatched at .co and .io, 5 years, Silver). Residue within the epsilon is DSL-KNOWN (XF 28). Sweep: compute_basis and baseline sentences verbatim, every binding based, all six policy_source verbatim, no factor id in a tool name.
- D1: each credits total is now one generic sentence — e.g. P1 "The lapsed-year credits are the credits below that apply to the renewal, added together."; P2 "The Domain Care credits of a grace-period renewal charge are the credits below that apply to it, added together, …"; components say "the percentage discount that applies"; standard-computation sentences say "no discount and no credit applies" / "no credit and no make-good applies" / "no Domain Care credit applies to the charge, so nothing is refunded". Baselines are computable from their own sentences. D1 as raised by the renderer is closed — but see N6.

### findings (revision_5)
- **D1 closed** as stated (no assembly sentence lists factor quantities; baselines name none).
- **D2 closed** (verified exhaustively).

**N6 — SOURCE-POLICY RED (XF 13 "a factor's sentences name the result they modify"; consequence on the unique solution).** With the credits now defined only as "the credits below that apply … added together", a factor quantity belongs to the total only if its own sentence makes it a credit. The hosting, volume, autopay and term factors are named "… credit"; the reseller discount, late fee, restore fee and make-good are visibly not credits. Two factor quantities are named neither way and no sentence says what they modify:
- the plan allowance in all eight policies — "The lapsed-year plan allowance is the amount by which the TLD's renewal_price exceeds its registration_price …" (P1), and the same shape for "the grace line's / manual line's / maximum-term / restored-year / transfer line's / restore line's / restore-day plan allowance" (P2–P8);
- the restore-day transfer price lock (P8) — "The restore-day transfer price lock is the amount by which the TLD's renewal_price exceeds its transfer_in_price …".
A reader who takes "the credits" to be the quantities called credits leaves these out; one who treats an allowance / price lock as a credit adds them. Revision_4 listed them by name in the assembly sentence, so the rework that closed D1 opened this. Consequence: two amounts for every scored write (task files). Artifact: the plan-allowance sentences of P1–P8 and the price-lock sentence of P8, read against each generic credits sentence. Bears on tasks 0 and 1.

Class sweep (all classes raised in revisions 1–5, whole charter): C1/N1, C2, C3, C4, C5/N3, C6, C7, C8, C9, N2, N4, N5 — no member (overwrites, edges, factors and bounds unchanged from revision_4); D1/XF 29 — no factor-listing assembly sentence remains; D2/XF 28 — every half-up rounding carries the epsilon; XF 13 — N6 above (all nine members). Observation O19: "the credits below" is a positional reference that the per-factor KB documents cannot carry; it is the wording N6 turns on.

## closing_checklist (revision_5)
Not reached: N6 open (tasks 0 and 1). Unchanged and confirmed: scopes, trees, factor counts and weights, owner-ruling acceptance, gates 7/7 (snapshot r5), GT equal to the recomputation under the reading that counts allowance and price lock as credits.

VERDICT revision_5: task0=RED task1=RED charter=N6

---

## revision_6

## charter_global_frozen (revision_6)
- Frozen 2026-10-22 before revision_6 GT; same auditor. Entry: worklog tail `REWORK round 6: gates 7/7 green`; snapshot `/tmp/erl0076_coord/snap_domain_renewals_and_transfers_r6.txt` (run by the auditor): 7/7 OK; check_traceability not run.
- Hashes: `domain.extended.yaml` 684a4602774632c51eb07542a178debaef6257c3934ddcd77b5c5702abd89757 (changed); `task_tools.py` 893226a2…e958 and both views unchanged. Diff against the revision_5 dump: overwrites, prerequisites, compute, factors/ladders, baselines, params and cross_category byte-identical; only rule sentences and compute_basis pointers changed. Base section identical to products/domain.yaml. Worklog read limited to "REWORK round 6 claims".

### verification (revision_6)
- Each total now reads "the amounts this rule names as one of the … credits, added together" (no factor list — XF 29 kept), and each member names itself in its own sentence: "The lapsed-year plan allowance, one of the lapsed-year credits, is …", "The restore-day transfer price lock, one of the restore-day credits, is …", "The grace line's hosting credit, one of the charge's Domain Care credits, is …", etc.
- Mechanical check: number of self-named members per rule = number of terms in the compute credits binding — P1 4/4, P2 5/5, P3 5/5, P4 5/5, P5 4/4, P6 4/4, P7 4/4, P8 5/5; the reseller discount, late fee, restore fee and make-good carry no such clause and are outside the totals in compute. "credits below" appears in no rule (O19 closed). compute_basis/baseline quotes verbatim; all six policy_source verbatim; no factor id in a tool name.
- account_tier_benefits claim: consistent with revision_1–4 checks of the seeded rows (tier discounts on the renewal/term component only, tier as recorded on each charge date; no account-charter sentence overwritten).

### findings (revision_6)
- **N6 closed** (one reading of every credits total; XF 13 satisfied for all nine former members).
- Sweep of every class raised in revisions 1–6 across the whole charter (C1/N1, C2, C3, C4, C5/N3, C6, C7, C8, C9, N2, N4, N5, D1/XF 29, D2/XF 28, N6/XF 13): no member. Compute and factors unchanged from revision_5, so bounds, rounding and ladder conclusions carry forward.
- Observations unchanged: O3, O8, O12–O16, O18.

## closing_checklist (revision_6)
- Per-task files carry revisions 1–6; both revision_6 comparisons PASS; GT equals the independent recomputation figure for figure.
- Scopes {P2, P3, P1, P4} / {P6, P7, P5, P8} disjoint and complete; task tools closed; uuid8s independent and frozen.
- Trees: 3 prerequisite problems, 2 value_input edges, one owner=user write accepted under owner ruling (b), acyclic; difficulty graph acyclic.
- Computations: self-sufficient baselines, 4–6 factors (≥ 2 parameter, ≥ 1 method), full ladders in the rules, every factor bearing weight, baselines definite and ≠ gold; multi-source and cross-difficulty factors in both tasks.
- Gates re-run on the final form: snapshot r6, 7/7 OK.
- All four relationships PASS for both tasks; no open charter finding. The difficulty passes the source-layer audit.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
