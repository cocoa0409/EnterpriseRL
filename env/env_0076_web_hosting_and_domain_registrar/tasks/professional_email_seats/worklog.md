# worklog — professional_email_seats (env_0076), M=2

Draws: task 0 prereq=1 factors [6,5]; task 1 prereq=2 factors [5,5,4].

| task | frozen_time | tree (topological order) | scored values |
|---|---|---|---|
| 0 | 2026-10-28 11:20:00 CDT | email_ext_reactivation_renewal (agent, 6f) -> email_ext_mail_pro_upgrade (user, PayPal checkout, 5f, root) | see tasks/0.json computations |
| 1 | 2026-10-24 10:40:00 CDT | email_ext_unbilled_seat_catch_up (agent, 4f) -> email_ext_term_renewal (agent, 5f) -> email_ext_annual_conversion (user, PayPal checkout, 4f, root) | see tasks/1.json computations |

Full per-task dossiers (factor cards, sensitivity runs, defining-sentence table, factor-reads table, all-pairs
method tiers, T1/T2, decoy/absent probes, events-with-triggers list, revision log) are in each task's design_rationale.

Trigger list (all tools, round 6): email_renewal_charge renewal / monthly_instalment -> email:email_term_renew (and
email_reactivate for the reactivation) in the same tool; email_seat_charge upgrade_proration -> email:email_plan_change
(same tool); email_seat_charge added_seats (seats already on the subscription). Tools write card or paypal only; no
account credit and no refund is written by any tool; nothing lands in another category.

Known judgement calls for the audit (round 6): the customer's own writes are payments the holder completes at
Harborline's secure checkout with PayPal (owner ruling (b)); Harborline's published schedule — seat-band list prices
(10-49 / 50+ seats, set by the seats on the charge that opened the term, a list price and not a discount), the
billing-plan price table, the reinstatement fee, the late-payment fee and "fees are never credited" — applies to
ordinary renewals and seat additions too (sibling tails), so no late or suspended customer pays less than an on-time
one; new subscriptions keep the base price (no opening charge sets a band yet); pro_/premium_seat_price_* restate the
target products' base prices because the DSL cannot read another variant's parameter; idle seats count the current
term's deletions by the stated whole-month test (DSL windows are month-granular).

