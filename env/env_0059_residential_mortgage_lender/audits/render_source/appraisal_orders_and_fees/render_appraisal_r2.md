# Remaining source mismatches reported by the appraisal renderer (agent a22a7e45878990fb9), render round 2 — copied verbatim by the coordinator

Input: appraisal.extended.yaml sha256 5fca2f1f…51ff, task_tools.py cb95da02… (unchanged).

**Remaining source mismatches (rendered as they stand):**
1. **The rule contradicts itself** (`appraisal_ext_size_value_addon`). The rule says "The complexity add-on is built from the parts below, in place of the report type's gross-living-area surcharge alone, and is reduced only by its arrival rule". It also says "Any amount already standing on the order's gross-living-area surcharge line is taken off the complexity add-on, the result never going below zero", which is a second reduction. The round-3 audit logged this as O-R3-1, not RED.
2. **A docstring claims an effect the tool body lacks** (all four tools in `task_tools.py`). The docstrings say "it is stored rounded half-up to 2 decimal places". The bodies use Python `round(float(x), 2)`, which is not half-up. The audit logged this as O-R3-3. All four hubs carry the docstring wording.
