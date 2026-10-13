# Policy-KB bijection audit — comfort_club_membership_care / task 1

Scope: product `plan`, extended policies `plan_ext_reinstatement_fee`, `plan_ext_reinstated_rate_lock`, `plan_ext_missed_visit_fee`, `plan_ext_reinstated_term_dues` (charter_scope of task 1), their base policies (`plan_reinstatement`, `plan_evt_missed_appointment`, `plan_dues_pricing`, `plan_renewal`, `plan_billing_collections`, `plan_tier_changes`, plus the eligibility/add-system/cancellation bases listed in `plan_ext_missed_visit_fee.base_policy_refs`), tier parameters read, and the four task tools. Corpus: 64 published plan docs (title/content view). Written after the runtime blind answer was frozen.

Entry conditions (Step 0), cited from the brief: policy-side PASS; `check_docs.py … plan` -> "DOCS OK"; `check_traceability.py …` -> "TRACEABILITY OK (2 tasks)", 1.json 24 copied / 0 missing; runtime view and DB path supplied. Complete.

## source_to_kb

### plan_ext_reinstatement_fee (tool `reinstate_lapsed_agreement_6e8e1b28`)
| Source atom | KB home | Judgement |
|---|---|---|
| Reinstated within grace at member's request: active, new term from day after lapsed term end, ends one day before same date 12 months later, count +1, same visit/benefit grants as the lapsed term incl. added systems | "Reinstating a Lapsed Comfort Club Agreement" (hub) §What reinstatement does | verbatim-equivalent |
| Leaves locked rate on file, posts no renewal dues; "the locked rate and the dues of the reinstated term are decided by the policies that settle them" | hub, same section + Basis questions | verbatim (source rule / overwrite replaced_by) |
| Fee 0.00 tiers: no fee, rules do not apply; otherwise computed at reinstatement from lapsed-term records | "Comfort Club Reinstatement Fee: Amount Charged" (computation) | equivalent |
| Baseline: lapse days; fee = adjusted × share + surcharge − courtesies, half up, floor 0, 0.00 posts no entry; adjusted = tier fee, share 1, others 0 | computation doc + order of working | complete; tier fee named -> "Term, Renewal and Reinstatement Schedule" |
| Factor `lapse_length_fee` (method): ≤7 none; 8–30 as is; >30 × days/30 rounded up to whole dollar | "Reinstatement Fee and the Length of the Lapse" | full ladder, rounding defined |
| Factor `tenure_fee_share`: ≥7 at lapse & no reinstatement fee ever: 0.5; ≥ loyalty count (3) not both: 0.8; else 1 | "Tenure Share of the Comfort Club Reinstatement Fee" | full ladder, compound condition intact |
| Factor `forfeited_visit_surcharge`: ≥2: 15; 1: 5; 0: 0 (lapsed-term no-show/late-cancel forfeits) | "Reinstatement Surcharge for Forfeited Tune-Ups" | full ladder |
| Factor `installation_customer_courtesy`: <12 m: 10; 12–<36 m: 5; else 0 | "Reinstatement Courtesy … Harbison Installation" | full ladder; names Replacement System Installations |
| Factor `protection_holder_courtesy`: 10-Yr P&L / 12-Yr Total / Total Plus: 10; other active: 5; none: 0 | "Reinstatement Courtesy … Protection Contract" | full ladder; names Harbison Protection Contracts |
| Tool contract (agent; fee posting billed to current month; receipt) | hub §System entry | equivalent |
| prerequisite `[]` | — | no prerequisite sentence carried for this policy | consistent |

