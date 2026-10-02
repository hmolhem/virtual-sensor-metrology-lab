# Source Code

Reusable simulator components live here. The simulator core is intentionally separated from verification scripts so the same implementation can later drive DOE generation, calibration/validation studies, dynamic tests, stability analysis, and uncertainty work.

Current modules:

- `chamber.py` — chamber static behavior and commanded-step generation
- `reference.py` — reference-instrument static measurement model
- `dut.py` — DUT static measurement model
- `daq.py` — acquisition timebase utilities
- `dynamics.py` — first-order dynamic response and estimators
- `simulation.py` — static and dynamic simulation orchestration
- `utils.py` — shared quantization and RNG utilities

Verification scripts under `verification/` import these modules directly. This prevents verification logic from drifting away from the implementation used by the project.
