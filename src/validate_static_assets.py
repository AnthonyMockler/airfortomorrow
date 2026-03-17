#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import polars as pl
import yaml

from src.data_collectors.airgradient_collector import AirGradientCollector
from src.data_processors.firms_data_processor import load_historical_data
from src.make_silver import (
    clean_elevation_data,
    clean_landcover_data,
    clean_worldpop_data,
)
from src.utils.config_loader import ConfigLoader


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "config.yaml"

ELEVATION_STEM = "LAO_THA_elevation"
LANDCOVER_STEM = "LAO_THA_landcover"
WORLDPOP_STEM = "LAO_THA_worldpop_h3_08"

DEM_DIR = REPO_ROOT / "assets" / "dem"
LANDCOVER_DIR = REPO_ROOT / "assets" / "landcover"
WORLDPOP_DIR = REPO_ROOT / "assets" / "worldpop"
AIRGRADIENT_SENSOR_FILE = REPO_ROOT / "assets" / "sensor_lists" / "airgradient_sensor_list.csv"
FIRMS_HISTORICAL_DIR = REPO_ROOT / "data" / "raw" / "firms" / "historical"


@dataclass
class ValidationResult:
    name: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that static/bootstrap tabular assets still match the loader "
            "contracts used by the AQ pipeline."
        )
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=500,
        help=(
            "Number of data rows to sample from large tabular files before running the "
            "loader contract checks (default: 500)."
        ),
    )
    return parser.parse_args()


def _resolve_preferred_tabular_file(base_dir: Path, stem: str) -> Path:
    parquet_path = base_dir / f"{stem}.parquet"
    csv_path = base_dir / f"{stem}.csv"
    if parquet_path.exists():
        return parquet_path
    if csv_path.exists():
        return csv_path
    raise FileNotFoundError(f"Missing tabular asset for {stem} in {base_dir}")


