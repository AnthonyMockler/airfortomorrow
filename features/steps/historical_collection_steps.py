from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
from behave import given, then


PRESERVED_TRACKED_DATA_FILES = {
    "data/training/silver_dataset.parquet",
}

PRESERVED_TRACKED_DATA_PREFIXES = (
    "data/raw/firms/historical/",
)

WORKSPACE_CLEANUPS = {
    "air_quality": [
        "data/raw/openaq/historical",
        "data/raw/airgradient/historical",
        "data/processed/airquality/historical",
    ],
    "firms": [
        "data/processed/firms",
    ],
    "himawari": [
        "data/raw/himawari",
        "data/processed/himawari",
        "data/cache/himawari",
        "data/cache/geoboundaries",
    ],
    "era5": [
        "data/raw/era5",
        "data/processed/era5/daily_aggregated/historical",
    ],
}

ARTIFACT_PREFIXES = {
    "openaq_raw": "data/raw/openaq/historical/location_",
    "airgradient_raw": "data/raw/airgradient/historical/airgradient_historical_",
    "air_quality": "data/processed/airquality/historical/air_quality_historical_",
    "firms_h3": "data/processed/firms/h3/historical/firms_kde_h308_",
    "himawari_h3": "data/processed/himawari/h3/historical/",
    "himawari_daily": "data/processed/himawari/daily_aggregated/historical/daily_h3_aod_",
    "himawari_interpolated": "data/processed/himawari/interpolated/historical/interpolated_h3_aod_",
    "era5": "data/processed/era5/daily_aggregated/historical/era5_daily_mean_",
}


def _is_preserved_tracked_data_path(repo_relative_path: str) -> bool:
    if repo_relative_path in PRESERVED_TRACKED_DATA_FILES:
        return True
    return any(
        repo_relative_path.startswith(prefix)
        for prefix in PRESERVED_TRACKED_DATA_PREFIXES
    )


def _clean_directory(context, raw_path: str) -> None:
    root = context.repo_root / raw_path
    root.mkdir(parents=True, exist_ok=True)

    for file_path in root.rglob("*"):
        if not (file_path.is_file() or file_path.is_symlink()):
            continue
        rel_path = file_path.relative_to(context.repo_root).as_posix()
        if not _is_preserved_tracked_data_path(rel_path):
            file_path.unlink()

    for dir_path in sorted(
        (candidate for candidate in root.rglob("*") if candidate.is_dir()),
        key=lambda candidate: len(candidate.parts),
        reverse=True,
    ):
        if any(dir_path.iterdir()):
            continue
        dir_path.rmdir()

    root.mkdir(parents=True, exist_ok=True)


def _require_last_result(context):
    if context.last_result is None:
        raise AssertionError("No command has been executed in this scenario.")
    return context.last_result


def _artifact_paths_from_run(context, label: str) -> list[Path]:
    result = _require_last_result(context)
    prefix = ARTIFACT_PREFIXES.get(label)
    assert prefix is not None, f"Unknown historical artifact label: {label}"

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


def _parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _selected_parquet_key(label: str) -> str:
    return f"selected_historical_parquet_{label}"


def _selected_paths_key(label: str) -> str:
    return f"selected_historical_paths_{label}"


def _context_get(context, name: str, default=None):
    try:
        return getattr(context, name)
    except (AttributeError, KeyError):
        return default


def _load_selected_parquet(context, label: str) -> pd.DataFrame:
    parquet_path = _context_get(context, _selected_parquet_key(label))
    assert parquet_path is not None, (
        f"No historical parquet selected for {label!r}. "
        "Run the corresponding 'current run should produce' step first."
    )
    assert parquet_path.exists(), f"Selected parquet does not exist: {parquet_path}"
    assert parquet_path.is_file(), f"Selected parquet is not a file: {parquet_path}"

    cache_path_key = f"_cached_{label}_historical_parquet_path"
    cache_df_key = f"_cached_{label}_historical_parquet_df"
    cached_path = _context_get(context, cache_path_key)
    cached_df = _context_get(context, cache_df_key)
    if cached_path == parquet_path and cached_df is not None:
        return cached_df

    df = pd.read_parquet(parquet_path)
    setattr(context, cache_path_key, parquet_path)
    setattr(context, cache_df_key, df)
    return df


