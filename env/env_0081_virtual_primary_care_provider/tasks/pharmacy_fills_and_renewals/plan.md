# plan.md — pharmacy_fills_and_renewals (rx), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[6,5,5]
- task 1: prerequisite_problems=1, factor_counts=[4,5]

Thin-charter finding: rx base gives per drug line at most member pct + benefit basis, per shipping line the
speed fee with the Premier waiver. Floors (4-6 factors, >=1 method) are reached by pricing whole shipments
(drug line + shipping line, netted against what stands collected) and by a Larkspur Pharmacy published
shipping surcharge schedule keyed on recorded keys (fill_date window, ship weekday, days supply, posted
drug charge). Value edges = "owed/overcharged shipping lines settle first, the shipment settlement nets".

Shared factor library (each policy states its own ladders; names after its own result):
- MEM (param, cross membership, multi-source): member pct by tier AND qualifying status (base mapping).
- PREM (method, cross membership): Premier waiver on expedited (0) / overnight (overnight less expedited) / else fee of recorded speed.
- PEAK (param, inv): carrier peak-season surcharge, fill_date inside published 2026-27 window, exp/overnight.
- WKND (param, inv): weekend-transit fee: overnight shipped Friday / expedited shipped Thu-Fri.
- P90 (param, inv): 90-day parcel surcharge on exp/overnight.
- PROT (param, inv): package protection by drug charge posted at shipment (>=100 / >=50 / else 0).
- BASIS (method, cross claim): benefit line: coverage in force+verified & lower_of -> lesser of pbm and member cash; not in force -> member cash; else as billed.

Policies (5):
- E1 rx_ext_owed_shipping_payment (user)  shipping-only: PREM PEAK WKND PROT            -> task1 prereq (4)
- E2 rx_ext_cash_shipment_refund (agent)  shipment net overcharge, cash: MEM PREM PEAK WKND PROT -> task1 root (5)
- E3 rx_ext_shipping_overcharge_refund (agent) shipping-only: PREM PEAK WKND P90 PROT   -> task0 prereq (5)
- E4 rx_ext_cash_shipment_balance (user)  shipment net shortfall, cash: MEM PREM PEAK WKND P90 PROT -> task0 root (6)
- E5 rx_ext_benefit_line_refund (agent)   benefit shipment net overcharge: MEM BASIS PREM P90 PROT -> task0 prereq (5)

Trees: task1 E2 <- E1 (value_input, state form). task0 E4 <- E3 (value_input), E4 <- E5 (state_gate, same prescription earlier benefit-billed shipment).
Worlds: task1 Specialty Generics 30-day cash, Premier Annual, overnight Friday in peak; task0 Extended Generics 90-day
(earlier shipment benefit-billed HDHP, then switched to cash), Premier Annual.
Order: yaml (E1,E2) -> task_tools -> task1 json? NO: tasks built in order 0 then 1; yaml E3,E4,E5 first.
Scratch: /tmp/pharmacy_fills_and_renewals_0081/
