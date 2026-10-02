from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.experiments import ExperimentalDesignConfig, build_all_test_matrices


def run_ed001():
    config = ExperimentalDesignConfig()
    matrices = build_all_test_matrices(config)
    rows: list[dict] = []

    def add(test_id, description, passed, observed, expected):
        rows.append({
            "Test_ID": test_id,
            "Description": description,
            "Status": "PASS" if bool(passed) else "FAIL",
            "Observed": str(observed),
            "Expected_or_Criterion": str(expected),
        })

    static = matrices["static"]
    add("ED-001A", "Static matrix contains full balanced factorial design",
        len(static) == 252, len(static), "252 condition-holds")

    cell_counts = static.groupby(["RH_Setpoint", "Temperature_Setpoint_C", "Direction"]).size()
    day_counts = static.groupby(["RH_Setpoint", "Temperature_Setpoint_C", "Direction", "Day_ID"]).size()
    add("ED-001B", "Static matrix is balanced across RH, temperature, direction, day, and run",
        cell_counts.nunique() == 1 and cell_counts.iloc[0] == 6 and day_counts.nunique() == 1 and day_counts.iloc[0] == 2,
        f"per RH/T/direction={sorted(cell_counts.unique())}; per RH/T/direction/day={sorted(day_counts.unique())}",
        "6 and 2 respectively")

    roles = static["Analysis_Role"].value_counts().to_dict()
    add("ED-001C", "Calibration, blind validation, and characterization roles have expected counts",
        roles == {"CHARACTERIZATION": 120, "CALIBRATION": 96, "VALIDATION": 36}, roles,
        "{'CALIBRATION': 96, 'VALIDATION': 36, 'CHARACTERIZATION': 120}")

    cal = static[static["Analysis_Role"] == "CALIBRATION"]
    val = static[static["Analysis_Role"] == "VALIDATION"]
    split_ok = (
        set(cal["RH_Setpoint"]) == set(config.calibration_rh_levels)
        and set(cal["Day_ID"]) == set(config.calibration_days)
        and set(val["RH_Setpoint"]) == set(config.validation_rh_levels)
        and set(val["Day_ID"]) == set(config.validation_days)
        and not (set(cal["Test_ID"]) & set(val["Test_ID"]))
    )
    add("ED-001D", "Calibration/validation split obeys predeclared RH and day holdouts", split_ok,
        f"CAL RH={sorted(cal.RH_Setpoint.unique())}, days={sorted(cal.Day_ID.unique())}; VAL RH={sorted(val.RH_Setpoint.unique())}, days={sorted(val.Day_ID.unique())}",
        "CAL RH 20/40/60/80 on days 1-2; VAL RH 30/50/70 on day 3")

    step = matrices["step"]
    step_combo = step.groupby(["RH_Start", "RH_End", "Temperature_Setpoint_C"]).size()
    add("ED-001E", "Dynamic step DOE has two directions, three temperatures, and five repetitions",
        len(step) == 30 and step_combo.nunique() == 1 and step_combo.iloc[0] == 5,
        f"rows={len(step)}, reps_per_step/T={sorted(step_combo.unique())}",
        "30 rows; 5 reps per step/temperature")

    ramp = matrices["ramp"]
    add("ED-001F", "Ramp DOE has 18 tests at 2 %RH/min with correct 20-minute ramp duration",
        len(ramp) == 18 and np.allclose(ramp["Ramp_Rate_RH_per_min"], 2.0) and np.allclose(ramp["Duration_s"], 1200.0),
        f"rows={len(ramp)}, durations={sorted(ramp.Duration_s.unique())}",
        "18 rows; 1200 s duration")

    cyclic = matrices["cyclic"]
    add("ED-001G", "Cyclic DOE has three sessions of five cycles at 25 C",
        len(cyclic) == 3 and (cyclic["Cycle_Count"] == 5).all() and np.allclose(cyclic["Temperature_Setpoint_C"], 25.0),
        f"rows={len(cyclic)}, cycle_count={sorted(cyclic.Cycle_Count.unique())}",
        "3 sessions; 5 cycles/session")

    sinusoidal = matrices["sinusoidal"]
    freq_ok = np.allclose(sinusoidal["Frequency_Hz"].values, 1.0 / sinusoidal["Period_s"].values)
    add("ED-001H", "Sinusoidal DOE preserves four predeclared periods and reciprocal frequency",
        set(sinusoidal["Period_s"]) == {600, 300, 120, 60} and freq_ok,
        f"periods={sorted(sinusoidal.Period_s.tolist(), reverse=True)}",
        "600, 300, 120, 60 s and f=1/T")

    stability = matrices["stability"]
    weekly = stability[stability["Schedule_Type"] == "WEEKLY_CENTER_CHECK"]
    monthly = stability[stability["Schedule_Type"] == "MONTHLY_MULTI_POINT"]
    add("ED-001I", "Ninety-day stability schedule contains weekly center checks and 30-day multi-point checks",
        len(stability) == 22 and len(weekly) == 13 and len(monthly) == 9 and set(monthly["Aging_Day"]) == {30, 60, 90},
        f"total={len(stability)}, weekly={len(weekly)}, monthly={len(monthly)}, monthly_days={sorted(monthly.Aging_Day.unique())}",
        "22 total = 13 weekly + 9 monthly; monthly days 30/60/90")

    uncertainty = matrices["uncertainty"]
    points = set(zip(uncertainty["RH_Setpoint"], uncertainty["Temperature_Setpoint_C"]))
    add("ED-001J", "Uncertainty evaluation points include three representative points and one worst-case point",
        points == {(30.0, 25.0), (50.0, 25.0), (70.0, 25.0), (80.0, 35.0)} and (uncertainty["Point_Type"] == "WORST_CASE").sum() == 1,
        f"points={sorted(points)}, worst_case_count={(uncertainty['Point_Type'] == 'WORST_CASE').sum()}",
        "30/50/70 %RH at 25 C plus 80 %RH at 35 C")

    all_ids = pd.concat([df[["Test_ID"]] for df in matrices.values()], ignore_index=True)["Test_ID"]
    add("ED-001K", "Test IDs are globally unique across all test families", all_ids.is_unique,
        f"total_ids={len(all_ids)}, unique_ids={all_ids.nunique()}", "all IDs unique")

    return pd.DataFrame(rows), matrices


if __name__ == "__main__":
    report, matrices = run_ed001()
    out_dir = Path(__file__).resolve().parent
    report.to_csv(out_dir / "ed001_verification_report.csv", index=False)
    for name, df in matrices.items():
        df.to_csv(out_dir / f"ed001_{name}_matrix.csv", index=False)
    print(report.to_string(index=False))
    print()
    print("Overall:", "PASS" if (report["Status"] == "PASS").all() else "FAIL")
