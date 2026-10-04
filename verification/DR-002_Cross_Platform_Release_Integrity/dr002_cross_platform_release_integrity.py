from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_MANIFEST_PATH = "data/generated/dataset_manifest.json"
CURRENT_COMMITMENT_PATH = "data/generated/release_commitment_v1_1.json"
HISTORICAL_COMMIT = "ab00064fb3b3f56014a6d4f7084a339de9254b9b"
HISTORICAL_MANIFEST_PATH = "data/generated/dataset_manifest.json"
REPORT = Path(__file__).with_name("dr002_verification_report.csv")

CSV_FILES = [
    "static_measurements.csv",
    "dynamic_step_measurements.csv",
    "ramp_measurements.csv",
    "cyclic_measurements.csv",
    "sinusoidal_measurements.csv",
    "stability_measurements.csv",
    "test_matrix.csv",
]

RELEASE_ARTIFACTS = [
    *(f"data/generated/{name}" for name in CSV_FILES),
    CURRENT_MANIFEST_PATH,
    CURRENT_COMMITMENT_PATH,
]

REQUIRED_ATTRIBUTES = {
    "data/generated/*.csv text eol=lf",
    "data/generated/*.json text eol=lf",
    "data/generated/README.md text eol=lf",
    "verification/**/*.csv text eol=lf",
}

PRIVATE_NAMES = {
    "static_campaign_truth_v1.csv",
    "step_campaign_truth_v1.csv",
    "ramp_campaign_truth_v1.csv",
    "cyclic_campaign_truth_v1.csv",
    "sinusoidal_campaign_truth_v1.csv",
    "stability_campaign_truth_v1.csv",
    "final_lab_personality_v1.json",
}


def record(check: str, description: str, passed: bool, detail: str) -> dict[str, str]:
    return {
        "Check": check,
        "Description": description,
        "Status": "PASS" if passed else "FAIL",
        "Detail": detail,
    }


def git_bytes(rev: str, path: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{rev}:{path}"])


def git_text(rev: str, path: str) -> str:
    return git_bytes(rev, path).decode("utf-8")


def git_json(rev: str, path: str) -> dict:
    payload = json.loads(git_text(rev, path))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {rev}:{path}")
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_shape_and_columns(data: bytes) -> tuple[int, list[str]]:
    text = data.decode("utf-8")
    handle = io.StringIO(text, newline="")
    reader = csv.reader(handle)
    header = next(reader)
    rows = sum(1 for _ in reader)
    return rows, header


def write_report(results: list[dict[str, str]]) -> None:
    with REPORT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Check", "Description", "Status", "Detail"],
        )
        writer.writeheader()
        writer.writerows(results)


