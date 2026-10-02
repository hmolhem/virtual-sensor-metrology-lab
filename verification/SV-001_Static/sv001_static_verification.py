from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.chamber import ChamberStaticSpec, chamber_static
from src.dut import DUTStaticSpec, dut_static
from src.reference import ReferenceStaticSpec, reference_static
from src.simulation import generate_hierarchical_fixture, generate_static_dataset
from src.utils import quantize_positive


def run_sv001():
    results = []

    def record(test_id, description, passed, observed, expected):
        results.append({
            "Test_ID": test_id,
            "Description": description,
            "Status": "PASS" if bool(passed) else "FAIL",
            "Observed": observed,
            "Expected_or_Criterion": expected,
        })

    rng = np.random.default_rng(1)
    x = np.full(5, 50.0)
    _, logged, _ = dut_static(
        x,
        DUTStaticSpec(offset=0.80, repeatability_sigma=0.0, resolution=0.1),
        rng,
    )
    record("SV-001A", "Deterministic DUT offset",
           np.allclose(logged, 50.8), float(logged[0]), "50.8 %RH exactly")

    rng = np.random.default_rng(2)
    _, logged, _ = reference_static(
        x,
        ReferenceStaticSpec(bias=0.10, repeatability_sigma=0.0, resolution=0.01),
        rng,
    )
    record("SV-001B", "Deterministic reference bias",
           np.allclose(logged, 50.10), float(logged[0]), "50.10 %RH exactly")

    dut_q = float(quantize_positive([50.836], 0.1)[0])
    ref_q = float(quantize_positive([50.836], 0.01)[0])
    record("SV-001C", "DUT/reference quantization",
           np.isclose(dut_q, 50.8) and np.isclose(ref_q, 50.84),
           f"DUT={dut_q:.1f}, REF={ref_q:.2f}", "DUT=50.8, REF=50.84")

    rng = np.random.default_rng(3)
    n_large = 100_000
    noise = rng.normal(0.0, 0.20, size=n_large)
    mu = float(noise.mean())
    sd = float(noise.std(ddof=1))
    record("SV-001D", "Repeatability noise mean/std",
           abs(mu) < 0.01 and abs(sd - 0.20) < 0.01,
           f"mean={mu:.5f}, sd={sd:.5f}",
           "|mean|<0.01 and |sd-0.20|<0.01")

    rng = np.random.default_rng(4)
    chamber_spec = ChamberStaticSpec(rh_stability_sigma=0.12)
    dut_true, _, _ = chamber_static(50.0, n_large, chamber_spec, rng)
    chamber_mean = float(dut_true.mean())
    chamber_sd = float(dut_true.std(ddof=1))
    record("SV-001E", "Chamber stability mean/std",
           abs(chamber_mean - 50.0) < 0.01 and abs(chamber_sd - 0.12) < 0.01,
           f"mean={chamber_mean:.5f}, sd={chamber_sd:.5f}",
           "|mean-50|<0.01 and |sd-0.12|<0.01")

    h = generate_hierarchical_fixture(master_seed=7140)
    day_constant = h.groupby("Day_ID")["True_Day_Effect"].nunique().max() == 1
    run_constant = h.groupby(["Day_ID", "Run_ID"])["True_Run_Effect"].nunique().max() == 1
    noise_varies = h.groupby(["Day_ID", "Run_ID"])["True_Repeatability_Noise"].nunique().min() > 1
    record("SV-001F", "Hierarchical day/run/random-noise structure",
           day_constant and run_constant and noise_varies,
           f"day_constant={day_constant}, run_constant={run_constant}, noise_varies={noise_varies}",
           "day=True, run=True, noise=True")

    p1, a1 = generate_static_dataset(master_seed=7140)
    p2, a2 = generate_static_dataset(master_seed=7140)
    _, a3 = generate_static_dataset(master_seed=7141)
    same_seed_same = a1.equals(a2) and p1.equals(p2)
    diff_seed_diff = not a1.equals(a3)
    record("SV-001G", "Fixed-seed reproducibility",
           same_seed_same and diff_seed_diff,
           f"same_seed_same={same_seed_same}, different_seed_diff={diff_seed_diff}",
           "True, True")

    forbidden_tokens = ("true_", "hidden_", "private_", "prequant")
    leaked = [c for c in a1.columns if any(tok in c.lower() for tok in forbidden_tokens)]
    record("SV-001H", "No private-truth fields in analyst dataset",
           len(leaked) == 0, f"leaked_columns={leaked}", "[]")

    return pd.DataFrame(results), p1, a1


if __name__ == "__main__":
    report, private_df, analyst_df = run_sv001()
    out_dir = Path(__file__).resolve().parent
    report.to_csv(out_dir / "sv001_verification_report.csv", index=False)
    private_df.to_csv(out_dir / "sv001_private_truth.csv", index=False)
    analyst_df.to_csv(out_dir / "sv001_analyst.csv", index=False)
    print(report.to_string(index=False))
    print()
    print("Overall:", "PASS" if (report["Status"] == "PASS").all() else "FAIL")
