from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .utils import quantize_positive


@dataclass(frozen=True)
class ReferenceStaticSpec:
    bias: float = 0.0
    repeatability_sigma: float = 0.0
    resolution: float = 0.01


def reference_static(rh_true_ref, spec, rng):
    """Apply static reference bias, repeatability noise, and quantization."""
    rh_true_ref = np.asarray(rh_true_ref, dtype=float)
    noise = rng.normal(0.0, spec.repeatability_sigma, size=len(rh_true_ref))
    raw = rh_true_ref + spec.bias + noise
    logged = quantize_positive(raw, spec.resolution)
    return raw, logged, noise
