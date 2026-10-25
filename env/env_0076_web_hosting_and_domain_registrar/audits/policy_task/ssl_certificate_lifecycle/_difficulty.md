# Policy-task audit — ssl_certificate_lifecycle / charter-global

## revision_1

## charter_global_frozen
- auditor: independent policy auditor (erl-task-policy-audit), not the instantiator; freeze 2026-10-22T15:14Z.
- hashes (verified against the brief): `ssl.extended.yaml` 3c004751aaeec076eeb25ac92e7fa7ccf1770ffe4384de1cf57399150786a9c1; `task_tools.py` c88e451c6d19ca0039581ee528e656dd899ded957d2567a82e31edf07ac9358c; views 0.view c339a78a…72f, 1.view 2a19fe76…ba1 (match).
- read: blueprint.yaml, db_schema.json, share_tools.py (ssl finders), products/ssl.yaml, account.yaml / domain.yaml / email.yaml (parameters + tier-benefit, spending and goodwill policies), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the two masked views.
- masked/unread until all derivations froze: tasks/*.json, plan.md, worklog.md (both), every evaluation_criteria / computations / closure / rationale field. No recursive grep touched the tasks directory.
- Step 0: gate snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r1.txt shows EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred by the coordinator. Entry conditions complete.
- Replay harness (scratch): /tmp/audit_ssl_certificate_lifecycle_0076/run.py evaluates each policy's `compute` with the gate's own DSL (`check_compute.build_env`); t0.py / t1.py replay the derived write chains and every baseline substitution.

### policy_conflict_scan
- Base copy: every top-level key of the extended file except `extended_policies` is `==` to products/ssl.yaml (python yaml compare) — verbatim.
- Six extended policies: coterm_order (ssl_order/ssl_purchase_charge, owner=user tool), support_renewal and autorenew_charge (both ssl_renewal_charge + ssl_subscription_extend), names_charge (owner=user tool), wait_credit (ssl_subscription_extend), install_charge.
- Overlap support_renewal vs autorenew_charge on ssl_renewal_charge: partitioned by "A renewal that Harborline support books for the customer during a conversation is a support renewal … every auto-renew charge is priced under the auto-renew charge rule". An auto-renew charge is itself posted by the agent during a conversation, so the partition rests on the "falls due … owed from that day" test; in a world where auto_renew is true and the charge is due and the customer asks for a renewal, both readings exist. Neither task world has that (task 0 sibling auto_renew false; task 1 customer never asks for a renewal) → observation O1.
- Base `ssl_pricing` sentence "The subscription runs from the order date …" is retired by both coterm_order and wait_credit; each replaced_by names the other's case (XF C16 satisfied). Base `ssl_renewal` billing sentence is retired by both support_renewal and autorenew_charge; the scope partition naming all three renewal kinds sits in each policy's first replaced_by, not in the second (observation O2).
- Cross-category read boundaries: account (variant_name, ssl_discount_pct, goodwill ledger), domain (status, auto_renew, nameservers), email (variant_name/status/email_domain) — declared in every `cross_category`.
- Scopes: task 0 = {coterm_order, support_renewal}; task 1 = {install_charge, autorenew_charge, wait_credit, names_charge}; disjoint, jointly complete over the six (to be confirmed against charter_scope after reveal).

### rule_compute_equivalence
- Mechanical sweep: every `compute_basis` quote, every `replaced_by`, every `baseline.rule` and every `policy_source` is a verbatim substring of its rule (whitespace-normalised) — no misses.
- Ladders: every tier named in `factors[].ladder` is a rule sentence and a branch of its binding, and vice versa, for all 28 factors.
- Rounding: every rule says half up; compute uses the DSL `RND` placed where the rule places it (coterm: reduced amount then result; support renewal/autorenew: same; names: per-name part then result; install: reduced then result; wait credit floor via `//`).
- Edge inputs (XF B9/B10) — members found:
  - E1 `mail_variant = CFIELD('email','variant_name', email_domain=F('common_name'), status='active')` vs rule "whose business email for the certificate's common name runs on an active Harborline email subscription": for a common name `www.x.com`, `shop.x.com` or `*.x.com` with mail on `x.com`, the rule grants the credit and compute grants 0. No tie rule for two active email subscriptions on one domain (first match).
  - E2 "latest term line … latest renewal or auto-renew charge line" (support_renewal, autorenew_charge, names_charge `paid_end`): a refunded renewal line still counts in compute (`LATEST(... event_type='ssl_renewal_charge')`) though base ssl_refunds says refunding a renewal brings the end date back by the years it added; the rule never says whether a refunded line is still the "latest term line" (contrast the install-line tests, which say "that no refund line reverses"). In names_charge such a world gives end < paid_end, a case none of the three tiers names.
  - E3 wait_credit `waiting_days` counts the latest passed http_file / approver_email check anywhere in the history; rule framing "where the customer's checks failed first" is not tested (no order check) and a passed check after the first certificate gives a negative wait with no rule tier.
- No empty promise found otherwise.

### action_binding_and_uuids
- Each `(target_tool, computes)` claimed once. uuid8s a53c4704, 0365c0e5, c41e0ea2, 7df48eab, b6002377, 757666ca: distinct, no shared prefix/sequence. No factor id is a substring of a tool name. Docstrings carry no ordering words, no other tool names, no concrete example values; no composite args; every write tool calls ctx.create/update in its own body; amounts >0 / credit_days ≥0 enforced; no tool validates a prerequisite.
- Tool-vs-rule contract (XF 20 member) T1-FUND: autorenew rule "it is paid through the account charter's funding order"; account_credit_spending "Every auto-renew charge in any category tries credit first where credit_first_for_auto_renew is true" (true for every tier) and "Credit pays a charge only when credit_balance covers the whole charge". `charge_certificate_autorenewal_c41e0ea2` hard-codes `payment_method="card"`. In any world where credit_balance ≥ the auto-renew amount the tool cannot write the policy's terminal state, and the owed account:account_credit_apply trigger (another category) is never written.
- Owner check (XF brief item) OWN: blueprint ssl summary: "The agent places orders and renewals, bills added names and installations … while cancelling an order before issuance is the customer's own decision that the customer performs"; base lifecycle has `by: user` only for pending_validation→cancelled. Both owner=user tools — `order_cotermed_certificate_a53c4704` ("Place, as the customer, an order …") and `add_certificate_name_7df48eab` ("Add, as the customer, one further name …") — are acts the scenario constitution assigns to the agent; the cancel-before-issuance act has no tool.

### prerequisite_graph
- Edges: coterm_order → support_renewal (value_input, gate days_left, action); names_charge → autorenew_charge (value_input, days_counted, state); wait_credit → autorenew_charge (state_gate, ssl_holdings.subscription_end_date, state); install_charge → autorenew_charge (value_input, certs_covered, state), → wait_credit (value_input, certs_covered, state), → names_charge (state_gate, ssl_holdings.extra_names, action). support_renewal and autorenew_charge: `[]`.
- All `problem` ids are extended ids, none self, acyclic (sinks support_renewal, autorenew_charge). `policy_source` verbatim in own rule (sweep). `fallback_reason` present exactly on the two action edges. `resolved_by` = depended-on target_tool in all six. value_input gates are real bindings (days_left, days_counted, certs_covered); state_gate gates are real holding fields. No authoring-viewpoint wording.

### prerequisite_sentences
- coterm: "The co-termed charge is not fixed until the sibling subscription has been renewed past its renewal window." Connective "not … until"; action form; no tool/id. Single reading in task 0 (sibling inside the 90-day window, auto_renew false → support renewal). Strength vs condition: the condition demands a renewal line; for a sibling whose end date is already >90 days away the sentence still requires a renewal that base ssl_renewal forbids (outside the window) — scope broader than the business case, no task world hits it (observation O3). Fallback: a state "a renewal line of charge type renewal for the term starting on the old end date" would single the write out (observation O4).
- names: "The added-name charge is fixed only after the subscription's billing carries every auto-renew charge that has fallen due on it." state form; one writer (autorenew tool). PASS.
- wait_credit: "The validation-wait credit is not added until any auto-renew charge due on the subscription stands on its billing." state form; one writer. PASS.
- install: (a) "Before the installation charge is worked out, the subscription's billing must carry any auto-renew charge due on it." (b) "… not fixed until the subscription end date carries every validation-wait credit owed on it." — the end date is moved by both the wait-credit tool and the renewal tools, but "validation-wait credit" names the state uniquely; (c) "… not fixed until every name the receiving server serves has been added to the certificate." action form, fallback justified (names list not recorded). PASS.
- No depended-on rule restates a dependent's sentence; no cross-problem order outside declared edges found.

### override_declarations
- coterm vs ssl_pricing: s1, s2, s5 retired and declared; s3 (billed while pending) and s4 (business only for OV/EV) followed. vs ssl_agg_volume_and_org_reuse: ladder unreachable ("placed on its own"), higher-of rule consistent (non-reseller tiers have ssl_discount_pct 0), org reuse followed. Account cross-charter: account_tier_benefits "it never applies to … proration lines" vs co-termed tier discount on "the day-weighted amount" — a co-termed line is a new-subscription line, observation O5.
- support_renewal vs ssl_renewal: s3/s4 retired and declared; status, window, expired-needs-new-order inherited.
- autorenew vs ssl_renewal: s4/s5 retired and declared; vs ssl_installation: managed re-installation fee (18/30) not declared against "Harborline support installs it for installation_fee" (0.00 on OV/EV products) — observation O6 (different charge line).
- names vs ssl_names: s3 retired/declared ("one name to an order"); s1, s2, s4 inherited; nm_reinstall fee on "the reissue that carries it" while s4 says the name "takes effect on a free reissue" — observation O7.
- wait_credit vs ssl_pricing s5 retired/declared.
- install vs ssl_installation s2 retired/declared; tier discount on the installation fee vs the account charter — see ACCT-SCOPE (cannot be declared here: another category's base).
- Event-meaning members (XF brief: a write bending a base event's stated meaning) EVT:
  - EVT-a coterm: base `ssl_order.subscription_end_date` "Order date plus the subscription years" and `ssl_purchase_charge.period_end` "Subscription end"; the co-termed write records years 1/2/3 by rate class and an end date = sibling's end.
  - EVT-b wait_credit: base `ssl_subscription_extend` "The subscription end date moves: extended by a renewal or brought back by a refunded renewal." — the credit moves it by neither.
  - EVT-c names tier 2: base `ssl_names_charge` "Names added … are billed for the remaining subscription", amount "Prorated amount", period_end "Subscription end date"; tier 2 bills to end date + next_year_days while the tool records period_end = current end date; the next auto-renew/support renewal then bills the same name for the same year again ("plus additional_name_price_per_year times the extra names times the years") — double billing in any world where a name is added 31–90 days before an unrenewed end with auto_renew false or on.

### factor_ladders
| policy | factors (effect) | param / method / cross | notes |
| --- | --- | --- | --- |
| coterm | term_class_co (P), san_bands_co (M), acct_tier_co (P, account), org_reuse_co (P), dom_bundle_co (P, domain) | 4/1/2 | multi-source: san_bands (names AND term), org_reuse (level AND date), dom_bundle |
| support_renewal | term_years_ren (M), acct_tier_ren (P, account), revetting_ren (P), dom_bundle_ren (P, domain) | 3/1 declared, **0 honest** | |
| autorenew | san_bands_ar (M), acct_tier_ar (P), managed_reinst_ar (P), dom_bundle_ar (P), dns_validation_ar (P) | 4/1/3 | |
| names | nm_band_rate (P), nm_paid_period (M), nm_dns_handling (P, domain), nm_reinstall (P), nm_dom_bundle (P, domain) | 4/1/2 | |
| wait_credit | wait_anchor_wc (M), long_wait_wc (P), sla_days_wc (P, account), reg_days_wc (P, domain), goodwill_settle_wc (P, account) | 4/1 declared, **0 honest** | |
| install | inst_cycles_mi (M, domain), repeat_rate_mi (P), acct_tier_mi (P, account), mail_bundle_mi (P, email) | 3/1/3 | |
- Factor independence (XF A1): no factor binding reads another factor's binding (checked binding by binding; assembly only in plain bindings / result). Combination order sentences present in all six (XF A5).
- Ladders ≥3 tiers, disjoint, boundaries stated (XF A8): all pass as stated.
- Method-shape all-pairs (XF A6) — SHAPE:
  - term_years_ren: tiers (price_3yr_per_year + n·r)·3, (price_2yr_per_year + n·r)·2, price_1yr + n·r — one combination of the same inputs with a substituted tariff value and a constant multiplier; all three pairs FAIL → a parameter factor labelled method; support_renewal has 0 method factors.
  - wait_anchor_wc: tier 1 DAYS(LATEST passed http_file check, first cert) and tier 2 DAYS(LATEST passed approver_email check, first cert) are the same aggregate of the same field (ssl_events.event_at) under a different filter → pair 1/2 FAILS; only 2 distinct methods remain (<3 tiers) → wait_credit has 0 method factors.
  - san_bands_co / san_bands_ar (added breakpoint), nm_paid_period (different field period_end vs end date; added tariff next_year_days), inst_cycles_mi (subscription_end_date vs dcv_validated_date+reuse vs constant 1): PASS.
- Realism (XF D18) — UNREAL (conditions no certificate reseller weighs for that quantity):
  - U1 domain auto-renew flag deciding certificate money: dom_bundle_co (8.00 vs 4.00), dom_bundle_ren (10/5), dom_bundle_ar (9/4), nm_dom_bundle (1.50/0.75) — the "auto_renew true vs false" part of each compound tier.
  - U2 subscription dcv_method while the domain is on Harborline DNS: dns_validation_ar (6 vs 3) and nm_dns_handling (0 vs 2.00) — base ssl_validation: on an active Harborline-DNS domain "DNS validation completes automatically without customer action", so the chosen method does not change the validation work the tier prices.
  - U3 reg_days_wc: a Harborline registration lengthens the validation-wait credit, and Harborline DNS lengthens it more (2 vs 1 days) — the opposite of base (Harborline DNS validates automatically, i.e. shortens waits).
  - U4 sla_days_wc: "the reseller issuance commitment … by the tier recorded on the customer's Harborline account" reads the current tier for a wait that happened at first issuance; account_tier_benefits "Benefits follow the tier recorded on the account on the charge date" — a commitment can only be owed for issuances made while the customer held the tier.
  - Not raised (observations O8): revetting fee, EV/OV reuse credit, repeat-installation rate, mail bundle credit, managed re-install fees — plausible Harborline schedules.
- Account-charter scope ACCT-SCOPE: acct_tier_mi applies ssl_discount_pct to the installation charge; account parameter_schema "ssl_discount_pct: Percent off SSL certificate subscription prices" and account_tier_benefits "A tier discount applies to the list or renewal price component of a charge only; it never applies to … setup fees …".
- Install cycle realism CYCLE: "covers the certificates automatic reissue will put on the same server, counted in installation cycles of max_cert_validity_days_from_2027_03_15 less auto_reissue_days_before_cert_expiry days from today" applies the 100-day limit from today, while base ssl_issuance_and_reissue keeps max_cert_validity_days (200, the real CA/B SC-081 2026 step) until 15 March 2027 — for any today before that date the stated count is not the certificates automatic reissue puts on the server.
- Zero/negative amounts (XF B9/22) ZERO: autorenew, DV Single Domain, Reseller Platinum, 1-year term, active auto-renew Harborline-DNS domain, dns_cname, no install line: RND(19.99·0.75)=14.99, −9 −6 = −0.01; names tier 1 (end date beyond paid end by credit days, paid end ≤ ~36 days away, Harborline DNS + dns_cname, no install, auto-renew domain): per-name part <1.50 minus 1.50 → negative. Every tool refuses amount ≤ 0; no rule tier covers it.
- Counts: every task's computations carry ≥1 multi-source and ≥1 cross_difficulty factor (task 0: acct_tier_co/ren, dom_bundle_*; task 1: acct/domain/email factors).

### findings
| id | verdict | summary | tasks |
| --- | --- | --- | --- |
| OWN | SOURCE-CHAIN RED | both owner=user tools are acts the blueprint gives the agent | 0, 1 |
| EVT | SOURCE-POLICY RED | co-termed order, wait credit and names tier 2 bend base event meanings (EVT-a/b/c) | 0 (a), 1 (b), charter (c) |
| SHAPE | SOURCE-FACTOR RED | term_years_ren and wait_anchor_wc are not methods; support_renewal and wait_credit have 0 honest method factors | 0, 1 |
| UNREAL | SOURCE-FACTOR RED | U1–U4 conditions no reseller weighs | 0 (U1), 1 (U1–U4) |
| ACCT-SCOPE | SOURCE-POLICY RED | tier discount on installation fee contradicts account charter | 1 |
| CYCLE | SOURCE-POLICY RED | 70-day cycles before 2027-03-15 contradict base 200-day validity | 1 |
| FUND | SOURCE-POLICY RED | auto-renew tool hard-codes card against the credit-first funding order | charter |
| ZERO | SOURCE-POLICY RED | producible worlds give non-positive autorenew / names charges | charter |
| EDGE | SOURCE-POLICY RED | E1 mail-domain match, E2 refunded renewal as latest term line, E3 unordered/negative http_file anchor | charter |
| SEED | SOURCE-FACTOR RED | seeded history not producible under the in-force charter (per-task detail in 0.md / 1.md) | 0, 1 |
Observations O1–O8 above.

## closing_checklist
- Written after both reveals. Per-task files 0.md, 1.md correspond to tasks 0.json, 1.json; scopes disjoint and jointly complete over the six extended policies; uuid8s independent; prerequisite graph acyclic; every tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges and an owner=user tool.
- Not closed: both tasks carry REDs (see task files) and the charter REDs listed under findings stand; instantiation gates not re-run by this auditor (coordinator's snapshot only).
- Stale-proof note (XF 27): task 1 prerequisite_closure.order_uniqueness asserts an identical terminal state for both orders of the wait credit and the added name; false (see 1.md).

VERDICT revision_1: task0=RED task1=RED charter=OWN,EVT,SHAPE,UNREAL,ACCT-SCOPE,CYCLE,FUND,ZERO,EDGE,SEED

## revision_2

## charter_global_frozen
- r2 inputs: `ssl.extended.yaml` 254d20d6b2286efa75cb845f23ff91328bf99966d63a0e1c0c0860e6192519ad, `task_tools.py` 95cc9402246323b054a32085d5ef14c8794c5b757cf8ab0db7c57f997aa49871 — both changed since r1, so every charter-global section below is re-derived (r1 text above left untouched). Views 0.view e4269286…4639, 1.view cfce8829…021f. Gate snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r2.txt (run by this auditor via snapshot.sh, script source not read): EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK. Worklog tail confirmed "REWORK round 2: gates 7/7 green"; only its "REWORK round 2 claims" section was read (item ids, no figures). owner_ruling.md read and applied.
- Written before either r2 task file was opened.

### policy_conflict_scan
- Base copy verbatim (yaml compare, no key differs).
- Six policies: install_charge (holder pays at checkout), support_renewal (holder, checkout), secondkey_order (holder, checkout), autorenew_charge (agent, stored card), names_charge (holder, checkout), wait_credit (agent). Renewal partition support/auto-renew/dashboard unchanged (O1 stands, no world asks for a renewal while one falls due). ssl_pricing s5 retired by secondkey and wait_credit, each naming the other (XF C16 ok).
- Scopes (pre-reveal): task 0 {install, support_renewal}, task 1 {secondkey, autorenew, names, wait_credit} — disjoint, cover all six.

### rule_compute_equivalence
- Mechanical sweep: every compute_basis quote, replaced_by and policy_source verbatim in its rule; secondkey's baseline.rule is two non-adjacent rule sentences, each verbatim. Every ladder tier is a rule sentence and a compute branch.
- Install reissue cover: an independent simulation of the rule sentences agrees with compute on 6000 random worlds whose end date lies more than 90 days ahead (the only worlds the policy prices, because a subscription inside its renewal window must be renewed first). It disagrees only when today is within 30 days of the end and an already-due reissue would precede it (compute 1, rule 2) — unreachable under the install prerequisite → observation E4.
- E1 (mail match) closed: every mail factor keys on domain_id + status + family. E2 closed: refunded renewal lines stated in autorenew and names. E3 closed: anchor only from a pass not later than the first certificate.
- E5 (new) secondkey: "runs … for the whole years from the order date to the sibling's subscription_end_date, at least one and at most max_subscription_years, so that it ends no later than the sibling" — when the sibling ends less than a whole year ahead and no auto-renew is due (auto_renew false, end 200 days away), "at least one" gives a 1-year subscription that ends after the sibling, contradicting "so that it ends no later than the sibling"; compute takes MX(1, …). Two readings (order 1 year / no second-key order possible).

### action_binding_and_uuids
- Tools: autorenew c41e0ea2 (agent), wait credit b6002377 (agent), renew 0365c0e5 (user), install 15b30562 (user), second-key 9d8b09ff (user), names 7df48eab (user). uuid8s distinct and unpatterned; no factor id is a tool-name substring; one enumerated arg per field (checkout_method card|paypal); no example values; every write calls ctx.create/update; amounts > 0 enforced; no prerequisite checks.
- EVT-a closed: second-key tool sets end = today + years and the purchase line's period_end the same. EVT-c closed: no names tier bills past the end date; the tool's period_end = end date.
- FUND closed: autorenew rule now sends charges the credit balance covers to the account's credit run and books the rest "in full to the default card on file under this rule", matching the card-only tool (observation: in a covered world the dependents wait on that run).
- OWN closed under owner_ruling.md (b): each holder tool's rule says the holder pays "personally at Harborline's secure checkout, by a card or PayPal account entered there, once the agent has quoted"; personas show the necessity (task 0 expired stored card; task 1 PayPal not on file).
- PAY (new): the same checkout sentences restrict payment to "a card or PayPal account entered there"; account_credit_spending: "for a purchase made in conversation credit is used only when the customer chooses it" — a holder who chooses account credit (balance covering the charge) has a base-charter right the extended rules deny. No task world has such a choice (both personas decline credit) → charter-level.

### prerequisite_graph
- install → support_renewal (value_input, certs_covered, action); secondkey → autorenew (value_input, sk_years, state), → names (value_input, n_extra, action); names → autorenew (value_input, days_counted, state), → wait_credit (state_gate, subscription_end_date, state); wait_credit → autorenew (state_gate). Acyclic; ids valid; fallback_reason exactly on the two action edges; resolved_by = target tools.

### prerequisite_sentences
- install: "A managed installation charge on a subscription inside its renewal window is not fixed until the subscription has been renewed past that window." Scope now limited to subscriptions inside the window (O3 closed). Fallback still avoidable by the state "a renewal line of charge type renewal for the term starting on the old end date" (O4 stands).
- secondkey (a) state form, single writer (auto-renew); (b) action, fallback justified (server names unrecorded).
- names (a) state form; (b) "The added-name charge is not fixed until the subscription end date carries any validation-wait credit that came due with its renewal." state form, single writer (credit tool) — pins credit → name (r1 T1-ORDER closed).
- wait_credit: state form.
- O9 (new, observation): wait_credit's rule "Harborline adds it … together with the first renewal or auto-renew charge billed on the subscription" also times the credit after a support renewal, an order with no declared edge; no task world earns a credit and takes a support renewal.

### override_declarations
- install: ssl_installation s2 retired/declared; zero-fee products carved out; reissue schedule restates base (200 days before 15 March 2027, 100 after) — CYCLE closed.
- support_renewal: ssl_renewal s3/s4 retired/declared; early-renewal promotion and tier "single higher" consistent with account_tier_benefits; managed re-install fee vs base installation_fee (O6 stands, observation).
- secondkey: ssl_pricing s1, s2, s5 retired/declared; ssl_agg higher-of consistent.
- autorenew: s4/s5 retired; tier on the due date matches account "Benefits follow the tier … on the charge date".
- names: ssl_names s3 retired; no tier discount (account: never on proration lines) — consistent.
- wait_credit: ssl_pricing s5 retired; EVT-b stands: the credit write uses ssl_subscription_extend, whose base meaning is "extended by a renewal or brought back by a refunded renewal"; adding it "together with" a renewal does not make it a renewal (reworker concedes the residual).
- ACCT-SCOPE closed: no tier discount on installation.

### factor_ladders
| policy | factors (effect, cross) |
| --- | --- |
| install | reissue_cover_mi (M), repeat_rate_mi (P), mail_bundle_mi (P, email), renew_bundle_mi (P), dns_check_mi (P, domain) |
| support_renewal | discount_family_ren (M, account), mail_bundle_ren (P, email), dns_bundle_ren (P, domain), managed_reinst_ren (P) |
| secondkey | san_bands_sk (M), acct_tier_sk (P, account), org_reuse_sk (P), dcv_reuse_sk (P), mail_bundle_sk (P, email) |
| autorenew | san_bands_ar (M), acct_tier_ar (P, account), revetting_ar (P), dns_bundle_ar (P, domain), mail_bundle_ar (P, email) |
| names | nm_band_rate (P), nm_paid_period (M), nm_dns_handling (P, domain), nm_org_vetting (P), nm_mail_bundle (P, email) |
| wait_credit | wait_anchor_wc (M), long_wait_wc (P), sla_days_wc (P, account), goodwill_settle_wc (P, account) |
- Independence (XF A1): no factor reads another factor's binding; assembly only in plain bindings/result; combination-order sentences present.
- Shape all-pairs (XF A6): reissue_cover (schedule to end / schedule capped at dcv+reuse / constant 1), san_bands_sk/ar (added breakpoints), nm_paid_period (period_end / cert_expiry input / end date), wait_anchor_wc (http_file pass event_at / org_validated_date / opened_date) — all pairs PASS.
  - SHAPE (r2 member): discount_family_ren tiers "the tier's own ssl_discount_pct", "early_renewal_pct", "no discount" are one combination (list × (100 − p)/100) with p a tier-selected value or a constant — exactly the shape the charter labels `parameter` in acct_tier_sk/acct_tier_ar; only the max-pick tier differs. Two distinct shapes in four tiers → not a method; support_renewal has 0 honest method factors.
- Realism (XF D18): U1–U4 closed (no domain auto-renew split, no DCV-method split under Harborline DNS, no registration days, commitment tier read on the purchase date).
  - U5 (new member): a mail bundle credit is attached to every certificate charge — second-key 5.00/2.50, support renewal 4.00/2.00, auto-renew 5.00/2.50, installation 3.00/1.50, added name 8%/4% — each policy's cross-difficulty email factor. In r1 a single installation bundle credit was recorded as observation O8; replicated as a standing credit on every charge type with five different amounts and no cost basis for the certificate work, it is padding no certificate reseller publishes.
  - Observations: renew_bundle_mi (renewal 2.50 vs auto-renew 1.50 billed today) is a weak split and its tier rests on the prerequisite's own write; dns_check_mi / dns_bundle_* external-nameserver tiers are a registration bundle credit under a DNS-check label.
- ZERO (r2 residual member): names tier 1 "where the subscription end date lies beyond the period_end of the latest term line … the days count from today to that period_end" — when today lies inside the credited days (auto_renew false, paid end passed, credit days remaining), DAYS(today, period_end) ≤ 0 → per-name part ≤ 0; on a Harborline-DNS DV Multi-Domain with no vetting fee the charge is ≤ 0.00 and the tool refuses it; no rule tier covers it ("No name is added on the subscription end date itself" carves out only the end date). Other policies: fixed credits now stay below the smallest list amounts (checked: autorenew ≥ 3.99, support renewal ≥ 7.99, second-key ≥ 1.99, install ≥ 4.99).
- Counts: every policy 4–5 factors with ≥2 parameter and 1 method declared (support_renewal fails on honesty, SHAPE); multi-source and cross-difficulty factors present in each task.

### findings (r2)
| id | verdict | status vs r1 | tasks |
| --- | --- | --- | --- |
| OWN | closed (ruling b) | closed | — |
| EVT | SOURCE-POLICY RED | a, c closed; b remains | 1 |
| SHAPE | SOURCE-FACTOR RED | term_years_ren / wait_anchor_wc closed; new member discount_family_ren | 0 |
| UNREAL | SOURCE-FACTOR RED | U1–U4 closed; U5 mail bundle padding | 0, 1 |
| ACCT-SCOPE, CYCLE, FUND | closed | closed | — |
| ZERO | SOURCE-POLICY RED | autorenew member closed; names tier-1 member remains | charter |
| EDGE | SOURCE-POLICY RED | E1–E3 closed; new E5 second-key term vs sibling end | charter (task 1's opening world is an E5 world, resolved by the auto-renew) |
| SEED | SOURCE-FACTOR RED | task 0 closed; task 1 missing 2026-12-02 tier review | 1 |
| PAY | SOURCE-POLICY RED | new | charter |
| HINT | SOURCE-CHAIN RED | new (task file 1.md) | 1 |

## closing_checklist (r2)
- Written after both r2 reveals. Files 0.md / 1.md carry revision_2 with frozen derivation, comparison and findings; scopes disjoint and complete; uuid8s independent; graph acyclic; tree sizes 1 and 3 with 1 and 3 value_input edges and owner=user writes accepted under the ruling.
- Gold matches the blind derivation in every write, argument and factor figure in both tasks; the remaining REDs are charter/world defects, not solution mismatches.
- Final sweep of every class raised in r1 or r2 across all six policies and both worlds: OWN (4 holder tools, ruling b) clean; EVT b only; SHAPE all method factors re-tabled, discount_family_ren only; UNREAL U1–U4 none left, U5 in all five priced policies; ACCT-SCOPE every discount application checked, clean; CYCLE clean (probe); FUND clean; ZERO all six minima checked, names tier 1 only; EDGE E5 only (E4 unreachable); SEED task 1 tier review only; PAY all four checkout rules; HINT task 1 persona only (task 0 persona conditional only).
- Gates: coordinator snapshot r2 7/7 OK; not re-run otherwise.

VERDICT revision_2: task0=RED task1=RED charter=EVT,SHAPE,UNREAL,ZERO,EDGE,SEED,PAY,HINT

## revision_3

## charter_global_frozen
- r3 inputs: `ssl.extended.yaml` dcb55a86cad0debb7aba0de0a38bfbb0707a0fe1131ce16a93cfeea0666efec1, `task_tools.py` 94d6fc077b025194519e87c4ab1eae93503bab1b5e1cb42f077a1ce7d7c02dbb (both changed → all charter-global sections re-derived; copies kept in /tmp/audit_ssl_certificate_lifecycle_0076/r3/). Views 0.view e4269286…4639 (unchanged), 1.view 9c64548d…dee5 (rebuilt). Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r3.txt: 7/7 OK. Worklog tail "REWORK round 3: gates 7/7 green" confirmed; only the round-3 claims section read. Written before either r3 task file was opened.

### policy_conflict_scan
- Base copy verbatim. Policies: install, support_renewal, secondkey, autorenew, names, wait_names (new; replaces wait_credit). ssl_names' proration sentence is retired by both names and wait_names; each replaced_by names the other's case ("Apart from complimentary names …" / "apart from complimentary names, every added name is billed under the added-name rule …") — XF C16 ok. Scopes: task 0 {install, support_renewal}; task 1 {secondkey, autorenew, names, wait_names}.

### rule_compute_equivalence
- Sweep: every compute_basis quote, replaced_by, baseline sentence and policy_source verbatim. Ladders match compute branches.
- E5 closed: "A second-key order is placed only where the sibling runs at least one whole year from the order date … where the sibling runs less than a whole year no second-key order is priced or booked"; compute result 0 when sk_years < 1.
- E6 (new): wait_names "is owed a validation-wait compensation once, while its billing carries no added-names line" — the grant (grant_complimentary_names_f9ed3e27) writes no billing line and no event, only a higher extra_names; after it the rule's own test still reports the same names owed (replay: 3 owed before and after the grant) until a paid name is billed. In any world where the grant is made and no paid name follows (holder abandons checkout), the records invite a second grant; "once" has no record. The names prerequisite sentence "The added-name charge is fixed only after the subscription carries every complimentary name owed on it." therefore waits on a state no record shows.

### action_binding_and_uuids
- Tools: autorenew c41e0ea2 (agent, card), grant f9ed3e27 (agent, no charge, new), renew 0365c0e5, install 15b30562, second-key 9d8b09ff, names 7df48eab (holder, checkout card|paypal). uuid8s distinct, no factor-id substrings, no example values, one enum per field, every write in its own body, positive/≥1 guards, no prerequisite checks. The end-date credit tool is gone.
- PAY closed: the four checkout rules each add "where the holder chooses account credit and the credit balance covers the whole charge, the account's credit run books … and it is not booked under this rule" (matches account_credit_spending).
- OWN, FUND: unchanged, closed.

### prerequisite_graph / prerequisite_sentences
- install → support_renewal (value_input, action; O4 stands); secondkey → autorenew (state), → names (action, fallback justified); names → autorenew (state), → wait_names (state_gate, "carries every complimentary name owed" — see E6); wait_names → autorenew (state_gate, state). Acyclic; fields consistent.

### override_declarations
- EVT closed: no write moves subscription_end_date except renewals; complimentary names use ssl_names_update ("The number of extra names on a multi-domain certificate changes"), restricted to multi-domain products within max_names.
- Other declarations as r2 (support renewal promotion now covers the certificate price only; multi-year name rate declared inside the retired billing sentences of autorenew and secondkey).

### factor_ladders
| policy | factors |
| --- | --- |
| install | reissue_cover_mi (M), repeat_rate_mi, mail_bundle_mi (email), renew_bundle_mi, dns_check_mi (domain) |
| support_renewal | discount_family_ren (M, account), mail_bundle_ren (email), dns_bundle_ren (domain), managed_reinst_ren |
| secondkey | san_bands_sk (M), acct_tier_sk (account), org_reuse_sk, dcv_reuse_sk, name_term_rate_sk |
| autorenew | san_bands_ar (M), acct_tier_ar (account), revetting_ar, dns_bundle_ar (domain), name_term_rate_ar |
| names | nm_band_rate, nm_paid_period (M), nm_dns_handling (domain), nm_org_vetting, nm_term_rate |
| wait_names | wait_anchor_cn (M), long_wait_cn, sla_days_cn (account), goodwill_settle_cn (account) |
- SHAPE closed: discount_family_ren now {max-pick on the whole list, whole list × tier pct, promotion on price_1yr only with names unreduced, none} — all pairs distinguished (split base / max op / nothing tier with no other zero tier). Other method factors pass as in r2.
- UNREAL: U1–U4 closed. U5 closed as a class: mail credits remain only on support renewal and installation (observation, as r1 O8). New members:
  - U6 nm_term_rate: "where more than nm_three_year_days days remain to the subscription end date it is multiplied by price_3yr_per_year divided by price_1yr" — the multi-year rate follows the days remaining, not the term the name is bought into; nm_paid_period's own tier says "the name joins that renewed term", and autorenew prices names for that same renewed term at the term's own rate (name_term_rate_ar by the renewed years). A name joining a two-year renewed term with 31 extra days left gets the three-year rate no term of the subscription carries.
  - U7 nm_paid_period tier 1: "the days count from today to that period_start plus days_per_year for each year the line covers" — when the line "still ends on the subscription end date", this is the baseline span (today to the end date) minus any 29 February inside it; the tier is a leap-day convention presented as a method, and on a leap-free span it equals the baseline exactly.
- ZERO closed: credited-days tier gone; minima re-checked (names ≥ 0.04, second-key ≥ 6.99, autorenew ≥ 8.99, support renewal ≥ 9.99, install ≥ 4.99; zero complimentary names not booked).
- Counts: 4–5 factors each, ≥2 parameter, 1 method; multi-source and cross-difficulty per task present.

### findings (r3)
| id | verdict | status | tasks |
| --- | --- | --- | --- |
| EVT, SHAPE, ZERO, SEED, PAY, HINT, OWN, ACCT-SCOPE, CYCLE, FUND | closed | closed in r3 (or earlier) | — |
| UNREAL | SOURCE-FACTOR RED | U1–U5 closed; new U6 (multi-year name rate by days left), U7 (leap-day counting tier) | 1 |
| EDGE | SOURCE-POLICY RED | E1–E5 closed; new E6 (complimentary-names dedup has no record) | 1 (charter) |

## closing_checklist (r3)
- After both r3 reveals: gold equals the blind derivation in every write, argument and factor figure in both tasks. Task 0 passes all four relationships. Task 1 carries U6, U7 and E6.
- Final sweep of every class raised in r1–r3 across all six policies and both worlds: OWN (4 holder checkout tools + 2 agent tools) clean; EVT clean (no end-date credit; names/second-key period fields true); SHAPE clean (all method factors all-pairs); UNREAL U1–U5 clean, U6 and U7 present (names policy only); ACCT-SCOPE clean (tier pct only on purchase/renewal list amounts); CYCLE clean; FUND clean; ZERO clean (minima re-checked); EDGE E1–E5 clean, E6 present (wait_names); SEED clean (both ledgers reproduce, tier review rows complete); PAY clean (all four checkout rules); HINT clean (both personas).
- Gates: coordinator snapshot r3 7/7 OK.

VERDICT revision_3: task0=PASS task1=RED charter=UNREAL,EDGE

## revision_4

## charter_global_frozen
- r4 inputs: `ssl.extended.yaml` 402fd93e04fbc969a9c2b0dc13d227c94e14de507e93e22608e1d50f7a7be4da, `task_tools.py` 007b7434102038b2f8184e2bf4f82d0725c688967303d0317b69219d218cdf61; views unchanged (e4269286…, 9c64548d…). Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r4.txt 7/7 OK; worklog tail "REWORK round 4: gates 7/7 green" confirmed; round-4 claims section read (ids only). yaml compare against the r3 copy: base section, install, support_renewal, secondkey, autorenew identical → their r3 conclusions carried by reference; names_charge and wait_names changed → re-derived below. Tools: only grant_complimentary_names_f9ed3e27 changed. Written before tasks/1.json r4 was opened.

### re-derived sections (names_charge, wait_names, grant tool)
- Sweep: compute_basis, replaced_by, baseline sentences, policy_source all verbatim; no factor-id substring in tool names.
- Grant tool: now writes an ssl_issuance (kind reissue) row and moves cert_issued_date/cert_expiry_date (base ssl_issuance → ssl_cert_update, same category); takes cert_expiry_date (YYYY-MM-DD, > today) — one fixed-format arg, no example values. Free (reissue_fee 0); base gates (issuable status, dcv_fresh, org_validation_fresh, max_reissues_per_30d) are the agent's to check, the tool checks none.
- E6 closed: wait_names is owed "while its service history shows no issuance of kind reissue and its billing carries no added-names line"; after the grant the rule's own test reports nothing owed, and the names prerequisite ("carries every complimentary name owed") reads the recorded reissue. The rule's lapse clause (any reissue or added-names line ends the compensation) is stated.
- U6 closed: nm_term_rate follows the years of "the purchase, renewal or auto-renew charge line whose period_end is the subscription end date".
- U7 tier removed; its substance moved into nm_renewal_join (below).
- New members:
  - ACCT-SCOPE (regressed): nm_renewal_join prices a name joining a renewal "at the added name's yearly price reduced by the ssl_discount_pct of the tier recorded on the customer's Harborline account" (tiers 1 and 2), booked as an ssl_names_charge line ("Prorated amount", name_addition_proration_basis); account_tier_benefits: "A tier discount applies to the list or renewal price component of a charge only; it never applies to … proration lines". Tier 2 ("already begun … the reduced yearly price times the calendar days from today to the subscription end date divided by days_per_year") is a proration by its own words.
  - SHAPE: nm_renewal_join tiers 2 ("reduced yearly price × days to end / 365") and 3 ("yearly price × days to end / 365") are one formula with and without (1 − ssl_discount_pct) — the acct_tier shape the charter labels parameter, and identical for non-reseller accounts; tier 1 ("each year the line covers … plus the days from today to that period_start prorated") equals tier 3's span for a non-reseller except for 29 February. The method's distinguishing effects are a tier percentage and a leap-day convention (the r3 U7 substance); names_charge has 0 honest method factors.
  - INDEP (XF A1/A2): nm_renewal_join's binding per_name_part reads year_name_price = nm_rate × name_ratio, the outputs of nm_band_rate and nm_term_rate; the factor owns the assembly of the amount.
- Observation O10: the grant records its reissue, while add_certificate_name_7df48eab says the paid name "goes onto the certificate with a free reissue" and records none.

### carried classes (unchanged policies, r3 conclusions by reference)
- OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED: closed in r3; re-swept on the changed policies — no new member (names minimum > 0; grant writes ssl_issuance/ssl_cert_update as their base meanings state; checkout credit-run clause still present in names).
- U1–U5, E1–E5 closed.

### findings (r4)
| id | verdict | tasks |
| --- | --- | --- |
| ACCT-SCOPE | SOURCE-POLICY RED (regression in names_charge) | 1 |
| SHAPE | SOURCE-FACTOR RED (nm_renewal_join) | 1 |
| INDEP | SOURCE-FACTOR RED (nm_renewal_join reads two factors' outputs) | 1 |
| UNREAL, EDGE | closed (U6; U7 tier removed, substance under SHAPE; E6) | — |

## closing_checklist (r4)
- Gold equals the blind derivation in both tasks. Task 0 PASS (carried, gold unchanged). Task 1 RED on three names_charge items.
- Final sweep of every class raised in r1–r4 across all six policies and both worlds: OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED clean; UNREAL U1–U7 clean as members (U7's substance now under SHAPE); EDGE E1–E6 clean; SHAPE: all method factors re-tabled — nm_renewal_join fails, the rest pass; ACCT-SCOPE: every tier-discount application re-checked — only names_charge applies one to a proration line; INDEP: every factor's bindings re-read — only nm_renewal_join reads other factors' outputs.
- Gates: coordinator snapshot r4 7/7 OK.

VERDICT revision_4: task0=PASS task1=RED charter=ACCT-SCOPE,SHAPE,INDEP

## revision_5

## charter_global_frozen
- r5 inputs: `ssl.extended.yaml` b44b1678…a459, `task_tools.py` 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r5.txt 7/7 OK; worklog tail "REWORK round 5: gates 7/7 green" confirmed; round-5 claims read (ids only). yaml compare vs the r4 copy: base and five policies identical (r4 conclusions carried by reference); only ssl_ext_names_charge changed; tools differ only in the add-name docstring (O10 closed: "takes effect on the certificate's next free reissue, which this call does not record"). Written before either r5 task file was opened.

### re-derived (names_charge)
- Sweep: compute_basis, replaced_by, baseline sentences, policy_source verbatim; no factor-id substring of a tool name.
- ACCT-SCOPE closed: no tier percentage in the added-name rule; cross_category reads domain only. Re-swept charter-wide: tier pct only on second-key, support-renewal and auto-renew list amounts.
- SHAPE closed: nm_billing_span = {MX(floor, prorated) | ceil(days/365) whole years | prorated}; all pairs distinct. Re-swept: reissue_cover_mi, discount_family_ren, san_bands_sk/ar, nm_billing_span, wait_anchor_cn pass.
- INDEP closed: no factor binding reads another factor's output (per_name_part = RND(MX(name_floor, year_name_price × bill_span), 2) is plain). Re-swept all six policies.
- ZERO: minimum added-name charge nm_min_name_charge 9.99 in the ≤ 90-day tier; every tier > 0.
- EVT (member, regression of r1 EVT-c): nm_billing_span tier 2 "the name is sold in whole name-years for the years left to the subscription end date, a part year counting as a whole year". Any part year bills name-time past subscription_end_date, which base ssl_lifecycle_clock forbids any certificate to outlast, and which the next renewal or auto-renew bills again. It bends base ssl_names_charge ("billed for the remaining subscription"; period_end "Subscription end date").
- COND (new id; prerequisite_graph check 7): ssl_ext_secondkey_order → ssl_ext_names_charge condition "… each carried by an added-names line" is stronger than its policy_source and has been false for every compensated world since complimentary names entered in r3 (they carry no billing line). Missed in my r3/r4 audits; recorded now.

### findings (r5)
| id | verdict | tasks |
| --- | --- | --- |
| ACCT-SCOPE, SHAPE, INDEP | closed | — |
| EVT | SOURCE-POLICY RED (names whole-year rounding past the end date) | 1 |
| COND | SOURCE-POLICY RED (second-key → names condition) | 1 |

## closing_checklist (r5)
- Gold equals the blind derivation in both tasks; task 0 PASS (carried); task 1 RED on EVT and COND.
- Final sweep of every class raised in r1–r5 across all six policies and both worlds: OWN, ZERO, PAY, HINT, CYCLE, FUND, SEED, ACCT-SCOPE, SHAPE, INDEP clean; UNREAL U1–U7 clean; EDGE E1–E6 clean; EVT: only names_charge's whole-year rounding; COND (prerequisite conditions vs their sentences, every edge re-read): only secondkey → names.
- Gates: coordinator snapshot r5 7/7 OK.

VERDICT revision_5: task0=PASS task1=RED charter=EVT,COND

## revision_6

## charter_global_frozen
- r6 inputs: `ssl.extended.yaml` 9f575223…eb72, `task_tools.py` unchanged 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r6.txt 7/7 OK; worklog tail "REWORK round 6: gates 7/7 green" confirmed; round-6 claims read (ids only). yaml compare vs r5: base, install, support_renewal, wait_names identical; secondkey, autorenew, names re-derived. Sweep (compute_basis, replaced_by, baseline sentences, policy_source verbatim; factor-id substrings) clean. Written before either r6 task file was opened.

### re-derived (secondkey, autorenew, names)
- EVT closed: names schedule "no added name is ever billed beyond the subscription end date"; nm_billing_span = {MX(floor, prorated) | MN(prorated, yearly × renewal years) for an unstarted renewal line | prorated} — every tier ends at the end date; shapes distinct; INDEP holds (factor decides name_floor and cap_years; per_name_part plain).
- COND closed: secondkey → names and names → wait_names conditions now match their sentences; every condition re-read.
- Component-wise tier percentage in autorenew and secondkey: price and full-rate names take the tier percentage; banded names take MX(band reduction, tier pct), never compounded — matches account_tier_benefits. Compute: banded/b1/b2/full_names, tier_part, band_part, reduced_amount = RND(tier_part × (100 − pct)/100 + band_part, 2), as the rule's combination sentence states.
- ACCT-SCOPE (new member, in the unchanged support_renewal; present since r3, missed by me in r3–r5): the rule says the early-renewal promotion "covers the certificate price only and never the extra names", then "where both apply, the list amount is reduced by the single higher of the tier percentage and the promotion"; compute `RND(list_amount * (100 - MX(tier_pct, K('early_renewal_pct'))) / 100, 2)`. For a Bronze account (10%) renewing more than 30 days ahead, the promotion's 15% reaches the extra names it "never" covers. The account charter's per-component single-higher reading gives price_1yr × 0.85 + names × 0.90; e.g. DV Multi-Domain with 12 names: 204.38 vs compute 195.39 before fees. No task world takes this tier (task 0 is a Business Account) → charter-level.

### findings (r6)
| id | verdict | tasks |
| --- | --- | --- |
| EVT, COND | closed | — |
| ACCT-SCOPE | SOURCE-POLICY RED (support_renewal both-apply tier; charter-level) | none (task 0 takes the promotion-only tier) |

## closing_checklist (r6)
- Gold equals the blind derivation in both tasks. Task 0 PASS (carried), task 1 PASS.
- Final sweep of every class raised in r1–r6 across all six policies and both worlds: OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED, SHAPE, INDEP, COND, U1–U7, E1–E6 clean. ACCT-SCOPE: every tier-percentage application re-read; one member remains in support_renewal (promotion reaching the extra names when both schedules apply), charter-level, no task world on that tier.
- Gates: coordinator snapshot r6 7/7 OK.

VERDICT revision_6: task0=PASS task1=PASS charter=ACCT-SCOPE

## revision_7

## charter_global_frozen
- r7 inputs: `ssl.extended.yaml` dd61647fa01d4119c225980cb2ebf21d779f4d90a5bed634ab905f04caf7d335, `task_tools.py` unchanged 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r7.txt 7/7 OK; worklog tail "REWORK round 7: gates 7/7 green" confirmed; round-7 claims read (ids only). yaml compare vs r6: base and five policies identical; only ssl_ext_support_renewal changed (rule, compute, compute_basis, factors). Sweep (compute_basis, replaced_by, baseline sentences, policy_source verbatim) clean. Written before the r7 reveal.

### re-derived (support_renewal)
- ACCT-SCOPE closed: both-apply tier now reads "price_1yr is reduced by the single higher of the tier percentage and the promotion, the two never being added, and the extra names, which the promotion never covers, are reduced by the tier percentage alone"; compute RND(price_1yr × (100 − MX(tier, 15))/100 + names × (100 − tier)/100, 2). Probes on the task-0 world with the tier swapped: Bronze 31 days ahead 204.38 (= the per-component reading I gave in r6), Bronze 20 days ahead 206.88 (tier only), Gold 31 days ahead 183.90 (tier above promotion → whole list at 20%) — rule and compute agree.
- SHAPE: discount_family_ren tiers {split base with max on the price component | whole list × tier | price-only promotion | none} — distinct; for Gold/Platinum the first tier coincides in value with the second but adds the max pick, which moves a Bronze/Silver world (T2) — pass.
- INDEP: reduced_amount reads tier_pct inside the factor's own bindings; unchanged structure.
- Account cross-product sweep, all six policies: tier pct on second-key and auto-renew certificate price and full-rate names (banded names single higher), support renewal per component, none on added names, installation, complimentary names — matches account_tier_benefits.
- Unchanged policies: r6 conclusions carried (EVT, COND, ZERO, OWN, PAY, HINT, CYCLE, FUND, SEED, INDEP, U1–U7, E1–E6 clean).

## closing_checklist (r7)
- Gold equals the blind derivation in both tasks; both PASS on all four relationships.
- Final sweep of every class raised in r1–r7 across all six policies and both worlds: OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED, SHAPE, INDEP, COND, ACCT-SCOPE, U1–U7, E1–E6 — no member remains. Open observations (not grounds for rework): O1 renewal partition, O4 action-form fallbacks (install → support renewal, second-key → names), O6 re-install fee vs installation_fee, O9 credit timing sentence (moot since wait_credit removed), two mail bundle credits, renew_bundle_mi split, external-nameserver credit tiers, E4 unreachable reissue-count edge, complimentary-names application reading.
- Per-task files 0.md / 1.md correspond to tasks 0.json / 1.json; scopes disjoint and jointly complete; uuid8s independent; graph acyclic; trees of 1 and 3 prerequisite problems with 1 and 3 value_input edges and accepted owner=user writes; every factor bears weight against an honest baseline.
- Gates: coordinator snapshot r7 7/7 OK (re-run by the coordinator's script, not by this auditor's own gate commands).

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen
- r8 inputs: `ssl.extended.yaml` 0b6cf81885e8242fa9b857d0ac2508db0e34522f87a975190a0d7f49a7b6ecc7, `task_tools.py` unchanged 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r8.txt 7/7 OK; worklog tail "REWORK round 8: gates 7/7 green" confirmed; round-8 claims read (ids only); renderer findings audits/render_source/ssl_certificate_lifecycle/render_r1.md read. yaml compare vs r7: base and support_renewal identical; install, secondkey, autorenew, names, wait_names changed → re-derived. Written before the r8 reveal.
- Relation to earlier revisions: F1–F4 and F6 are members of XF A1/A2 (assembly sentences naming two factors' quantities; plain bindings rebuilding a factor's ladder), F5 is XF C15 (replaced_by dropping in-force content). They were present in the r6/r7 charters, and I did not raise them in revision_6/revision_7, where I recorded CLEAN.

### renderer findings
- F1 (secondkey) closed: the sentence combining the tier percentage with the bands is gone; "The second-key discount percentage reduces only the certificate price component …, never its extra names"; the bindings banded/b1/b2/full_names/tier_part/band_part are removed; reduced_amount = RND(cert_part × (100 − pct)/100 + names_value, 2), where cert_part and names_value are plain bindings.
- F2 closed: name_term_rate_sk's sentence no longer names the bands.
- F3 (autorenew) closed: the same restructuring as F1/F2.
- F4 (names) closed: nm_band_rate now decides a multiplier (band_mult); "The yearly price of an added name is additional_name_price_per_year with every multiplier that applies to it" — generic.
- F5 closed: replaced_by restores "Every other subscription runs from its order date for the years bought, at most max_subscription_years".
- F6 closed: "Every multiplier of the waiting days acts first, every number of days added to the validation-wait credit is then added, and every percentage share acts on that total, which is rounded down to a whole day".
- A1 closed: install baseline.rule adds "Under that standard charge the per-certificate rate of a managed installation is installation_fee and the certificates covered are the one certificate installed."
- A2 closed: the same-day tie is stated (a renewal line wins over an auto-renew line), matching compute.
- A3: note only.

### XF A1–A3 mechanical sweep (all six policies)
- No factor binding reads another factor's binding. Plain assembly bindings that combine ≥2 factors' outputs, each checked against its basis sentence:
  - install list_amount / priced: baseline-defined terms.
  - support renewal result: generic.
  - secondkey and autorenew names_value / reduced_amount / priced / result: generic.
  - names year_name_price ("every multiplier") and result: generic.
  - wait_names credit_total / credit_days: generic.
- None names two factors' quantities.
- Observation O11: `list_amount` in secondkey and autorenew is now a dead binding (unused).
- Observation O12: base ssl_agg_volume_and_org_reuse says the single higher percentage "applies to a line". The secondkey rule restricts the tier percentage to the certificate price component. I read the base sentence as selecting which percentage, with the retired ssl_pricing reduction sentence having fixed where it applied, so I do not raise this as an undeclared override.

### other classes re-swept on the changed policies
- ACCT-SCOPE: tier percentage only on certificate price components (autorenew, secondkey), per component in support renewal, none on added names, installation or complimentary names; no two percentages on one component. Clean.
- SHAPE, INDEP, EVT, ZERO, COND, OWN, PAY, HINT, CYCLE, FUND, SEED, U1–U7, E1–E6: no new member (verbatim sweep clean; minima positive; conditions unchanged and matching).

## closing_checklist (r8)
- Gold equals the blind derivation in both tasks; both PASS.
- Renderer findings F1–F6 and A1–A2 closed; A3 note only.
- Final sweep of every class raised in r1–r8 across all six policies and both worlds: OWN, EVT, ZERO, PAY, HINT, CYCLE, FUND, SEED, SHAPE, INDEP, COND, ACCT-SCOPE, U1–U7, E1–E6, and XF A1/A2 assembly and C15 overwrite tails. No member remains. Observations O11 and O12, plus those listed in r7.
- Gates: coordinator snapshot r8 7/7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen
- r9 inputs: `ssl.extended.yaml` 2263959a2327d7875e6816e4851835712e3d55e07a97f874c454da5daf66df87, `task_tools.py` unchanged 3fcc53f0…a6e6; view 0 unchanged, view 1 rebuilt (620f16c4…adab). Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r9.txt 7/7 OK; worklog tail "REWORK round 9: gates 7/7 green" confirmed; round-9 claims read (ids only). The latest KB-VERDICT (audits/policy_kb/ssl_certificate_lifecycle/VERDICT.md, revision_2) was read after both task derivations were frozen; its only src item is SR1. yaml compare vs r8: only ssl_ext_support_renewal changed (first rule sentence and the matching replaced_by, the S4 claim).

### SR1
- Closed: the task-1 .ca auto-renew lines and their credit-apply entries now fall 35 days before each 3 April expiry (2024-02-28, 2025-02-27, 2026-02-27), the domain charter's auto_renew_first_attempt_days_before_expiry for .ca. Amounts, funding (card at balance 0 in 2024; credit thereafter, the balance covering) and the ledger sum (906.57) still reproduce. No scored value moves.

### S4 change (support_renewal scope sentence) → new finding SIB
- New support_renewal text: "every auto-renew charge that the account credit balance does not cover in full is priced under the auto-renew charge rule, and an auto-renew charge that the balance covers in full, paid from account credit by the account's credit run, and every renewal bought in the dashboard remain under the base renewal rule, which … bills the tier's price for the years renewed plus the extra names for those years, reduced by the account tier's ssl_discount_pct".
- Unchanged autorenew text (rule sentence 1 and the replaced_by of its overwrite of the base auto-renew sentence): "An auto-renew charge falls due … ; it is owed from that day, and only such a charge is priced under this rule; every support renewal is priced under the support renewal rule, and every renewal bought in the dashboard remains under the base renewal rule …". Its sentence 2 says a covered charge "is paid from account credit by the account's credit run and is not booked under this rule" — it is still priced by this rule's pricing sentences, which speak of "an auto-renew charge".
- Both policies retire the same base ssl_renewal billing sentence (XF C16 sibling tails). Their tails now assign the credit-covered auto-renew charge to different pricing rules: the auto-renew rule's own method, or the base renewal method (whole list including names × years, less the tier percentage). Whether the balance "covers in full" is tested against that same amount, so the two readings also decide whether a charge falls under the credit run at all.
- Demonstrated consequence (producible world): the task-1 sibling with a credit balance of 1720.00. Under the auto-renew rule the charge (1705.98) is covered, goes to the credit run, and nothing is booked by the tool. Under the support rule's base-rule reading the charge (1749.37) is not covered, so it is "charged in full to the default card on file" under the auto-renew rule. Two terminal states. No task world reaches it: task 1's balance 906.57 is short under both readings, and task 0 has no auto-renew → charter-level.
- SOURCE-POLICY RED (SIB).

### re-sweep
- Every class raised in r1–r8, across all six policies (five byte-identical to r8): no other member. The cross-product rule (account_tier_benefits) is unchanged and compliant. Seeded rows of both worlds re-checked against the owning rules as of their dates: .ca dates now correct; .com (task 0) 30 days before expiry correct; email 7 days before term end correct.

## closing_checklist (r9)
- Gold equals the blind derivation in both tasks; both PASS. KB src item SR1 closed.
- The S4 rewrite of support_renewal's scope sentence introduces SIB: two sibling tails assign the credit-covered auto-renew charge to different pricing rules. It is charter-level, with no task consequence.
- Final sweep of every class raised in r1–r9 across all six policies and both worlds: no other member.

VERDICT revision_9: task0=PASS task1=PASS charter=SIB

## revision_10

## charter_global_frozen
- r10 inputs: `ssl.extended.yaml` 58a40ff5…976a, `task_tools.py` unchanged 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r10.txt 7/7 OK; worklog tail "REWORK round 10: gates 7/7 green" confirmed; round-10 claims read (ids only). Resumed after an interruption: nothing of revision_10 was on disk. yaml compare vs r9: only support_renewal (scope sentence + new funding sentence, and the matching replaced_by) and autorenew (scope sentence, funding sentence, replaced_by, account credit_balance read, compute acct_balance / base_price / priced / result) changed.

### SIB
- Closed: the same funding sentence stands verbatim in both rules and both sibling tails. "An auto-renew charge is paid by the account's credit run and priced under the base renewal rule, and is not booked under the auto-renew charge rule, when the account credit balance on the day the charge falls due is at least the base renewal price of that renewal …; otherwise it is charged in full to the default card on file and priced under the auto-renew charge rule." The universal claim "only such a charge is priced under this rule" is gone. Compute: base_price = RND((year_price × years + names × name price × years) × (100 − tier)/100, 2); result 0 when the balance ≥ base_price. This matches the sentence.

### FUND (regression, new member)
- account_credit_spending: "Credit pays a charge only when credit_balance covers the whole charge … Every auto-renew charge in any category tries credit first where credit_first_for_auto_renew is true". credit_first_for_auto_renew is true for every tier.
- The new test compares the balance with the base renewal price, but the charge sent to the card is the auto-renew rule's price, which is usually lower (bands, multi-year name rate, credits). When the balance lies between the two prices, the charge actually made is one the balance covers in full, yet the rule sends it to the card. The account charter requires credit first. The rule also prices the same renewal higher when the customer holds more credit.
- Probe on the task-1 sibling (replay): balance 1720.00 → base price 1749.37 not reached → card charge 1705.98, which 1720.00 covers. Account charter: credit pays it. The reworker's own probe "balance 1720.00 … -> card" is this world.
- No task world reaches it (task 1 balance 906.57 is below both prices; task 0 has no auto-renew) → charter-level SOURCE-POLICY RED.

### re-sweep
- Other four policies byte-identical to r9; classes r1–r9 re-swept on the two changed policies: no other member. Trigger rule: the credit-run branch books nothing through the tool, consistent with the card-only tool.

## closing_checklist (r10)
- Gold equals the blind derivation in both tasks; both PASS. SIB closed.
- The new funding test (balance against the base renewal price) conflicts with the account charter's credit-first rule whenever the balance covers the card-route charge but not the base price → FUND, charter-level.
- Final sweep of every class raised in r1–r10 across all six policies and both worlds: no other member.

VERDICT revision_10: task0=PASS task1=PASS charter=FUND

## revision_11

## charter_global_frozen
- r11 inputs: `ssl.extended.yaml` ab5a2b60…f3ff, `task_tools.py` unchanged 3fcc53f0…a6e6; views unchanged. Snapshot /tmp/erl0076_coord/snap_ssl_certificate_lifecycle_r11.txt 7/7 OK; worklog tail "REWORK round 11: gates 7/7 green" confirmed; round-11 claims read (ids only). yaml compare vs r10: only the funding sentence (rule + matching replaced_by) of support_renewal and autorenew, and autorenew's compute/cross_category, changed. Sweep (compute_basis, replaced_by, baseline sentences, policy_source verbatim) clean.

### FUND
- Closed: both rules and both sibling tails carry "Every auto-renew charge that falls due is priced under the auto-renew charge rule, whatever pays it, and account credit pays it first, following the account charter: where the account credit balance on the day the charge falls due covers that amount in full, the account's credit run books it at that amount from account credit, and otherwise it is charged in full to the default card on file at that amount and booked under the auto-renew charge rule."
- This matches account_credit_spending (credit first for every auto-renew charge, only when the balance covers the whole charge).
- The price no longer depends on the balance: replay on the task-1 sibling gives the same amount at balances 906.57, 1720.00 and 5000.00. The credit_balance read is removed. The card-only tool books only the card-funded case, so no account-category write is needed (trigger rule held).
- SIB stays closed (one sentence in both tails, consistent with each rule's scope sentence).

### re-sweep
- Other four policies byte-identical to r10. All classes raised in r1–r10 re-swept on the two changed policies: no member. Observation carried: in a world where the balance covers a charge falling due today, the dependents wait on the credit run's booking (no task world).

## closing_checklist (r11)
- Gold equals the blind derivation in both tasks; both PASS. FUND closed; SIB stays closed.
- Final sweep of every class raised in r1–r11 across all six policies and both worlds: no member remains. The observations listed in r7, r8 and r11 stand.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
