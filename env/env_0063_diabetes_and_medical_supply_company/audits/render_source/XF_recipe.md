# Coordinator note: closing the XF class (computation documents naming factor quantities; factor sentences reading other factors)

Applies to every extended policy of every difficulty (env_0063, 2026-10-15). Not a verdict — the audit reports are the verdicts.

1. `baseline.rule` is a complete standard method in its own terms: it reads only records and default figures, yields a definite number, and never names a factor's quantity, a factor's zero default ("no spare sets", "no margin", "none by default"), or the fact that adjustments exist.
2. Plain quantities that several factors (or the result) use are defined in record terms in the standard-method paragraph, once.
3. Each factor's sentence reads only records and quantities the standard method defines, never another factor's output, tier or mode; a quantity only one factor uses is defined inside that factor's sentence; and each factor's sentence states exactly how it changes the standard amount (e.g. "adds … to the standard quantity", "multiplies the standard amount by …", "replaces the standard window with …").
4. The combination lives in `result` and is stated ONCE, generically, without naming any factor quantity (e.g. "Each adjustment set out below changes the standard amount as that adjustment states; the amount is then rounded …"). Where the order matters, state the order generically ("additions before multiplications") rather than by factor names.
5. No rule phrase defines a quantity "as another policy figures it" or names a sibling policy's factor.
6. Mechanical check before finishing, recorded in the worklog: for every sentence quoted in `compute_basis` for a non-factor binding, in `baseline.rule` and for `result`, list the factor ids/quantities it names (must be empty); for every factor, list the bindings it reads transitively (none may be another factor's output).
7. Scored values must stay unchanged (check_compute recomputes them); tools unchanged.
