# Render round 2: source findings, continence (continence_supply_program_services)

Source: continence.extended.yaml sha256 96455dea… (task_tools.py 8cf6605b…, unchanged).

## New source mismatches

None.

## Round-1 findings, re-checked against the new source

- F-1: closed. `excess_units` is now capped at the refill's units, which matches the Records-read sentence "never below zero and never more than the refill's units". Every unit concerned is now at most the refill's units, so the waiver-cover fall-through agrees with the compute.
- F-2: closed. The rule now reads "a payment plan request ... was received within the last 24 calendar months and now stands withdrawn", which matches the XCOUNT on received_at with request_status withdrawn.
- F-3: closed. The denial route now reads "the refill's excess over the limit", and the restocking form reads "the gross credit" / "one box's worth". Both are plain bindings defined in the computation documents.
- F-5: closed. XMAX over the active Ostomy programs matches "an active Ostomy Supply Program that carries a balance due above zero".

## Placement notes (no mismatch)

- Each rule's "Assembly." paragraph combines factor-decided quantities (route cap, straight-tip room, increase blocks; margin and cushion units; look-back postings, deduction and waiver share; restocking charge; term band, additions and first-installment form). The skill homes how inputs combine in the computation document, so each computation document carries its Assembly paragraph after the Method paragraph, which renders baseline.rule. The computation documents therefore name those quantities, as the source does. No factor document states the assembly.
- Two sentences are placed by binding, not by their position in the rule text:
  - "The cushion units are the expected-denial quantity per 30 days times the cushion days divided by 30, rounded down." This is a plain binding, written under "Delivery cushion". It is homed in the ABN computation document.
  - "The term is the term band plus both additions." This is a plain binding, written under "Tenure addition". It is homed in the installment computation document.
