from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd
from behave import given, then, when


OPENAQ_REALTIME_PREFIX = "data/raw/openaq/realtime/openaq_realtime_"


def _require_last_result(context):
    if context.last_result is None:
        raise AssertionError("No command has been executed in this scenario.")
    return context.last_result


def _parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _resolve_updated_openaq_realtime_parquets(context) -> list[Path]:
    result = _require_last_result(context)
    matches: list[Path] = []

    for rel_path in result.updated_data_files:
        if not rel_path.startswith(OPENAQ_REALTIME_PREFIX):
            continue
        if not rel_path.endswith(".parquet"):
            continue
        abs_path = context.repo_root / rel_path
        if abs_path.exists() and abs_path.is_file():
            matches.append(abs_path)

    return sorted(matches, key=lambda candidate: candidate.stat().st_mtime_ns)


def _load_latest_openaq_parquet(context) -> pd.DataFrame:
    parquet_path = getattr(context, "latest_openaq_realtime_parquet", None)
    assert parquet_path is not None, (
        "No OpenAQ parquet is selected yet. "
        "Run step: 'the current run should produce at least N updated OpenAQ realtime parquet files'."
    )
    assert parquet_path.exists(), f"OpenAQ parquet does not exist: {parquet_path}"
    assert parquet_path.is_file(), f"OpenAQ parquet path is not a file: {parquet_path}"

    cached_path = getattr(context, "_cached_openaq_parquet_path", None)
    cached_df = getattr(context, "_cached_openaq_parquet_df", None)
    if cached_path == parquet_path and cached_df is not None:
        return cached_df

    df = pd.read_parquet(parquet_path)
    context._cached_openaq_parquet_path = parquet_path
    context._cached_openaq_parquet_df = df
    return df


@given('I compute an OpenAQ live sample limit at one tenth of baseline locations with minimum {minimum:d}')
def step_compute_openaq_live_sample_limit(context, minimum: int):
    from src.data_collectors.openaq_collector import OpenAQCollector

    collector = OpenAQCollector()
    sensors_df = collector._get_sensors_country()
    assert not sensors_df.empty, "OpenAQ baseline discovery returned no sensors."
    assert "location_id" in sensors_df.columns, "OpenAQ sensor list is missing location_id."
    assert "sensor_id" in sensors_df.columns, "OpenAQ sensor list is missing sensor_id."

    baseline_locations = int(sensors_df["location_id"].dropna().nunique())
    baseline_sensors = int(sensors_df["sensor_id"].dropna().astype(str).nunique())
    assert baseline_locations > 0, "OpenAQ baseline location count is zero."
    assert baseline_sensors > 0, "OpenAQ baseline sensor count is zero."

    one_tenth_limit = math.ceil(baseline_locations / 10)
    sample_limit = max(minimum, one_tenth_limit)
    sample_limit = min(sample_limit, baseline_locations)

    context.openaq_benchmark_metadata = {
        "minimum_limit": minimum,
        "baseline_locations": baseline_locations,
        "baseline_sensors": baseline_sensors,
        "one_tenth_limit": one_tenth_limit,
        "sample_limit": sample_limit,
        "collection_days": 1,
    }


@when('I run OpenAQ realtime collection with the computed sample limit and timeout {timeout:d}')
def step_run_openaq_with_computed_sample_limit(context, timeout: int):
    metadata = getattr(context, "openaq_benchmark_metadata", None)
    assert metadata is not None, "OpenAQ benchmark metadata is missing. Run baseline step first."

    sample_limit = metadata["sample_limit"]
    command = f"./scripts/collect_openaq_realtime.sh --days 1 --limit {sample_limit}"
    metadata["command"] = command
    context.run_shell(command, timeout=timeout)


@then("the command output should report the computed OpenAQ location limit")
def step_output_reports_computed_openaq_limit(context):
    result = _require_last_result(context)
    metadata = getattr(context, "openaq_benchmark_metadata", None)
    assert metadata is not None, "OpenAQ benchmark metadata is missing."
    expected_text = f"Location limit: {metadata['sample_limit']}"
    assert expected_text in result.output, (
        f"Expected output to contain computed limit text: {expected_text!r}\n"
        f"Command output:\n{result.output}"
    )


@then('the command output should report OpenAQ collection duration of at least {min_seconds:d} seconds')
def step_output_reports_minimum_openaq_duration(context, min_seconds: int):
    result = _require_last_result(context)
    metadata = getattr(context, "openaq_benchmark_metadata", None)
    assert metadata is not None, "OpenAQ benchmark metadata is missing."

    match = re.search(
        r"Data collection completed in\s+([0-9]+(?:\.[0-9]+)?)\s+seconds",
        result.output,
    )
    assert match, (
        "Could not find OpenAQ collection duration marker in command output.\n"
        f"{result.output}"
    )
    duration_seconds = float(match.group(1))
    metadata["reported_duration_seconds"] = duration_seconds
    assert duration_seconds >= min_seconds, (
        f"Expected OpenAQ duration >= {min_seconds}s, found {duration_seconds:.2f}s"
    )


