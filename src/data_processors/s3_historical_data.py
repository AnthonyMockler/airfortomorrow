import boto3
import pandas as pd
import gzip
import io
import os
import time
import json
import math
import re
from datetime import date, datetime
import argparse
from tqdm import tqdm
from pathlib import Path
from botocore.exceptions import NoCredentialsError, ClientError
from botocore import UNSIGNED
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from time import perf_counter

# Add the project root directory to Python path for reliable imports
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_collectors.openaq_collector import OpenAQCollector

# Set a maximum number of workers for parallel processing
MAX_WORKERS = 8
DEFAULT_S3_CONNECT_TIMEOUT_SECONDS = 5
DEFAULT_S3_READ_TIMEOUT_SECONDS = 120
STAGE_TIMING_KEYS = [
    "skip_check_seconds",
    "skip_read_seconds",
    "s3_listing_seconds",
    "s3_get_object_seconds",
    "s3_body_read_seconds",
    "gzip_read_seconds",
    "dataframe_parse_seconds",
    "dataframe_concat_seconds",
    "parquet_write_seconds",
    "retry_sleep_seconds",
]


def _empty_stage_timings():
    return {key: 0.0 for key in STAGE_TIMING_KEYS}


def _empty_task_metrics():
    return {
        "csv_file_count": 0,
        "bytes_downloaded": 0,
        "rows_parsed": 0,
        "rows_written": 0,
        "retry_count": 0,
        "attempt_count": 0,
    }


