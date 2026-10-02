from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import pandas as pd


@dataclass(frozen=True)
class ExperimentalDesignConfig:
    static_rh_levels: tuple[float, ...] = (20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0)
    temperature_levels_c: tuple[float, ...] = (15.0, 25.0, 35.0)
    directions: tuple[str, ...] = ("Up", "Down")
    static_days: tuple[int, ...] = (1, 2, 3)
    runs_per_day: int = 2
    calibration_rh_levels: tuple[float, ...] = (20.0, 40.0, 60.0, 80.0)
    calibration_days: tuple[int, ...] = (1, 2)
    validation_rh_levels: tuple[float, ...] = (30.0, 50.0, 70.0)
    validation_days: tuple[int, ...] = (3,)
    stable_hold_s: int = 60
    sample_rate_hz: float = 1.0

    step_pairs: tuple[tuple[float, float], ...] = ((30.0, 70.0), (70.0, 30.0))
    step_repetitions: int = 5
    step_baseline_s: int = 60
    step_transient_s: int = 240

    ramp_pairs: tuple[tuple[float, float], ...] = ((30.0, 70.0), (70.0, 30.0))
    ramp_rate_rh_per_min: float = 2.0
    ramp_repetitions: int = 3

    cyclic_low_rh: float = 30.0
    cyclic_high_rh: float = 70.0
    cyclic_temperature_c: float = 25.0
    cyclic_cycles_per_session: int = 5
    cyclic_sessions: int = 3

    sinusoidal_center_rh: float = 50.0
    sinusoidal_amplitude_rh: float = 10.0
    sinusoidal_temperature_c: float = 25.0
    sinusoidal_periods_s: tuple[int, ...] = (600, 300, 120, 60)

    stability_days_total: int = 90
    stability_weekly_interval_days: int = 7
    stability_monthly_interval_days: int = 30
    stability_weekly_rh: float = 50.0
    stability_temperature_c: float = 25.0
    stability_monthly_rh_levels: tuple[float, ...] = (30.0, 50.0, 70.0)

    uncertainty_points: tuple[tuple[float, float], ...] = (
        (30.0, 25.0),
        (50.0, 25.0),
        (70.0, 25.0),
        (80.0, 35.0),
    )


def _assign_static_role(rh: float, day: int, config: ExperimentalDesignConfig) -> str:
    """Assign a mutually exclusive analysis role without validation leakage."""
    if rh in config.calibration_rh_levels and day in config.calibration_days:
        return "CALIBRATION"
    if rh in config.validation_rh_levels and day in config.validation_days:
        return "VALIDATION"
    return "CHARACTERIZATION"


