# render_r4 — erl-kb-doc-render account round 4 (agent a0a4e28bd398485ad), STOPPED pre-write; findings saved verbatim by the coordinator from the renderer's message

F1. The rounding grouping of the certificate charge is not fixed by the rule. Location: account_ext_renewal_prefund rule (~line 1574 ff.), bindings pf_cert_charge (line 1737); account_ext_retry_topup rule (~line 2651 ff.), binding tu_cert_charge (line 2849).
- Rule (prefund): "Its certificate price component is reduced by the account tier's ssl_discount_pct; its extra names are billed without that percentage at additional_name_price_per_year for each name and each year renewed, … The reduced amount is rounded half up to the cent; an OV or EV product … then adds a re-vetting fee …; a covered domain … then takes off a Harborline domain credit …; and the result is rounded half up to the cent." The top-up has the same wording ("That reduced amount is rounded half up to the cent").
- Compute: `pf_cert_charge: RND(RND(pf_cert_price * (100 - P('ssl_discount_pct')) / 100 + pf_cert_names + 0.000000001, 2) + pf_cert_fee - pf_cert_credit + 0.000000001, 2)`, and tu_cert_charge identically.
- The compute rounds the reduced price component and the extra-name amount together. The account rule never says what "the reduced amount" is; read naturally, it is the price component the percentage just reduced, with the names added afterwards unrounded. The two readings differ by a cent whenever the multi-year name rate leaves fractions of a cent.
- The SSL charter pins this down ("the reduced amount, the sum of the price components, is rounded half up to the cent before any fixed fee is added"). The account rule carries no such definition.
- Suggested fix: in both account rules, say "The reduced amount, the reduced certificate price component together with the extra-name amount, is rounded half up to the cent".

F2. A branch the rule never defines: an OV/EV product with no organisation validation date. Location: pf_cert_fee (line 1734) and tu_cert_fee (line 2846).
- Rule: "an OV or EV product whose organisation validation, counted as the days from the date it last completed to the current subscription end date plus 365, would be older than the product's org_validation_reuse_days then adds a re-vetting fee of revetting_fee_ov for an OV product or revetting_fee_ev for an EV product".
- Compute: the fee is also added when `CFIELD('ssl','org_validated_date', …) == None or … == ''`.
- The SSL charter's sentence also defines the fee only by that age.
- Fix: either drop the None/'' branch from both computes, or state in both rules that an OV or EV product with no recorded organisation validation also adds the fee (and it must agree with the published ssl docs).

Neither finding changes either task's scored values (task 0's OV has a validation date and no extra names; task 1's is DV).