def _percentile(values, percentile):
    """Return a simple nearest-rank percentile for a list of numeric values."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = max(0, math.ceil((percentile / 100) * len(sorted_values)) - 1)
    return sorted_values[index]


def _round_float(value):
    return round(float(value), 6)


def _build_numeric_summary(values):
    """Summarize a numeric series for timing or counter reporting."""
    if not values:
        return {
            "count": 0,
            "total": 0.0,
            "avg": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "max": 0.0,
        }
    total = sum(values)
    return {
        "count": len(values),
        "total": _round_float(total),
        "avg": _round_float(total / len(values)),
        "p50": _round_float(_percentile(values, 50)),
        "p95": _round_float(_percentile(values, 95)),
        "max": _round_float(max(values)),
    }


def _build_stage_summary(results):
    """Summarize per-stage timings across a set of task results."""
    summary = {}
    for key in STAGE_TIMING_KEYS + ["task_total_seconds"]:
        values = []
        for result in results:
            if key == "task_total_seconds":
                value = result.get("task_total_seconds", 0.0)
            else:
                value = result.get("stage_timings", {}).get(key, 0.0)
            if value > 0:
                values.append(value)
        summary[key] = _build_numeric_summary(values)
    return summary


def _summarize_metrics(results):
    """Summarize task-level counters across a set of task results."""
    metric_keys = ["csv_file_count", "bytes_downloaded", "rows_parsed", "rows_written", "retry_count", "attempt_count"]
    summary = {}
    for key in metric_keys:
        values = [result.get("metrics", {}).get(key, 0) for result in results]
        summary[key] = {
            "total": sum(values),
            "max": max(values) if values else 0,
            "avg": _round_float(sum(values) / len(values)) if values else 0.0,
        }
    return summary


def _top_slowest_tasks(results, limit=10):
    """Return the slowest location-year tasks with their dominant stages."""
    ranked = sorted(results, key=lambda item: item.get("task_total_seconds", 0.0), reverse=True)
    slowest = []
    for result in ranked[:limit]:
        stage_timings = result.get("stage_timings", {})
        dominant_stages = sorted(stage_timings.items(), key=lambda item: item[1], reverse=True)
        slowest.append({
            "location_id": result.get("location_id"),
            "year": result.get("year"),
            "status": result.get("status"),
            "task_total_seconds": _round_float(result.get("task_total_seconds", 0.0)),
            "dominant_stages": [
                {"stage": stage_name, "seconds": _round_float(seconds)}
                for stage_name, seconds in dominant_stages[:3]
                if seconds > 0
            ],
            "metrics": result.get("metrics", {}),
            "message": result.get("message"),
        })
    return slowest


def _build_download_profile(results, stats):
    """Build a structured summary of per-task timing results."""
    status_buckets = {}
    for status in sorted({result.get("status", "unknown") for result in results}):
        status_results = [result for result in results if result.get("status") == status]
        status_buckets[status] = {
            "count": len(status_results),
            "stage_summary": _build_stage_summary(status_results),
            "metric_summary": _summarize_metrics(status_results),
        }

    return {
        "stats": stats,
        "all_tasks_stage_summary": _build_stage_summary(results),
        "status_buckets": status_buckets,
        "top_slowest_tasks": _top_slowest_tasks(results),
    }


def _write_profile_report(output_dir, report):
    """Persist the timing report alongside the run artifacts."""
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    report_path = Path(output_dir) / f"historical_download_profile_{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report_path


def _print_profile_summary(run_profile, report_path):
    """Print the highest-signal timing summary for the current run."""
    location_profile = run_profile.get("location_discovery", {})
    download_profile = run_profile.get("download_profile", {})

    print("\nTiming Summary:")
    print(f"  - collector_init_seconds: {run_profile.get('collector_init_seconds', 0.0):.3f}s")
    print(f"  - location_discovery_total_seconds: {run_profile.get('location_discovery_total_seconds', 0.0):.3f}s")
    print(
        "    api_request_seconds="
        f"{location_profile.get('api_request_seconds', 0.0):.3f}s, "
        "processing_total_seconds="
        f"{location_profile.get('processing_total_seconds', 0.0):.3f}s"
    )
    print(f"  - bounded_download_total_seconds: {run_profile.get('bounded_download_total_seconds', 0.0):.3f}s")

    stage_summary = download_profile.get("all_tasks_stage_summary", {})
    ranked_stages = sorted(
        (
            (stage_name, summary["total"])
            for stage_name, summary in stage_summary.items()
            if summary.get("count", 0) > 0 and stage_name != "task_total_seconds"
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    for stage_name, total_seconds in ranked_stages[:5]:
        summary = stage_summary[stage_name]
        print(
            f"  - {stage_name}: total={total_seconds:.3f}s "
            f"avg={summary['avg']:.3f}s p95={summary['p95']:.3f}s max={summary['max']:.3f}s"
        )

    slowest_tasks = download_profile.get("top_slowest_tasks", [])
    if slowest_tasks:
        slowest = slowest_tasks[0]
        dominant = ", ".join(
            f"{item['stage']}={item['seconds']:.3f}s"
            for item in slowest.get("dominant_stages", [])
        )
        print(
            f"  - slowest_task: location={slowest['location_id']} year={slowest['year']} "
            f"status={slowest['status']} total={slowest['task_total_seconds']:.3f}s "
            f"stages=[{dominant}]"
        )

    print(f"Timing report written to: {report_path}")

KEY_DATE_PATTERN = re.compile(r"-(\d{8})\.csv\.gz$")


def _parse_yyyy_mm_dd(raw_value, arg_name):
    """Parse strict YYYY-MM-DD date strings used by CLI args."""
    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Invalid {arg_name}: {raw_value}. Expected YYYY-MM-DD.") from exc


def _extract_date_from_key(s3_key):
    match = KEY_DATE_PATTERN.search(s3_key)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def _year_overlaps_range(year, start_date, end_date):
    if start_date is None or end_date is None:
        return True
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    return not (year_end < start_date or year_start > end_date)


def _month_bounds_for_year(year, start_date, end_date):
    if start_date is None or end_date is None:
        return 1, 12
    month_start = start_date.month if year == start_date.year else 1
    month_end = end_date.month if year == end_date.year else 12
    return month_start, month_end


def _list_csv_files_for_location_year(
    s3_client,
    bucket_name,
    location_id,
    year,
    stage_timings,
    start_date=None,
    end_date=None,
):
    if not _year_overlaps_range(year, start_date, end_date):
        return []

    csv_files = []
    fallback_prefix = f"records/csv.gz/locationid={location_id}/year={year}"
    if start_date is None or end_date is None:
        prefixes_to_try = [fallback_prefix]
    else:
        month_start, month_end = _month_bounds_for_year(year, start_date, end_date)
        prefixes_to_try = [
            f"records/csv.gz/locationid={location_id}/year={year}/month={month:02d}/"
            for month in range(month_start, month_end + 1)
        ]

    seen_keys = set()

    def list_prefix(prefix):
        nonlocal csv_files
        continuation_token = None
        while True:
            list_kwargs = {"Bucket": bucket_name, "Prefix": prefix}
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token
            listing_start = perf_counter()
            response = s3_client.list_objects_v2(**list_kwargs)
            stage_timings["s3_listing_seconds"] += perf_counter() - listing_start

            for obj in response.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".csv.gz"):
                    continue
                if key in seen_keys:
                    continue
                if start_date is not None and end_date is not None:
                    key_date = _extract_date_from_key(key)
                    if key_date is None or key_date < start_date or key_date > end_date:
                        continue
                seen_keys.add(key)
                csv_files.append(key)

            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")

    for prefix in prefixes_to_try:
        list_prefix(prefix)

    # Fallback for older archive layouts if month-partitioned prefixes were empty.
    if (start_date is not None and end_date is not None) and not csv_files:
        list_prefix(fallback_prefix)

    return sorted(csv_files)


def _download_and_parse_csv_object(s3_client, bucket_name, csv_file):
    stage_values = {
        "s3_get_object_seconds": 0.0,
        "s3_body_read_seconds": 0.0,
        "gzip_read_seconds": 0.0,
        "dataframe_parse_seconds": 0.0,
    }

    get_object_start = perf_counter()
    obj = s3_client.get_object(Bucket=bucket_name, Key=csv_file)
    stage_values["s3_get_object_seconds"] = perf_counter() - get_object_start

    body_read_start = perf_counter()
    body_bytes = obj["Body"].read()
    stage_values["s3_body_read_seconds"] = perf_counter() - body_read_start

    gzip_start = perf_counter()
    csv_bytes = gzip.decompress(body_bytes)
    stage_values["gzip_read_seconds"] = perf_counter() - gzip_start

    parse_start = perf_counter()
    df = pd.read_csv(io.BytesIO(csv_bytes))
    stage_values["dataframe_parse_seconds"] = perf_counter() - parse_start

    return {
        "df": df,
        "rows": len(df),
        "bytes_downloaded": len(body_bytes),
        "stage_values": stage_values,
    }


def process_location_year(
    location_id,
    year,
    output_dir,
    s3_client,
    max_retries=3,
    per_location_download_workers=4,
    start_date=None,
    end_date=None,
):
    """Process a single location and year - returns result stats."""
    task_start = perf_counter()
    stage_timings = _empty_stage_timings()
    metrics = _empty_task_metrics()
    output_file = os.path.join(output_dir, f"location_{location_id}_{year}.parquet")

    def finalize(status, message, record_count=0, error=None):
        metrics["rows_written"] = record_count
        result = {
            "location_id": location_id,
            "year": year,
            "status": status,
            "message": message,
            "record_count": record_count,
            "task_total_seconds": _round_float(perf_counter() - task_start),
            "stage_timings": {key: _round_float(value) for key, value in stage_timings.items()},
            "metrics": metrics.copy(),
        }
        if error is not None:
            result["error"] = error
        return result

    skip_check_start = perf_counter()
    file_exists = os.path.exists(output_file)
    stage_timings["skip_check_seconds"] += perf_counter() - skip_check_start
    if file_exists:
        skip_read_start = perf_counter()
        try:
            existing_df = pd.read_parquet(output_file)
            record_count = len(existing_df)
        except Exception:
            record_count = 0
        stage_timings["skip_read_seconds"] += perf_counter() - skip_read_start
        return finalize(
            "skipped",
            f"File already exists for location {location_id} year {year}",
            record_count=record_count,
        )

    bucket_name = "openaq-data-archive"
    metrics["attempt_count"] = 1
    metrics["retry_count"] = 0

    try:
        csv_files = _list_csv_files_for_location_year(
            s3_client=s3_client,
            bucket_name=bucket_name,
            location_id=location_id,
            year=year,
            stage_timings=stage_timings,
            start_date=start_date,
            end_date=end_date,
        )
        metrics["csv_file_count"] = len(csv_files)
        if not csv_files:
            return finalize(
                "no_data",
                f"No CSV files found for location {location_id} year {year}",
            )

        all_dataframes = []
        with ThreadPoolExecutor(max_workers=per_location_download_workers) as object_executor:
            future_to_key = {
                object_executor.submit(
                    _download_and_parse_csv_object,
                    s3_client,
                    bucket_name,
                    csv_file,
                ): csv_file
                for csv_file in csv_files
            }
            for future in as_completed(future_to_key):
                csv_file = future_to_key[future]
                try:
                    object_result = future.result()
                except Exception as exc:
                    return finalize(
                        "failed",
                        f"Failed to download object {csv_file} for location {location_id} year {year}: {exc}",
                        error=type(exc).__name__,
                    )

                all_dataframes.append(object_result["df"])
                metrics["bytes_downloaded"] += object_result["bytes_downloaded"]
                metrics["rows_parsed"] += object_result["rows"]
                for stage_name, stage_value in object_result["stage_values"].items():
                    stage_timings[stage_name] += stage_value

        concat_start = perf_counter()
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        stage_timings["dataframe_concat_seconds"] += perf_counter() - concat_start
        record_count = len(combined_df)

        write_start = perf_counter()
        combined_df.to_parquet(output_file, index=False)
        stage_timings["parquet_write_seconds"] += perf_counter() - write_start

        return finalize(
            "success",
            f"Successfully downloaded {record_count} records for location {location_id} year {year}",
            record_count=record_count,
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "ClientError")
        if error_code == "NoSuchBucket":
            return finalize(
                "failed",
                f"Bucket {bucket_name} does not exist",
                error=error_code,
            )
        if error_code in {"NoSuchKey", "404"}:
            return finalize(
                "no_data",
                f"No data found for location {location_id} year {year}",
                error=error_code,
            )
        return finalize(
            "failed",
            f"S3 client error for location {location_id} year {year}: {error_code}",
            error=error_code,
        )
    except NoCredentialsError:
        return finalize(
            "failed",
            "AWS credentials not found. Using unsigned requests.",
            error="NoCredentialsError",
        )
    except Exception as exc:
        return finalize(
            "failed",
            f"Failed to process location {location_id} year {year}: {exc}",
            error=type(exc).__name__,
        )

def _derive_per_location_download_workers(max_workers):
    # Keep global S3 request fan-out bounded even when location-level workers are high.
    return max(2, min(8, max(1, 32 // max(1, max_workers))))


def _derive_max_pool_connections(max_workers, per_location_download_workers):
    projected_parallel_requests = max_workers * per_location_download_workers
    return max(32, min(512, projected_parallel_requests * 2))


def download_historical_data(
    location_ids,
    years,
    output_dir="./data/raw/openaq/historical",
    max_retries=3,
    start_date=None,
    end_date=None,
):
    """
    Download historical OpenAQ data from S3 for specified location IDs and years.
    Uses parallel processing for faster downloads and includes progress tracking.
    
    Args:
        location_ids: List of location IDs to download data for
        years: List of years to download data for
        output_dir: Directory to save the downloaded data
        max_retries: Maximum number of retries for failed downloads
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    per_location_download_workers = _derive_per_location_download_workers(MAX_WORKERS)
    max_pool_connections = _derive_max_pool_connections(MAX_WORKERS, per_location_download_workers)

    # Use botocore-native retry/backoff and tuned connection pooling.
    s3_client = boto3.client(
        "s3",
        config=Config(
            signature_version=UNSIGNED,
            retries={"mode": "adaptive", "max_attempts": max(2, max_retries + 1)},
            max_pool_connections=max_pool_connections,
            connect_timeout=DEFAULT_S3_CONNECT_TIMEOUT_SECONDS,
            read_timeout=DEFAULT_S3_READ_TIMEOUT_SECONDS,
        ),
    )
    
    # Statistics for reporting
    stats = {
        "success": 0,
        "failed": 0,
        "no_data": 0,
        "skipped": 0,
        "total_records": 0,
    }
    
    total_tasks = len(location_ids) * len(years)
    start_time = time.time()
    
    print(f"Starting download of historical data for {len(location_ids)} locations across {len(years)} years")
    print(f"Output directory: {output_dir}")
    print(f"Using {MAX_WORKERS} parallel workers for faster downloads")
    print(
        "S3 client settings: "
        f"retry_mode=adaptive, max_attempts={max(2, max_retries + 1)}, "
        f"max_pool_connections={max_pool_connections}, "
        f"per_location_download_workers={per_location_download_workers}"
    )
    
    # Create tasks for all location-year combinations
    tasks = []
    for location_id in location_ids:
        for year in years:
            tasks.append((location_id, year))
    
    # Process tasks in parallel with a progress bar
    progress_bar = tqdm(total=total_tasks, desc="Downloading data", unit="location-year combination")
    
    # Create a shared counter for completed tasks (to estimate remaining time)
    completed_tasks = 0
    results = []
    
    # Function to update progress
    def update_progress(future):
        nonlocal completed_tasks
        completed_tasks += 1
        progress_bar.update(1)
        
        # Calculate and update ETA based on average time per task
        elapsed = time.time() - start_time
        if completed_tasks > 0:
            avg_time_per_task = elapsed / completed_tasks
            remaining_tasks = total_tasks - completed_tasks
            eta = avg_time_per_task * remaining_tasks
            
            # Update progress bar description with ETA
            progress_bar.set_description(
                f"Downloading data - ETA: {format_time(eta)} - "
                f"Success: {stats['success']}, Failed: {stats['failed']}, "
                f"No data: {stats['no_data']}, Skipped: {stats['skipped']}"
            )
    
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(
                    process_location_year,
                    loc_id,
                    yr,
                    output_dir,
                    s3_client,
                    max_retries,
                    per_location_download_workers,
                    start_date,
                    end_date,
                ): (loc_id, yr) for loc_id, yr in tasks
            }
            
            # Process results as they complete
            for future in as_completed(future_to_task):
                result = future.result()
                results.append(result)
                
                # Update statistics based on result status
                status = result["status"]
                if status not in stats:
                    # If we encounter a new status type, add it to our stats
                    stats[status] = 0
                stats[status] += 1
                
                # Print success or failure messages and count records
                if status == "success":
                    record_count = result.get("record_count", 0)
                    stats["total_records"] += record_count
                    tqdm.write(result["message"])
                elif status == "skipped":
                    # Also count records from skipped files
                    record_count = result.get("record_count", 0)
                    stats["total_records"] += record_count
                elif status == "failed":
                    tqdm.write(f"Error: {result['message']}")
                
                # Update progress
                update_progress(future)
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        print("You can resume later - files that were successfully downloaded will be skipped.")
        sys.exit(1)
    
    progress_bar.close()
    
    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "="*50)
    print(f"Download Summary:")
    print(f"Total unique locations: {len(location_ids)}")
    print(f"Years requested: {years}")
    if start_date is not None and end_date is not None:
        print(f"Date window: {start_date.isoformat()} to {end_date.isoformat()}")
    print(f"Total location-year combinations: {len(location_ids) * len(years)}")
    print(f"Breakdown by location-year result:")
    print(f"  - Successfully downloaded: {stats['success']}")
    print(f"  - Skipped (already downloaded): {stats['skipped']}")
    print(f"  - No data available: {stats['no_data']}")
    print(f"  - Failed downloads: {stats['failed']}")
    print(f"Total records downloaded: {stats['total_records']}")
    print(f"Time taken: {format_time(elapsed_time)}")
    print("="*50)
    
    return {
        "stats": stats,
        "results": results,
        "profile": _build_download_profile(results, stats),
        "s3_settings": {
            "retry_mode": "adaptive",
            "max_attempts": max(2, max_retries + 1),
            "max_pool_connections": max_pool_connections,
            "per_location_download_workers": per_location_download_workers,
        },
    }

