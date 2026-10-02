from __future__ import annotations

import math
import numpy as np


def first_order_step_analytic(t, y0, y1, tau_s, dead_time_s=0.0):
    """Continuous-time first-order response with pure dead time."""
    t = np.asarray(t, dtype=float)
    y = np.full_like(t, fill_value=float(y0), dtype=float)
    mask = t > dead_time_s
    y[mask] = y1 + (y0 - y1) * np.exp(-(t[mask] - dead_time_s) / tau_s)
    return y


def threshold_level(y0, y1, fraction):
    return y0 + fraction * (y1 - y0)


def estimate_threshold_time(t, y, y0, y1, fraction=0.9):
    """Return the first sampled threshold crossing for a rise or fall."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    target = threshold_level(y0, y1, fraction)
    idx = np.flatnonzero(y >= target) if y1 > y0 else np.flatnonzero(y <= target)
    return np.nan if len(idx) == 0 else float(t[idx[0]])


def estimate_tau_log_linear(t, y, y0, y1, dead_time_s=0.0):
    """Estimate tau from a clean isolated first-order trace."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    remaining = (y - y1) / (y0 - y1)
    mask = (t > dead_time_s) & (remaining > 1e-5) & (remaining < 0.999999)
    x = t[mask] - dead_time_s
    z = np.log(remaining[mask])
    slope, intercept = np.polyfit(x, z, 1)
    return float(-1.0 / slope), float(intercept)


def zoh_first_order(input_signal, dt_s, tau_s, y_initial=None):
    """Exact discrete first-order update for zero-order-hold input."""
    u = np.asarray(input_signal, dtype=float)
    if y_initial is None:
        y_initial = float(u[0])
    y = np.empty_like(u, dtype=float)
    y[0] = y_initial
    a = math.exp(-dt_s / tau_s)
    for k in range(1, len(u)):
        y[k] = a * y[k - 1] + (1.0 - a) * u[k - 1]
    return y