### plan_ext_reinstated_rate_lock (tool `set_reinstated_rate_lock_0c66ac3f`)
| Source atom | KB home | Judgement |
|---|---|---|
| Tier with price lock; decided once for the reinstated term, written as the locked rate | "Comfort Club Price Lock for a Reinstated Term" (hub) | equivalent |
| Days since lapse (to day before current term start); locked = retained + surcharge − credits, half up, ≤ current first-system rate; baseline retained = current rate, others 0 | "Locked Rate of a Reinstated Comfort Club Term" (computation) | complete; ceiling stated |
| Factor `lock_retention` (method): ≤15 days keep; >15 & ≥6 terms incl. reinstated: locked + half difference half up; else current rate | "Price Lock Retention After a Lapse" | full ladder |
| Factor `maintenance_lock_surcharge`: 0 tune-ups in 12 m: 10; 1: 5; ≥2: 0 | "Locked-Rate Surcharge for Missed Maintenance" | full ladder |
| Factor `registration_lock_credit`: ≥12 yrs: 6; 10–11: 3; else 0 | "Locked-Rate Credit for Registered Manufacturer Parts Warranties" | full ladder; names Replacement System Installations |
| Factor `protection_lock_credit`: 10-Yr P&L / 12-Yr Total / Plus: 6; other active: 3; none: 0 | "Locked-Rate Credit … Active Protection Contract" | full ladder |
| Tool contract | hub §System entry | equivalent |

### plan_ext_missed_visit_fee (tool `post_missed_visit_fee_325d3ccb`)
| Source atom | KB home | Judgement |
|---|---|---|
| Forfeiting tier; no-show/late-cancel forfeit charged a fee on the dues ledger billed to the posting month; worked out when the most recent forfeit carries no fee | "Comfort Club Missed-Visit Fee on Forfeited Tune-Ups" (hub) | verbatim-equivalent |
| Fee = min(repeat-miss fee, tenure cap) − attendance reduction, forfeit treatment applied, floor 0; baseline repeat = tier fee, cap 1000 (no limit), reduction 0, treatment as is | "Comfort Club Missed-Visit Fee Amount" (computation) | complete; tier fee named -> "Tune-Up Appointment Terms" |
| Factor `repeat_miss_fee`: ≥3 forfeits in 24 m: +25; exactly 2: +10; else tier fee | "Missed-Visit Fee for Repeat Misses" | full ladder |
| Factor `tenure_fee_cap`: ≥84 m: 30; 48–<84: 40; else none | "Missed-Visit Fee Cap by Membership Tenure" | full ladder |
| Factor `attendance_reduction`: ≥4 tune-ups in 24 m: 5; 2–3: 3; else 0 | "Missed-Visit Fee Reduction for Kept Tune-Ups" | full ladder |
| Factor `forfeit_treatment` (method): latest late-cancel & ≥5 terms: half, down to whole dollar; latest late-cancel & <5: ×3/4, up to whole dollar; no-show: as is | "Treatment of Late Cancellations in the Comfort Club Missed-Visit Fee" | full ladder, "most recent forfeited visit" defined |

### plan_ext_reinstated_term_dues (tool `pay_reinstated_term_dues_c2f743bd`, owner user)
| Source atom | KB home | Judgement |
|---|---|---|
| Annual reinstated dues billed and paid in one payment for the reinstated term; fees billed separately; amount follows the gap rule | "Dues for a Reinstated Comfort Club Term" (hub); gap rule sentence in "Reinstated-Term Dues by Reinstatement Gap" | equivalent |
| Order: gross (first-system rate + additional rate × share per extra system); one combined discount taken once, half up; whole-term dues; baseline values (current rate, share 1, discounts 0) | "Reinstated-Term Dues: Gross Dues, Discount and Amount Billed" (computation) | complete; product figures named -> "Dues Rate Card" |
| Factor `price_lock_application` (method): locked < current & ≥60 m: locked; locked < current & <60: average half up; else current | "Price Lock and the First-System Rate of a Reinstated Term" | full ladder |
| Factor `new_installation_share`: contract signed <12 m: 0.6; 12–<36: 0.8; else 1 | "Additional-System Rate for Members with a Recent Harbison Installation" | full ladder |
| Factor `appointment_loyalty`: ≥7 terms & no missed-visit fee in 12 m: 8%; ≥ tier count (3) not both: tier %; else 0 | "Loyalty Discount on Reinstated-Term Dues and the Appointment Record" | full ladder; tier % table |
| Factor `trouble_free_discount`: none billed in 24 m: 3%; < 500.00: 1.5%; else 0 | "Trouble-Free Discount" | full ladder; line types defined |
| Factor `protection_bundle_discount`: bought with installation: 2%; other active: 1%; none: 0 | "Protection Bundle Discount" | full ladder |
| Factor `lapse_gap_proration` (method): gap >30 & ≥5 terms: × whole months / 12; gap >15 otherwise: × days through term end both counted / 365; else whole; each half up | "Reinstated-Term Dues by Reinstatement Gap" | full ladder; gap definition stated |
| Tool contract incl. payment_method enum | hub §System entry | equivalent |

