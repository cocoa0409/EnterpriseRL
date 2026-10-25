# Render-source findings — window (round 2)

Source: `window.extended.yaml` sha256 837d7727… (source revision 9), `task_tools.py` sha256 c0b715a7… (unchanged).

Round-1 items, re-checked against the changed source:
- F1 (late charge: periods already charged) — closed at source. The rule, the overwrite and compute (`last_late_entry`, `periods_charged`) agree: a full period counts as charged when it ended on or before the date of the latest late balance charge entry. Re-rendered: the late balance charge hub, its computation document and the catch-up rate document.
- F2 (account standing reads) — closed at source. The rule and compute both read only the contract's financing account in force. Re-rendered: the financing account standing document.
- F3 (returning household ladder gloss) — closed at source. This was an authoring field only; the document already followed the rule, so it was not changed.
- F4 (door credit basis, largest count) — closed at source. Re-rendered: the credit-basis document.

New findings: none. Rule, compute, compute_basis, overwrite and prerequisite sentences were re-checked for verbatim carriage and agreement.
