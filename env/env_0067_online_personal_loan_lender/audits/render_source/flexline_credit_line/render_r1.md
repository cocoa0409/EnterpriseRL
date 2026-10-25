# Renderer findings — product line (d=flexline_credit_line), render round 1 (saved verbatim by the coordinator)

Renderer agent ad06366677cc19aa4 published docs/line (DOCS OK) and reported these source edge cases, which it judged not blocking and carried in the source wording:

- **Replacement relief on a returned-payment fee:** the rule says a personal-loan fee that "already carries a personal-loan fee waiver" sets the basis to the line's fee less the waived amount. The code applies this only when the waived amount is above 0. The two diverge only if the personal-loan waiver is exactly 0.00 and the line fee is above the tier's flat 15.00.
- **Credit-limit review:** the rule says review "lowers" the limit. The outstanding-balance floor could produce a figure above the current limit if the balance were already over the limit.
