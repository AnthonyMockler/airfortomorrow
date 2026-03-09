from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd
from behave import given, then


HIMAWARI_H3_REALTIME_PREFIX = "data/processed/himawari/h3/realtime/"
HIMAWARI_DAILY_REALTIME_PREFIX = "data/processed/himawari/daily_aggregated/realtime/daily_h3_aod_"
HIMAWARI_INTERP_REALTIME_PREFIX = "data/processed/himawari/interpolated/realtime/interpolated_h3_aod_"
HIMAWARI_RAW_PREFIX = "data/raw/himawari/"


def _require_last_result(context):
    if context.last_result is None:
        raise AssertionError("No command has been executed in this scenario.")
    return context.last_result


def _parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _resolve_updated_parquets(context, prefix: str) -> list[Path]:
    result = _require_last_result(context)
    matches: list[Path] = []
    for rel_path in result.updated_data_files:
        if not rel_path.startswith(prefix):
            continue
        if not rel_path.endswith(".parquet"):
            continue
        abs_path = context.repo_root / rel_path
        if abs_path.exists() and abs_path.is_file():
            matches.append(abs_path)
    return sorted(matches, key=lambda candidate: candidate.stat().st_mtime_ns)


def _resolve_updated_raw_files(context) -> list[Path]:
    result = _require_last_result(context)
    matches: list[Path] = []
    for rel_path in result.updated_data_files:
        if not rel_path.startswith(HIMAWARI_RAW_PREFIX):
            continue
        if not rel_path.endswith(".nc"):
            continue
        abs_path = context.repo_root / rel_path
        if abs_path.exists() and abs_path.is_file():
            matches.append(abs_path)
    return sorted(matches, key=lambda candidate: candidate.stat().st_mtime_ns)


def _load_selected_himawari_parquet(context, key: str, label: str) -> pd.DataFrame:
    parquet_path = getattr(context, key, None)
    assert parquet_path is not None, (
        f"No {label} parquet selected yet. "
        f"Run the corresponding 'current run should produce' step first."
    )
    assert parquet_path.exists(), f"{label} parquet does not exist: {parquet_path}"
    assert parquet_path.is_file(), f"{label} parquet path is not a file: {parquet_path}"

    cache_key_path = f"_cached_{key}_path"
    cache_key_df = f"_cached_{key}_df"
    cached_path = getattr(context, cache_key_path, None)
    cached_df = getattr(context, cache_key_df, None)
    if cached_path == parquet_path and cached_df is not None:
        return cached_df

    df = pd.read_parquet(parquet_path)
    setattr(context, cache_key_path, parquet_path)
    setattr(context, cache_key_df, df)
    return df


@given("I reset the Himawari boundary cache directory")
def step_reset_himawari_boundary_cache(context):
    cache_dir = context.repo_root / "data" / "cache" / "geoboundaries"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    context.himawari_boundary_cache_dir = cache_dir


@then('the command output should include Himawari CLI options "{options_csv}"')
def step_output_includes_himawari_cli_options(context, options_csv: str):
    result = _require_last_result(context)
    options = _parse_csv(options_csv)
    missing = [option for option in options if option not in result.output]
    assert not missing, (
        f"Missing expected Himawari CLI options in command output: {missing}\n"
        f"Command output:\n{result.output}"
    )


@then('the command wall-clock duration should be at least {min_seconds:d} seconds')
def step_command_duration_at_least(context, min_seconds: int):
    result = _require_last_result(context)
    duration = float(result.elapsed_seconds)
    context.last_command_elapsed_seconds = duration
    assert duration >= min_seconds, (
        f"Expected command duration >= {min_seconds}s, found {duration:.2f}s"
    )


@then('the current run should produce at least {count:d} updated Himawari raw files for mode "{mode}"')
def step_current_run_himawari_raw_files(context, count: int, mode: str):
    matches = _resolve_updated_raw_files(context)
    assert len(matches) >= count, (
        f"Expected at least {count} updated Himawari raw files for mode {mode!r}, "
        f"found {len(matches)}. Matched files: {[str(path) for path in matches]}"
    )
    context.updated_himawari_raw_files = matches
    context.latest_himawari_raw_file = matches[-1]


@then('the updated Himawari raw files for mode "{mode}" should include path tokens "{tokens_csv}"')
def step_updated_himawari_raw_files_include_tokens(context, mode: str, tokens_csv: str):
    paths = getattr(context, "updated_himawari_raw_files", None)
    assert paths, (
        f"No updated Himawari raw files are available for mode {mode!r}. "
        "Run the corresponding 'current run should produce' step first."
    )

    rel_paths = [path.relative_to(context.repo_root).as_posix() for path in paths]
    tokens = _parse_csv(tokens_csv)
    missing = [token for token in tokens if not any(token in rel_path for rel_path in rel_paths)]
    assert not missing, (
        f"Updated Himawari raw files for mode {mode!r} did not include path tokens {missing}. "
        f"Matched files: {rel_paths}"
    )