### Prerequisites (five edges), each carried verbatim in the blocked policy's hub and nowhere else (exact-string sweep: one hit each)
| Edge | Form | Home of policy_source | Resolution basis | Strength/connective |
|---|---|---|---|---|
| term_dues -> reinstatement_fee | state | "Dues for a Reinstated Comfort Club Term" ("fixed only after the agreement shows active status with a term starting the day after the lapsed term ended") | reinstatement hub describes returning to active with the new term from the day after the lapsed term ended; record status `lapsed` | match |
| term_dues -> reinstated_rate_lock | action (declared fallback) | same hub ("not billed until the price lock for that term has been decided") | price-lock hub "decided once for the reinstated term and written as the agreement's locked rate" | match; action form is the source's declared form |
| term_dues -> missed_visit_fee | state | same hub ("not fixed until the dues ledger carries a missed-visit fee for every visit forfeited in the lapsed term") | missed-visit hub "charged a missed-visit fee on the agreement's dues ledger"; records: lapsed-term late-cancel forfeit without a fee | match |
| rate_lock -> reinstatement_fee | state | "Comfort Club Price Lock for a Reinstated Term" (+ same-form "Restated: …" in that doc) | reinstatement hub; record status | match |
| missed_visit_fee -> reinstatement_fee | state | "Comfort Club Missed-Visit Fee on Forfeited Tune-Ups" (+ same-form "In the same terms: …") | reinstatement hub; record status | match |
`condition`, `resolved_by`, `fallback_reason` have no home in any doc. The depended-on hub (reinstatement) carries none of the blocked sentences.

### Retired surface
- `plan_reinstatement` (3 overwrites across the extended policies: renew-as-automatic; flat fee; loses price lock): "Reinstatement Grace Window After a Lapse" §No longer in force lists all three; grace window and closure-after-grace carried in force.
- `plan_dues_pricing` (5 overwrites: loyalty reduction; annual first+additional; billed once in advance; lower-of locked/current; additional at catalogue): "Dues Pricing Rules" cl.1.1, 1.2, 4.1 (both items), 4.2 marked no longer in force; monthly billing, first monthly charge, autopay, web discount, monthly renewal, rounding and frequency-change clauses in force.
- `plan_evt_missed_appointment` (1 overwrite): "Missed and Late-Cancelled Tune-Ups" cl.4 no longer in force; cl.1–3, 5–6 in force.
No retired clause stated as in force, none vanished, none retired without a declared overwrite.

Tier figures read (Gold: first 249.00, additional 169.00, reinstatement fee 25.00, grace 45, missed fee 25.00, loyalty 5%/3 terms, price lock Yes, forfeits Yes) match the variant parameters exactly.