def build_static_test_matrix(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    """Build the balanced static RH x temperature x direction x day x run design."""
    rows: list[dict] = []
    counters = {"CALIBRATION": 0, "VALIDATION": 0, "CHARACTERIZATION": 0}
    prefixes = {"CALIBRATION": "CAL", "VALIDATION": "VAL", "CHARACTERIZATION": "ST"}

    for rh, temp_c, direction, day, run in product(
        config.static_rh_levels,
        config.temperature_levels_c,
        config.directions,
        config.static_days,
        range(1, config.runs_per_day + 1),
    ):
        role = _assign_static_role(rh, day, config)
        counters[role] += 1
        test_id = f"{prefixes[role]}-{counters[role]:03d}"
        rows.append(
            {
                "Test_ID": test_id,
                "Test_Family": "STATIC",
                "Analysis_Role": role,
                "RH_Setpoint": rh,
                "Temperature_Setpoint_C": temp_c,
                "Direction": direction,
                "Day_ID": day,
                "Run_ID": run,
                "Hold_s": config.stable_hold_s,
                "Sample_Rate_Hz": config.sample_rate_hz,
                "Expected_Samples": int(round(config.stable_hold_s * config.sample_rate_hz)),
                "Chamber_State_Required": "STABLE",
            }
        )

    return pd.DataFrame(rows)


def build_step_test_matrix(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    rows: list[dict] = []
    idx = 0
    duration_s = config.step_baseline_s + config.step_transient_s
    for (rh_start, rh_end), temp_c, rep in product(
        config.step_pairs,
        config.temperature_levels_c,
        range(1, config.step_repetitions + 1),
    ):
        idx += 1
        direction = "Up" if rh_end > rh_start else "Down"
        rows.append(
            {
                "Test_ID": f"DY-STEP-{idx:03d}",
                "Test_Family": "DYNAMIC_STEP",
                "RH_Start": rh_start,
                "RH_End": rh_end,
                "Temperature_Setpoint_C": temp_c,
                "Direction": direction,
                "Repetition": rep,
                "Baseline_s": config.step_baseline_s,
                "Transient_s": config.step_transient_s,
                "Duration_s": duration_s,
                "Sample_Rate_Hz": config.sample_rate_hz,
                "Primary_Metrics": "dead_time;tau;t90;settling_time;overshoot",
            }
        )
    return pd.DataFrame(rows)


def build_ramp_test_matrix(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    rows: list[dict] = []
    idx = 0
    for (rh_start, rh_end), temp_c, rep in product(
        config.ramp_pairs,
        config.temperature_levels_c,
        range(1, config.ramp_repetitions + 1),
    ):
        idx += 1
        direction = "Up" if rh_end > rh_start else "Down"
        duration_s = abs(rh_end - rh_start) / config.ramp_rate_rh_per_min * 60.0
        rows.append(
            {
                "Test_ID": f"DY-RAMP-{idx:03d}",
                "Test_Family": "DYNAMIC_RAMP",
                "RH_Start": rh_start,
                "RH_End": rh_end,
                "Temperature_Setpoint_C": temp_c,
                "Direction": direction,
                "Repetition": rep,
                "Ramp_Rate_RH_per_min": config.ramp_rate_rh_per_min,
                "Duration_s": duration_s,
                "Sample_Rate_Hz": config.sample_rate_hz,
                "Primary_Metrics": "tracking_error;max_dynamic_error;rmse",
            }
        )
    return pd.DataFrame(rows)


def build_cyclic_test_matrix(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    rows: list[dict] = []
    for session in range(1, config.cyclic_sessions + 1):
        rows.append(
            {
                "Test_ID": f"DY-CYC-{session:03d}",
                "Test_Family": "DYNAMIC_CYCLIC",
                "RH_Low": config.cyclic_low_rh,
                "RH_High": config.cyclic_high_rh,
                "Temperature_Setpoint_C": config.cyclic_temperature_c,
                "Session": session,
                "Cycle_Count": config.cyclic_cycles_per_session,
                "Sample_Rate_Hz": config.sample_rate_hz,
                "Primary_Metrics": "cycle_to_cycle_repeatability;hysteresis;dynamic_drift",
            }
        )
    return pd.DataFrame(rows)


def build_sinusoidal_test_matrix(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    rows: list[dict] = []
    for idx, period_s in enumerate(config.sinusoidal_periods_s, start=1):
        rows.append(
            {
                "Test_ID": f"DY-SIN-{idx:03d}",
                "Test_Family": "DYNAMIC_SINUSOIDAL",
                "RH_Center": config.sinusoidal_center_rh,
                "RH_Amplitude": config.sinusoidal_amplitude_rh,
                "Temperature_Setpoint_C": config.sinusoidal_temperature_c,
                "Period_s": period_s,
                "Frequency_Hz": 1.0 / period_s,
                "Sample_Rate_Hz": config.sample_rate_hz,
                "Primary_Metrics": "gain;phase_lag",
            }
        )
    return pd.DataFrame(rows)


def build_stability_schedule(config: ExperimentalDesignConfig = ExperimentalDesignConfig()) -> pd.DataFrame:
    rows: list[dict] = []
    idx = 0

    weekly_days = list(
        range(0, config.stability_days_total, config.stability_weekly_interval_days)
    )
    monthly_days = list(
        range(
            config.stability_monthly_interval_days,
            config.stability_days_total + 1,
            config.stability_monthly_interval_days,
        )
    )

    for day in weekly_days:
        idx += 1
        rows.append(
            {
                "Test_ID": f"STAB-{idx:03d}",
                "Test_Family": "STABILITY",
                "Schedule_Type": "WEEKLY_CENTER_CHECK",
                "Aging_Day": day,
                "RH_Setpoint": config.stability_weekly_rh,
                "Temperature_Setpoint_C": config.stability_temperature_c,
                "Primary_Metrics": "bias;drift_from_baseline",
            }
        )

    for day, rh in product(monthly_days, config.stability_monthly_rh_levels):
        idx += 1
        rows.append(
            {
                "Test_ID": f"STAB-{idx:03d}",
                "Test_Family": "STABILITY",
                "Schedule_Type": "MONTHLY_MULTI_POINT",
                "Aging_Day": day,
                "RH_Setpoint": rh,
                "Temperature_Setpoint_C": config.stability_temperature_c,
                "Primary_Metrics": "bias;span_change;drift_from_baseline",
            }
        )

    return pd.DataFrame(rows)


def build_uncertainty_evaluation_points(
    config: ExperimentalDesignConfig = ExperimentalDesignConfig(),
) -> pd.DataFrame:
    rows: list[dict] = []
    for idx, (rh, temp_c) in enumerate(config.uncertainty_points, start=1):
        rows.append(
            {
                "Test_ID": f"UNC-{idx:03d}",
                "Test_Family": "UNCERTAINTY_EVALUATION",
                "RH_Setpoint": rh,
                "Temperature_Setpoint_C": temp_c,
                "Point_Type": "WORST_CASE" if (rh, temp_c) == (80.0, 35.0) else "REPRESENTATIVE",
            }
        )
    return pd.DataFrame(rows)


def build_all_test_matrices(
    config: ExperimentalDesignConfig = ExperimentalDesignConfig(),
) -> dict[str, pd.DataFrame]:
    """Return all currently defined experimental-design tables."""
    return {
        "static": build_static_test_matrix(config),
        "step": build_step_test_matrix(config),
        "ramp": build_ramp_test_matrix(config),
        "cyclic": build_cyclic_test_matrix(config),
        "sinusoidal": build_sinusoidal_test_matrix(config),
        "stability": build_stability_schedule(config),
        "uncertainty": build_uncertainty_evaluation_points(config),
    }
