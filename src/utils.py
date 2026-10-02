from __future__ import annotations

import numpy as np


def quantize_positive(x, resolution):
    """Quantize non-negative measurements using half-up behavior."""
    x = np.asarray(x, dtype=float)
    return np.floor(x / resolution + 0.5) * resolution


def make_rngs(master_seed: int):
    """Create independent RNG streams for chamber, reference, DUT, and DAQ."""
    children = np.random.SeedSequence(master_seed).spawn(4)
    return {
        "chamber": np.random.default_rng(children[0]),
        "reference": np.random.default_rng(children[1]),
        "dut": np.random.default_rng(children[2]),
        "daq": np.random.default_rng(children[3]),
    }
