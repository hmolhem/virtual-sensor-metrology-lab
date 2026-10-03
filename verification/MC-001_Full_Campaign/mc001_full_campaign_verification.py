from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.campaign import all_data, check_commitment, loadj, safe  # noqa: E402
from src.config_boundary import load_private_truth  # noqa: E402

PRIVATE = ROOT / "config" / "private" / "final_lab_personality_v1.json"
COMMITMENT = ROOT / "config" / "public" / "private_personality_commitment_v1.json"
EXECUTION = ROOT / "config" / "public" / "campaign_execution_v1.json"
REPORT = Path(__file__).with_name("mc001_verification_report.csv")

EXPECTED_ROWS = {
    "static": 15120,
    "step": 9030,
    "ramp": 21618,
    "cyclic": 9003,
    "sinusoidal": 5404,
    "stability": 1320,
}
EXPECTED_TESTS = {
    "static": 252,
    "step": 30,
    "ramp": 18,
    "cyclic": 3,
    "sinusoidal": 4,
    "stability": 22,
}


def record(check, description, passed, detail):
    return {
        "Check": check,
        "Description": description,
        "Status": "PASS" if passed else "FAIL",
        "Detail": detail,
    }


def main() -> int:
    results = []
    truth = load_private_truth(PRIVATE)
    commitment = loadj(COMMITMENT)
    execution = loadj(EXECUTION)

    try:
        check_commitment(truth, commitment)
        ok = True
        detail = "frozen personality hash matches commitment"
    except Exception as exc:
        ok = False
        detail = str(exc)
    results.append(record("A", "Frozen hidden personality commitment", ok, detail))

    analyst, private = all_data(truth, execution)

    observed_rows = {name: len(frame) for name, frame in analyst.items()}
    results.append(
        record(
            "B",
            "Analyst row counts match campaign design",
            observed_rows == EXPECTED_ROWS,
            str(observed_rows),
        )
    )

    observed_tests = {
        name: int(frame["Test_ID"].nunique()) for name, frame in analyst.items()
    }
    results.append(
        record(
            "C",
            "Unique test counts match experimental design",
            observed_tests == EXPECTED_TESTS,
            str(observed_tests),
        )
    )

    try:
        for name, frame in analyst.items():
            safe(frame, name)
        safe_ok = True
        safe_detail = "no simulator-only analyst columns"
    except Exception as exc:
        safe_ok = False
        safe_detail = str(exc)
    results.append(record("D", "Analyst schema contains no hidden-truth fields", safe_ok, safe_detail))

    analyst2, _ = all_data(truth, execution)
    reproducible = all(analyst[name].equals(analyst2[name]) for name in analyst)
    results.append(
        record(
            "E",
            "Campaign is bitwise reproducible in memory",
            reproducible,
            "all analyst DataFrames identical on repeated generation",
        )
    )

    private_has_truth = all(
        any("True_" in str(column) or "_True_" in str(column) for column in frame.columns)
        for frame in private.values()
    )
    results.append(
        record(
            "F",
            "Private campaign products retain simulator truth separately",
            private_has_truth,
            "truth-bearing columns present only in private products",
        )
    )

    quantized = (
        ((analyst["static"]["RH_DUT"] * 10).round(8) % 1 == 0).all()
        and ((analyst["static"]["RH_Reference"] * 100).round(8) % 1 == 0).all()
    )
    results.append(
        record(
            "G",
            "Static DUT/reference quantization is preserved",
            bool(quantized),
            "DUT=0.1 %RH; reference=0.01 %RH",
        )
    )

    finite = all(
        frame[["RH_Reference", "RH_DUT"]].notna().all().all()
        and frame[["RH_Reference", "RH_DUT"]].applymap(lambda x: abs(float(x)) < 200).all().all()
        for frame in analyst.values()
    )
    results.append(record("H", "Measurement outputs are finite and physically bounded", finite, "no NaN/Inf/extreme RH values"))

    with REPORT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Check", "Description", "Status", "Detail"])
        writer.writeheader()
        writer.writerows(results)

    passed = sum(row["Status"] == "PASS" for row in results)
    print(f"MC-001: {passed}/{len(results)} checks PASS")
    for row in results:
        print(f"{row['Check']}: {row['Status']} - {row['Description']}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
