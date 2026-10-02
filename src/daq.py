from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class DAQSpec:
    sample_period_s: float = 1.0


def elapsed_time(n: int, spec: DAQSpec):
    """Create the static acquisition time base."""
    return np.arange(n, dtype=float) * spec.sample_period_s


def sampled_timebase(duration_s: float, dt_s: float):
    """Create an inclusive dynamic-acquisition time base."""
    return np.arange(0.0, duration_s + dt_s, dt_s)
