# volume_rebates (env_0083) — instantiation plan (round 1)

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2 (3 problems), factor_counts [5, 6, 4]
- task 1: prerequisite_problems=1 (2 problems), factor_counts [4, 5]
=> 5 extended policies, 24 factors; each task >=1 owner=user write, >=1 multi-source, >=1 cross-difficulty factor.

Identifier band: phones 7175550180-199; surnames Sheridan, Oduya, Petrov, Galloway, Iwasaki, Montrose, Bianchi;
fleets Keystone Bulk Transport Inc., Susquehanna Valley Dairy Co-op, Lancaster Pike Builders LLC, Lehigh Valley Medical Transport Inc.;
EIN/card last4 start 5; unit prefix PA-; ref prefix 35; PA ZIPs 15xxx-19xxx.

DSL note: within_months uses MONTHS(d, NOW) in [0,N): a frozen_time on the 31st makes each band a calendar month exactly
(band k = XSUM(w=k+1) - XSUM(w=k)). Plan frozen_time on a 31st.

Status: design in progress (see worklog.md for the running log).
