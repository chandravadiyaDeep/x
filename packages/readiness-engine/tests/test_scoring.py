import numpy as np
import pandas as pd

from numpa_readiness import assess


def make_churn_df(n=500, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "tenure_months": rng.integers(1, 72, n).astype(float),
            "monthly_charges": rng.normal(65, 20, n),
            "support_tickets": rng.poisson(1.5, n),
            "contract_type": rng.choice(["monthly", "one_year", "two_year"], n),
            "churned": rng.choice([0, 1], n, p=[0.85, 0.15]),
        }
    )
    # inject some missingness and duplicates
    df.loc[rng.choice(n, 20, replace=False), "monthly_charges"] = np.nan
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)
    return df


def test_classification_assessment_runs():
    df = make_churn_df()
    result = assess(df, task="classification", target="churned")
    assert result.overall_score is not None
    assert 0 <= result.overall_score <= 100
    assert result.coverage["total_checks"] > 0


def test_missing_target_is_critical():
    df = make_churn_df()
    result = assess(df, task="classification", target=None)
    target_dim = next(d for d in result.dimensions if d.name == "target_suitability")
    assert target_dim.applicable is False
    assert any(c.status == "critical" for c in target_dim.checks)


def test_clustering_has_no_target_dimension():
    df = make_churn_df()
    result = assess(df, task="clustering", target=None)
    target_dim = next(d for d in result.dimensions if d.name == "target_suitability")
    assert target_dim.applicable is False
    assert "target_suitability" in result.coverage["not_applicable_dimensions"]


def test_leakage_flags_near_perfect_correlation():
    df = make_churn_df()
    df["leak_copy_of_target"] = df["churned"] * 1.0
    result = assess(df, task="classification", target="churned")
    leakage_dim = next(d for d in result.dimensions if d.name == "leakage_validation")
    assert leakage_dim.quality < 0.5
    assert any("leak_copy_of_target" in c.id for c in leakage_dim.checks)
