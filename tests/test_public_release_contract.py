import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_release_is_v1_1_and_frozen():
    manifest = json.loads(
        (ROOT / "data/generated/dataset_manifest.json").read_text(encoding="utf-8")
    )
    commitment = json.loads(
        (ROOT / "data/generated/release_commitment_v1_1.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["release_id"] == "VSM-LAB-DATA-v1.1"
    assert commitment["release_id"] == "VSM-LAB-DATA-v1.1"
    assert commitment["freeze_status"] == "FROZEN"
    assert commitment["measurement_payload_changed"] is False


def test_private_truth_is_not_tracked_in_public_release():
    generated = ROOT / "data/generated"
    forbidden = {
        "static_campaign_truth_v1.csv",
        "step_campaign_truth_v1.csv",
        "ramp_campaign_truth_v1.csv",
        "cyclic_campaign_truth_v1.csv",
        "sinusoidal_campaign_truth_v1.csv",
        "stability_campaign_truth_v1.csv",
        "final_lab_personality_v1.json",
    }
    assert not ({p.name for p in generated.iterdir()} & forbidden)
