# Northbridge Cloud Services: architecture record

The ontology fits a regional enterprise cloud provider: organizations hold capacity and service contracts, and resource meters, charges, credits and collections continually book against them. Products are sold in six capacity or supported-spend bands, rather than in six invented grades of service. Contract quantities describe actual resource consumption and receivables, not a fictional prepaid wallet.

## Industry enumeration: manual dimensions

- Compute: vCPU and memory packages, instance hours, operating-system licenses, persistent boot disks, reserved term commitments, region factors, spot exclusions, start/stop metering, dedicated tenancy, and consumption corrections.
- Storage: hot/cool/archive capacity, request classes, retrieval volumes, minimum storage duration, early deletion, replication, version storage, internet transfer, lifecycle migration and reconciliation of object meters.
- Database: provisioned cores and memory, node hours, engine license, high availability, replicas, storage and IOPS, backup retention, restore operations, maintenance exclusions and reservation coverage.
- Network: committed bandwidth, measured transfer, regional and cross-region destinations, private interconnect port hours, traffic processing, public addresses, connection setup, data transfer allowances and outbound corrections.
- Support: supported-spend bands, percentage fees, minimum fees, included contacts, severity response entitlements, named contacts, incident support, proactive reviews, excluded marketplace spend and support-fee reconciliation.
- Backup: protected capacity, backup storage, incremental ingestion, retention, immutable copies, cross-region copies, restore volumes, export and early deletion of committed retention.
- Security: protected workload bands, workload hours, log ingestion, retention, scanning, incident response, key operations, managed rule subscriptions, archive retrieval and security billing corrections.
- Across all categories: signed applications, provisioning status, contract amendments, resource scope, account ownership, legal entity and tax evidence, billing periods and currency, negotiated price overrides, reservation versus promotional exclusions, exact rounding, portfolio discount basis, invoice lines, corrections, original-line correlation, credited-to-date caps, remittance allocation, returned payments, overpayment refunds, verified outages, claim deadlines, suspension and customer termination.

## Industry enumeration: frequent support requests

Unexpected usage or price, a missing reservation discount, wrong region or meter classification, duplicate charge, failed payment allocation, returned remittance, invoice correction, tax exemption correction, outage credit, refund of an overpayment, service suspension or resumption, contract capacity changes, opening or terminating a resource contract, and explanations of consumption across organizational holdings are all covered by declared policies and events. Requests to negotiate an unapproved bespoke commercial clause, determine a foreign tax jurisdiction absent from the tax mapping, or compensate consequential business losses are uncovered and use the shared policy handoff.

## Functional closure ledger

Every charter carries its own admission, provisioning, amendment, metering, invoice, pricing override, portfolio aggregation, correction, service credit, collection, payment return, overpayment refund, suspension/resumption and exit policies. Read-only queries use the shared finders. Customer signatures and disposal of resources remain customer actions; agents perform service accounting. Charges are positive receivable deltas and payments/credits negative; returns and refunds restore receivables. Consumption meters and meter reversals close the physical quantity loop. Original event references bind every derived correction to its narrowest source line. No automatic trigger changes a neighboring category: combination conditions alter only the category being handled.

The five claimed desks are compute_accounting, storage_accounting, database_accounting, network_accounting and support_accounting. Backup and Security are independent unclaimed expansion products. All resource, money and time measures have units, event grain and authoritative source fields. The detailed product-specific rate maps are reviewed with their charter at each persisted batch.

## Final constitution review

The review added historical tier and price-component dimensions to event records, so an amendment cannot silently reprice earlier consumption and split commitment quantities remain distinguishable. Monetary components now carry an explicit signed convention; correction totals retain gross tax-inclusive amounts while service-credit caps consume only pretax service-credit amounts. Dedicated, spot, replica, storage-class, transfer-destination and support-fee minimum rules each specify precedence over the common calculation where appropriate.

Customer requests and approved reviews retain their effective commercial attributes. Application and disposal references remain on the holding and are reachable through the same all-reference finder. A customer closes a resource directly after authorizing disposal; there is no separate agent-operated asynchronous closure intake. A positive unbilled signed commitment liability triggers its termination invoice, with the disposal request identifying the source occurrence; ordinary zero-fee activation and restoration create no artificial fee events.

The source-level review scoped usage-versus-fee eligibility and correction-versus-service-credit eligibility explicitly, separated timely claim filing from later review, and anchored collection grace to the actual invoice issue record. All seven product parameter dictionaries have consumers in common accounting policies or the category-specific meter policy. The three quantitative accounts/bases used operationally are resource consumption, signed receivables and source-specific credit components derived from their event histories; cached balances are deliberately absent. All three final machine gates are rerun after these amendments; their printed output is retained in gates.txt.