## REWORK round 2 claims
- CG-1: late monthly renewal prerequisite sentence and condition now accept "at least the scheduled seat count where one is set and is lower", a state the seat catch-up's scheduled-count tier always reaches; probe recorded in tasks/1.json design_rationale.
- CG-2: Pro upgrade edge condition restated at the sentence's own scope (paid new-subscription or renewal charge whose period start is the term start date); task 0 closure condition copied from it.
- CG-3: seat catch-up tier rate now reads the tier the account holds when the catch-up is billed (account charter: new tier's figures apply from the next charge); date test, binding and cross read of tier_changed_date removed; whole class checked — every policy reads the current tier.
- CG-4: per owner ruling (b), the customer's own writes are payments the holder completes at Harborline's secure checkout with PayPal, a method never stored on the account: the Pro upgrade (task 0) and the annual conversion (task 1); each rule states it, each tool writes paypal, each persona makes the necessity visible; the late monthly renewal is now owner=agent on the card on file. No email base rule sentence assigns that billing to the agent, so no extra overwrite.
- F0-1: closed by CG-4 (upgrade paid by the holder at checkout with PayPal).
- F0-2: task 0 seeds the Business plan's hosting_charges and the domain's domain_charges, priced by their charters, read by find_hosting_charges / find_domain_charges.
- F0-3: volume-factor proof text (factor_trace, factor_sensitivity tier_taken, evaluation_criteria objective/necessity, rationale) now names the charge that opened the current term.
- F1-1: closed by CG-4 (conversion paid by the holder; late renewal by the agent).
- F1-2: task 1 seeds the Pro plan's hosting_charges and the domain's full domain_charges, including the credit-first 2026-05-15 auto-renewal with its ledger entry (credit balance restated).
- O1: late monthly eligibility now reads "only while the subscription status is active".
- Other observations (O2–O10) left as recorded; no realism observation names a ladder no host publishes.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- CG-5: the late monthly renewal's prerequisite effect text now states that the catch-up line leaves the month carrying every non-idle seat, or at least the scheduled seat count where one is set and is lower; text-only, rules/compute/tools unchanged.
- F0-3: task 0 tracing of both writes names the charge that opened the current term (period start = term start) as the seat-volume evidence, and every proof/rationale sentence names the reactivation write by its index (step 12) and the upgrade by its index (step 14).
- Sweep (both tasks and the charter): every factor_trace, tracing, necessity, objective, closure and design_rationale text checked mechanically for stale step numbers, "latest renewal" selections, old credit balances, tier-date wording and old owners; task 1's credit near-miss sentence and catch-up necessity corrected; no other stale text found.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- F1: the reinstatement charge is now a per-seat binding owned by reactivation_reinstatement (list monthly seat price times the reinstatement months), with its defining sentence moved into the factor's wording; result multiplies it by the renewed seats; no factor binding reads another factor's binding.
- F2: unused_days and month_days moved into conversion_credit_basis.bindings.
- F3: scheduled_seats moved into catch_up_idle_seats.bindings.
- F4: the suspension overwrite's second clause now reads "... whose renewal went unpaid and whose scheduled product is none ...", in both replaced_by and the rule.
- Class sweep: every policy re-scanned mechanically for bindings read by exactly one factor but held outside it; the only remaining ones (standard_seats x2, standard_fraction, standard_catch_up_seats) are the baseline paragraph's own quantities, the fall-throughs named by the factors' baselines, and stay with the computation document. Every overwrite tail re-checked for scope wording. Proof text updated where the moved binding was named; scored values, tools and tier outcomes unchanged.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- XP-1: every discount stack now follows account_tier_benefits — the additive Harborline Mail rate card is removed from all five policies; the account-tier rate (tier recorded on the charge date) is the only percentage and reduces only list/renewal components (reactivation renewal, late monthly renewal, annual conversion), once, rounded half up before any fee or credit is applied; it never reaches the Pro upgrade line or the seat catch-up line (proration/added-seat lines).
- XP-1 (class): the former hosting-bundle, domain and volume percentages became included seats (hosting-included, domain-included and volume seats: licensed, never billed), so no percentage is ever added to or compounded with the tier rate; zero-billed cases are carved out by each policy's scope sentence.
- XP-1 (Pro upgrade): the account tier reaches the upgrade only through the credited seat price (the price the current term billed each seat at, by the tier recorded on the opening charge's date); the line itself carries no percentage.
- XP-1 (seeded cross-product rows): hosting, domain and email ledger rows re-checked against the account rule (single percentage on the list/renewal component, discounted component rounded before the ICANN fee, tier on the charge date); task 1 world now carries 23 seats so the catch-up stays owed after included seats.
- Probes: decoy/absent rows for every first-match read (hosting, domain, account, opening charge date) recorded in the task rationales; missing account or opening charge falls to the list-price credit.
- Proof text: factor_trace, factor_sensitivity, tracing, necessities, closure texts and design_rationale of both tasks rewritten for the new figures; kb= items are the renderer's (the published email corpus must be re-rendered from this charter).
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- CG-6: the only percentage left is the account-tier rate, on a Harborline Mail list or renewal component, applied once before rounding; volume pricing is a seat-band list price (a published list price, not a discount), so no percentage is added or compounded; Microsoft 365 seats, fees, credits and proration lines take no tier.
- CG-7: every seat a line covers is billed; each tool books that count in the line's seats field (reactivation and late renewal: the renewed seats; upgrade and conversion: the seat count; catch-up: the catch-up seats), and the docstrings say so.
- CG-8: no tier is read as of a past date; the Pro upgrade credits the term by the amount on the charge that opened it, net of the fees that charge carried.
- CG-9: all 15 included-seat factors removed; the replacement dimensions are Harborline's published seat-band list prices, the billing-plan price table, the reinstatement fee, the late-payment fee, the upgrade proration span, the credit basis and "fees are never credited"; the sibling tails make ordinary renewals and seat additions use the same band prices and drop idle seats, so no suspended or late customer pays less than an on-time one.
- F0-4: the stale "seat-volume rate" wording is gone; every proof text of both tasks (factor traces, sensitivities, tracing, objectives, necessities, closure, solvability, rationale) was regenerated from the round-6 runs.
- XP-1 (kept closed): account_tier_benefits is complied with in every policy and in every seeded row (tier recorded on the charge date, one percentage, discounted component rounded before fees, none on proration lines; the in-window whole-term upgrade rebill is a list component).
- O12 / O13: the catch-up now bills the whole period at list and takes the tier; the zero-billed carve-outs are gone with the included seats.
- Ruling (B) reshaping: task 0 root takes 6 factors and its prerequisite 5; the late monthly renewal is now email_ext_late_renewal (any plan, the renewal due at the term end paid late while still active), so the plan table is a real three-tier ladder; Microsoft 365 is in the scope of all five policies (the upgrade's top product is Business Premium).
- Idle seats: only the current term's deletions count (a stated whole-month record test), so seats dropped at one renewal are never dropped again; both worlds were re-seeded (hosting and domain rows dropped because no factor reads them, history re-priced at band prices, task 1 deletions moved into October).
- XF sweep: A1 factor-reads check clean (r6/mech.py); A3 defining-sentence table, A6 all-pairs method tiers, A7 T1/T2, B9/B10 decoy and absent probes, D20 triggers, D21 owed-at-once are in each design_rationale; B11 half-up epsilon is present, and no rounded input lies within 1e-6 of a half cent; B12 compute_basis quotes are verbatim; E23-E26 tools pass.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- CG-6: seat-band list prices removed from all five policies, their rules, compute, params and seeds; every charge is priced at the product's current seat price for the billing plan, and the account-tier rate is the only percentage, once, on a Harborline Mail renewal or list component, rounded before fees.
- CG-10: every plan-price factor removed; the billing plan's seat price and months are part of each baseline (the standard method every subscription is charged); each remaining factor's baseline is a default a producible world is charged (tier 0, no reinstatement or late fee, no idle seats, remaining-days fraction, the base price difference as credit basis, list paid-month value, no fee carried, no credit).
- CG-11: every replaced_by restates the base text verbatim for what its policy does not price (renewal seat-price, seat-addition, suspension and mailbox clauses); the grace-clause overwrite is dropped; on-time renewals of active subscriptions are now inside email_ext_term_renewal, so dropping idle seats at a renewal is priced by compute and never by words; seeded ordinary rows are re-priced by the base rules alone.
- XP-1 / account_tier_benefits: the Pro upgrade is a proration line and takes no account-tier rate; no percentage is added or compounded anywhere; seeded rows carry the tier recorded on their charge dates.
- O14: closed with the bands. O15 (fees inferred from the opening charge's charge-date offset) stands as stated in the rules.
- Class sweep: factor reads (r7/mech.py) clean; compute_basis verbatim; decoy/absent probes and half-cent check re-run (r7t/probes.py, halfcent.py); proof text of both tasks regenerated (no band, plan-factor, tier-on-upgrade or round-6 figure left outside the dated revision log).
- Draw: not met. The honest factor counts are reactivation 3, Pro upgrade 3, catch-up 2, term renewal 3, conversion 4. This charter has no further real, evidence-backed dimension for these charges: a late fee on a reactivation is a constant, the plan price is the standard method, bands are a volume discount, and the account tier on an upgrade line is barred. check_extended and check_compute report the counts.
REWORK round 7: gates RED check_extended check_compute

## REWORK round 8 claims
- Draw (round-7 RED, check_extended / check_compute): re-tree tabulated in plan.md (ROUND 8) before writing; task 0 is now a month-to-month suspended subscription (reactivation renewal 6 factors -> Pro upgrade 5), task 1 keeps catch-up -> late term renewal -> annual conversion (5 / 5 / 4) on a world with a scheduled seat count; both draws met.
- Realism of the added dimensions: billing-plan seat price (base price tables; month-to-month and annual-billed-monthly above the annual commitment), Harborline's published late-payment fee by days past due (1-3 / 4-14 / 15+), the published reinstatement fee, seats kept for mailboxes deleted less than a whole month ago (still restorable; a restore needs a free seat), the scheduled seat count as the catch-up target, the short-month whole-weeks proration convention already published for conversion credits, the opening line's carried late-payment fee and reinstatement charge; no invented padding, no RED-marked factor re-admitted.
- CG-6 (kept closed): no seat-band price anywhere; the account-tier rate is the only percentage, once, on Harborline Mail list or renewal components, never on the Pro upgrade (a proration line), fees or credits.
- CG-10 (kept closed, whole class): every baseline is a default a producible world is charged — the annual-commitment seat price, no tier, no late or reinstatement fee, no idle or kept seat, the seat count as catch-up target, the base remaining-days fraction, the list credit, no fee carried, no credit; no baseline fixes the opposite billing plan and months follow the subscription's own term.
- CG-11 (kept closed): every overwrite restates the base text verbatim for cases its policy does not price; seeded ordinary rows (task 0 order, April renewal, added seats, May-September renewals; task 1 history) are priced by the base rules or the in-scope term-renewal rule.
- XP-1 / account_tier_benefits: unchanged compliance; tier recorded on each seeded row's charge date.
- O15: fees carried are read from the opening line's charge-date offset, stated as a rule; the late-payment fee and the reinstatement charge are separate published fees and are taken off separately.
- Class sweep: factor reads clean (r8/mech.py); compute_basis verbatim; decoy/absent probes and half-cent check re-run on both worlds (r8t/probes.py, halfcent.py); every proof text of both tasks regenerated from the round-8 runs.
REWORK round 8: gates 7/7 green

## REWORK round 9 claims
- CG-12: the four two-valued ladders (reactivation_kept_seats, term_renewal_kept_seats, catch_up_kept_seats, catch_up_idle_seats) are removed; the tier ladders now put Microsoft 365 inside "otherwise"; every ladder of all five policies was swept and no two tiers share an outcome.
- CG-13: one seat-basis method in the reactivation, the term renewal and the catch-up target; where a scheduled seat count is set it bills the lower of that count and the seat count, never fewer than the mailboxes in use (seat count less idle seats); otherwise seat count less idle seats, or the seat count; the term renewal's prerequisite condition is restated to match.
- O16: closed with the kept seats (no whole-month retention proxy left).
- Added dimension: catch_up_billing_span (the base proration of added seats as the default; the whole ended term where the renewal is still due; the short-month whole-weeks convention).
- CG-6 / CG-10 / CG-11 / XP-1: kept closed (no bands; honest defaults; out-of-scope base text verbatim; the account-tier rate only on Harborline Mail list or renewal components).
- Draw: not met after closing CG-12 and CG-13 (task 0 has 5 and 5 factors against [6, 5]; task 1 has 4, 4 and 4 against [5, 5, 4]); plan.md ROUND 9 records why none of the four suggested base dimensions adds an honest load-bearing factor to these trees.
- Class sweep: factor reads clean (r9/mech.py); decoy/absent probes and the half-cent check were re-run on both worlds (r9t); proof text of both tasks regenerated.
REWORK round 9: gates RED check_compute

## REWORK round 10 claims
- CG-12 / CG-13: kept closed (round-9 structure unchanged; no ladder shares an outcome; the seat basis keeps the lower-of rule with the in-use floor).
- CG-6 / CG-10 / CG-11 / XP-1: kept closed.
- Draw shortfall (task 0 one factor, task 1 two): each of the eight parameters named in the round-10 ruling was checked against its parameter_schema meaning, the base rules and the db schema (plan.md ROUND 10). None yields a ladder with three distinct outcomes resting on records that are both producible and load-bearing in these worlds: four are one value for every product, two decide no amount, shared mailboxes have no record in the schema, and migration is booked only on a cross-family order that neither tree writes. No factor was added, so the round-9 charter, tools and tasks stand.
REWORK round 10: gates RED check_compute

## REWORK round 11 claims
- Route (a), task 0: the reactivation renewal now prices the renewal product (the scheduled product recorded in email_holdings.scheduled_variant, which the base renewal rule applies; otherwise the current product) and the price column (annual-commitment / annual-billed-monthly / month-to-month); the plan-price factor is replaced by these two, and Microsoft 365 products take no tier. The world was re-seeded with Harborline Mail Starter scheduled by the holder; the reactivation applies and clears it. The Pro upgrade from Starter holds under the base plan-change rule because Pro is one of Starter's upgrade_targets, and the move takes effect at once. The retention_on_downgrade storage check is stated as run before billing, a failed change being cleared, so the scheduled product on record is authoritative. Task 0 meets its draw [6, 5].
- Route (a), task 1: the late term renewal carries the same renewal-product and price-column factors (5); the world has Starter scheduled, and the conversion then prices Starter.
- Tools: reactivate_suspended_mail_4fbd3039 and pay_late_mail_renewal_a889cd52 apply a scheduled product at the renewal and clear it, and their docstrings say so.
- Route (b): not taken. A 168-hour cancellation-window refund cannot replace the catch-up here, because the subscription is month to month and the base never refunds a month-to-month charge (monthly_plan_refundable false). An annual or Microsoft 365 world would remove the price-column factor from the renewal, and the account tier as well on Microsoft 365.
- Route (c), shortfall: task 1 is one factor short (seat catch-up 4, annual conversion 4, where the draw needs a second 5). Candidates tried: the refund above; the renewal product in the conversion, which is vacuous because the late renewal applies and clears the scheduled product first; the renewal product in the catch-up, which bills the ended term on the current product.
- CG-6 / CG-10 / CG-11 / CG-12 / CG-13 / XP-1: kept closed; the ladder sweep finds no two tiers sharing an outcome in any policy.
- Class sweep: factor reads clean; decoy/absent probes and the half-cent check re-run on both worlds (r10t); proof text of both tasks regenerated.
REWORK round 11: gates RED check_compute

## REWORK round 12 claims
- Draw, task 1 (coordinator route (2)): email_ext_annual_conversion now carries conversion_annual_start. The annual term starts on the term start date when today is fewer than conversion_start_days into the paid month (whole month credited), on the term end date when conversion_end_days or fewer days remain (nothing credited), and otherwise today (the days left credited). conversion_credit_days is now the credit convention. Task 1 has [5, 5, 4]; every factor bears load on the seeded world.
- Route (1): not taken. No record dates an added seat, so a back-billing limit would rest on no seeded row (plan.md ROUND 12).
- Tool contract: convert_mail_to_annual_cfde09f1 books the term from the same annual start date, and its docstring states the rule. The charge date is today.
- Rule sweep: the scope, monthly-renewal tail (rule and overwrite replaced_by), eligibility and baseline sentences say "the annual start date" instead of "today". The compute_basis quotes are verbatim.
- Persona: the customer asks for yearly billing "right away". The request snippets in the solvability contract are updated to match.
- Task 0: not rebuilt. Its content is unchanged. The replay write-back reorders db_closure rows, so its bytes are not identical to the round-11 file.
- Class sweep: factor reads clean (r11/mech.py). The ladder sweep finds no two tiers sharing an outcome. Decoy and absent-record probes and the half-cent check were re-run on the task 1 world (r11t). The task 1 proof text, sensitivities and skipped-edge text were regenerated.
REWORK round 12: gates 7/7 green

## REWORK round 13 claims
- CG-14: in the reactivation renewal and the term renewal, the framing sentence "a scheduled product still on record is one that passed it" is replaced. A scheduled lower product is now applied at that renewal; a mailbox above the lower product's mailbox_storage_gb is full and, where send_block_at_full is true, stops sending until space is freed. email_plan_changes is added to base_policy_refs, with a scoped overwrite of its "otherwise the change is skipped at that renewal" clause; replaced_by restates it verbatim for every other renewal and names its scope. The "which the base rule applies" wording in the renewal-product head now reads "which is applied".
- F0-5: task 0's persona gives a reason for Pro that does not contradict the scheduled downgrade (bigger attachments, more shared inboxes; no mailbox-space request). The design rationale is rewritten to the overwrite reading.
- CG-15: convert_mail_to_annual_cfde09f1 takes annual_start_date as an agent-supplied argument, checked for format only, and records it. Its docstring carries no thresholds and the tool body picks nothing. The same class is closed in the reactivation and late-renewal tools: renewal_product is an agent-supplied argument and the tools no longer read scheduled_variant. Gold arguments and tracing are added in both tasks.
- CG-16: compute and rule now agree on when a scheduled product applies, in both renewal policies. The invented date condition is replaced by a record test stated in the rule ladder and in the factor's "otherwise" tier: no upgrade line of the current term ends on the term end date. Decoy and in-term probes run.
- Class sweep: factor reads clean (r13/mech.py). Ladders are distinct. Basis, overwrite and baseline quotes are verbatim. Stale-text sweep (storage check, "passed it", tool-picked dates, mailbox-space reason) is clean. The half-cent check is clean. Every scored figure, sensitivity and baseline is unchanged. Both task files were rebuilt; replay ran once with write-back, then with --check.
- XP-1 (account_tier_benefits): kept closed. Only the tier percentage applies, on list or renewal price components; it is never applied to fees, credits, proration lines or Microsoft 365 seats, and seeded rows are unchanged.
REWORK round 13: gates 7/7 green

## REWORK round 14 claims
- F1-3: task 1's persona has the customer complete the yearly checkout with the reference number, the amount and the annual start date the agent gives her. Her surface request is now "yearly billing now, however the start date works out", so she has no start-date preference of her own against the rule. Her request sentence, action semantics and evidence snippets are reworded to match.
- F1-4: task 1's solvability_contract request_alignment claim now reads that the yearly term starts on the date the conversion rules set. Design rationale, closure, sensitivity and tracing texts were swept: no "starting today", "right away" or "start today" wording remains, and the baseline tier is described as starting on the conversion day. Text only; no value, argument or world row moved.
- Charter and task 0: no change. Task 0's content is untouched, but the replay write-back reordered its db_closure rows (bytes only); every later gate run used replay --check.
REWORK round 14: gates 7/7 green

## REWORK round 15 claims
- G1: the seat catch-up is one added-seat line from the term start date to the term end date on every billing plan, priced for the term's calendar months. The annual-billed-monthly instalment-month branch is removed from the rule, the compute and the tool body and docstring. The booked line counts among the seats billed for the current term, so the late renewal's wait can be met on every plan (probe in scratch r15t).
- G2: in the Pro upgrade, the fees carried by the opening charge come off the instalment before it is counted for the term's months. A credit-count binding sits in the credit-basis factor, and the term-credit sentence keeps its order with "times the months it is counted for" inserted. The ladder and baseline say "counted once".
- G3: in both renewal policies, every scheduled-product tier requires that no upgrade line whose period end is the term end date belongs to the current term. Rule words, ladder tiers and compute agree; the fall-through names the same case.
- G4: scheduled_seats moved into the seat-basis factor's bindings in the reactivation renewal, the term renewal and the seat catch-up.
- G5: the late-renewal tool's capability text covers a term renewal billed on or before its due date or overdue after it, matching the rule's scope.
- Task values: no world row, scored amount, sensitivity or baseline moved. The renewal-product quote in each task's tracing was patched in place to the new rule wording; that is the only byte change in tasks/0.json and tasks/1.json. Replay ran with --check only.
- Class sweep: factor reads clean; ladders distinct; basis, overwrite and baseline quotes verbatim. Decoy and absent-record probes, the upgrade-line probes and the half-cent check were re-run. account_tier_benefits stack unchanged: one tier percentage on the price component only, never on fees, credits or the upgrade proration line.
REWORK round 15: gates 7/7 green

## REWORK round 16 claims
- SR-1: both seeded worlds now produce their October declines under the published rules. The unused credit of the single deposit is withdrawn to its card inside the 180-day window before the first attempt, so each credit-first auto-renew finds 0.00 and goes to the card, which declines. The ledger reconciles with the recorded balance, and the trailing-365-day deposits still qualify the tier. Each attempt was re-priced as a term renewal by the published rules, and every other seeded row was re-checked against its owning rule as of its date. Seed-consistency, ledger-read and rationale texts were rewritten to match, including the retired "renewal due exceeded the credit" claims.
- BL-1: the Pro upgrade's opening-charge-date binding and its sentence ("a fee is part of what that charge billed but never of what a term is credited") are removed. Each carried-fee factor reads the opening renewal charge's date in its own binding, and its sentence names that charge. The computation document carries baseline sentences only. Class sweep: no other policy has a plain binding read only by factors (the conversion's charge date already sits in its carried-fees factor).
- Scored values: none moved. Every amount, sensitivity and baseline is as before, and the half-cent check plus the decoy, absent-record and upgrade-line probes were re-run. Both task files were rebuilt for the ledger change; replay ran once with write-back, then with --check.
- account_tier_benefits: unchanged. One tier percentage on the price component only, never on fees, credits, proration lines or Microsoft 365 seats; the seeded added-seat proration line carries no tier rate.
REWORK round 16: gates 7/7 green
