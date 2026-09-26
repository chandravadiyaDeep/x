from .missing_values import impute_missing_values
from .duplicates import remove_duplicates
from .encoding import one_hot_encode
from .scaling import standard_scale
from .outliers import remove_outliers_iqr
from .dtypes import convert_dtype
from .text import clean_text
from .rename import rename_columns

# Maps operation "type" strings (as used in a pipeline step definition)
# to their implementation. The website/API reads this registry to know
# what operations exist and what parameters they take, so the frontend
# and backend never maintain a second, conflicting list.
OPERATIONS = {
    "impute_missing_values": impute_missing_values,
    "remove_duplicates": remove_duplicates,
    "one_hot_encode": one_hot_encode,
    "standard_scale": standard_scale,
    "remove_outliers_iqr": remove_outliers_iqr,
    "convert_dtype": convert_dtype,
    "clean_text": clean_text,
    "rename_columns": rename_columns,
}

__all__ = ["OPERATIONS"]
