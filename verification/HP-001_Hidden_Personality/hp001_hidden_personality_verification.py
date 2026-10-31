from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config_boundary import ConfigurationBoundaryError, load_private_truth  # noqa: E402

PRIVATE_PATH = ROOT / "config" / "private" / "final_lab_personality_v1.json"
COMMITMENT_PATH = ROOT / "config" / "public" / "private_personality_commitment_v1.json"


def canonical_sha256(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def classify(value: float, limit: float, lower_ratio: float = 0.85) -> str:
    ratio = abs(value) / limit
    if ratio < lower_ratio:
        return "PASS"
    if ratio <= 1.05:
        return "BORDERLINE"
    return "FAIL"


def proxy_categories(private: dict) -> set[str]:
    dut = private["dut_truth"]
    static = dut["static"]
    dynamics = dut["dynamics"]

    categories = {
        classify(static["repeatability_sigma_rh_percent"], 0.30),
        classify(static["hysteresis_loop_width_rh_percent"], 1.0),
        classify(static["temperature_coefficient_rh_percent_per_c"], 0.05),
        classify(dut["drift"]["annual_rh_percent"], 0.8),
        classify(dynamics["dead_time_s"] + 2.303 * dynamics["tau_up_s"], 60.0),
        classify(dynamics["dead_time_s"] + 2.303 * dynamics["tau_down_s"], 60.0),
    }
    return categories


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    if not PRIVATE_PATH.exists():
        print(
            "HP-001: SKIPPED — requires private simulator configuration at "
            f"{PRIVATE_PATH.relative_to(ROOT)}. Public clones intentionally do "
            "not contain this file; verify the published SHA-256 commitment instead."
        )
        return 0

    commitment = json.loads(COMMITMENT_PATH.read_text(encoding="utf-8"))
    checks.append(("A", commitment["personality_id"] == "VSM-LAB-HP-v1", "commitment identity"))

    try:
        private = load_private_truth(PRIVATE_PATH)
        checks.append(("B", True, "private file loaded only from protected path"))
    except ConfigurationBoundaryError as exc:
        print(f"B: FAIL - {exc}")
        return 1

    checks.append(("C", private["schema_version"] == "1.0", "private schema version"))

    digest = canonical_sha256(private)
    checks.append(("D", digest == commitment["sha256"], "SHA-256 commitment match"))

    top_level_ok = {
        "schema_version",
        "personality_id",
        "dut_truth",
        "reference_truth",
        "chamber_truth",
        "random_effects",
        "rng",
    }.issubset(private)
    checks.append(("E", top_level_ok, "required hidden domains present"))

    dut = private["dut_truth"]
    reference = private["reference_truth"]
    chamber = private["chamber_truth"]

    physical_sanity = (
        0.0 < dut["static"]["repeatability_sigma_rh_percent"] < 1.0
        and dut["static"]["resolution_rh_percent"] == 0.1
        and dut["dynamics"]["tau_up_s"] > 0.0
        and dut["dynamics"]["tau_down_s"] > 0.0
        and dut["dynamics"]["dead_time_s"] >= 0.0
        and 0.0 < reference["static"]["repeatability_sigma_rh_percent"] < 0.2
        and reference["static"]["resolution_rh_percent"] == 0.01
        and reference["dynamics"]["tau_s"] > 0.0
        and chamber["static"]["stability_sigma_rh_percent"] > 0.0
        and chamber["dynamics"]["tau_up_s"] > 0.0
        and chamber["dynamics"]["tau_down_s"] > 0.0
    )
    checks.append(("F", physical_sanity, "basic physical/range sanity"))

    rng_ok = isinstance(private["rng"]["master_seed"], int) and private["rng"]["master_seed"] > 0
    checks.append(("G", rng_ok, "deterministic campaign seed present"))

    categories = proxy_categories(private)
    mixed_behavior = {"PASS", "BORDERLINE", "FAIL"}.issubset(categories)
    checks.append(("H", mixed_behavior, "mixed pass/borderline/fail proxy behavior present"))

    passed = sum(ok for _, ok, _ in checks)
    print(f"HP-001: {passed}/{len(checks)} checks PASS")
    for check_id, ok, description in checks:
        print(f"{check_id}: {'PASS' if ok else 'FAIL'} - {description}")

    if digest == commitment["sha256"]:
        print("Commitment verified. Exact hidden values remain undisclosed.")

    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
