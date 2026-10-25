# physical_damage_claims — rework round 6 claims (cross-product re-judge, policy_kb revision_3)

Seed-only round bounded to item S3.

- **S3**: task 1's bind-time "vehicle added" row for term 1's Camry is removed. Under the auto rules that row type schedules an additional or replacement vehicle mid-term with an additional premium; a vehicle present at binding is carried by the term's new-business premium and vehicle count with no such row, the convention task 0 already follows. The Camry stays recorded by term 1's new-business premium, its vehicle count and its removal change on the replacement date. The seed check for the removed row was dropped and term 1's vehicle-change read objective and the rationale were reworded. The gold read set is unchanged: the term 1 vehicle-change read still returns the removal and the Accord's addition, and replay closure equals the seed.
- **Gold**: unchanged. No physdam rule reads that row: the recent-purchase cap reads the vehicle-added change for the Accord's VIN, and the short-rate substitution tier reads the coverage's own owner term (term 2). check_compute recomputes every scored figure equal to the stored gold.
- **S2**: not changed (coordinator decision).
- **Frozen files**: physdam.extended.yaml sha prefix f165003a and task_tools.py sha prefix 43a3e10b, both confirmed unchanged.
