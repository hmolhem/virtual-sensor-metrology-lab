from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config_boundary import (  # noqa: E402
    ConfigurationBoundaryError,
    assert_analyst_payload_safe,
    load_private_truth,
    load_public_config,
    write_analyst_json,
)


VERIFY_DIR = ROOT / "verification" / "CB-001_Config_Boundary"
PRIVATE_FIXTURE = ROOT / "config" / "private" / "cb001_fixture_truth.json"
ANALYST_OUTPUT = VERIFY_DIR / "cb001_analyst_output.json"
REPORT = VERIFY_DIR / "cb001_verification_report.csv"


def record(check_id: str, description: str, passed: bool, detail: str) -> dict[str, str]:
    return {
        "Check": check_id,
        "Description": description,
        "Status": "PASS" if passed else "FAIL",
        "Detail": detail,
    }


def tracked_private_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "config/private", "data/private_truth"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    results: list[dict[str, str]] = []

    public = load_public_config()
    results.append(
        record(
            "A",
            "Public configuration loads with required sections",
            public["schema_version"] == "1.0",
            f"schema_version={public['schema_version']}",
        )
    )

    dut_limits = public["dut_public_spec"]["acceptance_limits"]
    expected_limits = {
        "static_accuracy_abs_rh_percent",
        "repeatability_sigma_max_rh_percent",
        "hysteresis_max_rh_percent",
        "linearity_max_rh_percent",
        "temperature_influence_max_rh_percent_per_c",
        "t90_max_s",
        "settling_band_abs_rh_percent",
        "drift_max_rh_percent_per_year",
    }
    results.append(
        record(
            "B",
            "Public DUT acceptance limits are complete",
            expected_limits.issubset(dut_limits),
            f"limits={sorted(dut_limits)}",
        )
    )

    try:
        assert_analyst_payload_safe(public)
        safe_public = True
        safe_detail = "no private-key markers found"
    except ConfigurationBoundaryError as exc:
        safe_public = False
        safe_detail = str(exc)
    results.append(
        record(
            "C",
            "Public configuration contains no private fields",
            safe_public,
            safe_detail,
        )
    )

    dummy_private = {
        "schema_version": "CB-001-fixture",
        "dut_truth": {"offset_rh_percent": 0.25, "tau_up_s": 12.0},
        "reference_truth": {"bias_rh_percent": -0.05},
        "chamber_truth": {"bias_rh_percent": 0.10},
        "random_effects": {"day_sigma_rh_percent": 0.01},
        "rng": {"master_seed": 12345},
    }
    PRIVATE_FIXTURE.write_text(json.dumps(dummy_private, indent=2) + "\n", encoding="utf-8")

    try:
        loaded_private = load_private_truth(PRIVATE_FIXTURE)
        private_ok = loaded_private["schema_version"] == "CB-001-fixture"
        private_detail = "dummy verification truth loaded only from config/private"
    except Exception as exc:
        private_ok = False
        private_detail = str(exc)
    finally:
        PRIVATE_FIXTURE.unlink(missing_ok=True)

    results.append(
        record(
            "D",
            "Private loader accepts protected local fixture",
            private_ok,
            private_detail,
        )
    )

    outside_private = VERIFY_DIR / "cb001_private_fixture.json"
    outside_private.write_text(json.dumps(dummy_private), encoding="utf-8")
    try:
        try:
            load_private_truth(outside_private)
            reject_outside = False
            reject_detail = "loader incorrectly accepted private truth outside config/private"
        except ConfigurationBoundaryError:
            reject_outside = True
            reject_detail = "private truth outside config/private rejected"
    finally:
        outside_private.unlink(missing_ok=True)
    results.append(
        record(
            "E",
            "Private loader rejects unprotected paths",
            reject_outside,
            reject_detail,
        )
    )

    safe_record = {
        "Timestamp": "2026-10-03T12:00:00",
        "RH_DUT": 50.1,
        "RH_Reference": 49.9,
        "Temperature_DUT": 25.0,
        "Temperature_Reference": 25.0,
        "RH_Setpoint": 50.0,
        "T_Setpoint": 25.0,
        "Test_ID": "CB001-DEMO",
        "Run_ID": "R1",
        "Day_ID": "D1",
        "Direction": "UP",
        "Chamber_State": "STABLE",
    }
    try:
        assert_analyst_payload_safe(safe_record)
        safe_record_ok = True
        safe_record_detail = "canonical analyst record accepted"
    except ConfigurationBoundaryError as exc:
        safe_record_ok = False
        safe_record_detail = str(exc)
    results.append(
        record(
            "F",
            "Canonical analyst record passes boundary gate",
            safe_record_ok,
            safe_record_detail,
        )
    )

    leaked_record = dict(safe_record)
    leaked_record["true_rh"] = 50.0
    leaked_record["dut_truth"] = {"offset": 0.25}
    try:
        assert_analyst_payload_safe(leaked_record)
        leak_rejected = False
        leak_detail = "leaked private fields were not rejected"
    except ConfigurationBoundaryError as exc:
        leak_rejected = True
        leak_detail = str(exc)
    results.append(
        record(
            "G",
            "Leaked private fields are rejected",
            leak_rejected,
            leak_detail,
        )
    )

    try:
        write_analyst_json(safe_record, ANALYST_OUTPUT)
        exported = json.loads(ANALYST_OUTPUT.read_text(encoding="utf-8"))
        export_ok = set(exported) == set(safe_record)
        export_detail = f"exported_fields={len(exported)}"
    except Exception as exc:
        export_ok = False
        export_detail = str(exc)
    finally:
        ANALYST_OUTPUT.unlink(missing_ok=True)
    results.append(
        record(
            "H",
            "Analyst JSON writer enforces safe serialization",
            export_ok,
            export_detail,
        )
    )

    ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_ignore_lines = {
        "config/private/*",
        "!config/private/README.md",
        "data/private_truth/*",
        "!data/private_truth/README.md",
    }
    ignore_ok = all(line in ignore_text.splitlines() for line in required_ignore_lines)
    results.append(
        record(
            "I",
            "Git ignore policy protects final private truth",
            ignore_ok,
            "required private-path rules present" if ignore_ok else "missing private-path ignore rule",
        )
    )

    tracked = tracked_private_files()
    allowed_tracked = {"config/private/README.md", "data/private_truth/README.md"}
    tracked_ok = set(tracked).issubset(allowed_tracked)
    results.append(
        record(
            "J",
            "No private truth files are tracked",
            tracked_ok,
            f"tracked_private_paths={tracked}",
        )
    )

    role_policy = public["experimental_design"]["static"]["role_policy"]
    split_ok = (
        "Days 1-2" in role_policy["calibration"]
        and "Day 3" in role_policy["validation"]
        and "characterization" in role_policy
    )
    results.append(
        record(
            "K",
            "Public experiment role policy matches declared design boundary",
            split_ok,
            f"roles={sorted(role_policy)}",
        )
    )

    with REPORT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Check", "Description", "Status", "Detail"],
        )
        writer.writeheader()
        writer.writerows(results)

    passed = sum(row["Status"] == "PASS" for row in results)
    print(f"CB-001: {passed}/{len(results)} checks PASS")
    for row in results:
        print(f"{row['Check']}: {row['Status']} - {row['Description']}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
