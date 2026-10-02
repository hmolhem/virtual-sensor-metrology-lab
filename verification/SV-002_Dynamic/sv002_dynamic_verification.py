from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.dynamics import (
    estimate_tau_log_linear,
    estimate_threshold_time,
    first_order_step_analytic,
)
from src.simulation import simulate_dynamic_chain


def run_sv002():
    rows = []

    def add(test_id, description, passed, observed, expected):
        rows.append({
            "Test_ID": test_id,
            "Description": description,
            "Status": "PASS" if bool(passed) else "FAIL",
            "Observed": observed,
            "Expected_or_Criterion": expected,
        })

    y0, y1, tau, dead_time = 30.0, 70.0, 20.0, 3.0

    y_tau = float(first_order_step_analytic([tau], y0, y1, tau_s=tau)[0])
    expected_tau_level = y0 + (1.0 - math.exp(-1.0)) * (y1 - y0)
    add("SV-002A", "Ideal first-order response reaches 63.2% at one time constant",
        abs(y_tau - expected_tau_level) < 1e-10,
        f"{y_tau:.8f} %RH", f"{expected_tau_level:.8f} %RH")

    t90_exact = -tau * math.log(0.1)
    expected_t90 = 2.302585092994046 * tau
    add("SV-002B", "Ideal first-order t90 analytical relation",
        abs(t90_exact - expected_t90) < 1e-10,
        f"{t90_exact:.8f} s", f"{expected_t90:.8f} s")

    observed_with_dead_time = dead_time + t90_exact
    expected_with_dead_time = 3.0 + 2.302585092994046 * 20.0
    add("SV-002C", "Pure dead time shifts observed t90 without changing intrinsic tau",
        abs(observed_with_dead_time - expected_with_dead_time) < 1e-10,
        f"{observed_with_dead_time:.8f} s", f"{expected_with_dead_time:.8f} s")

    dt = 1.0
    t = np.arange(0.0, 140.0 + dt, dt)
    clean = first_order_step_analytic(t, y0, y1, tau_s=tau, dead_time_s=dead_time)
    tau_hat, _ = estimate_tau_log_linear(t, clean, y0, y1, dead_time_s=dead_time)
    add("SV-002D", "Log-linear estimator recovers known isolated DUT time constant",
        abs(tau_hat - tau) / tau < 0.005,
        f"tau_hat={tau_hat:.8f} s", "relative error < 0.5%")

    t90_sampled = estimate_threshold_time(t, clean, y0, y1, fraction=0.9)
    exact_observed = dead_time + t90_exact
    add("SV-002E", "1 Hz sampled t90 threshold timing is bounded by one sample",
        0.0 <= (t90_sampled - exact_observed) <= dt + 1e-12,
        f"sampled={t90_sampled:.3f} s; exact={exact_observed:.3f} s",
        "0 <= sampled - exact <= 1.0 s")

    tau_up, tau_down = 20.0, 28.0
    t90_up = -tau_up * math.log(0.1)
    t90_down = -tau_down * math.log(0.1)
    ratio = t90_down / t90_up
    add("SV-002F", "Rise/fall time constants produce proportional t90 asymmetry",
        abs(ratio - tau_down / tau_up) < 1e-12 and t90_down > t90_up,
        f"t90_up={t90_up:.4f}, t90_down={t90_down:.4f}, ratio={ratio:.4f}",
        f"ratio={tau_down / tau_up:.4f} and down > up")

    private, analyst = simulate_dynamic_chain(master_seed=7140)
    final_command = float(private["RH_Command"].iloc[-1])
    final_chamber = float(private["RH_True_Chamber"].iloc[-1])
    final_ref = float(private["Reference_Dynamic_State"].iloc[-1])
    final_dut = float(private["DUT_Dynamic_State"].iloc[-1])
    converged = (
        abs(final_chamber - final_command) < 0.1
        and abs(final_ref - final_command) < 0.1
        and abs(final_dut - final_command) < 0.15
    )
    add("SV-002G", "Cascaded chamber/reference/DUT dynamic states converge to final command",
        converged,
        f"cmd={final_command:.4f}, chamber={final_chamber:.4f}, ref={final_ref:.4f}, dut={final_dut:.4f}",
        "all final-state errors within configured tolerances")

    private_2, analyst_2 = simulate_dynamic_chain(master_seed=7140)
    _, analyst_3 = simulate_dynamic_chain(master_seed=7141)
    same = private.equals(private_2) and analyst.equals(analyst_2)
    different = not analyst.equals(analyst_3)
    add("SV-002H", "Dynamic simulation is reproducible for fixed seed",
        same and different,
        f"same_seed_same={same}, different_seed_diff={different}", "True, True")

    forbidden = ("true_", "dynamic_state", "after_deadtime", "private_", "hidden_")
    leaked = [column for column in analyst.columns if any(token in column.lower() for token in forbidden)]
    add("SV-002I", "Analyst dataset contains no dynamic private-truth fields",
        len(leaked) == 0, f"leaked_columns={leaked}", "[]")

    dt_fine = 0.25
    t_fine = np.arange(0.0, 140.0 + dt_fine, dt_fine)
    y_fine = first_order_step_analytic(t_fine, y0, y1, tau_s=tau, dead_time_s=dead_time)
    t90_fine = estimate_threshold_time(t_fine, y_fine, y0, y1, fraction=0.9)
    err_coarse = abs(t90_sampled - exact_observed)
    err_fine = abs(t90_fine - exact_observed)
    add("SV-002J", "Finer sampling does not worsen threshold-timing discretization error",
        err_fine <= err_coarse + 1e-12 and err_fine <= dt_fine + 1e-12,
        f"1Hz_error={err_coarse:.4f} s; 4Hz_error={err_fine:.4f} s",
        "4 Hz error <= 1 Hz error and <= 0.25 s")

    return pd.DataFrame(rows), private, analyst


if __name__ == "__main__":
    report, private_df, analyst_df = run_sv002()
    out_dir = Path(__file__).resolve().parent
    report.to_csv(out_dir / "sv002_verification_report.csv", index=False)
    private_df.to_csv(out_dir / "sv002_private_fixture.csv", index=False)
    analyst_df.to_csv(out_dir / "sv002_analyst_fixture.csv", index=False)
    print(report.to_string(index=False))
    print()
    print("Overall:", "PASS" if (report["Status"] == "PASS").all() else "FAIL")