@then("the benchmark metadata should record one-tenth sample sizing")
def step_benchmark_metadata_records_sample_sizing(context):
    metadata = getattr(context, "openaq_benchmark_metadata", None)
    assert metadata is not None, "OpenAQ benchmark metadata is missing."

    baseline_locations = metadata["baseline_locations"]
    one_tenth_limit = metadata["one_tenth_limit"]
    sample_limit = metadata["sample_limit"]
    minimum_limit = metadata["minimum_limit"]

    expected_limit = max(minimum_limit, one_tenth_limit)
    expected_limit = min(expected_limit, baseline_locations)
    assert sample_limit == expected_limit, (
        f"Expected computed sample_limit={expected_limit}, got {sample_limit}. "
        f"Metadata: {metadata}"
    )
    assert baseline_locations >= sample_limit, (
        f"Sample limit ({sample_limit}) cannot exceed baseline locations ({baseline_locations})"
    )
    assert metadata["baseline_sensors"] > 0, "Baseline sensors should be positive."


@then('the command output should include CLI options "{options_csv}"')
def step_output_includes_cli_options(context, options_csv: str):
    result = _require_last_result(context)
    options = _parse_csv(options_csv)
    missing = [option for option in options if option not in result.output]
    assert not missing, (
        f"Missing expected CLI options in command output: {missing}\n"
        f"Command output:\n{result.output}"
    )


@then('the current run should produce at least {count:d} updated OpenAQ realtime parquet files')
def step_current_run_produces_openaq_parquet(context, count: int):
    matches = _resolve_updated_openaq_realtime_parquets(context)
    assert len(matches) >= count, (
        f"Expected at least {count} updated OpenAQ realtime parquet files, found {len(matches)}. "
        f"Matched files: {[str(path) for path in matches]}"
    )
    context.latest_openaq_realtime_parquet = matches[-1]
    context._cached_openaq_parquet_path = None
    context._cached_openaq_parquet_df = None


@then('the latest updated OpenAQ realtime parquet should contain at least {min_rows:d} rows')
def step_latest_openaq_parquet_min_rows(context, min_rows: int):
    df = _load_latest_openaq_parquet(context)
    assert len(df) >= min_rows, (
        f"Expected at least {min_rows} rows in OpenAQ parquet, found {len(df)}"
    )


@then('the latest updated OpenAQ realtime parquet should include columns "{columns_csv}"')
def step_latest_openaq_parquet_has_columns(context, columns_csv: str):
    df = _load_latest_openaq_parquet(context)
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Missing required columns in OpenAQ parquet: {missing_columns}. "
        f"Available columns: {list(df.columns)}"
    )


@then('the latest updated OpenAQ realtime parquet should have non-null values in columns "{columns_csv}"')
def step_latest_openaq_parquet_non_null_columns(context, columns_csv: str):
    df = _load_latest_openaq_parquet(context)
    required_columns = _parse_csv(columns_csv)
    missing_columns = [column for column in required_columns if column not in df.columns]
    assert not missing_columns, (
        f"Cannot validate nulls because required columns are missing: {missing_columns}"
    )

    null_counts = {
        column: int(df[column].isna().sum())
        for column in required_columns
    }
    bad_columns = {column: count for column, count in null_counts.items() if count > 0}
    assert not bad_columns, (
        f"Expected non-null values in columns {required_columns}, but found nulls: {bad_columns}"
    )


@then('the latest updated OpenAQ realtime parquet should have numeric values in column "{column}"')
def step_latest_openaq_parquet_numeric_column(context, column: str):
    df = _load_latest_openaq_parquet(context)
    assert column in df.columns, f"Column {column!r} not found in OpenAQ parquet"
    numeric_series = pd.to_numeric(df[column], errors="coerce")
    invalid_count = int(numeric_series.isna().sum())
    assert invalid_count == 0, (
        f"Expected numeric values in column {column!r}, found {invalid_count} non-numeric values"
    )


@then('the latest updated OpenAQ realtime parquet should have at least {min_unique:d} unique values in column "{column}"')
def step_latest_openaq_parquet_min_unique(context, min_unique: int, column: str):
    df = _load_latest_openaq_parquet(context)
    assert column in df.columns, f"Column {column!r} not found in OpenAQ parquet"
    unique_count = int(df[column].nunique(dropna=True))
    assert unique_count >= min_unique, (
        f"Expected at least {min_unique} unique values in {column!r}, found {unique_count}"
    )
