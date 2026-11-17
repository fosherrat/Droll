# Droll

Spherical rolling/flying robot. Design spec lives in the "Droll Design Spec" artifact;
this repo holds the parametric source for Part 2 (central drive) and Part 3 (wheel module).

- `droll/params.py` — shared parameters, single source of truth (status tag on every value)
- `part3/analysis/` — calculation scripts for the wheel module
- `docs/part3/` — step docs; `generated/` is script output, do not edit by hand

Regenerate Part 3 step-0 outputs:

    pip install numpy matplotlib
    python3 part3/analysis/requirements_check.py
