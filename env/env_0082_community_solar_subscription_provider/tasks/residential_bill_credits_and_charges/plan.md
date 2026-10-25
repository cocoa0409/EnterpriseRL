# plan — residential_bill_credits_and_charges (category home), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2 (3 problems), factor_counts=[6,6,4]
- task 1: prerequisite_problems=2 (3 problems), factor_counts=[5,6,4]

Hard order: plan.md -> extended yaml (base verbatim + policies one by one) -> task_tools.py (gate after each) -> task 0 json piecewise -> per-task gates -> task 1 -> final gates -> worklog last line.
Scratch: /tmp/residential_bill_credits_and_charges_0082/ only.

Constraints carried (coordinator inst_common.md): read isolation; base frozen; XF_recipe A-H applied to every policy/tool;
realism bar R1-R6 / X1-X4 (company factor never moves a utility/state amount or date); owner=user = holder payment via secure
portal (method not on file, stated in rule + persona); T1 cross-difficulty factor per task (access/waitlist/garden/biz records of same customer);
RND(x+1e-9,2); no datetime/time/random/uuid/secrets imports; no docstring example values; factor ids not substrings of tool names;
identifier band: phones 6515550100-6515550119, surnames Thornbury/Adeyemi/Kowalczyk/Halvorsen/Esposito-Park/Wainwright,
businesses Brightwell Dental PLLC / Juniper Lane Bakery LLC, prefix 21, house numbers 1100-1199.

Provisional design (refined in worklog.md):
- 6 extended policies = 2 trees x 3 problems; root of each tree = subscriber's own payment (owner=user), prerequisites = agent
  bookings (fee / billing credit / estimate) that change the payment amount (value_input) or gate it.
- Worklog tables kept in worklog.md: factor-reads table, defining-sentence table, probe table, pairwise method-tier table, trigger list.
