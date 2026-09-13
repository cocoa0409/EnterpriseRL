# Policy-task audit — storage_accounting / charter-global

## charter_global_frozen

Auditor: independent source auditor /root/audit_source_storage. Round 1; frozen 2026-09-12T17:02:44.004266+00:00.

- storage.extended.yaml SHA256: 6002eac76141a644b421faad1cce4c747bbfd4a98083e3eadce8e19f15ddb331
- task_tools.py SHA256: 1654f2c73ad1272ba1ecbfee74674175e523e752003a7827efc366d91fe887ae
- Permitted: blueprint, schema, shared tool contracts, this extended charter and task tool effects; allowlisted frozen_time/user_scenario/initial_state views only.
- Masked: every original task JSON, evaluation_criteria, computations, scope, closure, solvability, rationale, document requirements, all author worklogs and verification side files. Both tasks must freeze before either reveal.
- contamination_disclosure: none. The supplied gate snapshot was read as entry evidence only; it exposes gate metrics but no scored amounts or sequence arguments.
- Entry evidence: `env/enterprise_cloud_service_accounting/gate_snapshots/source/storage_accounting/round_1_20260912T165837364242Z.txt`: actual command/output pairs include EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; seven EXIT_CODE=0. Gates were not rerun by this auditor. Input-view hashes match supplied manifest hashes. KB traceability deferred by coordinator until render.

### policy_conflict_scan

Base copy is structurally identical to blueprint/products/storage.yaml for every original key and value. All 23 base policies were inspected, including otherwise unclaimed admission, lifecycle, meter, invoice, collection and return provisions. The three cool-storage policies form a source-specific correction branch; the five outage policies form a different service_credit/refund branch. Common storage_review and storage_credit event types are disambiguated by correction versus outage subject and exact source/request. No cross-category mutation occurs: backup contributes an active same-customer/entity committed_quantity; support contributes an active same-customer/entity tier portfolio_discount. Primary price, tax, identity and original-payment boundaries persist except explicitly declared concessions. The complete roots partition 3 + 5 policies; hidden claimed scopes await reveal.

The conflict scan found P1 below in the outage request lifecycle. No demonstrated conflict in the concrete cool-storage source correction was found. Financial amounts, ordinary rounding, untaxed handling and support amount overrides have an internally consistent arithmetic reading; that does not cure P1's divergent terminal states.

### action_binding_and_uuids

Each of the eight target_tool/computes pairs is claimed once. Owners are agent for capacity, billing review, correction, outage assessment, concession and refund; user for outage claim and exact refund authorization. Function bodies are unconditional ctx.update/ctx.create effects and do not inspect or validate any business prerequisite. No hidden prerequisite hint/refusal is implemented. Refund tool specifies ACH; the concrete source uses ACH, so no demonstrated method conflict in the task world.

UUID suffixes: 88579e54, dc2a1af3, 02018d1e, 6a92fd5d, 30bc4acc, cfd2170f, 9b3e6afe, 1b2c5ab5. They are distinct, frozen in the module, and show no common-prefix/adjacent sequence pattern. Independent random-generation provenance cannot be proven from the four audit artifacts; this is an observation, not evidence of reuse.

### prerequisite_graph

Dependent -> prerequisite, all value_input: cool_review -> capacity_entitlement (entitlement); cool_credit -> cool_review (target); outage_review -> outage_claim (claimed); outage_credit -> outage_review (approved); outage_authorize -> outage_credit (credits); outage_refund -> outage_authorize (authorized). Leaves and workflow declare []. Every target is local, nonbase and distinct from its dependent; graph is acyclic with no parallel interfering branches. Every quoted policy_source occurs literally in its rule and every gate names a real compute binding. Conditions match the quoted rule without added restrictions; the referenced tool effect supplies the stated quantity/status. Concrete opening-state and omit-write tests are in each task's own file. P1 means the outage graph's posted-request state cannot simultaneously satisfy inherited request-filing policy.

### findings

#### P1 — SOURCE-POLICY RED; outage request state and occurrence time disagree with inherited filing rule

Symptom: an outage claim and customer refund authorization cannot be filed with one policy-consistent state. Root cause: the extended request policies do not overwrite the base request lifecycle sentence, while downstream calculation assumes posted requests and tools post them without replacing occurred_at.

Verbatim base `policies[id=storage_evt_request].rule`: “Set notice_at and occurred_at to the frozen clock and status pending on filing; cancellation is a new request event with status cancelled linked to the original request.”

Verbatim extended `storage_ext_outage_review.rule`: “Before assessing the outage concession, the customer claim must be filed. Read credited_amount of that posted claim selected by the holding request_id.” Its compute binds claimed with `status='posted'`. Extended `storage_ext_outage_refund.rule`: “Before paying out the concession refund, its exact customer refund authorization must be posted.”

Verbatim tools: claim body sets `status="posted", notice_at=ctx.now()`; authorization body likewise sets `status="posted", notice_at=ctx.now()`. Neither assigns occurred_at. Claim docstring says “The claim becomes posted with the exact claimed USD amount and current notice time”. Authorization docstring says “The selected refund authorization becomes posted with its approved cash amount”.

Neither `storage_ext_outage_claim.overwrite` nor `storage_ext_outage_authorize.overwrite` names storage_evt_request at all. Their overrides cover only service_credit and combination. Thus filing under the inherited rule yields pending/current occurrence time and no contribution to the posted-only claim binding, whereas the executable path yields posted/old occurrence time and a positive contribution. Concrete numerical consequence is demonstrated in task 1; task 0 performs no request filing and is not affected. Affected files: storage.extended.yaml base storage_evt_request and extended outage request/review/refund rules; task_tools.py lines 53–66 and 112–129. First audit, no earlier revision.

Observation: workflow charter does not itself carry requires_external_wait or zero_wait_proof keys. It supplies order_rationale stating completed report/payment and synchronous actions. Required solvability annotations remain masked until all freezes; absent charter keys alone do not demonstrate a real-world wait.

### rule_compute_equivalence

The following binding-level sweep quotes the actual compute_basis and expression for every extended computation. Each quote was checked as literal rule text. Monetary half-up RND occurs at stated result/ceiling/cap boundaries, not on raw inputs. The support band constants 0.1/0.2/0.3 and thresholds 99/95 equal every storage tier's declared descending bands; target is 99.9, cap 0.3. All six storage variants have cool_storage_rate 0.0124, quantity_precision 6 and amount_precision 2. Same-source and same-period selectors, credit subtype exclusions, bank-payment/principal inclusion and signed refund arithmetic agree with the prose. Eligibility refusals remain rule-level decisions, not tool validations. The correspondence does not remove P1.


