from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ChamberStaticSpec:
    rh_setpoint_bias: float = 0.0
    rh_spatial_offset_dut: float = 0.0
    rh_spatial_offset_ref: float = 0.0
    rh_stability_sigma: float = 0.0


def chamber_static(rh_setpoint, n, spec, rng):
    """Generate local true RH at DUT and reference positions."""
    common_fluctuation = rng.normal(0.0, spec.rh_stability_sigma, size=n)
    base = rh_setpoint + spec.rh_setpoint_bias
    rh_true_dut = base + spec.rh_spatial_offset_dut + common_fluctuation
    rh_true_ref = base + spec.rh_spatial_offset_ref + common_fluctuation
    return rh_true_dut, rh_true_ref, common_fluctuation


def delayed_command(t, y0, y1, step_time_s):
    """Generate an ideal commanded step at step_time_s."""
    t = np.asarray(t, dtype=float)
    return np.where(t < step_time_s, y0, y1).astype(float)
