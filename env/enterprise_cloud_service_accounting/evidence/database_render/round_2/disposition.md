# Database render rework, round 2

DB-KB-01 is corrected in every reported bearing document. Independent re-audit remains pending.

The report identified the original sentence beginning “Use included protection protected volume in GB”. The frozen Database source instead says “Use plan_capacity_gb of the single active Managed Backup contract for the same customer and billing entity, or zero when none exists; multiple matches require selecting the contract named in the signed authorization before processing.” The exact source locators are database_ext_external_retention.compute_basis.capacity, database_ext_native_retention.compute_basis.capacity, and database_ext_retention_statement.compute_basis.capacity. Each matching compute binding reads CPARAM for Backup plan_capacity_gb.

The declared Backup blueprint defines this parameter as “Reference protected source capacity; GB integer.” Its backup_evt_category_meters rule identifies it as “a protected-capacity price band, not included protection.” The revised Database prose therefore identifies the reference protected source volume in GB defining the selected Backup tier’s price band. Contract state, customer and entity correlation, no-match zero, and signed selection among multiple matches remain unchanged. No foreign tier value, task identifier, GT quantity or new accounting operation is added.

The three corrected documents are:

- external_retention_capacity_af07355b.json
- native_retention_capacity_24b34830.json
- retention_statement_capacity_3463a446.json

All 143 documents were rebuilt in staging from the frozen source ledger and published by recoverable directory replacement. The other 140 document files are byte-identical, including the entire previously passing task-1 policy and workflow domain. The complete audit input inventory, exact before/after source mapping, preservation proof, updated ledger, prose-only reconstruction, source-formula checks, manual acceptance, staging gate and official gate are saved alongside this report. Both document gates pass. All source fingerprints are unchanged. No source-layer blocker was found. Only the Database staging directory and its temporary authoring scripts were removed after the official gate passed.