#### storage_ext_capacity_entitlement

- `measured`: `SUM('storage_events','quantity',event_type='storage_supplemental_meter',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))),meter_code='cool_storage')`
  - Basis: “For a cool-storage correction, sum quantity of completed supplemental cool_storage meters for the holding, the period of the source charge, and the source charge identified by source_event_id of the authorization selected by the holding request_id.”
- `reversed`: `SUM('storage_events','quantity',event_type='storage_meter_reversal',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))`
  - Basis: “Add the signed quantity of posted meter reversals for that same source charge and period.”
- `shared`: `0 if F('payment_status') == 'restricted' else (CFIELD('backup','committed_quantity',status='active',billing_entity=F('billing_entity')) or 0)`
  - Basis: “Read committed_quantity from the active backup contract with the same customer and billing_entity, using zero when absent; this is the shared capacity ceiling in GB-month. When storage payment_status is restricted the shared capacity ceiling is zero instead.”
- `already_used`: `SUM('storage_events','included_quantity_applied',event_type='storage_service_record',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))`
  - Basis: “Subtract included_quantity_applied on completed storage service records for that exact source and period from the shared capacity ceiling.”
- `remaining`: `MX(shared-already_used,0)`
  - Basis: “Floor the remaining shared capacity at zero.”
- `eligible`: `remaining if F('payment_status') == 'clear' else 0`
  - Basis: “A clear storage payment_status permits the remaining shared capacity; a restricted payment_status permits zero.”
- `billable`: `MX(measured+reversed,0)`
  - Basis: “Floor the sum of measured and reversed quantity at zero.”
- `result`: `RND(MN(billable,eligible),P('quantity_precision'))`
  - Basis: “Record the smaller of the resulting billable quantity and eligible remaining capacity, rounded half-up only at the result to quantity_precision decimal places in GB-month.”

#### storage_ext_cool_review

- `measured`: `SUM('storage_events','quantity',event_type='storage_supplemental_meter',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))),meter_code='cool_storage')`
  - Basis: “For a cool-storage correction, sum quantity of completed supplemental cool_storage meters for the holding, the period of the source charge, and the source charge identified by source_event_id of the authorization selected by the holding request_id.”
- `reversed`: `SUM('storage_events','quantity',event_type='storage_meter_reversal',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))`
  - Basis: “Add the signed quantity of posted meter reversals for that same source charge and period.”
- `entitlement`: `SUM('storage_events','quantity',event_type='storage_service_record',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),period=LATEST('storage_events','period',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))`
  - Basis: “Before the corrected cool-storage review is handled, the source-charge shared-capacity entitlement must be completed. Sum quantity on completed storage service records for this exact source charge and source charge period.”
- `shared`: `0 if F('payment_status') == 'restricted' else (CFIELD('backup','committed_quantity',status='active',billing_entity=F('billing_entity')) or 0)`
  - Basis: “Read committed_quantity from the active backup contract with the same customer and billing_entity, using zero when absent; this is the shared capacity ceiling in GB-month. When storage payment_status is restricted the shared capacity ceiling is zero instead.”
- `allowance`: `MN(entitlement,shared)`
  - Basis: “Use the smaller of completed entitlement quantity and the current shared capacity ceiling as the included allowance.”
- `rate`: `P('cool_storage_rate')`
  - Basis: “Use the storage tier cool_storage_rate in USD per GB-month.”
- `quantity`: `MX(measured+reversed-allowance,0)`
  - Basis: “Subtract the included allowance from the sum of measured and signed reversal quantity, then floor at zero.”
- `result`: `RND(quantity*rate,P('amount_precision'))`
  - Basis: “Multiply that remaining quantity by the cool-storage rate and round only the net target half-up to amount_precision decimal places.”

#### storage_ext_cool_credit

