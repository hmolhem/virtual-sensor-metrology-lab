# Private Simulator Configuration

This directory is the only allowed location for the final hidden DUT/reference/chamber simulator configuration.

Actual private truth files exist only in local working copies and must never be committed. `.gitignore` protects the directory and tracks only this README.

Expected private domains include:

- exact DUT static-error parameters
- exact DUT dynamic parameters such as time constants and dead time
- exact hysteresis and drift laws
- day/run random-effect parameters
- exact reference-instrument bias/error parameters
- exact chamber bias/nonuniformity/error parameters
- RNG configuration used to create the frozen measurement campaign

`src/config_boundary.py` enforces that private truth can be loaded only from this protected directory.

Verification fixtures may contain dummy known truth, but final hidden laboratory truth is not stored in Git.
