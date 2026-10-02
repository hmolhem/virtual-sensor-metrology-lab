from __future__ import annotations

import math
import numpy as np
import pandas as pd

from .chamber import ChamberStaticSpec, chamber_static, delayed_command
from .daq import DAQSpec, elapsed_time, sampled_timebase
from .dut import DUTStaticSpec, dut_static
from .dynamics import zoh_first_order
from .reference import ReferenceStaticSpec, reference_static
from .utils import make_rngs


def generate_static_dataset(
    master_seed=7140,
    n=60,
    rh_setpoint=50.0,
    temperature_setpoint=25.0,
    chamber_spec=ChamberStaticSpec(
        rh_setpoint_bias=-0.05,
        rh_spatial_offset_dut=+0.08,
        rh_spatial_offset_ref=-0.04,
        rh_stability_sigma=0.12,
    ),
    reference_spec=ReferenceStaticSpec(
        bias=+0.10,
        repeatability_sigma=0.05,
        resolution=0.01,
    ),
    dut_spec=DUTStaticSpec(
        offset=+0.80,
        repeatability_sigma=0.20,
        resolution=0.10,
    ),
    daq_spec=DAQSpec(sample_period_s=1.0),
):
    rngs = make_rngs(master_seed)
    elapsed = elapsed_time(n, daq_spec)
    rh_true_dut, rh_true_ref, chamber_fluct = chamber_static(
        rh_setpoint, n, chamber_spec, rngs["chamber"]
    )
    ref_raw, ref_logged, ref_noise = reference_static(
        rh_true_ref, reference_spec, rngs["reference"]
    )
    dut_raw, dut_logged, dut_noise = dut_static(
        rh_true_dut, dut_spec, rngs["dut"]
    )

    private = pd.DataFrame({
        "Elapsed_s": elapsed,
        "RH_Setpoint": rh_setpoint,
        "Temperature_Setpoint_C": temperature_setpoint,
        "RH_True_DUT": rh_true_dut,
        "RH_True_Reference": rh_true_ref,
        "True_Chamber_Fluctuation": chamber_fluct,
        "True_Reference_Noise": ref_noise,
        "True_DUT_Noise": dut_noise,
        "Reference_Raw_PreQuant": ref_raw,
        "DUT_Raw_PreQuant": dut_raw,
        "RH_Reference": ref_logged,
        "RH_DUT": dut_logged,
    })

    public = pd.DataFrame({
        "Elapsed_s": elapsed,
        "Test_ID": "SV001_STATIC",
        "Day_ID": 1,
        "Run_ID": 1,
        "RH_Setpoint": rh_setpoint,
        "Temperature_Setpoint_C": temperature_setpoint,
        "Chamber_State": "STABLE",
        "RH_Reference": ref_logged,
        "RH_DUT": dut_logged,
    })
    return private, public


def generate_hierarchical_fixture(
    master_seed=7140,
    days=3,
    runs_per_day=2,
    samples_per_run=100,
    day_sigma=0.25,
    run_sigma=0.12,
    repeatability_sigma=0.20,
):
    rngs = make_rngs(master_seed)
    dut_rng = rngs["dut"]
    rows = []
    for day in range(1, days + 1):
        day_effect = dut_rng.normal(0.0, day_sigma)
        for run in range(1, runs_per_day + 1):
            run_effect = dut_rng.normal(0.0, run_sigma)
            noise = dut_rng.normal(0.0, repeatability_sigma, size=samples_per_run)
            for k in range(samples_per_run):
                rows.append({
                    "Day_ID": day,
                    "Run_ID": run,
                    "Sample_ID": k + 1,
                    "True_Day_Effect": day_effect,
                    "True_Run_Effect": run_effect,
                    "True_Repeatability_Noise": noise[k],
                    "RH_DUT_PreQuant": 50.0 + day_effect + run_effect + noise[k],
                })
    return pd.DataFrame(rows)


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
    t = sampled_timebase(duration_s, dt_s)
    command = delayed_command(t, rh0, rh1, step_time_s)
    chamber = zoh_first_order(command, dt_s, chamber_tau_s, y_initial=rh0)
    reference_state = zoh_first_order(chamber, dt_s, reference_tau_s, y_initial=rh0)

    delay_samples = int(round(dut_dead_time_s / dt_s))
    if not math.isclose(delay_samples * dt_s, dut_dead_time_s, rel_tol=0, abs_tol=1e-12):
        raise ValueError("For this verification fixture, dead time must be an integer number of samples.")

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

    private = pd.DataFrame({
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
    })

    analyst = pd.DataFrame({
        "Elapsed_s": t,
        "Test_ID": "SV002_DYNAMIC",
        "RH_Command": command,
        "RH_Reference": rh_reference,
        "RH_DUT": rh_dut,
    })
    return private, analyst
