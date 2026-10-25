# plan (scratch) managed_services_agreements env_0069
draws: t0 prereq=3 factors[6,4,6,6]; t1 prereq=3 factors[6,6,4,5]
DSL notes: hist prims scoped to managed_agreement_id=HID, eq filters exact (kw values may be exprs), within_months from NOW;
 LATEST picks max str(date_field), first row wins ties; no slicing; DAYS(a,b)=b-a; weekday=DAYS(ref,d)%7.
Decided problem pool (6 prereqs needed; Rn vs L conflict -> separate tasks):
 T0 (ETF theme): root E = client e-signs early-termination notice (user) -> notice on agreement + ETF row (triggered event), computed ETF amount
   prereqs: R renewal recorded at term end (agent, state_due, rate), M monthly fee current month (agent, state_due), Rn reinstatement (agent, status->active + fee)
   edges: E<-R (value: months/rate), E<-M (value: avg-fee method), M<-R (value: rate), E<-Rn (state_gate: active)
 T1 (upgrade theme, Monitor->Essentials): root U = client e-signs tier upgrade amendment (user), computed new seat rate
   prereqs: L late fee owed at 1st-of-month assessment (agent), B remote labor charge owed (agent), O onsite visit charge owed (agent)
   edges: U<-L (value: standing factor), L<-B (value: balance), L<-O (value: balance)
Tools: seat? none. invoice numbers seeded INV-01xxxx; generated INV-01 + 4 hash digits.
## REVISED (final) allocation
DSL selection: only holding-level computations or single-record scopes keyed by exact filters.
T0 (ETF theme, Standard tier, draw [6,4,6,6]): root E(6, user: e-sign pending early-termination request -> notice on agreement + ETF row)
  R(6) renewal at term end (agent, state_due), M(6) current-month monthly fee (agent, state_due), Rn(4) reinstatement + fee (agent, state_due)
  edges: E<-R value (months/rate), E<-M value (3-fee average basis), M<-R value (rate/term in force), E<-Rn state_gate (status active)
T1 (upgrade theme, Monitor->Essentials, draw [6,6,4,5]): root U(6, user e-sign upgrade amendment -> tier change on agreement)
  L(5) late fee, scope: assessed invoice is the agreement's only invoice with unpaid balance (holding-level sum)
  B(6) remote after-hours labor charge, scope: latest resolved invoice-route remote_after_hours ticket
  O(4) onsite business-hours visit charge, scope: latest resolved invoice-route onsite_business_hours ticket
  edges: U<-L value (late-fee count standing factor), L<-B value (balance), L<-O value (balance)
