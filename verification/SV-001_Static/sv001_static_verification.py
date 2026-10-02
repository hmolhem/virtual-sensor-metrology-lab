from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


def quantize_positive(x, resolution):
    """Quantize non-negative measurements using half-up behavior."""
    x = np.asarray(x, dtype=float)
    return np.floor(x / resolution + 0.5) * resolution


def make_rngs(master_seed: int):
    """Create independent RNG streams for chamber, reference, DUT, and DAQ."""
    children = np.random.SeedSequence(master_seed).spawn(4)
    return {
        "chamber": np.random.default_rng(children[0]),
        "reference": np.random.default_rng(children[1]),
        "dut": np.random.default_rng(children[2]),
        "daq": np.random.default_rng(children[3]),
    }


@dataclass(frozen=True)
class ChamberStaticSpec:
    rh_setpoint_bias: float = 0.0
    rh_spatial_offset_dut: float = 0.0
    rh_spatial_offset_ref: float = 0.0
    rh_stability_sigma: float = 0.0


@dataclass(frozen=True)
class ReferenceStaticSpec:
    bias: float = 0.0
    repeatability_sigma: float = 0.0
    resolution: float = 0.01


@dataclass(frozen=True)
class DUTStaticSpec:
    offset: float = 0.0
    repeatability_sigma: float = 0.0
    resolution: float = 0.1


@dataclass(frozen=True)
class DAQSpec:
    sample_period_s: float = 1.0


def chamber_static(rh_setpoint, n, spec, rng):
    """Generate local true RH at DUT and reference positions."""
    common_fluctuation = rng.normal(0.0, spec.rh_stability_sigma, size=n)
    base = rh_setpoint + spec.rh_setpoint_bias
    rh_true_dut = base + spec.rh_spatial_offset_dut + common_fluctuation
    rh_true_ref = base + spec.rh_spatial_offset_ref + common_fluctuation
    return rh_true_dut, rh_true_ref, common_fluctuation


def reference_static(rh_true_ref, spec, rng):
    noise = rng.normal(0.0, spec.repeatability_sigma, size=len(rh_true_ref))
    raw = rh_true_ref + spec.bias + noise
    logged = quantize_positive(raw, spec.resolution)
    return raw, logged, noise


def dut_static(rh_true_dut, spec, rng, day_effect=0.0, run_effect=0.0):
    noise = rng.normal(0.0, spec.repeatability_sigma, size=len(rh_true_dut))
    raw = rh_true_dut + spec.offset + day_effect + run_effect + noise
    logged = quantize_positive(raw, spec.resolution)
    return raw, logged, noise


def generate_static_dataset(
    master_seed=7140,
    n=60,
    rh_setpoint=50.0,
    temperature_setpoint=25.0,
    chamber_spec=ChamberStaticSpec(
        rh_setpoint_bias=-0.05,
        rh_spatial_offset_dut=+0.08,
        rh_spatial_offset_ref=-0.04,
        rh_stability_sigma=0.12,
    ),
    reference_spec=ReferenceStaticSpec(
        bias=+0.10,
        repeatability_sigma=0.05,
        resolution=0.01,
    ),
    dut_spec=DUTStaticSpec(
        offset=+0.80,
        repeatability_sigma=0.20,
        resolution=0.10,
    ),
    daq_spec=DAQSpec(sample_period_s=1.0),
):
    rngs = make_rngs(master_seed)
    elapsed = np.arange(n, dtype=float) * daq_spec.sample_period_s

    rh_true_dut, rh_true_ref, chamber_fluct = chamber_static(
        rh_setpoint, n, chamber_spec, rngs["chamber"]
    )
    ref_raw, ref_logged, ref_noise = reference_static(
        rh_true_ref, reference_spec, rngs["reference"]
    )
    dut_raw, dut_logged, dut_noise = dut_static(
        rh_true_dut, dut_spec, rngs["dut"]
    )

    private = pd.DataFrame({
        "Elapsed_s": elapsed,
        "RH_Setpoint": rh_setpoint,
        "Temperature_Setpoint_C": temperature_setpoint,
        "RH_True_DUT": rh_true_dut,
        "RH_True_Reference": rh_true_ref,
        "True_Chamber_Fluctuation": chamber_fluct,
        "True_Reference_Noise": ref_noise,
        "True_DUT_Noise": dut_noise,
        "Reference_Raw_PreQuant": ref_raw,
        "DUT_Raw_PreQuant": dut_raw,
        "RH_Reference": ref_logged,
        "RH_DUT": dut_logged,
    })

    public = pd.DataFrame({
        "Elapsed_s": elapsed,
        "Test_ID": "SV001_STATIC",
        "Day_ID": 1,
        "Run_ID": 1,
        "RH_Setpoint": rh_setpoint,
        "Temperature_Setpoint_C": temperature_setpoint,
        "Chamber_State": "STABLE",
        "RH_Reference": ref_logged,
        "RH_DUT": dut_logged,
    })
    return private, public


def generate_hierarchical_fixture(
    master_seed=7140,
    days=3,
    runs_per_day=2,
    samples_per_run=100,
    day_sigma=0.25,
    run_sigma=0.12,
    repeatability_sigma=0.20,
):
    rngs = make_rngs(master_seed)
    dut_rng = rngs["dut"]
    rows = []

    for day in range(1, days + 1):
        day_effect = dut_rng.normal(0.0, day_sigma)
        for run in range(1, runs_per_day + 1):
            run_effect = dut_rng.normal(0.0, run_sigma)
            noise = dut_rng.normal(0.0, repeatability_sigma, size=samples_per_run)
            for k in range(samples_per_run):
                rows.append({
                    "Day_ID": day,
                    "Run_ID": run,
                    "Sample_ID": k + 1,
                    "True_Day_Effect": day_effect,
                    "True_Run_Effect": run_effect,
                    "True_Repeatability_Noise": noise[k],
                    "RH_DUT_PreQuant": 50.0 + day_effect + run_effect + noise[k],
                })
    return pd.DataFrame(rows)


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
    report.to_csv("sv001_verification_report.csv", index=False)
    private_df.to_csv("sv001_private_truth.csv", index=False)
    analyst_df.to_csv("sv001_analyst.csv", index=False)
    print(report.to_string(index=False))
    print()
    print("Overall:", "PASS" if (report["Status"] == "PASS").all() else "FAIL")