@then('the updated Himawari raw files for mode "{mode}" should include month/day directories')
def step_updated_himawari_raw_files_have_month_day_dirs(context, mode: str):
    paths = getattr(context, "updated_himawari_raw_files", None)
    assert paths, (
        f"No updated Himawari raw files are available for mode {mode!r}. "
        "Run the corresponding 'current run should produce' step first."
    )

    rel_paths = [path.relative_to(context.repo_root).as_posix() for path in paths]
    bad_paths = [
        rel_path
        for rel_path in rel_paths
        if re.fullmatch(r"data/raw/himawari/\d{6}/\d{2}/[^/]+\.nc", rel_path) is None
    ]
    assert not bad_paths, (
        f"Expected raw Himawari files to use YYYYMM/DD directories for mode {mode!r}. "
        f"Bad paths: {bad_paths}"
    )


@then('the latest updated Himawari raw file for mode "{mode}" should be non-empty')
def step_latest_himawari_raw_file_non_empty(context, mode: str):
    raw_path = getattr(context, "latest_himawari_raw_file", None)
    assert raw_path is not None, (
        f"No latest Himawari raw file is available for mode {mode!r}. "
        "Run the corresponding 'current run should produce' step first."
    )
    assert raw_path.exists(), f"Latest Himawari raw file does not exist: {raw_path}"
    assert raw_path.stat().st_size > 0, f"Latest Himawari raw file is empty: {raw_path}"


@then('the current run should produce at least {count:d} updated Himawari realtime H3 parquet files')
def step_current_run_himawari_h3_parquets(context, count: int):
    matches = _resolve_updated_parquets(context, HIMAWARI_H3_REALTIME_PREFIX)
    assert len(matches) >= count, (
        f"Expected at least {count} updated Himawari H3 realtime parquet files, found {len(matches)}. "
        f"Matched files: {[str(path) for path in matches]}"
    )
    context.latest_himawari_h3_realtime_parquet = matches[-1]
    context._cached_latest_himawari_h3_realtime_parquet_path = None
    context._cached_latest_himawari_h3_realtime_parquet_df = None


@then('the current run should produce at least {count:d} updated Himawari realtime daily aggregated parquet files')
def step_current_run_himawari_daily_parquets(context, count: int):
    matches = _resolve_updated_parquets(context, HIMAWARI_DAILY_REALTIME_PREFIX)
    assert len(matches) >= count, (
        f"Expected at least {count} updated Himawari daily realtime parquet files, found {len(matches)}. "
        f"Matched files: {[str(path) for path in matches]}"
    )
    context.latest_himawari_daily_realtime_parquet = matches[-1]
    context._cached_latest_himawari_daily_realtime_parquet_path = None
    context._cached_latest_himawari_daily_realtime_parquet_df = None


@then('the current run should produce at least {count:d} updated Himawari realtime interpolated parquet files')
def step_current_run_himawari_interpolated_parquets(context, count: int):
    matches = _resolve_updated_parquets(context, HIMAWARI_INTERP_REALTIME_PREFIX)
    assert len(matches) >= count, (
        f"Expected at least {count} updated Himawari interpolated realtime parquet files, found {len(matches)}. "
        f"Matched files: {[str(path) for path in matches]}"
    )
    context.latest_himawari_interpolated_realtime_parquet = matches[-1]
    context._cached_latest_himawari_interpolated_realtime_parquet_path = None
    context._cached_latest_himawari_interpolated_realtime_parquet_df = None


@then('the latest updated Himawari realtime H3 parquet should contain at least {min_rows:d} rows')
def step_latest_h3_min_rows(context, min_rows: int):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_h3_realtime_parquet",
        "Himawari realtime H3",
    )
    assert len(df) >= min_rows, (
        f"Expected at least {min_rows} rows in Himawari realtime H3 parquet, found {len(df)}"
    )


@then('the latest updated Himawari realtime daily aggregated parquet should contain at least {min_rows:d} rows')
def step_latest_daily_min_rows(context, min_rows: int):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_daily_realtime_parquet",
        "Himawari realtime daily aggregated",
    )
    assert len(df) >= min_rows, (
        f"Expected at least {min_rows} rows in Himawari daily realtime parquet, found {len(df)}"
    )


@then('the latest updated Himawari realtime interpolated parquet should contain at least {min_rows:d} rows')
def step_latest_interpolated_min_rows(context, min_rows: int):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_interpolated_realtime_parquet",
        "Himawari realtime interpolated",
    )
    assert len(df) >= min_rows, (
        f"Expected at least {min_rows} rows in Himawari interpolated realtime parquet, found {len(df)}"
    )


@then('the latest updated Himawari realtime H3 parquet should include columns "{columns_csv}"')
def step_latest_h3_has_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_h3_realtime_parquet",
        "Himawari realtime H3",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Missing required columns in Himawari realtime H3 parquet: {missing_columns}. "
        f"Available columns: {list(df.columns)}"
    )


@then('the latest updated Himawari realtime daily aggregated parquet should include columns "{columns_csv}"')
def step_latest_daily_has_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_daily_realtime_parquet",
        "Himawari realtime daily aggregated",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Missing required columns in Himawari daily realtime parquet: {missing_columns}. "
        f"Available columns: {list(df.columns)}"
    )