- `original`: `SUM('storage_events','amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read the amount of the posted source charge identified by source_event_id of the authorization selected by the holding request_id.”
- `prior_credits`: `SUM('storage_events','amount',event_type='storage_credit',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),source_subtype='correction')`
  - Basis: “Add signed amounts of all posted correction credits for that exact source charge; exclude service-credit concessions.”
- `prior_debits`: `SUM('storage_events','amount',event_type='storage_debit_adjustment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),source_subtype='correction')`
  - Basis: “Add signed amounts of all posted correction debit adjustments for that exact source charge.”
- `target`: `SUM('storage_events','net_amount',event_type='storage_review',status='approved',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),decision='incorrect')`
  - Basis: “Before posting a cool-storage correction, its corrected review must be approved with decision incorrect. Sum net_amount of approved incorrect billing reviews for that exact source charge; the branch admits exactly one current review and no superseded review.”
- `shared`: `0 if F('payment_status') == 'restricted' else (CFIELD('backup','committed_quantity',status='active',billing_entity=F('billing_entity')) or 0)`
  - Basis: “Read committed_quantity from the active backup contract with the same customer and billing_entity, using zero when absent; this is the shared capacity ceiling in GB-month. When storage payment_status is restricted the shared capacity ceiling is zero instead.”
- `rate`: `P('cool_storage_rate')`
  - Basis: “Use the storage tier cool_storage_rate in USD per GB-month.”
- `cap`: `RND(shared*rate,P('amount_precision'))`
  - Basis: “Multiply the shared capacity ceiling by the cool-storage rate and round the resulting maximum correction net amount half-up to amount_precision.”
- `difference`: `MX(original+prior_credits+prior_debits-target,0)`
  - Basis: “Subtract the approved corrected net target from the original amount plus signed prior correction credits and debits, then floor at zero.”
- `result`: `-RND(MN(difference,cap),P('amount_precision'))`
  - Basis: “The correction amount is the negative of the smaller of that overcharge and the maximum correction net amount, rounded half-up to amount_precision; zero makes no new financial write.”

#### storage_ext_outage_claim

- `original`: `SUM('storage_events','net_amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Locate the source charge from source_event_id on the authorization selected by the storage holding request_id, and read net_amount of that exact posted storage charge.”
- `availability`: `LATEST('storage_events','availability_percent',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read availability_percent from the latest completed storage incident linked to that exact source charge; incident chronology is ordered by occurred_at.”
- `band`: `0 if availability >= P('sla_target_percent') else (0.1 if availability >= 99 else (0.2 if availability >= 95 else 0.3))`
  - Basis: “At or above the storage tier sla_target_percent the band is zero; otherwise use the first descending sla_credit_bands fraction whose minimum is no greater than the recorded availability.”
- `partner`: `CPARAM('support','portfolio_discount',status='active',billing_entity=F('billing_entity')) or 0`
  - Basis: “Read portfolio_discount from the tier of the active support contract with the same customer and billing_entity; use zero when no such contract exists.”
- `fraction`: `MN(band+partner,P('credit_cap_fraction')) if band > 0 else 0`
  - Basis: “When the availability band is positive, add the support portfolio_discount to that band and cap the combined fraction at storage credit_cap_fraction; when the band is zero the combined fraction is zero.”
- `ceiling`: `RND(original*fraction,P('amount_precision'))`
  - Basis: “Multiply the original source net amount once by that combined fraction and round the total service-credit ceiling half-up to amount_precision decimal places.”
- `prior`: `-SUM('storage_events','net_amount',event_type='storage_credit',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),source_subtype='service_credit')`
  - Basis: “Subtract the magnitude of signed net_amount on all posted service_credit credits for the exact source charge; correction credits are excluded.”
- `cause`: `LATEST('storage_events','cause',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read cause on the same latest completed source-linked incident.”
- `entitlement`: `MX(ceiling-prior,0) if cause == 'provider_fault' else 0`
  - Basis: “Only provider_fault incidents qualify; subtract prior service-credit magnitude from the total ceiling and floor the additional entitlement at zero, otherwise the additional entitlement is zero.”
- `result`: `RND(entitlement,P('amount_precision'))`
  - Basis: “The customer files the additional entitlement as a nonnegative claimed amount, rounded half-up to amount_precision; the tool records notice_at from the frozen clock immediately.”

#### storage_ext_outage_review

- `original`: `SUM('storage_events','net_amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Locate the source charge from source_event_id on the authorization selected by the storage holding request_id, and read net_amount of that exact posted storage charge.”
- `availability`: `LATEST('storage_events','availability_percent',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read availability_percent from the latest completed storage incident linked to that exact source charge; incident chronology is ordered by occurred_at.”
- `band`: `0 if availability >= P('sla_target_percent') else (0.1 if availability >= 99 else (0.2 if availability >= 95 else 0.3))`
  - Basis: “At or above the storage tier sla_target_percent the band is zero; otherwise use the first descending sla_credit_bands fraction whose minimum is no greater than the recorded availability.”
- `partner`: `CPARAM('support','portfolio_discount',status='active',billing_entity=F('billing_entity')) or 0`
  - Basis: “Read portfolio_discount from the tier of the active support contract with the same customer and billing_entity; use zero when no such contract exists.”
- `fraction`: `MN(band+partner,P('credit_cap_fraction')) if band > 0 else 0`
  - Basis: “When the availability band is positive, add the support portfolio_discount to that band and cap the combined fraction at storage credit_cap_fraction; when the band is zero the combined fraction is zero.”
- `ceiling`: `RND(original*fraction,P('amount_precision'))`
  - Basis: “Multiply the original source net amount once by that combined fraction and round the total service-credit ceiling half-up to amount_precision decimal places.”
- `prior`: `-SUM('storage_events','net_amount',event_type='storage_credit',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),source_subtype='service_credit')`
  - Basis: “Subtract the magnitude of signed net_amount on all posted service_credit credits for the exact source charge; correction credits are excluded.”
- `cause`: `LATEST('storage_events','cause',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read cause on the same latest completed source-linked incident.”
- `entitlement`: `MX(ceiling-prior,0) if cause == 'provider_fault' else 0`
  - Basis: “Only provider_fault incidents qualify; subtract prior service-credit magnitude from the total ceiling and floor the additional entitlement at zero, otherwise the additional entitlement is zero.”
- `claimed`: `SUM('storage_events','credited_amount',event_type='storage_request',status='posted',storage_event_id=F('request_id'))`
  - Basis: “Before assessing the outage concession, the customer claim must be filed. Read credited_amount of that posted claim selected by the holding request_id.”
- `result`: `RND(MN(entitlement,claimed),P('amount_precision'))`
  - Basis: “Approve the smaller of the remaining entitlement and the customer-claimed amount, rounded half-up to amount_precision; record eligible for a positive approved amount.”

#### storage_ext_outage_credit

- `original`: `SUM('storage_events','net_amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Locate the source charge from source_event_id on the authorization selected by the storage holding request_id, and read net_amount of that exact posted storage charge.”
- `availability`: `LATEST('storage_events','availability_percent',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read availability_percent from the latest completed storage incident linked to that exact source charge; incident chronology is ordered by occurred_at.”
- `band`: `0 if availability >= P('sla_target_percent') else (0.1 if availability >= 99 else (0.2 if availability >= 95 else 0.3))`
  - Basis: “At or above the storage tier sla_target_percent the band is zero; otherwise use the first descending sla_credit_bands fraction whose minimum is no greater than the recorded availability.”
- `partner`: `CPARAM('support','portfolio_discount',status='active',billing_entity=F('billing_entity')) or 0`
  - Basis: “Read portfolio_discount from the tier of the active support contract with the same customer and billing_entity; use zero when no such contract exists.”
- `fraction`: `MN(band+partner,P('credit_cap_fraction')) if band > 0 else 0`
  - Basis: “When the availability band is positive, add the support portfolio_discount to that band and cap the combined fraction at storage credit_cap_fraction; when the band is zero the combined fraction is zero.”
- `ceiling`: `RND(original*fraction,P('amount_precision'))`
  - Basis: “Multiply the original source net amount once by that combined fraction and round the total service-credit ceiling half-up to amount_precision decimal places.”
- `prior`: `-SUM('storage_events','net_amount',event_type='storage_credit',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),source_subtype='service_credit')`
  - Basis: “Subtract the magnitude of signed net_amount on all posted service_credit credits for the exact source charge; correction credits are excluded.”
- `cause`: `LATEST('storage_events','cause',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read cause on the same latest completed source-linked incident.”
- `entitlement`: `MX(ceiling-prior,0) if cause == 'provider_fault' else 0`
  - Basis: “Only provider_fault incidents qualify; subtract prior service-credit magnitude from the total ceiling and floor the additional entitlement at zero, otherwise the additional entitlement is zero.”
- `approved`: `SUM('storage_events','credited_amount',event_type='storage_review',status='approved',decision='eligible',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')),request_id=F('request_id'))`
  - Basis: “Before posting the outage concession, the claim assessment must be approved and eligible. Read credited_amount on approved eligible reviews for the exact source charge and this claim request_id; there is exactly one current review for a request.”
- `result`: `-RND(MN(entitlement,approved),P('amount_precision'))`
  - Basis: “Post the negative of the smaller of additional entitlement and the approved claimed amount, rounded half-up to amount_precision; net_amount equals amount and tax_amount is zero.”

#### storage_ext_outage_authorize

- `original`: `SUM('storage_events','net_amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Locate the source charge from source_event_id on the authorization selected by the storage holding request_id, and read net_amount of that exact posted storage charge.”
- `availability`: `LATEST('storage_events','availability_percent',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read availability_percent from the latest completed storage incident linked to that exact source charge; incident chronology is ordered by occurred_at.”
- `band`: `0 if availability >= P('sla_target_percent') else (0.1 if availability >= 99 else (0.2 if availability >= 95 else 0.3))`
  - Basis: “At or above the storage tier sla_target_percent the band is zero; otherwise use the first descending sla_credit_bands fraction whose minimum is no greater than the recorded availability.”
- `partner`: `CPARAM('support','portfolio_discount',status='active',billing_entity=F('billing_entity')) or 0`
  - Basis: “Read portfolio_discount from the tier of the active support contract with the same customer and billing_entity; use zero when no such contract exists.”
- `fraction`: `MN(band+partner,P('credit_cap_fraction')) if band > 0 else 0`
  - Basis: “When the availability band is positive, add the support portfolio_discount to that band and cap the combined fraction at storage credit_cap_fraction; when the band is zero the combined fraction is zero.”
- `ceiling`: `RND(original*fraction,P('amount_precision'))`
  - Basis: “Multiply the original source net amount once by that combined fraction and round the total service-credit ceiling half-up to amount_precision decimal places.”
- `cause`: `LATEST('storage_events','cause',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read cause on the same latest completed source-linked incident.”
- `charges`: `SUM('storage_events','amount',event_type='storage_charge',status='posted')`
  - Basis: “For the refund, sum amount of all posted storage charges on this holding; this is a complete holding balance calculation.”
- `payments`: `SUM('storage_events','amount',event_type='storage_payment',status='posted')`
  - Basis: “Add the signed amount of all posted bank-confirmed storage payments on this holding.”
- `credits`: `SUM('storage_events','amount',event_type='storage_credit',status='posted')`
  - Basis: “Add the signed amount of all posted storage credits on this holding, including the completed outage concession.”
- `refunds`: `SUM('storage_events','amount',event_type='storage_refund',status='posted')`
  - Basis: “Add positive amounts of all posted prior storage refunds on this holding.”
- `returns`: `SUM('storage_events','amount',event_type='storage_payment_return',status='posted')`
  - Basis: “Add positive amounts of all posted bank payment returns on this holding.”
- `debits`: `SUM('storage_events','amount',event_type='storage_debit_adjustment',status='posted')`
  - Basis: “Add positive amounts of all posted debit adjustments on this holding.”
- `balance`: `MX(-(charges+payments+credits+refunds+returns+debits),0)`
  - Basis: “Negate the sum of charges, payments, credits, refunds, returns and debit adjustments, and floor at zero to obtain the cash credit balance.”
- `principal`: `MX(-SUM('storage_events','amount',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))-SUM('storage_events','amount',event_type='storage_refund',status='posted',source_event_id=LATEST('storage_events','storage_event_id',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))-SUM('storage_events','amount',event_type='storage_payment_return',status='posted',source_event_id=LATEST('storage_events','storage_event_id',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))),0)`
  - Basis: “For this procedure the target source invoice has exactly one completed original payment; take the magnitude of that source-linked payment and subtract only posted refunds and returns linked to its payment identifier, then floor at zero. Earlier fully settled invoices do not contribute principal to this payment. A target invoice with several original payments remains under the base allocation procedure.”
- `available`: `MN(balance,principal,ceiling) if cause == 'provider_fault' else 0`
  - Basis: “The maximum refund for the concession request is the smallest of the cash credit balance, the remaining original-payment principal and the total support-adjusted service-credit ceiling. Only a provider_fault incident permits a refund under this concession procedure; otherwise its available amount is zero.”
- `result`: `RND(available,P('amount_precision'))`
  - Basis: “Before authorizing the concession refund, the assessed outage concession must be posted. The customer authorizes the maximum available refund, rounded half-up to amount_precision, after being shown its original-payment destination; the authorization is exact and not a blank mandate.”

#### storage_ext_outage_refund

- `original`: `SUM('storage_events','net_amount',event_type='storage_charge',status='posted',storage_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Locate the source charge from source_event_id on the authorization selected by the storage holding request_id, and read net_amount of that exact posted storage charge.”
- `availability`: `LATEST('storage_events','availability_percent',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read availability_percent from the latest completed storage incident linked to that exact source charge; incident chronology is ordered by occurred_at.”
- `band`: `0 if availability >= P('sla_target_percent') else (0.1 if availability >= 99 else (0.2 if availability >= 95 else 0.3))`
  - Basis: “At or above the storage tier sla_target_percent the band is zero; otherwise use the first descending sla_credit_bands fraction whose minimum is no greater than the recorded availability.”
- `partner`: `CPARAM('support','portfolio_discount',status='active',billing_entity=F('billing_entity')) or 0`
  - Basis: “Read portfolio_discount from the tier of the active support contract with the same customer and billing_entity; use zero when no such contract exists.”
- `fraction`: `MN(band+partner,P('credit_cap_fraction')) if band > 0 else 0`
  - Basis: “When the availability band is positive, add the support portfolio_discount to that band and cap the combined fraction at storage credit_cap_fraction; when the band is zero the combined fraction is zero.”
- `ceiling`: `RND(original*fraction,P('amount_precision'))`
  - Basis: “Multiply the original source net amount once by that combined fraction and round the total service-credit ceiling half-up to amount_precision decimal places.”
- `cause`: `LATEST('storage_events','cause',event_type='storage_incident',status='completed',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))`
  - Basis: “Read cause on the same latest completed source-linked incident.”
- `charges`: `SUM('storage_events','amount',event_type='storage_charge',status='posted')`
  - Basis: “For the refund, sum amount of all posted storage charges on this holding; this is a complete holding balance calculation.”
- `payments`: `SUM('storage_events','amount',event_type='storage_payment',status='posted')`
  - Basis: “Add the signed amount of all posted bank-confirmed storage payments on this holding.”
- `credits`: `SUM('storage_events','amount',event_type='storage_credit',status='posted')`
  - Basis: “Add the signed amount of all posted storage credits on this holding, including the completed outage concession.”
- `refunds`: `SUM('storage_events','amount',event_type='storage_refund',status='posted')`
  - Basis: “Add positive amounts of all posted prior storage refunds on this holding.”
- `returns`: `SUM('storage_events','amount',event_type='storage_payment_return',status='posted')`
  - Basis: “Add positive amounts of all posted bank payment returns on this holding.”
- `debits`: `SUM('storage_events','amount',event_type='storage_debit_adjustment',status='posted')`
  - Basis: “Add positive amounts of all posted debit adjustments on this holding.”
- `balance`: `MX(-(charges+payments+credits+refunds+returns+debits),0)`
  - Basis: “Negate the sum of charges, payments, credits, refunds, returns and debit adjustments, and floor at zero to obtain the cash credit balance.”
- `principal`: `MX(-SUM('storage_events','amount',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))-SUM('storage_events','amount',event_type='storage_refund',status='posted',source_event_id=LATEST('storage_events','storage_event_id',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id'))))-SUM('storage_events','amount',event_type='storage_payment_return',status='posted',source_event_id=LATEST('storage_events','storage_event_id',event_type='storage_payment',status='posted',source_event_id=LATEST('storage_events','source_event_id',storage_event_id=F('request_id')))),0)`
  - Basis: “For this procedure the target source invoice has exactly one completed original payment; take the magnitude of that source-linked payment and subtract only posted refunds and returns linked to its payment identifier, then floor at zero. Earlier fully settled invoices do not contribute principal to this payment. A target invoice with several original payments remains under the base allocation procedure.”
- `available`: `MN(balance,principal,ceiling) if cause == 'provider_fault' else 0`
  - Basis: “The maximum refund for the concession request is the smallest of the cash credit balance, the remaining original-payment principal and the total support-adjusted service-credit ceiling. Only a provider_fault incident permits a refund under this concession procedure; otherwise its available amount is zero.”
- `authorized`: `SUM('storage_events','credited_amount',event_type='storage_request',status='posted',source_subtype='refund')`
  - Basis: “Before paying out the concession refund, its exact customer refund authorization must be posted. Read credited_amount on the posted refund request for this holding; exactly one current authorization is admitted.”
- `result`: `RND(authorized,P('amount_precision')) if authorized <= available and authorized >= P('refund_minimum') else 0`
  - Basis: “For an authorization not exceeding available refund, pay the authorized amount, rounded half-up to amount_precision; an amount exceeding available is refused rather than reduced. Amounts below refund_minimum remain on account.”

### override_declarations

Sentence-level sweep below covers every referenced base rule. Declared sentence replacements are shown explicitly. Other sentences are inherited (including nonapplicable subtype/lifecycle branches); no blanket replacement was assumed. P1 flags the specific inherited sentence contradicted by request effects.

#### storage_evt_category_meters

- “The tier plan_capacity_gb is a pricing-band reference, not free storage or a hard capacity cap.” — Inherited; compatible with applicable extended scope.
- “Primary hot-class quantity is actual GB-month at unit_rate.” — Inherited; compatible with applicable extended scope.
- “cool_storage and archive_storage use cool_storage_rate and archive_storage_rate.” — Inherited; compatible with applicable extended scope.
- “put_requests and get_requests use put_request_rate and get_request_rate per thousand operations; preserve the export quantity_unit thousand_operations and do not treat it as raw operations.” — Inherited; compatible with applicable extended scope.
- “cool_retrieval, archive_retrieval and expedited_retrieval use their correspondingly named rates per GB; a retrieval has exactly one class and urgency, so these rates never stack.” — Inherited; compatible with applicable extended scope.
- “replication and internet_egress use replication_rate and egress_rate per GB.” — Inherited; compatible with applicable extended scope.
- “For cool_early_delete or archive_early_delete, compute the positive remaining calendar dates as the corresponding minimum-days parameter less authoritative age_days, multiply object GB by that remainder divided by actual calendar dates in the deletion month, and use the corresponding storage rate.” — Inherited; compatible with applicable extended scope.
- “Equality with minimum retention incurs no early-deletion charge.” — Inherited; compatible with applicable extended scope.
- “age_days counts UTC date changes from the object creation record to the deletion record; retention is attached to each object version, not its containing bucket.” — Inherited; compatible with applicable extended scope.
- “Replicated and versioned copies are distinct source object references and are metered independently.” — Inherited; compatible with applicable extended scope.
- “For every ancillary meter, multiply the nonincluded measured quantity by its selected rate, then round the net line using amount_precision and rounding_mode and tax under evt_tax.” — Inherited; compatible with applicable extended scope.
- “An allowance is consumed chronologically by interval_start then source_event_id within the named holding and UTC period; reversal of its source returns only that source allocation.” — Inherited; compatible with applicable extended scope.
- “Source subtype supplemental identifies these amounts so the primary discount policy does not apply.” — Inherited; compatible with applicable extended scope.
- “Completed service records prove nonfinancial entitlements; unknown meter codes or units are POLICY_NOT_COVERED instead of guessed prices.” — Declared replacement by storage_ext_capacity_entitlement.
- “These calculations never authorize an unapproved customer-only action.” — Inherited; compatible with applicable extended scope.
- “For included capacities denominated in GB-month, contact-month or package-month, prorate the capacity by actual active interval seconds divided by actual seconds in its UTC month before comparing measured quantity.” — Inherited; compatible with applicable extended scope.
- “Category-specific primary inclusions replace the generic included_quantity where expressly named; they are not added twice.” — Inherited; compatible with applicable extended scope.
- “A mandatory minimum fee is a pricing minimum, not a second charge.” — Inherited; compatible with applicable extended scope.

#### storage_evt_combination

- “A current Northbridge Enterprise Support holding for the same customer and billing entity provides assisted invoice explanation, but does not itself reduce this category price or waive debt.” — Declared replacement by storage_ext_outage_claim, storage_ext_outage_review, storage_ext_outage_credit, storage_ext_outage_authorize, storage_ext_outage_refund.
- “An approved negotiated rate is a contract-specific override; the presence of a paid support holding makes assisted negotiated-amendment intake available through support as well as portal and api.” — Inherited; compatible with applicable extended scope.
- “Without that combination the signed amendment is submitted through portal or api.” — Inherited; compatible with applicable extended scope.
- “A promotional primary-price entitlement is suppressed wherever a commitment price covers the same quantity, and no benefit from an unrelated category is stacked.” — Inherited; compatible with applicable extended scope.
- “The combination changes only request-channel eligibility, not approval authority.” — Declared replacement by storage_ext_outage_claim, storage_ext_outage_review, storage_ext_outage_credit, storage_ext_outage_authorize, storage_ext_outage_refund.

#### storage_evt_correction

- “For source_subtype correction, the source charge has an approved review with decision incorrect.” — Inherited; compatible with applicable extended scope.
- “This gate is inapplicable to other source_subtype values.” — Inherited; compatible with applicable extended scope.
- “Correct an erroneous charge to the approved review net_amount plus tax_amount, following evt_tax.” — Inherited; compatible with applicable extended scope.
- “Compare that corrected gross amount with the source original gross amount less cumulative correction credits plus cumulative debit adjustments; do not include service-credit concessions in this correction comparison.” — Inherited; compatible with applicable extended scope.
- “Credit the positive overcharge, debit the positive undercharge, and make no write when equal.” — Declared replacement by storage_ext_cool_credit.
- “A credit amount is negative and its net and tax components preserve the source proportions except an approved tax correction.” — Inherited; compatible with applicable extended scope.
- “An upward correction carries positive amount.” — Inherited; compatible with applicable extended scope.
- “Return the existing adjustment when the reviewed target has already been achieved.” — Inherited; compatible with applicable extended scope.
- “No cash refund is implicit in an invoice correction.” — Inherited; compatible with applicable extended scope.
- “Link source_event_id to the original charge and related_event_id to the approved review, never to a broad invoice containing several lines.” — Inherited; compatible with applicable extended scope.
- “Use correction_gross from msr_source_credits for the correction comparison; service_credit_net never changes the approved corrected billing target.” — Inherited; compatible with applicable extended scope.

#### storage_evt_refund

- “The customer-authorized refund request and completed original payment refer to the same holding and source payment.” — Inherited; compatible with applicable extended scope.
- “The customer files an exact refund authorization; the agent refunds a confirmed overpayment only to the method and destination of its original payment.” — Inherited; compatible with applicable extended scope.
- “Available refund is the smaller of the negative net receivable magnitude and original payment principal less prior returns and refunds linked to that payment.” — Declared replacement by storage_ext_outage_refund.
- “A requested amount exceeding that limit is refused, not silently reduced.” — Inherited; compatible with applicable extended scope.
- “Use refund_methods, require at least refund_minimum, and record a positive receivable delta for cash paid out.” — Inherited; compatible with applicable extended scope.
- “A smaller positive balance remains on account.” — Inherited; compatible with applicable extended scope.
- “Refunds require no active service contract and remain possible after closure.” — Inherited; compatible with applicable extended scope.
- “Repetition of the same request and source payment returns the existing refund.” — Inherited; compatible with applicable extended scope.
- “A third-party destination or unconfirmed payment is refused.” — Inherited; compatible with applicable extended scope.

#### storage_evt_request

- “Only the customer may file or cancel an authorization, claim or disposal request.” — Inherited; compatible with applicable extended scope.
- “Preserve the exact external_reference and the narrowest source_event_id.” — Inherited; compatible with applicable extended scope.
- “Set notice_at and occurred_at to the frozen clock and status pending on filing; cancellation is a new request event with status cancelled linked to the original request.” — P1 RED: not overwritten; tool and posted-only downstream selector disagree.
- “An unsupported channel is refused.” — Inherited; compatible with applicable extended scope.
- “A repeated identical request reference returns the existing event.” — Inherited; compatible with applicable extended scope.
- “Filing a request never confirms a system approval or changes an accounting balance.” — Inherited; compatible with applicable extended scope.

#### storage_evt_review

- “The source event and the evidence record identify the same holding and narrowest business object.” — Inherited; compatible with applicable extended scope.
- “A service accountant reviews one precise source event against its authoritative export, contract terms, bank notice, tax record or incident record.” — Inherited; compatible with applicable extended scope.
- “Record decision correct or incorrect for a billing review, and eligible or ineligible for an outage claim; status approved means the review is complete and authoritative, not that a credit necessarily follows.” — Inherited; compatible with applicable extended scope.
- “Record corrected net_amount and tax_amount for incorrect billing, or credited_amount for an eligible outage after applying evt_service_credit.” — Declared replacement by storage_ext_cool_review, storage_ext_outage_review.
- “A rejected review cannot authorize money movement.” — Inherited; compatible with applicable extended scope.
- “The customer may provide a locator but cannot dictate an official decision.” — Inherited; compatible with applicable extended scope.
- “Repeating the same source and request review returns the existing decision; materially new evidence is a distinct review linked through related_event_id.” — Inherited; compatible with applicable extended scope.
- “Review alone books no money.” — Inherited; compatible with applicable extended scope.

#### storage_evt_service_credit

- “For a service_credit financial posting, an approved review has decision eligible and positive credited_amount for the exact source charge; this gate does not constrain filing or reviewing the request.” — Inherited; compatible with applicable extended scope.
- “For a service_credit request being filed, the outage claim is filed no later than credit_claim_days after the official incident closes.” — Inherited; compatible with applicable extended scope.
- “For a newly filed claim, frozen handling time is its notice_at; the request is recorded immediately.” — Inherited; compatible with applicable extended scope.
- “Later review and credit use that recorded notice_at to evaluate the same boundary, so a timely request does not expire while awaiting review.” — Inherited; compatible with applicable extended scope.
- “Add credit_claim_days UTC calendar dates to incident_closed_at, preserving its time of day; calendar dates are counted without substituting business days or elapsed-hour periods.” — Inherited; compatible with applicable extended scope.
- “Equality at the deadline qualifies; a later claim is rejected without a credit.” — Inherited; compatible with applicable extended scope.
- “The provider incident must be completed, with cause outside outage_exclusions.” — Inherited; compatible with applicable extended scope.
- “Availability at or above sla_target_percent gives no credit.” — Inherited; compatible with applicable extended scope.
- “Below the target choose the first descending sla_credit_bands entry whose minimum is no greater than the recorded availability_percent.” — Inherited; compatible with applicable extended scope.
- “Multiply the original source charge net_amount by that fraction; subtract the service_credit_net component of prior credits for that exact source, and cap total service credits at credit_cap_fraction of that original net amount.” — Declared replacement by storage_ext_outage_claim, storage_ext_outage_review, storage_ext_outage_credit, storage_ext_outage_authorize, storage_ext_outage_refund.
- “Floor the additional credit at zero and round with amount_precision and rounding_mode.” — Inherited; compatible with applicable extended scope.
- “Apply the original tax component proportionately.” — Inherited; compatible with applicable extended scope.
- “A review writes its nonnegative approved result; a financial credit writes the negative approved amount only after that approved review exists.” — Inherited; compatible with applicable extended scope.
- “This service-credit branch applies only to source_subtype service_credit; evt_correction applies only to source_subtype correction.” — Inherited; compatible with applicable extended scope.
- “Excluded incidents, ineligible reviews and zero remaining entitlement result in no financial write.” — Inherited; compatible with applicable extended scope.
- “A request for consequential-loss compensation is not covered.” — Inherited; compatible with applicable extended scope.
- “A service-credit financial posting requires an approved review with decision eligible and positive credited_amount; the request and incident alone cannot authorize the financial posting.” — Inherited; compatible with applicable extended scope.

#### storage_evt_tax

- “The applicable tax classification has an approved system review.” — Inherited; compatible with applicable extended scope.
- “Use the source contract tax_treatment reviewed at the service date and tax_rates.” — Inherited; compatible with applicable extended scope.
- “Apply tax to the final rounded net service amount; round tax separately using amount_precision and rounding_mode.” — Inherited; compatible with applicable extended scope.
- “For a correction or credit use the original charge tax basis unless an approved tax-error review supplies the corrected treatment.” — Inherited; compatible with applicable extended scope.
- “Tax credits have negative tax_amount; charges and upward adjustments have positive tax_amount.” — Inherited; compatible with applicable extended scope.
- “Unsupported tax jurisdictions are POLICY_NOT_COVERED, not assumed exempt.” — Inherited; compatible with applicable extended scope.
- “Sum net subtotal and signed tax to obtain the financial amount.” — Inherited; compatible with applicable extended scope.
- “A verified exemption overrides the ordinary taxable rate; there is no stacking of tax treatments.” — Inherited; compatible with applicable extended scope.

## closing_checklist

Post-reveal difficulty disposition: RED; this is a completed audit, not a successful all-PASS closure. The source artifacts were not edited and no fix was arranged.

- `_difficulty.md`, `0.md`, and `1.md` exist one-to-one for the shared charter and two tasks. Both source_derivation_frozen sections were written before either original task was read, with hashes in freeze_manifest.json. First audit revision; there are no overwritten older revisions.
- Task 0: task-applicable policy PASS; problem tree PASS; computed solution equals GT; SOURCE-TASK RED because the proof asserts past exact-source correction history absent from initial_state (T0-1).
- Task 1: SOURCE-POLICY RED and SOURCE-TASK RED. T1-1 demonstrates request filing state/timestamp conflict; T1-2 demonstrates two valid values for a scored authorization argument. Amounts and conditional edge sensitivity calculations match GT.
- Task scopes are pairwise disjoint: task0 claims capacity_entitlement/cool_review/cool_credit and their three tools, with no workflow; task1 claims all five outage policies/tools and the sole storage_outage_refund_workflow. The union covers all eight extended policies and tools; no cross-task prerequisite introduces a cycle. Exactly one workflow is claimed by exactly one task.
- Each graph has at least two prerequisites and at least one value_input: task0 has2/2, task1 has4/4. No parallel write ambiguity or tool-layer prerequisite guards was found. Task1's all-base-compatible progression nevertheless fails on P1.
- UUID suffixes are distinct/frozen/no sequence pattern. Four audit inputs cannot establish independent random-generation provenance; no fabricated proof of that property is asserted.
- Final-form gates: the coordinator supplied seven successful reruns and full output in `env/enterprise_cloud_service_accounting/gate_snapshots/source/storage_accounting/round_1_20260912T165837364242Z.txt`; this audit made no source changes, and charter/tool/view hashes remained unchanged. Per Step0, the auditor did not rerun the gates. No successful all-PASS closeout is claimed while RED findings remain. Published-KB traceability remains deferred until rendering.

Reports contain evidence only. Cross-difficulty merge conclusions and fixes are outside this audit.

## revision_2

### charter_global_frozen

Closure/regression re-audit recorded 2026-09-12T17:18:58.662465+00:00. contamination_disclosure: this resumed auditor saw round-1 GT. This is not a fresh blind audit. Revised original task JSONs remain unread until both revised source determinations are saved. Round-1 sections are immutable and retained above.

Current shared hashes: storage.extended.yaml a72acbcc0edf87b25388d5a76c9b81d8fb188045275b664db598d33f21502e56; task_tools.py 28fec3a9040a517eadcdf73e8ad341dddec7367dffd18ab8e08ec6dce9f179ee. Both changed, so all shared checks were reconsidered rather than carrying the entire charter section forward by hash. Blueprint base remains byte-content/parsed-value compatible; all original keys equal blueprint/products/storage.yaml. Round2 view hashes equal round1: task0 8de9cc6daf104471c14c2b9153cfacc07bc1a1be6301b2f69da5138bef7aeace; task1 d3edbbf295f9c338e59d1dda76bd72955fac08c34b952660c4a14cfc9106686f.

Entry snapshot `env/enterprise_cloud_service_accounting/gate_snapshots/source/storage_accounting/round_2_20260912T171640050005Z.txt` contains complete actual commands and outputs: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; all seven EXIT_CODE=0. Auditor checked supplied evidence, did not rerun these gates. No author side files read.

#### policy_conflict_scan

Rescanned complete base/extended charter. The three cool-storage rules remain source-and-period-specific and separate from the five outage/service_credit/refund rules. Base lifecycle, primary pricing, collection, fees and returns do not add work to either root. Untaxed eligibility, completed incident/payment, same entity, deadline, original-payment principal and no-zero-financial-write conditions remain intact. Cross-category reads remain numeric backup committed_quantity or support tier portfolio_discount, with no cross-category writes. No new overlap or contradictory result was demonstrated.

P1 is now closed at the charter/tool layer. Both outage_claim and outage_authorize explicitly overwrite the full pending-filing sentence in storage_evt_request with: “For the immediate outage-concession claim and its exact refund authorization, filing records status posted and sets both notice_at and occurred_at to the frozen clock; posted means customer intent has been submitted, not that a system approval or financial entry has occurred. Cancellation remains a new request event with status cancelled linked to the original request.” This exact replacement is also in each rule. Both actual function bodies now set status posted, notice_at=ctx.now(), occurred_at=ctx.now(). This resolves the old conflicting state and timestamp rather than merely hiding its description; cancellation and customer ownership remain preserved.

#### rule_compute_equivalence

Rechecked all eight complete compute lists against literal compute_basis and rule sentences. No expression or basis in the original binding-level table is absent/changed in the new policy surface (comparison below). Quantity/status/payment filters, exact source and period, shared ceiling/prior consumed allocation, target and cap, availability bands, support increment, prior service-credit subtraction, holding balance, payment-specific principal, minimum and half-up rounding all retain the same semantics. Added filing and exact-ID sentences govern tool effects/object bindings and add no hidden numeric operation. They do not alter incident selection (still event_type storage_incident), so moving request occurred_at to handling time cannot change latest incident. No input branch or computation loses correspondence.

#### action_binding_and_uuids

All eight target_tool/computes pairs remain unique; owners remain six agent/two user. Same frozen UUID suffixes remain distinct/no sequence pattern; unchanged tools retain their IDs as revisions rather than creating spurious new tool identities. No random-generation provenance beyond the artifact evidence is claimed. All bodies were re-read: no prerequisite query, check, refusal or hint was introduced. Authorization now updates storage_event_id itself. Its contract requires that ID and request_id both equal the selected pending refund request's own storage_event_id, with source_event_id copied from that request and related_event_id from the actual concession receipt. This agrees with the new rule and removes the former generic unused evidence argument.

#### prerequisite_graph

All prerequisite fields remain present. Same six value_input edges form two disjoint chains: review->entitlement->leaf and correction->review; assessment->claim, concession->assessment, authorization->concession, refund->authorization. The edge policy_source remains literal in each rule; conditions and compute gate names match, every resolver exists and supplies the cited value/status, and graph is acyclic with no parallel interference. The one five-write workflow/dataflow remains claim receipt->assessment->concession receipt->exact authorization->refund. Root and own-moment per-world checks are recorded independently in revision2 of each task report.

#### override_declarations

Rechecked each sentence of each base_policy_refs rule against all applicable extended policies. The original sentence-by-sentence table still applies to untouched provisions, including service-credit amount/support overrides, review target and capped correction. The only revised disposition is the full storage_evt_request pending/notice/occurrence/cancellation sentence: it is now explicitly replaced for immediate outage claim and refund authorization by both governing policies. Other customer-only filing/channel/dedup/no-balance-changing-file provisions are inherited. New ID specificity neither changes approval authority nor adds a new prerequisite. No undeclared changed quantity or terminal-state sentence was demonstrated.

- storage_ext_capacity_entitlement: all 8 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=record_capacity_entitlement_88579e54/quantity.
- storage_ext_cool_review: all 8 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=record_storage_correction_review_dc2a1af3/net_amount.
- storage_ext_cool_credit: all 9 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=post_storage_correction_02018d1e/amount.
- storage_ext_outage_claim: all 10 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=file_storage_outage_claim_6a92fd5d/credited_amount.
- storage_ext_outage_review: all 11 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=assess_storage_outage_30bc4acc/credited_amount.
- storage_ext_outage_credit: all 11 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=post_storage_service_concession_cfd2170f/amount.
- storage_ext_outage_authorize: all 17 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=authorize_storage_refund_9b3e6afe/credited_amount.
- storage_ext_outage_refund: all 18 expressions present unchanged in round1 reviewed binding table=True; each compute_basis literal in current rule=True; target=refund_storage_overpayment_1b2c5ab5/amount.

### findings

Round2 charter P1 CLOSED: both customer-filing policies declare the exact base lifecycle override and both tools implement posted/current-notice/current-occurrence semantics. Per-task demonstrations are in task1 revision2. No new charter-global RED. UUID provenance observation remains limited to what the frozen module can show and does not establish a defect.

### closing_checklist

- Task0 and task1 revision2 each contain a saved source determination preceding revised GT inspection, disclosure that old GT was known, item-by-item comparison and PASS. Original round1 report text and freeze/evidence files are preserved. New freeze manifest: freeze_manifest_round2.json.
- Task0: policy PASS, chain PASS, unique solution/proof PASS; T0-1 CLOSED. Task1: policy PASS, chain PASS, unique solution/proof PASS; P1/T1-1 and T1-2 CLOSED.
- Complete current scope union covers eight extended policies and eight task tools: task0 three cool-storage policies/tools, task1 five outage/refund policies/tools. Scopes are pairwise disjoint, including entire prerequisite trees. Exactly one workflow exists and only task1 claims it.
- Both problem trees have at least2 prerequisite nodes and at least1 value_input edge:2/2 and4/4 respectively. Whole difficulty remains an acyclic graph with no cross-task cycle or parallel write interference. Current tool bodies contain no prerequisite guards; task1's two user actions are real contemporaneous filings and the workflow's five writes have closed dataflow.
- Tool suffixes remain distinct and frozen, with no observed reuse/sequence pattern; provenance of original randomness is not independently established by these artifacts, as already recorded.
- The coordinator reran all seven source instantiation gates on this unchanged final source form; full actual command/output evidence is `env/enterprise_cloud_service_accounting/gate_snapshots/source/storage_accounting/round_2_20260912T171640050005Z.txt`, seven EXIT_CODE=0. The auditor made no source changes, so those final-form reruns remain applicable. No gate rerun was delegated or performed by this audit. KB traceability remains deferred per pipeline until rendering.

Round2 difficulty source-layer audit: PASS. Every originally reported RED is closed with evidence; no new demonstrated defect or regression. The audit edits only its own report/evidence directory and arranges no fixes or cross-difficulty merge.
