from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .utils import quantize_positive


@dataclass(frozen=True)
class DUTStaticSpec:
    offset: float = 0.0
    repeatability_sigma: float = 0.0
    resolution: float = 0.1


def dut_static(rh_true_dut, spec, rng, day_effect=0.0, run_effect=0.0):
    """Apply static DUT offset, random effects, repeatability noise, and quantization."""
    rh_true_dut = np.asarray(rh_true_dut, dtype=float)
    noise = rng.normal(0.0, spec.repeatability_sigma, size=len(rh_true_dut))
    raw = rh_true_dut + spec.offset + day_effect + run_effect + noise
    logged = quantize_positive(raw, spec.resolution)
    return raw, logged, noise