def main() -> int:
    results: list[dict[str, str]] = []

    current_manifest = git_json("HEAD", CURRENT_MANIFEST_PATH)
    commitment = git_json("HEAD", CURRENT_COMMITMENT_PATH)
    historical_manifest = git_json(HISTORICAL_COMMIT, HISTORICAL_MANIFEST_PATH)

    identity_ok = (
        current_manifest.get("release_id") == "VSM-LAB-DATA-v1.1"
        and commitment.get("release_id") == "VSM-LAB-DATA-v1.1"
        and commitment.get("parent_release_id") == "VSM-LAB-DATA-v1"
        and commitment.get("parent_dataset_commit_sha") == HISTORICAL_COMMIT
        and commitment.get("release_type") == "CORRECTIVE"
    )
    results.append(record("A", "Corrective release identity and parent linkage are valid", identity_ok, f"release_id={current_manifest.get('release_id')}"))

    attributes = {
        line.strip()
        for line in (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    attr_ok = REQUIRED_ATTRIBUTES.issubset(attributes)
    results.append(record("B", "Canonical LF policy is enforced by .gitattributes", attr_ok, "required LF rules present" if attr_ok else f"missing={sorted(REQUIRED_ATTRIBUTES - attributes)}"))

    manifest_blob = git_bytes("HEAD", CURRENT_MANIFEST_PATH)
    manifest_hash = sha256_bytes(manifest_blob)
    expected_manifest_hash = commitment.get("dataset_manifest_sha256")
    manifest_hash_ok = manifest_hash == expected_manifest_hash
    results.append(record("C", "Committed v1.1 manifest SHA-256 matches release commitment", manifest_hash_ok, f"observed={manifest_hash}; expected={expected_manifest_hash}"))

    manifest_files = current_manifest.get("files", {})
    mismatched_hashes: list[str] = []
    for name in CSV_FILES:
        observed = sha256_bytes(git_bytes("HEAD", f"data/generated/{name}"))
        expected = manifest_files.get(name, {}).get("sha256")
        if observed != expected:
            mismatched_hashes.append(name)
    csv_hashes_ok = not mismatched_hashes
    results.append(record("D", "Committed CSV payload hashes match the v1.1 manifest", csv_hashes_ok, "all CSV hashes match" if csv_hashes_ok else f"mismatches={mismatched_hashes}"))

    payload_changed: list[str] = []
    historical_files = historical_manifest.get("files", {})
    for name in CSV_FILES:
        current_sha = manifest_files.get(name, {}).get("sha256")
        historical_sha = historical_files.get(name, {}).get("sha256")
        if current_sha != historical_sha:
            payload_changed.append(name)
    payload_preserved = not payload_changed and commitment.get("measurement_payload_changed") is False
    results.append(record("E", "Measurement payload commitments are unchanged from VSM-LAB-DATA-v1", payload_preserved, "all seven CSV SHA-256 commitments preserved" if payload_preserved else f"changed={payload_changed}"))

    normalized_current = deepcopy(current_manifest)
    normalized_current["release_id"] = historical_manifest.get("release_id")
    semantic_scope_ok = normalized_current == historical_manifest
    results.append(record("F", "Manifest semantic change is limited to the release identifier", semantic_scope_ok, "only release_id differs from historical v1 manifest" if semantic_scope_ok else "additional semantic differences detected"))

    cr_artifacts: list[str] = []
    for path in RELEASE_ARTIFACTS:
        if b"\r" in git_bytes("HEAD", path):
            cr_artifacts.append(path)
    canonical_lf_ok = not cr_artifacts
    results.append(record("G", "Committed release artifacts use canonical LF with no CR bytes", canonical_lf_ok, "canonical LF confirmed" if canonical_lf_ok else f"CR bytes found in={cr_artifacts}"))

    shape_mismatches: list[str] = []
    for name in CSV_FILES:
        rows, columns = csv_shape_and_columns(git_bytes("HEAD", f"data/generated/{name}"))
        expected_rows = manifest_files.get(name, {}).get("rows")
        expected_columns = manifest_files.get(name, {}).get("columns")
        if rows != expected_rows or columns != expected_columns:
            shape_mismatches.append(name)
    schema_ok = not shape_mismatches
    results.append(record("H", "Committed row counts and schemas match the v1.1 manifest", schema_ok, "all rows/columns match" if schema_ok else f"mismatches={shape_mismatches}"))

    hidden_boundary_ok = (
        current_manifest.get("analyst_private_truth_included") is False
        and current_manifest.get("hidden_personality_id") == historical_manifest.get("hidden_personality_id")
        and current_manifest.get("hidden_personality_sha256_commitment") == historical_manifest.get("hidden_personality_sha256_commitment")
    )
    results.append(record("I", "Analyst/private-truth boundary and hidden-personality commitment are preserved", hidden_boundary_ok, "boundary preserved" if hidden_boundary_ok else "boundary metadata changed"))

    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", "HEAD", "data/generated"],
        text=True,
    ).splitlines()
    leaked = sorted(Path(path).name for path in tracked if Path(path).name in PRIVATE_NAMES)
    no_private_files = not leaked
    results.append(record("J", "No private simulator-truth files are tracked in the release directory", no_private_files, "no private files tracked" if no_private_files else f"leaked={leaked}"))

    frozen_ok = (
        commitment.get("freeze_status") == "FROZEN"
        and commitment.get("verification_gate") == "DR-002"
        and commitment.get("verification_status") == "PASS (11/11)"
        and commitment.get("measurement_payload_changed") is False
    )
    results.append(record("K", "Corrective release commitment is in the final frozen state", frozen_ok, f"freeze_status={commitment.get('freeze_status')}; verification_status={commitment.get('verification_status')}"))

    write_report(results)
    passed = sum(row["Status"] == "PASS" for row in results)
    print(f"DR-002: {passed}/{len(results)} checks PASS")
    for row in results:
        print(f"{row['Check']}: {row['Status']} - {row['Description']}")

    if passed == len(results):
        print("VSM-LAB-DATA-v1.1 corrective release is frozen and cross-platform integrity is verified.")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
