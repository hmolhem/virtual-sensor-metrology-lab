# Configuration

Configuration is intentionally split into two information domains.

## Public configuration

Tracked analyst-visible laboratory specifications live under `config/public/`.

Current canonical file:

- `config/public/lab_spec_v1.json`

It contains only declared laboratory information such as DUT acceptance limits, reference and chamber specifications, DAQ settings, and experimental-design metadata.

It must not contain final simulator truth, latent physical states, injected error components, or exact hidden DUT/reference/chamber parameters.

## Private simulator configuration

Final simulator-only truth belongs under `config/private/` in local working copies only.

`.gitignore` blocks private configuration files while allowing only `config/private/README.md` to remain tracked as policy documentation.

Private truth is loaded through `src/config_boundary.py`, which rejects private configuration paths outside the protected directory.

## Boundary rule

The laboratory may use both public specification and private truth internally, but analyst-facing outputs and the future dataset release must pass the no-private-fields serialization gate before leaving the lab boundary.

Verification of this policy is maintained under `verification/CB-001_Config_Boundary/`.