def _copy_csv_head(source: Path, destination: Path, sample_rows: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("r", encoding="utf-8", errors="ignore") as src_handle, destination.open(
        "w", encoding="utf-8", newline=""
    ) as dest_handle:
        for line_number, line in enumerate(src_handle):
            dest_handle.write(line)
            if line_number >= sample_rows:
                break


def _copy_parquet_head(source: Path, destination: Path, sample_rows: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    (
        pl.scan_parquet(source)
        .head(sample_rows)
        .collect()
        .write_parquet(destination, compression="zstd", compression_level=12)
    )


def _copy_tabular_head(source: Path, destination: Path, sample_rows: int) -> None:
    if source.suffix == ".parquet":
        _copy_parquet_head(source, destination, sample_rows)
        return
    _copy_csv_head(source, destination, sample_rows)


def _build_sample_config(temp_root: Path, sample_rows: int) -> Path:
    with CONFIG_PATH.open("r", encoding="utf-8") as config_handle:
        config = yaml.safe_load(config_handle)

    sample_assets_root = temp_root / "assets"
    dem_dir = sample_assets_root / "dem"
    landcover_dir = sample_assets_root / "landcover"
    worldpop_dir = sample_assets_root / "worldpop"

    elevation_source = _resolve_preferred_tabular_file(DEM_DIR, ELEVATION_STEM)
    landcover_source = _resolve_preferred_tabular_file(LANDCOVER_DIR, LANDCOVER_STEM)
    worldpop_source = _resolve_preferred_tabular_file(WORLDPOP_DIR, WORLDPOP_STEM)

    _copy_tabular_head(elevation_source, dem_dir / elevation_source.name, sample_rows)
    _copy_tabular_head(landcover_source, landcover_dir / landcover_source.name, sample_rows)
    _copy_tabular_head(worldpop_source, worldpop_dir / worldpop_source.name, sample_rows)

    config["paths"]["assets"]["dem"] = str(dem_dir)
    config["paths"]["assets"]["landcover"] = str(landcover_dir)
    config["paths"]["assets"]["worldpop"] = str(worldpop_dir)
    config["paths"]["base"] = str(temp_root)

    sample_config_path = temp_root / "config.yaml"
    with sample_config_path.open("w", encoding="utf-8") as config_handle:
        yaml.safe_dump(config, config_handle, sort_keys=False)

    return sample_config_path


def _empty_silver_frame() -> pl.LazyFrame:
    return pl.DataFrame(
        schema={
            "cell": pl.UInt64,
            "date": pl.Date,
        }
    ).lazy()


def _assert_columns(df: pl.DataFrame, required_columns: set[str], asset_name: str) -> None:
    missing = required_columns.difference(df.columns)
    if missing:
        raise AssertionError(f"{asset_name} missing required output columns: {sorted(missing)}")


def _assert_non_empty(df, asset_name: str) -> None:
    if getattr(df, "empty", False):
        raise AssertionError(f"{asset_name} produced an empty dataframe")
    if hasattr(df, "height") and df.height == 0:
        raise AssertionError(f"{asset_name} produced an empty dataframe")
    if hasattr(df, "__len__") and len(df) == 0:
        raise AssertionError(f"{asset_name} produced an empty dataframe")


def _validate_elevation(config_path: Path, logger: logging.Logger) -> str:
    config_loader = ConfigLoader(str(config_path))
    status, elevation_lf = clean_elevation_data(
        _empty_silver_frame(), ["THA", "LAO"], logger, config_loader
    )
    if status != "success":
        raise AssertionError(f"elevation loader returned status {status!r}")
    elevation_df = elevation_lf.collect()
    _assert_non_empty(elevation_df, "elevation")
    _assert_columns(elevation_df, {"cell", "elevation"}, "elevation")
    if elevation_df["cell"].n_unique() != elevation_df.height:
        raise AssertionError("elevation output contains duplicate cells after loader processing")
    return f"{elevation_df.height} sampled rows"


def _validate_landcover(config_path: Path, logger: logging.Logger) -> str:
    config_loader = ConfigLoader(str(config_path))
    status, landcover_lf = clean_landcover_data(
        _empty_silver_frame(), ["THA", "LAO"], logger, config_loader
    )
    if status != "success":
        raise AssertionError(f"landcover loader returned status {status!r}")
    landcover_df = landcover_lf.collect()
    _assert_non_empty(landcover_df, "landcover")
    _assert_columns(
        landcover_df,
        {
            "cell",
            "trees",
            "grass",
            "shrub_and_scrub",
            "crops",
            "bare",
            "snow_and_ice",
            "flooded_vegetation",
            "built",
            "water",
        },
        "landcover",
    )
    if landcover_df["cell"].n_unique() != landcover_df.height:
        raise AssertionError("landcover output contains duplicate cells after loader processing")
    return f"{landcover_df.height} sampled rows"


def _validate_worldpop(config_path: Path, logger: logging.Logger) -> str:
    config_loader = ConfigLoader(str(config_path))
    status, worldpop_lf = clean_worldpop_data(
        _empty_silver_frame(), ["THA", "LAO"], logger, config_loader
    )
    if status != "success":
        raise AssertionError(f"worldpop loader returned status {status!r}")
    worldpop_df = worldpop_lf.collect()
    _assert_non_empty(worldpop_df, "worldpop")
    _assert_columns(worldpop_df, {"cell", "worldpop_population"}, "worldpop")
    if worldpop_df["cell"].n_unique() != worldpop_df.height:
        raise AssertionError("worldpop output contains duplicate cells after loader processing")
    return f"{worldpop_df.height} sampled rows"


def _validate_airgradient_seed_sensors(temp_root: Path, logger: logging.Logger) -> str:
    sample_sensor_file = temp_root / "airgradient_sensor_list.csv"
    runtime_sensor_file = temp_root / "runtime_sensor_cache" / "airgradient_sensor_list.csv"
    _copy_csv_head(AIRGRADIENT_SENSOR_FILE, sample_sensor_file, sample_rows=10_000)

    class SampleAirGradientCollector(AirGradientCollector):
        SEED_SENSOR_LIST_PATH = sample_sensor_file
        RUNTIME_SENSOR_LIST_PATH = runtime_sensor_file

    collector = SampleAirGradientCollector(str(CONFIG_PATH))
    sensor_df = collector.master_sensor_list

    if not runtime_sensor_file.exists():
        raise AssertionError("airgradient runtime sensor cache was not seeded from the bootstrap file")
    _assert_non_empty(sensor_df, "airgradient_seed_sensors")
    missing_columns = {"locationId", "latitude", "longitude"}.difference(sensor_df.columns)
    if missing_columns:
        raise AssertionError(
            f"airgradient seed sensor loader missing required columns: {sorted(missing_columns)}"
        )
    return f"{len(sensor_df)} sampled rows"


def _validate_firms_historical_samples(temp_root: Path, sample_rows: int) -> str:
    sample_firms_dir = temp_root / "firms_historical"
    sample_firms_dir.mkdir(parents=True, exist_ok=True)

    parquet_files = sorted(FIRMS_HISTORICAL_DIR.glob("*.parquet"))
    csv_files = sorted(FIRMS_HISTORICAL_DIR.glob("*.csv"))
    source_files = parquet_files if parquet_files else csv_files
    if not source_files:
        raise AssertionError(f"No historical FIRMS parquet/CSV files found in {FIRMS_HISTORICAL_DIR}")

    for source_file in source_files:
        _copy_tabular_head(source_file, sample_firms_dir / source_file.name, sample_rows)

    with contextlib.redirect_stdout(io.StringIO()):
        viirs_df, modis_df = load_historical_data(str(sample_firms_dir))
    _assert_non_empty(viirs_df, "firms_historical_samples.viirs")
    _assert_non_empty(modis_df, "firms_historical_samples.modis")

    required_columns = {"latitude", "longitude", "acq_date", "acq_time", "frp", "instrument"}
    viirs_missing = required_columns.difference(viirs_df.columns)
    modis_missing = required_columns.difference(modis_df.columns)
    if viirs_missing:
        raise AssertionError(f"VIIRS sampled loader output missing columns: {sorted(viirs_missing)}")
    if modis_missing:
        raise AssertionError(f"MODIS sampled loader output missing columns: {sorted(modis_missing)}")

    sample_format = "parquet" if source_files and source_files[0].suffix == ".parquet" else "csv"
    return f"format={sample_format}, viirs={len(viirs_df)} rows, modis={len(modis_df)} rows"


def _run_validation(
    name: str,
    validator: Callable[[], str],
) -> ValidationResult:
    try:
        detail = validator()
        return ValidationResult(name=name, status="success", detail=detail)
    except Exception as exc:  # noqa: BLE001 - contract validator should report any failure
        return ValidationResult(name=name, status="failure", detail=str(exc))


def main() -> int:
    args = parse_args()

    logger = logging.getLogger("static_asset_validator")
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.ERROR)

    with tempfile.TemporaryDirectory(prefix="static_asset_validation_") as temp_dir_name:
        temp_root = Path(temp_dir_name)
        sample_config_path = _build_sample_config(temp_root, args.sample_rows)

        results = [
            _run_validation("elevation", lambda: _validate_elevation(sample_config_path, logger)),
            _run_validation("landcover", lambda: _validate_landcover(sample_config_path, logger)),
            _run_validation("worldpop", lambda: _validate_worldpop(sample_config_path, logger)),
            _run_validation(
                "airgradient_seed_sensors",
                lambda: _validate_airgradient_seed_sensors(temp_root, logger),
            ),
            _run_validation(
                "firms_historical_samples",
                lambda: _validate_firms_historical_samples(temp_root, args.sample_rows),
            ),
        ]

    print("Asset format policy: parquet_preferred")
    print("Validated static asset loaders:")
    for result in results:
        print(f"- {result.name}: {result.status} ({result.detail})")

    failures = [result for result in results if result.status != "success"]
    if failures:
        print("Static asset contract validation failed.")
        return 1

    print("Static asset contract validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
