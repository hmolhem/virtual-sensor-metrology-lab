from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.campaign import FILES, safe  # noqa: E402

GENERATED = ROOT / "data" / "generated"
MANIFEST = GENERATED / "dataset_manifest.json"
REPORT = Path(__file__).with_name("dr001_verification_report.csv")
COMMITMENT = ROOT / "config" / "public" / "private_personality_commitment_v1.json"

EXPECTED_ROWS = {
    "static_measurements.csv": 15120,
    "dynamic_step_measurements.csv": 9030,
    "ramp_measurements.csv": 21618,
    "cyclic_measurements.csv": 9003,
    "sinusoidal_measurements.csv": 5404,
    "stability_measurements.csv": 1320,
    "test_matrix.csv": 333,
}

EXPECTED_TESTS = {
    "static_measurements.csv": 252,
    "dynamic_step_measurements.csv": 30,
    "ramp_measurements.csv": 18,
    "cyclic_measurements.csv": 3,
    "sinusoidal_measurements.csv": 4,
    "stability_measurements.csv": 22,
}

RELEASE_FILES = [
    "static_measurements.csv",
    "dynamic_step_measurements.csv",
    "ramp_measurements.csv",
    "cyclic_measurements.csv",
    "sinusoidal_measurements.csv",
    "stability_measurements.csv",
    "test_matrix.csv",
    "dataset_manifest.json",
]


def record(check: str, description: str, passed: bool, detail: str) -> dict[str, str]:
    return {
        "Check": check,
        "Description": description,
        "Status": "PASS" if passed else "FAIL",
        "Detail": detail,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def main() -> int:
    results: list[dict[str, str]] = []

    missing = [name for name in RELEASE_FILES if not (GENERATED / name).exists()]
    results.append(
        record(
            "A",
            "Required release files exist",
            not missing,
            "all required files present" if not missing else f"missing={missing}",
        )
    )
    if missing:
        with REPORT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Check", "Description", "Status", "Detail"])
            writer.writeheader()
            writer.writerows(results)
        print("DR-001: 0/1 checks PASS")
        return 1

    manifest = load_json(MANIFEST)
    commitment = load_json(COMMITMENT)

    current_release_id = manifest.get("release_id")
    if current_release_id != "VSM-LAB-DATA-v1":
        print(
            "DR-001: SKIPPED — historical VSM-LAB-DATA-v1 gate; "
            f"current release is {current_release_id!r}. Use DR-002 for v1.1."
        )
        return 0

    identity_ok = (
        manifest.get("release_id") == "VSM-LAB-DATA-v1"
        and manifest.get("hidden_personality_id") == commitment.get("personality_id")
        and manifest.get("hidden_personality_sha256_commitment") == commitment.get("sha256")
        and manifest.get("analyst_private_truth_included") is False
    )
    results.append(
        record(
            "B",
            "Release identity and frozen hidden-personality commitment match",
            identity_ok,
            f"release_id={manifest.get('release_id')}",
        )
    )

    manifest_files = manifest.get("files", {})
    hash_detail: list[str] = []
    hashes_ok = True
    for filename in EXPECTED_ROWS:
        path = GENERATED / filename
        observed = sha256_file(path)
        expected = manifest_files.get(filename, {}).get("sha256")
        if observed != expected:
            hashes_ok = False
            hash_detail.append(filename)
    results.append(
        record(
            "C",
            "On-disk CSV hashes match dataset_manifest.json",
            hashes_ok,
            "all CSV hashes match" if hashes_ok else f"mismatches={hash_detail}",
        )
    )

    frames = {
        filename: pd.read_csv(GENERATED / filename)
        for filename in EXPECTED_ROWS
    }
    observed_rows = {filename: len(frame) for filename, frame in frames.items()}
    results.append(
        record(
            "D",
            "On-disk row counts match the frozen campaign design",
            observed_rows == EXPECTED_ROWS,
            str(observed_rows),
        )
    )

    observed_tests = {
        filename: int(frames[filename]["Test_ID"].nunique())
        for filename in EXPECTED_TESTS
    }
    results.append(
        record(
            "E",
            "On-disk unique test counts match the experimental design",
            observed_tests == EXPECTED_TESTS,
            str(observed_tests),
        )
    )

    safe_ok = True
    safe_detail = "no simulator-only columns in analyst CSV files"
    try:
        for filename in EXPECTED_TESTS:
            safe(frames[filename], filename)
    except Exception as exc:
        safe_ok = False
        safe_detail = str(exc)
    results.append(
        record(
            "F",
            "Analyst-facing CSV schemas contain no hidden-truth fields",
            safe_ok,
            safe_detail,
        )
    )

    static = frames["static_measurements.csv"]
    quantized = (
        ((static["RH_DUT"] * 10).round(8) % 1 == 0).all()
        and ((static["RH_Reference"] * 100).round(8) % 1 == 0).all()
    )
    results.append(
        record(
            "G",
            "Static DUT/reference quantization is preserved on disk",
            bool(quantized),
            "DUT=0.1 %RH; reference=0.01 %RH",
        )
    )

    numeric_ok = True
    for filename in EXPECTED_TESTS:
        frame = frames[filename]
        values = frame[["RH_Reference", "RH_DUT"]]
        if not (
            values.notna().all().all()
            and values.map(lambda x: abs(float(x)) < 200).all().all()
        ):
            numeric_ok = False
            break
    results.append(
        record(
            "H",
            "Released measurement outputs are finite and physically bounded",
            numeric_ok,
            "no NaN/Inf/extreme RH values",
        )
    )

    private_names = {
        "static_campaign_truth_v1.csv",
        "step_campaign_truth_v1.csv",
        "ramp_campaign_truth_v1.csv",
        "cyclic_campaign_truth_v1.csv",
        "sinusoidal_campaign_truth_v1.csv",
        "stability_campaign_truth_v1.csv",
        "final_lab_personality_v1.json",
    }
    leaked_private_files = sorted(
        path.name for path in GENERATED.iterdir() if path.name in private_names
    )
    results.append(
        record(
            "I",
            "Release directory contains no private simulator-truth files",
            not leaked_private_files,
            "no private files present" if not leaked_private_files else f"leaked={leaked_private_files}",
        )
    )

    manifest_rows_ok = all(
        manifest_files.get(filename, {}).get("rows") == expected
        for filename, expected in EXPECTED_ROWS.items()
    )
    results.append(
        record(
            "J",
            "Manifest row metadata agrees with the frozen release",
            manifest_rows_ok,
            "manifest row metadata verified",
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
    print(f"DR-001: {passed}/{len(results)} checks PASS")
    for row in results:
        print(f"{row['Check']}: {row['Status']} - {row['Description']}")

    if passed == len(results):
        print("Historical VSM-LAB-DATA-v1 release verification: PASS.")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