@then('the latest updated Himawari realtime interpolated parquet should include columns "{columns_csv}"')
def step_latest_interpolated_has_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_interpolated_realtime_parquet",
        "Himawari realtime interpolated",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Missing required columns in Himawari interpolated realtime parquet: {missing_columns}. "
        f"Available columns: {list(df.columns)}"
    )


@then('the latest updated Himawari realtime H3 parquet should have non-null values in columns "{columns_csv}"')
def step_latest_h3_non_null_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_h3_realtime_parquet",
        "Himawari realtime H3",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Cannot validate nulls because required columns are missing: {missing_columns}"
    )

    null_counts = {column: int(df[column].isna().sum()) for column in required_columns}
    bad_columns = {column: count for column, count in null_counts.items() if count > 0}
    assert not bad_columns, (
        f"Expected non-null values in columns {required_columns}, but found nulls: {bad_columns}"
    )


@then('the latest updated Himawari realtime daily aggregated parquet should have non-null values in columns "{columns_csv}"')
def step_latest_daily_non_null_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_daily_realtime_parquet",
        "Himawari realtime daily aggregated",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Cannot validate nulls because required columns are missing: {missing_columns}"
    )

    null_counts = {column: int(df[column].isna().sum()) for column in required_columns}
    bad_columns = {column: count for column, count in null_counts.items() if count > 0}
    assert not bad_columns, (
        f"Expected non-null values in columns {required_columns}, but found nulls: {bad_columns}"
    )


@then('the latest updated Himawari realtime interpolated parquet should have non-null values in columns "{columns_csv}"')
def step_latest_interpolated_non_null_columns(context, columns_csv: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_interpolated_realtime_parquet",
        "Himawari realtime interpolated",
    )
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Cannot validate nulls because required columns are missing: {missing_columns}"
    )

    null_counts = {column: int(df[column].isna().sum()) for column in required_columns}
    bad_columns = {column: count for column, count in null_counts.items() if count > 0}
    assert not bad_columns, (
        f"Expected non-null values in columns {required_columns}, but found nulls: {bad_columns}"
    )


@then('the latest updated Himawari realtime H3 parquet should have numeric values in column "{column}"')
def step_latest_h3_numeric_column(context, column: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_h3_realtime_parquet",
        "Himawari realtime H3",
    )
    assert column in df.columns, f"Column {column!r} not found in Himawari realtime H3 parquet"
    non_null = df[column].dropna()
    assert len(non_null) > 0, f"Column {column!r} has no non-null values to validate"
    numeric_series = pd.to_numeric(non_null, errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r}, found {invalid_count} non-numeric non-null values"
    )


@then('the latest updated Himawari realtime daily aggregated parquet should have numeric values in column "{column}"')
def step_latest_daily_numeric_column(context, column: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_daily_realtime_parquet",
        "Himawari realtime daily aggregated",
    )
    assert column in df.columns, f"Column {column!r} not found in Himawari daily realtime parquet"
    non_null = df[column].dropna()
    assert len(non_null) > 0, f"Column {column!r} has no non-null values to validate"
    numeric_series = pd.to_numeric(non_null, errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r}, found {invalid_count} non-numeric non-null values"
    )


@then('the latest updated Himawari realtime interpolated parquet should have numeric values in column "{column}"')
def step_latest_interpolated_numeric_column(context, column: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_interpolated_realtime_parquet",
        "Himawari realtime interpolated",
    )
    assert column in df.columns, f"Column {column!r} not found in Himawari interpolated realtime parquet"
    non_null = df[column].dropna()
    assert len(non_null) > 0, f"Column {column!r} has no non-null values to validate"
    numeric_series = pd.to_numeric(non_null, errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r}, found {invalid_count} non-numeric non-null values"
    )


@then('the latest updated Himawari realtime H3 parquet should have at least {min_unique:d} unique values in column "{column}"')
def step_latest_h3_min_unique(context, min_unique: int, column: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_h3_realtime_parquet",
        "Himawari realtime H3",
    )
    assert column in df.columns, f"Column {column!r} not found in Himawari realtime H3 parquet"
    unique_count = int(df[column].nunique(dropna=True))
    assert unique_count >= min_unique, (
        f"Expected at least {min_unique} unique values in {column!r}, found {unique_count}"
    )


@then('the latest updated Himawari realtime daily aggregated parquet should have at least {min_unique:d} unique values in column "{column}"')
def step_latest_daily_min_unique(context, min_unique: int, column: str):
    df = _load_selected_himawari_parquet(
        context,
        "latest_himawari_daily_realtime_parquet",
        "Himawari realtime daily aggregated",
    )
    assert column in df.columns, f"Column {column!r} not found in Himawari daily realtime parquet"
    unique_count = int(df[column].nunique(dropna=True))
    assert unique_count >= min_unique, (
        f"Expected at least {min_unique} unique values in {column!r}, found {unique_count}"
    )
