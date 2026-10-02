from __future__ import annotations

import math
import numpy as np
import pandas as pd


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

    if y1 > y0:
        idx = np.flatnonzero(y >= target)
    else:
        idx = np.flatnonzero(y <= target)

    if len(idx) == 0:
        return np.nan
    return float(t[idx[0]])


def estimate_tau_log_linear(t, y, y0, y1, dead_time_s=0.0):
    """Estimate tau from a clean isolated first-order trace."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    denom = y0 - y1
    remaining = (y - y1) / denom
    mask = (t > dead_time_s) & (remaining > 1e-5) & (remaining < 0.999999)

    x = t[mask] - dead_time_s
    z = np.log(remaining[mask])

    slope, intercept = np.polyfit(x, z, 1)
    tau_hat = -1.0 / slope
    return float(tau_hat), float(intercept)


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


def delayed_command(t, y0, y1, step_time_s):
    t = np.asarray(t, dtype=float)
    return np.where(t < step_time_s, y0, y1).astype(float)


def simulate_dynamic_chain(
    master_seed=7140,
    dt_s=1.0,
    duration_s=240.0,
    step_time_s=10.0,
    rh0=30.0,
    rh1=70.0,
    chamber_tau_s=30.0,
    reference_tau_s=4.0,
    dut_tau_s=20.0,
    dut_dead_time_s=3.0,
    reference_noise_sigma=0.03,
    dut_noise_sigma=0.10,
):
    """Simulate command -> chamber -> reference/DUT dynamic chain."""
    seed_sequence = np.random.SeedSequence(master_seed)
    ref_rng, dut_rng = [np.random.default_rng(s) for s in seed_sequence.spawn(2)]

    t = np.arange(0.0, duration_s + dt_s, dt_s)
    command = delayed_command(t, rh0, rh1, step_time_s)

    chamber = zoh_first_order(command, dt_s, chamber_tau_s, y_initial=rh0)
    reference_state = zoh_first_order(chamber, dt_s, reference_tau_s, y_initial=rh0)

    delay_samples = int(round(dut_dead_time_s / dt_s))
    if not math.isclose(
        delay_samples * dt_s,
        dut_dead_time_s,
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise ValueError(
            "For this verification fixture, dead time must be an integer number of samples."
        )

    dut_input = np.full_like(chamber, rh0)
    if delay_samples == 0:
        dut_input[:] = chamber
    else:
        dut_input[delay_samples:] = chamber[:-delay_samples]

    dut_state = zoh_first_order(dut_input, dt_s, dut_tau_s, y_initial=rh0)

    reference_noise = ref_rng.normal(0.0, reference_noise_sigma, size=len(t))
    dut_noise = dut_rng.normal(0.0, dut_noise_sigma, size=len(t))

    rh_reference = reference_state + reference_noise
    rh_dut = dut_state + dut_noise

    private = pd.DataFrame(
        {
            "Elapsed_s": t,
            "RH_Command": command,
            "RH_True_Chamber": chamber,
            "Reference_Dynamic_State": reference_state,
            "DUT_Input_After_DeadTime": dut_input,
            "DUT_Dynamic_State": dut_state,
            "True_Reference_Noise": reference_noise,
            "True_DUT_Noise": dut_noise,
            "RH_Reference": rh_reference,
            "RH_DUT": rh_dut,
        }
    )

    analyst = pd.DataFrame(
        {
            "Elapsed_s": t,
            "Test_ID": "SV002_DYNAMIC",
            "RH_Command": command,
            "RH_Reference": rh_reference,
            "RH_DUT": rh_dut,
        }
    )

    return private, analyst


def run_sv002():
    rows = []

    def add(test_id, description, passed, observed, expected):
        rows.append(
            {
                "Test_ID": test_id,
                "Description": description,
                "Status": "PASS" if bool(passed) else "FAIL",
                "Observed": observed,
                "Expected_or_Criterion": expected,
            }
        )

    y0, y1, tau, dead_time = 30.0, 70.0, 20.0, 3.0

    # SV-002A — 63.2% property.
    y_tau = float(first_order_step_analytic([tau], y0, y1, tau_s=tau)[0])
    expected_tau_level = y0 + (1.0 - math.exp(-1.0)) * (y1 - y0)
    add(
        "SV-002A",
        "Ideal first-order response reaches 63.2% at one time constant",
        abs(y_tau - expected_tau_level) < 1e-10,
        f"{y_tau:.8f} %RH",
        f"{expected_tau_level:.8f} %RH",
    )

    # SV-002B — t90 analytical relation.
    t90_exact = -tau * math.log(0.1)
    expected_t90 = 2.302585092994046 * tau
    add(
        "SV-002B",
        "Ideal first-order t90 analytical relation",
        abs(t90_exact - expected_t90) < 1e-10,
        f"{t90_exact:.8f} s",
        f"{expected_t90:.8f} s",
    )

    # SV-002C — dead-time shift.
    observed_with_dead_time = dead_time + t90_exact
    expected_with_dead_time = 3.0 + 2.302585092994046 * 20.0
    add(
        "SV-002C",
        "Pure dead time shifts observed t90 without changing intrinsic tau",
        abs(observed_with_dead_time - expected_with_dead_time) < 1e-10,
        f"{observed_with_dead_time:.8f} s",
        f"{expected_with_dead_time:.8f} s",
    )

    # SV-002D — tau estimator.
    dt = 1.0
    t = np.arange(0.0, 140.0 + dt, dt)
    clean = first_order_step_analytic(t, y0, y1, tau_s=tau, dead_time_s=dead_time)
    tau_hat, _ = estimate_tau_log_linear(
        t,
        clean,
        y0,
        y1,
        dead_time_s=dead_time,
    )
    add(
        "SV-002D",
        "Log-linear estimator recovers known isolated DUT time constant",
        abs(tau_hat - tau) / tau < 0.005,
        f"tau_hat={tau_hat:.8f} s",
        "relative error < 0.5%",
    )

    # SV-002E — sampled threshold timing.
    t90_sampled = estimate_threshold_time(t, clean, y0, y1, fraction=0.9)
    exact_observed = dead_time + t90_exact
    add(
        "SV-002E",
        "1 Hz sampled t90 threshold timing is bounded by one sample",
        0.0 <= (t90_sampled - exact_observed) <= dt + 1e-12,
        f"sampled={t90_sampled:.3f} s; exact={exact_observed:.3f} s",
        "0 <= sampled - exact <= 1.0 s",
    )

    # SV-002F — rise/fall asymmetry.
    tau_up = 20.0
    tau_down = 28.0
    t90_up = -tau_up * math.log(0.1)
    t90_down = -tau_down * math.log(0.1)
    ratio = t90_down / t90_up
    add(
        "SV-002F",
        "Rise/fall time constants produce proportional t90 asymmetry",
        abs(ratio - tau_down / tau_up) < 1e-12 and t90_down > t90_up,
        f"t90_up={t90_up:.4f}, t90_down={t90_down:.4f}, ratio={ratio:.4f}",
        f"ratio={tau_down / tau_up:.4f} and down > up",
    )

    # SV-002G — full cascaded convergence.
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
    add(
        "SV-002G",
        "Cascaded chamber/reference/DUT dynamic states converge to final command",
        converged,
        (
            f"cmd={final_command:.4f}, chamber={final_chamber:.4f}, "
            f"ref={final_ref:.4f}, dut={final_dut:.4f}"
        ),
        "all final-state errors within configured tolerances",
    )

    # SV-002H — seed reproducibility.
    private_2, analyst_2 = simulate_dynamic_chain(master_seed=7140)
    _, analyst_3 = simulate_dynamic_chain(master_seed=7141)
    same = private.equals(private_2) and analyst.equals(analyst_2)
    different = not analyst.equals(analyst_3)
    add(
        "SV-002H",
        "Dynamic simulation is reproducible for fixed seed",
        same and different,
        f"same_seed_same={same}, different_seed_diff={different}",
        "True, True",
    )

    # SV-002I — public/private separation.
    forbidden = ("true_", "dynamic_state", "after_deadtime", "private_", "hidden_")
    leaked = [
        column
        for column in analyst.columns
        if any(token in column.lower() for token in forbidden)
    ]
    add(
        "SV-002I",
        "Analyst dataset contains no dynamic private-truth fields",
        len(leaked) == 0,
        f"leaked_columns={leaked}",
        "[]",
    )

    # SV-002J — sampling-rate effect.
    dt_fine = 0.25
    t_fine = np.arange(0.0, 140.0 + dt_fine, dt_fine)
    y_fine = first_order_step_analytic(
        t_fine,
        y0,
        y1,
        tau_s=tau,
        dead_time_s=dead_time,
    )
    t90_fine = estimate_threshold_time(t_fine, y_fine, y0, y1, fraction=0.9)
    err_coarse = abs(t90_sampled - exact_observed)
    err_fine = abs(t90_fine - exact_observed)
    add(
        "SV-002J",
        "Finer sampling does not worsen threshold-timing discretization error",
        err_fine <= err_coarse + 1e-12 and err_fine <= dt_fine + 1e-12,
        f"1Hz_error={err_coarse:.4f} s; 4Hz_error={err_fine:.4f} s",
        "4 Hz error <= 1 Hz error and <= 0.25 s",
    )

    report = pd.DataFrame(rows)
    return report, private, analyst


if __name__ == "__main__":
    report, private_df, analyst_df = run_sv002()

    report.to_csv("sv002_verification_report.csv", index=False)
    private_df.to_csv("sv002_private_fixture.csv", index=False)
    analyst_df.to_csv("sv002_analyst_fixture.csv", index=False)

    print(report.to_string(index=False))
    print()
    print("Overall:", "PASS" if (report["Status"] == "PASS").all() else "FAIL")
