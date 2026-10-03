from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigurationBoundaryError(ValueError):
    """Raised when configuration or analyst output violates the lab boundary."""


PUBLIC_REQUIRED_KEYS = frozenset(
    {
        "schema_version",
        "lab_identity",
        "dut_public_spec",
        "reference_public_spec",
        "chamber_public_spec",
        "daq_public_spec",
        "experimental_design",
    }
)

PRIVATE_REQUIRED_KEYS = frozenset(
    {
        "schema_version",
        "dut_truth",
        "reference_truth",
        "chamber_truth",
        "random_effects",
        "rng",
    }
)

FORBIDDEN_EXACT_KEYS = frozenset(
    {
        "truth",
        "private_truth",
        "simulation_truth",
        "hidden_truth",
        "latent_state",
        "injected_error",
        "true_rh",
        "true_temperature",
        "true_value",
        "dut_truth",
        "reference_truth",
        "chamber_truth",
    }
)

FORBIDDEN_PREFIXES = ("true_", "hidden_", "latent_", "injected_", "private_")
FORBIDDEN_SUFFIXES = ("_truth",)


def repository_root() -> Path:
    """Return the repository root inferred from this source file."""
    return Path(__file__).resolve().parents[1]


def default_public_config_path() -> Path:
    """Return the canonical analyst-visible laboratory configuration path."""
    return repository_root() / "config" / "public" / "lab_spec_v1.json"


def private_config_root() -> Path:
    """Return the protected local simulator-truth directory."""
    return repository_root() / "config" / "private"


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigurationBoundaryError(f"Configuration file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationBoundaryError(f"Invalid JSON configuration: {path}") from exc

    if not isinstance(payload, dict):
        raise ConfigurationBoundaryError("Configuration root must be a JSON object.")
    return payload


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _key_is_private(key: str) -> bool:
    normalized = key.strip().lower()
    return (
        normalized in FORBIDDEN_EXACT_KEYS
        or normalized.startswith(FORBIDDEN_PREFIXES)
        or normalized.endswith(FORBIDDEN_SUFFIXES)
    )


def find_private_keys(payload: Any, prefix: str = "$") -> list[str]:
    """Return JSON-style paths for fields prohibited in analyst-facing payloads."""
    findings: list[str] = []

    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}"
            if _key_is_private(key_text):
                findings.append(path)
            findings.extend(find_private_keys(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            findings.extend(find_private_keys(value, f"{prefix}[{index}]"))

    return findings


def assert_analyst_payload_safe(payload: Any) -> None:
    """Fail closed if an analyst/public payload contains simulator-only field names."""
    findings = find_private_keys(payload)
    if findings:
        joined = ", ".join(findings[:10])
        raise ConfigurationBoundaryError(
            f"Analyst payload contains private/simulator-only fields: {joined}"
        )


def load_public_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load the analyst-visible lab specification and enforce the public boundary."""
    config_path = Path(path) if path is not None else default_public_config_path()

    if _is_within(config_path, private_config_root()):
        raise ConfigurationBoundaryError(
            "Public configuration cannot be loaded from config/private."
        )

    payload = _load_json_object(config_path)
    missing = sorted(PUBLIC_REQUIRED_KEYS - payload.keys())
    if missing:
        raise ConfigurationBoundaryError(
            f"Public configuration missing required sections: {missing}"
        )

    assert_analyst_payload_safe(payload)
    return payload


def load_private_truth(path: str | Path) -> dict[str, Any]:
    """Load simulator-only truth strictly from the protected config/private directory."""
    config_path = Path(path)
    if not _is_within(config_path, private_config_root()):
        raise ConfigurationBoundaryError(
            "Private simulator truth must be loaded from config/private."
        )

    payload = _load_json_object(config_path)
    missing = sorted(PRIVATE_REQUIRED_KEYS - payload.keys())
    if missing:
        raise ConfigurationBoundaryError(
            f"Private configuration missing required sections: {missing}"
        )
    return payload


def write_analyst_json(payload: Any, path: str | Path) -> Path:
    """Serialize analyst-facing JSON only after the no-private-fields gate passes."""
    assert_analyst_payload_safe(payload)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return output_path
