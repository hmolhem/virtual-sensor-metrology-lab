# Source Code

Reusable simulator components live here. The simulator core is intentionally separated from verification scripts so the same implementation can drive the laboratory measurement campaign without duplicating scientific logic.

Current modules:

- `chamber.py` — chamber static behavior and commanded-step generation
- `reference.py` — reference-instrument static measurement model
- `dut.py` — DUT static measurement model
- `daq.py` — acquisition timebase utilities
- `dynamics.py` — first-order dynamic response and estimators
- `simulation.py` — static and dynamic simulation orchestration
- `experiments.py` — reproducible experimental-design and test-matrix generation
- `config_boundary.py` — public/private configuration loading and analyst-output leakage protection
- `utils.py` — shared quantization and RNG utilities

Verification scripts under `verification/` import these modules directly. This prevents verification logic from drifting away from the implementation used by the project.

`config_boundary.py` does not contain final hidden sensor values. It only enforces where private truth may be loaded from and blocks simulator-only field names from analyst-facing serialized payloads.
