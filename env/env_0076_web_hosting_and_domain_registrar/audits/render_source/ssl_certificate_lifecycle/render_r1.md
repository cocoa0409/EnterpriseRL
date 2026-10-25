# render_r1 — erl-kb-doc-render ssl (agent ad996554f5cc38697), STOPPED pre-write (scan-first). Findings saved verbatim by the coordinator from the renderer's reply (its scratch was removed).

All locations are in env/env_0076_web_hosting_and_domain_registrar/tasks/ssl_certificate_lifecycle/ssl.extended.yaml.

## Findings (blocking)

**F1. `ssl_ext_secondkey_order`: an assembly sentence names two factors' quantities, and plain bindings rebuild a factor's ladder.**
- `tier_part` (l.2072) and `band_part` (l.2073, basis l.2137/2139) quote: "Following the account charter, the tier percentage of a second-key order reduces only the certificate price and the extra names billed at additional_name_price_per_year; an extra name billed in a band takes the single higher of its band's reduction (100 percent less the band percentage) and the tier percentage, the two never being added or compounded."
- That sentence combines the tier percentage (factor `acct_tier_sk`) with the bands (factor `san_bands_sk`).
- The plain bindings `banded`, `b1_names`, `b2_names` and `full_names` (l.2068–2071) read the factor binding `names_part` and work out band membership again from `sk_band1_start`/`sk_band2_start`. `band_part` also reads `sk_band1_pct`/`sk_band2_pct`.
- So whichever document homes these bindings has to name or describe another factor: the computation document would carry the band thresholds and the tier percentage, or one factor document would describe the other. A family factor (bands and tier percentage as one ladder) or an equivalent restructuring would close it.

**F2. `ssl_ext_secondkey_order`, factor `name_term_rate_sk`: the factor's own sentence names another factor's quantity.**
- `name_ratio` basis (l.2113): "...that multiplier acts on the names part after its bands."
- The bands are `san_bands_sk`. The order is then fixed again in the plain binding `list_amount` (l.2054): `(year_price + names_part * name_ratio) * sk_years`.

**F3. `ssl_ext_autorenew_charge`: the same pattern as F1 and F2.**
- `tier_part` (l.2393) and `band_part` (l.2394, basis l.2459/2461): same sentence for "a auto-renew charge". This combines `acct_tier_ar` with `san_bands_ar`.
- The plain bindings `banded`, `b1_names`, `b2_names` and `full_names` (l.2389–2392) rebuild the `san_bands_ar` ladder from `names_part` and the `ar_band*` constants.
- `name_ratio` basis (l.2435): "...that multiplier acts on the names part after its bands." (`name_term_rate_ar` names `san_bands_ar`.)

**F4. `ssl_ext_names_charge`: an assembly sentence names two factors' quantities.**
- `year_name_price` (l.2724 `nm_rate * name_ratio`, basis l.2763): "The yearly price is additional_name_price_per_year after the band rate and the multi-year name rate". It names `nm_band_rate` and `nm_term_rate`.
- The ladder of `nm_band_rate` states an absolute value ("nm_band2_pct percent of additional_name_price_per_year"). So the two factors only compose correctly through this sentence, and its bearing document would have to name both.

**F5. `ssl_ext_secondkey_order`, overwrite 3: the `replaced_by` drops content that is still in force.**
- Superseded base clause (`ssl_pricing`): "The subscription runs from the order date for the years bought, at most max_subscription_years, and the names covered may not exceed max_names; a wildcard name can be ordered only on a product whose wildcard_supported is true."
- The `replaced_by` (l.1943) gives non-second-key orders only: "Every other subscription runs from its order date for the years bought; the names covered may not exceed max_names, and a wildcard name can be ordered only on a product whose wildcard_supported is true."
- The cap "at most max_subscription_years" for every other new subscription is lost.

**F6. `ssl_ext_wait_names`: an assembly sentence names several factors' quantities.**
- `credit_total`/`credit_days` (l.3026/3032, basis l.3071): "The waiting days are first multiplied, the commitment days are then added, and that total is multiplied by the share and rounded down to a whole day".
- It names `long_wait_cn` (the multiplier), `sla_days_cn` (the commitment days) and `goodwill_settle_cn` (the share). The order is load-bearing because the steps don't commute.
- This would close with generic, kind-level wording, e.g. "every multiplier of the waiting days acts first, every number of days added to the credit is then added, and every percentage share acts on that total, which is rounded down to a whole day".

## Advisory
- **A1. `ssl_ext_install_charge`, `list_amount` (l.1491, basis l.1526):** "The per-certificate rate times the certificates covered is rounded half up to the cent before every fixed credit is subtracted" uses `rate_pct` (`repeat_rate_mi`) and `certs_covered` (`reissue_cover_mi`); renders cleanly only if `baseline.rule` itself defines the per-certificate rate as installation_fee and the certificates covered as the one certificate installed.
- **A2. `ssl_ext_install_charge`, `bundle_credit` (l.1484):** the rule doesn't say what happens when a renewal line and an auto-renew line are billed on the same day; ladder and compute give renewal priority. Reachable in this difficulty.
- **A3. `ssl_ext_secondkey_order`:** `baseline.rule` is two non-adjacent pieces of the rule (note only).
