# Private Truth Data

This directory is reserved for simulator-only truth products that may be useful for internal laboratory audit or post-analysis comparison.

Final hidden truth data must remain local and must not be committed. `.gitignore` protects this directory and tracks only this README.

Examples of prohibited tracked content include latent chamber states, exact DUT/reference/chamber error components, injected bias components, and truth trajectories used to generate analyst-facing measurements.

The analyst-facing release under `data/generated/` must not depend on or expose files from this directory.
