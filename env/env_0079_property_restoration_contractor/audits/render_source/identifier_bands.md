# Identifier bands (assigned by the coordinator before fan-out; every seeded customer of a difficulty, persona or not)

| difficulty | phone: 10 digits <area>555<NNNN>, NNNN in | names (person surnames AND organization names start with) | statable reference numbers (claim/policy/loan/job) end in 4 digits in |
|---|---|---|---|
| water_mitigation_billing      | 0100-0199 | A-D | 1100-1999 |
| mold_remediation_jobs         | 0200-0299 | E-H | 2100-2999 |
| rebuild_contracts_and_draws   | 0300-0399 | I-M | 3100-3999 |
| contents_packout_and_storage  | 0400-0499 | N-R | 4100-4999 |
| insurance_claim_services      | 0500-0599 | S-Z | 5100-5999 |

Emails must be unique to the customer (local part built from that customer's own name / business). No customer name, phone,
email or reference number may repeat across difficulties; the coordinator scans name, phone and email at merge acceptance.