## kb_to_source
- Every normative prose claim in the 20 docs above traces to the source; clarifications checked as same-source derivations ("The forfeit being charged counts among them when it is dated within those 24 months"; "Day 15 is within the keep days"; boundary rows). The late-fee waiver sentence "the same calendar date one year earlier is not inside them" has its source in measure `plan_msr_late_fee_waivers_12m`.
- No added confirmation, review, notification or procedure.
- Cross-problem operational guidance: none; each task tool appears only in its own hub.
- Opening world state as policy fact: none (all examples hypothetical; no figure of this customer's records appears).

## bijection_verdict
**PASS.** First revision; no affected document.

Policy-side notes (do not change this verdict):
1. The loyalty factor's window "within the 12 months before the date of handling" is the source's own phrase; the compute counts a missed-visit fee posted on the date of handling (which is what makes the `due_loyalty_pct` edge bear weight). The KB renders the phrase unchanged; the visible reading that includes the date of handling is supported by the measure-derived convention in "Dues Ledger" ("The 12 months run back from the date of handling") and by the edge sentence itself. The source wording could be tighter; the blind audit reached the GT reading.
2. The `plan_dues_pricing` overwrites retire the annual-dues, billing-timing and renewal price-lock/loyalty clauses for the whole charter while their replacements are scoped to reinstated terms, so the corpus no longer states an in-force rule for ordinary annual enrollment and automatic-renewal dues. The KB renders this faithfully; it is a policy-side scope question.
3. The reinstatement rule (overwrite replaced_by, rendered verbatim) says "the locked rate and the dues of the reinstated term are decided by the policies that settle them" — a depended-on rule that acknowledges, without naming a tool, an order or a route, that other policies settle those figures. It is source text, not a rendering addition.

## dependency_form
Hop marks from the blind answer: four **state-derived**, one **action-named** (the declared action-form edge); none pre-solved.
Sweep of the whole plan corpus:
- State-form sentences restated as actions, or naming the resolving action/tool/problem: none; the "Restated:" / "In the same terms:" / "Equivalently" sentences are same-form restatements in the same document.
- A dependency or order stated in a second document: none. The reinstatement hub's "decided by the policies that settle them" is the source's own rule sentence (policy-side note 3), states no order and names no problem; not counted.
- Aggregated tables/checklists/routes, cross-problem examples or FAQs: none. Worked examples in the computation docs stay inside one policy.
- Titles/openings: general subjects; none mirrors task 1 (lapse after switching auto-renew off, paying by phone).
- Computation docs: no "unless", "adjustments may apply" or pointers. Observation, not RED: two computation docs illustrate a baseline clause with figures that coincide with factor tiers — "Reinstated-Term Dues: Gross Dues…" §The combined discount uses "8% plus 3% plus 2%", and "Locked Rate of a Reinstated … Term" §Ceiling uses "a working that came to 254.00". Both illustrate source baseline clauses (combine once; never above the current rate) that only bite with non-zero components; neither names a factor, a tier condition or a document, so neither routes the search. Recorded for traceability only.
- Factor docs do not name or point at the computation docs or each other, and do not say which tier customers usually fall on; each is reachable from record words (lapse days, consecutive terms, dues-ledger reinstatement/missed-appointment fee lines, forfeit entries, install-ledger member credit / registration / contract signing, contract tier and purchase channel, repair lines).

**PASS** (no KB-EXPLICIT RED).

## difficulty_closeout (comfort_club_membership_care)
| Task | Runtime blind | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |
- Audit files one-to-one with tasks: runtime_context/…/task_0.md, task_1.md; policy_kb/…/task_0.md, task_1.md. First revision; no older revisions.
- Every normative atom of the six extended policies (and their bases) is entailed by the plan docs; every prerequisite sentence (6 edges) stands verbatim in its blocked policy's documents only; every factor ladder is complete and findable.
- Gate lines on the final form (re-run by the coordinator, cited): `check_docs.py env/env_0037_residential_hvac_company plan` -> "DOCS OK"; `check_traceability.py env/env_0037_residential_hvac_company/tasks/comfort_club_membership_care` -> "TRACEABILITY OK" (0.json 22/0, 1.json 24/0).
- Coverage note: cross-product contradictions are outside this skill's range; base products claimed by no difficulty are not audited here.
