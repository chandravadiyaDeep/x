import numpy as np
import pandas as pd

from numpa_cleaning import PipelineStep, run_pipeline


def make_df():
    df = pd.DataFrame(
        {
            "age": [25, 30, np.nan, 40, 200, 25],
            "city": ["Mumbai", "Delhi", "mumbai ", " Delhi", "Pune", "Mumbai"],
            "plan": ["A", "B", "A", "B", "A", "A"],
        }
    )
    return pd.concat([df, df.iloc[[0]]], ignore_index=True)  # add a duplicate row


def test_pipeline_runs_in_order_and_preserves_original():
    df = make_df()
    original_rows = len(df)

    steps = [
        PipelineStep(id="s1", type="impute_missing_values", params={"columns": ["age"], "strategy": "median"}),
        PipelineStep(id="s2", type="remove_duplicates", params={}),
        PipelineStep(id="s3", type="clean_text", params={"columns": ["city"]}),
        PipelineStep(id="s4", type="one_hot_encode", params={"columns": ["plan"]}),
    ]

    result = run_pipeline(df, steps)

    # original untouched
    assert len(df) == original_rows
    assert df["age"].isna().sum() == 1

    assert result.cleaned_df["age"].isna().sum() == 0
    assert result.final_rows < result.original_rows  # duplicate removed
    assert "plan_B" in result.cleaned_df.columns
    assert result.cleaned_df["city"].str.contains(" ").sum() == 0
    assert len(result.steps) == 4
    assert result.steps[1].summary.startswith("Removed")


def test_unknown_operation_raises():
    df = make_df()
    steps = [PipelineStep(id="bad", type="not_a_real_operation", params={})]
    try:
        run_pipeline(df, steps)
        assert False, "expected ValueError"
    except ValueError:
        pass
