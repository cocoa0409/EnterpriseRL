# worklog — pharmacy_fills_and_renewals (rx), M=2

## Step 0 — draw and difficulty pre-check
`draw_counts.py --tasks 2`:
- task 0: prerequisite_problems=2, factor_counts=[6,5,5]
- task 1: prerequisite_problems=1, factor_counts=[4,5]

Thin-charter finding (recorded decision, closest established rule = memory route "thin-charter merges +
schema-keyed ladders"): the rx base gives a drug line at most two rules that move its price (member percent by
membership tier/status; benefit basis lower-of) and a shipping line one (speed fee with the Premier waiver).
Per-line computations therefore cannot reach 4-6 factors. Route: (a) price whole shipments — drug line plus
shipping line, netted against everything collected on the dispensed fill; (b) a Larkspur Pharmacy published
shipping surcharge schedule (R1, keyed on recorded keys: fill_date window, ship weekday, days supply, fill
charges posted on the ship date) declared as a scoped overwrite of the base shipping sentence in every policy
that prices shipping. Realism note for the audit: the four surcharges (carrier peak-season, weekend transit,
90-day parcel, package protection) are carrier pass-through concepts real carriers publish; they are the
only invented figures and are the most likely realism observation.

Scopes partition shipments by the basis the fill charge line was posted on (B7 coarse exact record test):
- cash_price basis  -> owed shipping posted by the patient (rx_ext_owed_shipping_payment), then net refund
  (rx_ext_cash_shipment_refund)                                                    [task 1]
- cash_member_price -> shipping line corrected on its own line (rx_ext_shipping_overcharge_refund), then the
  balance (rx_ext_cash_shipment_balance)                                           [task 0]
- pbm_patient_pay basis on a lower_of level -> whole-shipment refund (rx_ext_benefit_line_refund) [task 0]

Owner ruling: the two owner=user writes are payments the patient completes personally (ruling (c)); each rule
states the payment is the patient's own act after the agent quotes it; personas make the necessity visible
(HSA card not on file; card on file cancelled).

## Policies and tools (claimed so far)
| policy | tool | owner | task | factors |
|---|---|---|---|---|
| rx_ext_benefit_line_refund | refund_rx_benefit_line_87d0f93d | agent | 0 | member_percent, premier_speed_waiver, weekend_transit_fee, ninety_day_parcel, package_protection (5) |
| rx_ext_shipping_overcharge_refund | refund_rx_shipping_overcharge_36ef431c | agent | 0 | premier_speed_waiver, peak_season_surcharge, weekend_transit_fee, ninety_day_parcel, package_protection (5) |
| rx_ext_cash_shipment_balance | pay_rx_shipment_balance_955e5801 | user | 0 | member_percent, premier_speed_waiver, peak_season_surcharge, weekend_transit_fee, ninety_day_parcel, package_protection (6) |

Capability cards (Step 2):
- refund_rx_shipping_overcharge_36ef431c (agent/write): object = one shipping charge line; action = book one
  billing-error refund line (negative amount, refund_reason billing_error, original_charge_id = the line, same
  rx_id / rx_fill_id); receipt refund_line_id, original_charge_id, rx_id, rx_fill_id, amount, refund_reason,
  charge_date, status. Body enforces: positive cent amount, the line exists and is a shipping charge line.