@given('I prepare the historical collection workspace for "{workflow}"')
def step_prepare_historical_collection_workspace(context, workflow: str):
    cleanup_paths = WORKSPACE_CLEANUPS.get(workflow)
    assert cleanup_paths is not None, f"Unknown historical workflow: {workflow}"

    for raw_path in cleanup_paths:
        _clean_directory(context, raw_path)

    if workflow == "himawari":
        boundary_cache_dir = context.repo_root / "data" / "cache" / "geoboundaries"
        if boundary_cache_dir.exists():
            shutil.rmtree(boundary_cache_dir)
        boundary_cache_dir.mkdir(parents=True, exist_ok=True)


@then('the current run should produce at least {count:d} updated historical parquet files for "{label}"')
def step_current_run_produces_historical_parquets(context, count: int, label: str):
    matches = _artifact_paths_from_run(context, label)
    assert len(matches) >= count, (
        f"Expected at least {count} updated historical parquet files for {label!r}, "
        f"found {len(matches)}. Matched files: {[str(path) for path in matches]}"
    )
    setattr(context, _selected_paths_key(label), matches)
    setattr(context, _selected_parquet_key(label), matches[-1])


@then('the current run should produce no more than {count:d} updated historical parquet files for "{label}"')
def step_current_run_produces_no_more_than_historical_parquets(context, count: int, label: str):
    matches = _artifact_paths_from_run(context, label)
    assert len(matches) <= count, (
        f"Expected no more than {count} updated historical parquet files for {label!r}, "
        f"found {len(matches)}. Matched files: {[str(path) for path in matches]}"
    )
    if matches:
        setattr(context, _selected_paths_key(label), matches)
        setattr(context, _selected_parquet_key(label), matches[-1])


@then("the current run should create at least {count:d} new log files")
def step_current_run_creates_new_log_files(context, count: int):
    result = _require_last_result(context)
    assert len(result.new_log_files) >= count, (
        f"Expected at least {count} new log files, found {len(result.new_log_files)}. "
        f"New logs: {result.new_log_files}"
    )


@then('the updated historical parquet files for "{label}" should include date tokens "{tokens_csv}"')
def step_historical_updated_files_include_date_tokens(context, label: str, tokens_csv: str):
    paths = _context_get(context, _selected_paths_key(label))
    assert paths is not None, (
        f"No selected historical paths are available for {label!r}. "
        "Run the corresponding 'current run should produce' step first."
    )

    rel_paths = [path.relative_to(context.repo_root).as_posix() for path in paths]
    tokens = _parse_csv(tokens_csv)
    missing = [
        token for token in tokens if not any(token in rel_path for rel_path in rel_paths)
    ]
    assert not missing, (
        f"Updated historical parquet files for {label!r} did not include date tokens {missing}. "
        f"Matched files: {rel_paths}"
    )


@then('the latest updated historical parquet for "{label}" should contain at least {min_rows:d} rows')
def step_latest_historical_parquet_min_rows(context, label: str, min_rows: int):
    df = _load_selected_parquet(context, label)
    assert len(df) >= min_rows, (
        f"Expected at least {min_rows} rows in historical parquet for {label!r}, "
        f"found {len(df)}"
    )


@then('the latest updated historical parquet for "{label}" should include columns "{columns_csv}"')
def step_latest_historical_parquet_has_columns(context, label: str, columns_csv: str):
    df = _load_selected_parquet(context, label)
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Missing required columns in historical parquet for {label!r}: {missing_columns}. "
        f"Available columns: {list(df.columns)}"
    )