def format_time(seconds):
    """Format time in seconds to a human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def main():
    """Main function to run the script from command line."""
    # Get access to the global variable
    global MAX_WORKERS
    run_start = perf_counter()
    
    parser = argparse.ArgumentParser(description='Download historical OpenAQ data from S3')
    parser.add_argument('--years', type=int, nargs='+', default=[2024], 
                        help='Years to download data for (default: 2024)')
    parser.add_argument('--country-codes', type=int, nargs='+', default=[111],
                        help='Country codes to download data for (default: 111 for Thailand)')
    parser.add_argument('--output-dir', type=str, default='./data/raw/openaq/historical',
                        help='Directory to save the downloaded parquet files')
    parser.add_argument('--max-retries', type=int, default=3,
                        help='Maximum number of retries for failed downloads')
    parser.add_argument('--max-workers', type=int, default=MAX_WORKERS,
                        help=f'Maximum number of parallel downloads (default: {MAX_WORKERS})')
    parser.add_argument('--location-limit', type=int, default=None,
                        help='Maximum locations to process in this run (default: unlimited)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Optional start date for filtering downloaded objects (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='Optional end date for filtering downloaded objects (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # Update MAX_WORKERS if specified in arguments
    MAX_WORKERS = args.max_workers

    if (args.start_date and not args.end_date) or (args.end_date and not args.start_date):
        parser.error("Both --start-date and --end-date are required when using date filtering")

    requested_start_date = None
    requested_end_date = None
    years_to_process = sorted(set(args.years))
    if args.start_date and args.end_date:
        requested_start_date = _parse_yyyy_mm_dd(args.start_date, "--start-date")
        requested_end_date = _parse_yyyy_mm_dd(args.end_date, "--end-date")
        if requested_end_date < requested_start_date:
            parser.error("--end-date must be on or after --start-date")
        years_to_process = list(range(requested_start_date.year, requested_end_date.year + 1))
    
    # Initialize OpenAQCollector to get location IDs
    print("Initializing OpenAQ collector to get location IDs...")
    collector_init_start = perf_counter()
    collector = OpenAQCollector()
    collector_init_seconds = perf_counter() - collector_init_start
    
    # Get location IDs for specified countries
    print(f"Getting location IDs for country codes: {args.country_codes}")
    
    # Temporarily modify the OpenAQ countries in the shared config loader for this run.
    original_country_codes = list(collector.config_loader.config['data_collection']['openaq']['countries'])
    collector.config_loader.config['data_collection']['openaq']['countries'] = args.country_codes

    location_discovery_start = perf_counter()
    locations_gdf = collector._get_sensors_country()
    location_discovery_total_seconds = perf_counter() - location_discovery_start
    
    # Restore original country codes
    collector.config_loader.config['data_collection']['openaq']['countries'] = original_country_codes
    
    if locations_gdf.empty:
        print("Error: No locations found for the specified countries")
        return
    
    # Print country distribution to verify filtering
    country_counts = locations_gdf['country'].value_counts()
    print(f"Country distribution of locations: {country_counts.to_dict()}")
    
    # Extract location IDs
    location_ids = locations_gdf['location_id'].unique().tolist()
    if args.location_limit is not None:
        location_ids = location_ids[:args.location_limit]
        print(f"Location limit: {args.location_limit}")
    print(f"Found {len(location_ids)} unique locations for countries {args.country_codes}")
    print(
        f"Will process {len(location_ids) * len(years_to_process)} location-year combinations "
        f"({len(location_ids)} locations × {len(years_to_process)} years)"
    )
    if requested_start_date is not None and requested_end_date is not None:
        print(f"Requested date window: {requested_start_date.isoformat()} to {requested_end_date.isoformat()}")
    
    try:
        # Download data
        download_start = perf_counter()
        download_result = download_historical_data(
            location_ids,
            years_to_process,
            args.output_dir,
            args.max_retries,
            requested_start_date,
            requested_end_date,
        )
        bounded_download_total_seconds = perf_counter() - download_start
        run_profile = {
            "started_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "collector_init_seconds": _round_float(collector_init_seconds),
            "location_discovery_total_seconds": _round_float(location_discovery_total_seconds),
            "location_discovery": collector.last_sensor_country_profile,
            "bounded_download_total_seconds": _round_float(bounded_download_total_seconds),
            "run_total_seconds": _round_float(perf_counter() - run_start),
            "args": {
                "years": years_to_process,
                "country_codes": args.country_codes,
                "output_dir": args.output_dir,
                "max_retries": args.max_retries,
                "max_workers": args.max_workers,
                "location_limit": args.location_limit,
                "start_date": args.start_date,
                "end_date": args.end_date,
            },
            "download_profile": download_result["profile"],
            "s3_settings": download_result["s3_settings"],
        }
        report_path = _write_profile_report(args.output_dir, run_profile)
        _print_profile_summary(run_profile, report_path)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main() 