- refund_rx_benefit_line_87d0f93d: same on a fill charge line.
- pay_rx_shipment_balance_955e5801 (user/write): object = one dispensed fill of a prescription; action = post
  one fill charge line on the cash member price basis; args rx_id, rx_fill_id, membership_id, coverage_id
  (the blueprint's fixed action_bindings for the three rx_fill_charged gates), amount. Body enforces positive
  cent amount and that the references belong to the same patient/prescription. No prerequisite is checked.
D4 trigger list: rx_charge_refunded triggers [], rx_fill_charged triggers [], rx_shipping_charged triggers []
— nothing lands in another category.

## XF tables
Defining-sentence table (A3): every policy's baseline paragraph defines its own result's quantities, each
named after the result ("the shipping fee the shipment balance allows", "the member cash price the
benefit-line refund allows", ...); each factor sentence defines only its own surcharge/percent/speed fee; the
assembly sentence "The shipping fee X allows is the speed fee X allows plus the surcharges and fees X allows for
the fill, each counted once" is the single generic combination (additions commute; the Premier waiver
replaces the speed fee before additions). baseline.params = exactly the cash prices and speed fees the
paragraph uses.

Transitive factor-reads table (A1): member_percent reads mb_tier/mb_stat (CFIELD membership); premier_speed_waiver
reads sp_tier/sp_stat (CFIELD membership) + plain speed/speed_fee; peak reads pk_date (LATEST fill_date) +
speed; weekend reads wk_wd (DAYS from a Monday anchor) + speed; parcel reads pn_days (LATEST days supply) +
speed; protection reads pr_drug (SUM fill charges on the ship date) + speed. No factor reads another factor's
binding; the plain bindings speed, speed_fee, fdate, days, cash, *_pct_lvl are not factor-owned.

A6 method tier table (premier_speed_waiver, the only method factor): tier1 waived (constant 0.00) vs tier2
overnight less expedited (subtraction of two tariff parameters) — adds an operation; tier2 vs tier3 fee of the
recorded speed (selection by speed) — adds a data-selected input; tier1 vs tier3 — selection vs constant. PASS.

A7 T1/T2 (lesser-of in rx_ext_benefit_line_refund): T1 member_percent on the task world moves 33.40 -> 12.40;
T2 a world with pbm above full cash price at every other baseline moves too (lesser(pbm, cash) follows cash).
The MX(0, ...) floors on the three settlement results do not bind on any task world (T1 sensitivity table
below, one case reaching 0.00 is a substitution, not the gold world).

B2 probe table:
| read | decoy / absent | outcome |
|---|---|---|
| latest dispensed fill (E3/E4) | authorization line rx_fills_authorized; older Jan/Apr/Jul fills | filtered by event_type, latest fill_date = 2026-10-09 |
| shipping line of the fill | July shipping line 7.95 (other fill) | keyed rx_fill_id; absent -> None, sums 0 |
| latest pbm-basis fill line (E5) | Jan/Apr lines carry a pbm figure but are cash_member_price basis | filter price_basis=pbm_patient_pay; absent -> bline None -> out of scope 0 |
| fill charges on ship date (protection) | a later balance line on the same fill | charge_date = fill_date filter |
| refunds counted in collected | July refund (other fill) | keyed rx_fill_id of the settled fill |
| membership | only one holding seeded; status filter via member_discount_statuses | Access/cancelled -> fall-through |

B1 edge probes (scratch run): absent shipping line -> ship_posted 0 (E3 -> 0.00); amount exactly at
prot_mid_floor 50.00 -> mid tier (>=); fill_date = peak_start / peak_end -> inside (inclusive both ends);
Friday standard -> no weekend fee; 30-day fill -> no parcel; negative differences -> MX floor 0, no line.
B4 rounding: compute RND(x+1e-9,2) on non-negative values; tools use Decimal ROUND_HALF_UP class static
helper `_Cents.parse`; all scored/sensitivity figures are whole cents.
B5 compute_basis sweep: every quote verbatim in its rule (scratch sweep: 0 misses for all policies).

## Task 0 — closed
Root rx_ext_cash_shipment_balance (user) <- rx_ext_shipping_overcharge_refund (value_input, state form,
gate `collected`) and <- rx_ext_benefit_line_refund (state_gate, state form, gate rx_charges.original_charge_id).
Prerequisite sentences: affirmative "The shipment balance is fixed only after ..."; negated "The shipment
balance is not collected until ...". Exactly one write brings each state about (shipping-line refunds are
written only by the shipping overcharge refund; refunds on benefit-basis lines only by the benefit-line refund).

