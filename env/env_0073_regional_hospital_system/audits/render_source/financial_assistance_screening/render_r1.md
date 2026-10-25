# Renderer findings — product assist (difficulty financial_assistance_screening), render round 1
Saved verbatim by the coordinator from renderer agent aed5a34bece68abd5 (2026-10-21). Scan-first STOP; no document written. Gate read: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`. Quotes from tasks/financial_assistance_screening/assist.extended.yaml.

## 1. The "held account" selection is a non-factor binding only one factor uses (XF A.4) — three policies
The checker requires the computation document's covers to include every non-factor binding, but their only defining sentence is part of the hold rule: in the computation document it breaks silence about variations; in the factor document the covers home lacks its text.
- `assist_ext_supplement_debt_claim`: Rule (l.1322–1324): "The held account is the patient's account on a billing hold for a charge dispute or, when no account is on such a hold, the account on a billing hold for an itemization review (when several accounts qualify, the one listed first among the patient's accounts)." Compute (l.1402–1404): `dispute_acct: CFIELD('encounter','encounter_id', billing_hold_reason='CHARGE_DISPUTE')`, `review_acct: CFIELD(... billing_hold_reason='ITEMIZATION_REVIEW')`, `held_acct: dispute_acct if dispute_acct != None else review_acct`. Only factor `hold_holdout` uses them; its bindings (l.1586–1591) list none of them.
- `assist_ext_other_costs_debt`: same sentence (l.2243–2245) and compute lines (l.2347–2349); only `hold_restore` uses them (bindings l.2650–2656).
- `assist_ext_renewal_debt_claim`: same sentence (l.3166–3168) and compute lines (l.3247–3249); only `renewal_hold_holdout` uses them (bindings l.3431–3436).

## 2. `assist_ext_hardship_cap`: the kept share has no place in the stated order, and its rounding point differs from compute (XF A.3, B.10)
- Rule (l.2768–2771): "they apply in this order: every reduction of the cap percent applies first (the cap percent never going below zero), the scaling of the annual household income at the resulting percent applies next, rounded half-up to the cent, and every addition applies last".
- Rule (l.2794–2797) gives the kept share only as "heavy_keep of the figure is kept … middle_keep is kept" — not which figure, nor where this step falls relative to the rounding or the asset addition.
- Compute (l.2900): `RND(MX(0, RND(income * cap_pct / 100 * debt_keep, 2) + asset_raise - std_cap), 2)` — rounds after the kept share, not after "the scaling … at the resulting percent".
- Hypothetical: income 10,001.00, cap percent 8.5, kept share 0.85 → compute 850.085 × 0.85 = 722.57225 → 722.57; rule as written 850.09 × 0.85 = 722.5765 → 722.58; kept share after the asset addition gives yet another figure.

## 3. Framing that ties one factor or policy to another (XF A.4 / A.5 / B.12)
- `assist_ext_qualifying_debt`, factor `selfpay_basis` (l.1767–1769): "Unless the self-pay account is the estimated account or the disputed estimate's linked account (both described above), whose bills those adjustments value, its bill is revalued…" — the exclusion points at other factors (`gfe_account_basis`, `gfe_undisputed`); compute `sp_delta: 0 if (sp_acct == ga_acct or sp_acct == gu_acct) else …`.
- `assist_ext_other_costs_debt`: add-backs framed as restoring what another policy's claim took off ("amounts the claim set aside" l.2236; "nothing is added for an appeal and any cost sharing the claim held out stays out" l.2278; "An amount the claim held out for a billing hold is added back" l.2278–2279). No record test shows any claim held these amounts out.

## 4. Tool contract gap: `assist_ext_response_window` / `send_missing_information_notice_7f5665e5`
- Rule (l.3587–3588): "A renewal application that lacks any document type in its tier's required_document_types receives a missing-information notice listing each missing document"; the renewal's tier is "the tier that percent points to", so it can be any tier.
- The tool can only request four document types (`income_proof_request`, `residency_request`, `outside_bills_request`, `bank_statement_request`); it cannot list `MEDICAID_DETERMINATION_NOTICE`, which the 80% and 60% tiers require.
- `assist_ext_response_window` is otherwise clean (month windows, tie rules, case-scoped document counts, None handling match).