@then('the latest updated historical parquet for "{label}" should have non-null values in columns "{columns_csv}"')
def step_latest_historical_parquet_non_null_columns(context, label: str, columns_csv: str):
    df = _load_selected_parquet(context, label)
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Cannot validate nulls because required columns are missing for {label!r}: {missing_columns}"
    )

    null_counts = {column: int(df[column].isna().sum()) for column in required_columns}
    bad_columns = {column: count for column, count in null_counts.items() if count > 0}
    assert not bad_columns, (
        f"Expected non-null values in columns {required_columns} for {label!r}, "
        f"but found nulls: {bad_columns}"
    )


@then('the latest updated historical parquet for "{label}" should have numeric values in column "{column}"')
def step_latest_historical_parquet_numeric_column(context, label: str, column: str):
    df = _load_selected_parquet(context, label)
    assert column in df.columns, f"Column {column!r} not found in historical parquet for {label!r}"
    non_null = df[column].dropna()
    assert len(non_null) > 0, (
        f"Column {column!r} has no non-null values to validate in historical parquet for {label!r}"
    )
    numeric_series = pd.to_numeric(non_null, errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r} for {label!r}, "
        f"found {invalid_count} non-numeric non-null values"
    )


@then(
    'the latest updated historical parquet for "{label}" should have all numeric values in column "{column}" between "{minimum}" and "{maximum}"'
)
def step_latest_historical_parquet_numeric_range(
    context, label: str, column: str, minimum: str, maximum: str
):
    df = _load_selected_parquet(context, label)
    assert column in df.columns, f"Column {column!r} not found in historical parquet for {label!r}"
    non_null = df[column].dropna()
    assert len(non_null) > 0, (
        f"Column {column!r} has no non-null values to validate in historical parquet for {label!r}"
    )
    numeric_series = pd.to_numeric(non_null, errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r} for {label!r}, "
        f"found {invalid_count} non-numeric non-null values"
    )

    lower_bound = float(minimum)
    upper_bound = float(maximum)
    below = numeric_series < lower_bound
    above = numeric_series > upper_bound
    out_of_range_count = int((below | above).sum())
    assert out_of_range_count == 0, (
        f"Expected column {column!r} in historical parquet for {label!r} to stay within "
        f"[{lower_bound}, {upper_bound}], found {out_of_range_count} out-of-range values"
    )


@then('the latest updated historical parquet for "{label}" should have at least {min_unique:d} unique values in column "{column}"')
def step_latest_historical_parquet_min_unique(context, label: str, min_unique: int, column: str):
    df = _load_selected_parquet(context, label)
    assert column in df.columns, f"Column {column!r} not found in historical parquet for {label!r}"
    unique_count = int(df[column].nunique(dropna=True))
    assert unique_count >= min_unique, (
        f"Expected at least {min_unique} unique values in column {column!r} for {label!r}, "
        f"found {unique_count}"
    )


@then(
    'the latest updated historical parquet for "{label}" should have date values in column "{column}" within "{start_date}" and "{end_date}"'
)
def step_latest_historical_parquet_date_range(
    context, label: str, column: str, start_date: str, end_date: str
):
    df = _load_selected_parquet(context, label)
    assert column in df.columns, f"Column {column!r} not found in historical parquet for {label!r}"

    parsed = pd.to_datetime(df[column], errors="coerce")
    invalid_count = int(parsed.isna().sum())
    assert invalid_count == 0, (
        f"Expected date-like values in column {column!r} for {label!r}, "
        f"found {invalid_count} invalid entries"
    )

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    if getattr(parsed.dt, "tz", None) is not None:
        normalized = parsed.dt.tz_localize(None).dt.normalize()
    else:
        normalized = parsed.dt.normalize()
    below = normalized < start
    above = normalized > end
    out_of_range_count = int((below | above).sum())
    assert out_of_range_count == 0, (
        f"Expected dates in column {column!r} for {label!r} to stay within "
        f"[{start_date}, {end_date}], found {out_of_range_count} out-of-range entries"
    )
