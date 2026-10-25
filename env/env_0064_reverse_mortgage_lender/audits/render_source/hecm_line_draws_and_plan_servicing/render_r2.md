# Renderer findings — product hecm, render round 2 (agent af7b474ee21d1f58c, 2026-10-15)
Saved verbatim by the coordinator. 58 docs published, check_docs DOCS OK. Two small source notes (renderer: neither blocks):

- **Restore baseline:** `hecm_ext_reinstatement_restore` lists `restoration_grace_months` (3) among its baseline params, but its baseline rule never uses it. The gate makes the computation document carry the key, so its meta lists it while only the wait-period factor document actually states the 3-month figure.
- **Whole years in the payment release:** the payment release rule says "whole years from the closing date" without defining a whole month, unlike the reset rule. The compute counts whole months the same way the reset rule defines them, so the two only read differently on month-end dates.

(Policy re-auditor revision_5 observation, same class: "The release's 'whole years' (age) and the restore's 'whole calendar months' (wait period) don't state their end-of-month convention, though the reset now does.")