Handling-time figures (scratch evaluator over check_compute primitives):
- E5 33.40; sensitivities member 12.40, premier 23.45, weekend 37.40, parcel 35.40, protection 35.35; all-baseline 10.40
- E3 9.95; premier 0.00, peak 13.45, weekend 17.95, parcel 13.95, protection 11.90; all-baseline 17.45
- E4 4.20 (after both refunds); member 25.20, premier 14.15, peak 0.70, weekend 0.00, parcel 0.20, protection 2.25; all-baseline 17.70
Prerequisite sensitivity: skip E3 -> E4 = 0.00 (collected 101.20 > 95.45); skip E5 -> E4 unchanged 4.20,
July refund row missing (state_gate). Order E5/E3 commutes (33.40 and 9.95 either way).
Seed revision log: replay closure demanded every seeded row be read -> dropped renewal-notice rows, added
reads of membership charges, coverage and the prescribing visit; empty FK fields set to null; refund tools'
first argument renamed original_charge_id and the balance tool given rx_id/membership_id/coverage_id (blueprint
action_bindings of the dedup and fill-charge gates).
check_traceability before docs: only the three unlock tool-name misses (expected pre-render).
Per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
Revision (B1 probe): absent benefit-basis line made `MN(pbm, member_cash)` raise on None, and an absent
dispensed fill made the weekday/peak reads compare None -> symptom TypeError in a scratch probe; root cause
unguarded first-match reads; change `MN(pbm, member_cash) if pbm != None else member_cash`, fill_date reads
`or ''` / `or anchor`; re-run: every absent-record probe returns 0.00 (no line), task values unchanged.

## Task 1 — closed
Draw prerequisite_problems=1, factor_counts=[4,5]. Root rx_ext_cash_shipment_refund (agent,
refund_rx_cash_shipment_4224ad9e, 5 factors: member_percent, premier_speed_waiver, peak_season_surcharge,
weekend_transit_fee, package_protection) <- rx_ext_owed_shipping_payment (user, pay_rx_owed_shipping_bbdf4b04,
4 factors: premier_speed_waiver, peak_season_surcharge, weekend_transit_fee, package_protection), value_input,
state form, gate `collected`: "The cash shipment refund is worked out only after the shipment's records carry a
shipping line for the dispensed fill whenever the shipping fee the cash shipment refund allows is above zero."
(affirmative; task 0 carries the negated direction too). Only the owed shipping payment writes shipping
charge lines -> unique resolver.
World: Daniel Pettigrew, Premier Annual active, Specialty Generics teriflunomide 30-day cash; October 9
(Friday, peak window) overnight shipment posted 89.00 on the cash price basis, no shipping line.
Figures: owed shipping 28.45 (premier 38.40, peak 24.95, weekend 20.45, protection 26.50; all-baseline 24.95);
refund 13.35 after the payment (member 0.00, premier 3.40, peak 16.85, weekend 21.35, protection 15.30;
all-baseline 3.50). Skip the payment -> refund 0.00. 90-day parcel clause stated in both rules but not a
declared factor here (30-day fill; its ladder bites in task 0).
Capability cards: pay_rx_owed_shipping_bbdf4b04 (user/write) posts one shipping charge line on a dispensed
fill (args rx_fill_id, membership_id = blueprint action binding of free_expedited_state, amount);
refund_rx_cash_shipment_4224ad9e (agent/write) books one billing-error refund on a fill charge line. D4: both
events trigger nothing outside rx.
Per-task gates task 1: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Difficulty closing
Union: 5 policies, 5 tools, scopes disjoint (task 0: benefit-line refund, shipping overcharge refund, shipment
balance; task 1: owed shipping payment, cash shipment refund). Suite: history_rows_max 16, branches_max 80.
check_traceability (pre-render): only the 5 unlock tool-name misses, as expected before the KB exists.
Known audit-facing risks: invented Larkspur shipping surcharges (realism R1 claim); netted shipment
settlements make some shipping factors bear weight through netting (mechanically load-bearing).
Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
ROUND 1: gates 7/7 green
