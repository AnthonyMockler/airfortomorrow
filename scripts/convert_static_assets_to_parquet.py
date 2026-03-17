#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import polars as pl
import polars_h3 as plh3

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.utils.config_loader import ConfigLoader  # noqa: E402


@dataclass
class ConversionResult:
    source: Path
    target: Path
    source_size: int
    target_size: int
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert large static tabular assets into typed parquet files with ZSTD compression."
        )
    )
    parser.add_argument(
        "--compression-level",
        type=int,
        default=12,
        help="ZSTD compression level for parquet output (default: 12).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing parquet files.",
    )
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Delete CSV sources after successful parquet conversion.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned conversions without writing files.",
    )
    return parser.parse_args()


def _require_columns(df: pl.DataFrame, required: list[str], source: Path) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")


def _write_parquet(df: pl.DataFrame, target: Path, compression_level: int, dry_run: bool) -> int:
    if dry_run:
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(target, compression="zstd", compression_level=compression_level)
    return target.stat().st_size


def _read_tabular(source: Path) -> pl.DataFrame:
    if source.suffix == ".parquet":
        return pl.read_parquet(source)
    return pl.read_csv(source)


def _resolve_source(base_dir: Path, stem: str) -> Path:
    csv_source = base_dir / f"{stem}.csv"
    parquet_source = base_dir / f"{stem}.parquet"
    if csv_source.exists():
        return csv_source
    if parquet_source.exists():
        return parquet_source
    return csv_source


def _convert_elevation(source: Path) -> pl.DataFrame:
    df = _read_tabular(source)
    if "cell" in df.columns:
        cell_expr = pl.col("cell").cast(pl.UInt64)
    elif "hex_id" in df.columns:
        cell_expr = plh3.str_to_int("hex_id")
    else:
        raise ValueError(f"{source} requires either cell or hex_id column")

    _require_columns(df, ["elevation"], source)
    return (
        df.with_columns(
            [
                cell_expr.alias("cell"),
                pl.col("elevation").cast(pl.Int32).alias("elevation"),
            ]
        )
        .select(["cell", "elevation"])
        .unique(subset=["cell"])
    )


def _convert_landcover(source: Path) -> pl.DataFrame:
    df = _read_tabular(source)
    if "cell" in df.columns:
        cell_expr = pl.col("cell").cast(pl.UInt64)
    elif "h3_08" in df.columns:
        cell_expr = plh3.str_to_int("h3_08")
    else:
        raise ValueError(f"{source} requires either cell or h3_08 column")

    metric_cols = [
        "trees",
        "grass",
        "shrub_and_scrub",
        "crops",
        "bare",
        "snow_and_ice",
        "flooded_vegetation",
        "built",
        "water",
    ]
    _require_columns(df, metric_cols, source)

    return (
        df.with_columns(
            [cell_expr.alias("cell")]
            + [pl.col(col).cast(pl.Float32).alias(col) for col in metric_cols]
        )
        .select(["cell", *metric_cols])
        .unique(subset=["cell"])
    )


def _convert_worldpop(source: Path) -> pl.DataFrame:
    df = _read_tabular(source)

    if "cell" in df.columns:
        cell_expr = pl.col("cell").cast(pl.UInt64)
    elif "h3_08" in df.columns:
        cell_expr = plh3.str_to_int("h3_08")
    else:
        raise ValueError(f"{source} requires either cell or h3_08 column")

    if "worldpop_population" in df.columns:
        population_expr = pl.col("worldpop_population")
    elif "general" in df.columns:
        population_expr = pl.col("general")
    else:
        raise ValueError(f"{source} requires either worldpop_population or general column")

    return (
        df.with_columns(
            [
                cell_expr.alias("cell"),
                population_expr.cast(pl.Float32).alias("worldpop_population"),
            ]
        )
        .select(["cell", "worldpop_population"])
        .unique(subset=["cell"])
    )


def _convert_firms_tabular(source: Path) -> pl.DataFrame:
    if source.suffix == ".parquet":
        df = pl.read_parquet(source)
    else:
        df = pl.read_csv(
            source,
            infer_schema_length=50_000,
            schema_overrides={
                "acq_date": pl.String,
                "acq_time": pl.String,
                "confidence": pl.String,
                "version": pl.String,
                "satellite": pl.String,
                "instrument": pl.String,
                "daynight": pl.String,
            },
        )

    if "" in df.columns:
        df = df.drop("")
    if "Unnamed: 0" in df.columns:
        df = df.drop("Unnamed: 0")

    if "acq_date" not in df.columns:
        raise ValueError(f"{source} is missing required column: acq_date")
    if "instrument" not in df.columns:
        raise ValueError(f"{source} is missing required column: instrument")

    if df["acq_date"].dtype == pl.Date:
        parsed_dates = pl.col("acq_date")
    else:
        parsed_dates = pl.coalesce(
            [
                pl.col("acq_date").cast(pl.String, strict=False).str.strptime(pl.Date, "%Y-%m-%d", strict=False),
                pl.col("acq_date").cast(pl.String, strict=False).str.strptime(pl.Date, "%Y%m%d", strict=False),
            ]
        )

    cast_exprs: list[pl.Expr] = [
        parsed_dates.alias("acq_date"),
        pl.col("acq_time").cast(pl.UInt16, strict=False).alias("acq_time"),
    ]

    numeric_float32 = [
        "latitude",
        "longitude",
        "brightness",
        "scan",
        "track",
        "bright_t31",
        "frp",
    ]
    for col in numeric_float32:
        if col in df.columns:
            cast_exprs.append(pl.col(col).cast(pl.Float32, strict=False).alias(col))

    text_columns = ["satellite", "instrument", "confidence", "version", "daynight"]
    for col in text_columns:
        if col in df.columns:
            cast_exprs.append(pl.col(col).cast(pl.String, strict=False).alias(col))

    converted = df.with_columns(cast_exprs)
    if converted["acq_date"].is_null().any():
        raise ValueError(f"Failed to parse acq_date values in {source}")

    required_output = ["latitude", "longitude", "acq_date", "acq_time", "frp", "instrument"]
    _require_columns(converted, required_output, source)
    return converted.select(required_output)


def _convert_one(
    source: Path,
    target: Path,
    converter: Callable[[Path], pl.DataFrame],
    compression_level: int,
    overwrite: bool,
    dry_run: bool,
    delete_source: bool,
) -> ConversionResult:
    if not source.exists():
        return ConversionResult(source, target, 0, 0, "missing")

    if target.exists() and not overwrite:
        return ConversionResult(
            source,
            target,
            source.stat().st_size,
            target.stat().st_size,
            "skipped_exists",
        )

    source_size = source.stat().st_size
    df = converter(source)
    target_size = _write_parquet(df, target, compression_level, dry_run)

    if delete_source and not dry_run and target.exists() and source != target:
        source.unlink()

    return ConversionResult(source, target, source_size, target_size, "converted")


def _print_results(results: list[ConversionResult]) -> int:
    converted = [r for r in results if r.status == "converted"]
    skipped = [r for r in results if r.status == "skipped_exists"]
    missing = [r for r in results if r.status == "missing"]

    for result in results:
        print(
            f"- {result.status:13s} {result.source} -> {result.target} "
            f"({result.source_size} -> {result.target_size} bytes)"
        )

    src_total = sum(r.source_size for r in converted)
    dst_total = sum(r.target_size for r in converted)

    print("\nSummary:")
    print(f"- converted: {len(converted)}")
    print(f"- skipped_existing: {len(skipped)}")
    print(f"- missing: {len(missing)}")
    if src_total > 0 and dst_total > 0:
        ratio = src_total / dst_total
        pct = (1 - (dst_total / src_total)) * 100
        print(f"- converted source total: {src_total} bytes")
        print(f"- converted target total: {dst_total} bytes")
        print(f"- shrink ratio: {ratio:.2f}x ({pct:.1f}% smaller)")

    return 0


def main() -> int:
    args = parse_args()
    config_loader = ConfigLoader()

    dem_dir = config_loader.get_path("assets.dem")
    landcover_dir = config_loader.get_path("assets.landcover")
    worldpop_dir = config_loader.get_path("assets.worldpop")
    firms_historical_dir = config_loader.get_path("raw.firms.historical")

    static_jobs: list[tuple[Path, Path, Callable[[Path], pl.DataFrame]]] = [
        (
            _resolve_source(dem_dir, "LAO_THA_elevation"),
            dem_dir / "LAO_THA_elevation.parquet",
            _convert_elevation,
        ),
        (
            _resolve_source(landcover_dir, "LAO_THA_landcover"),
            landcover_dir / "LAO_THA_landcover.parquet",
            _convert_landcover,
        ),
        (
            _resolve_source(worldpop_dir, "LAO_THA_worldpop_h3_08"),
            worldpop_dir / "LAO_THA_worldpop_h3_08.parquet",
            _convert_worldpop,
        ),
    ]

    results: list[ConversionResult] = []

    for source, target, converter in static_jobs:
        results.append(
            _convert_one(
                source,
                target,
                converter,
                compression_level=args.compression_level,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
                delete_source=args.delete_source,
            )
        )

    firms_csv_files = sorted(firms_historical_dir.glob("fire_*.csv"))
    firms_parquet_files = sorted(firms_historical_dir.glob("fire_*.parquet"))
    firms_sources = firms_csv_files if firms_csv_files else firms_parquet_files
    for source in firms_sources:
        target = source.with_suffix(".parquet")
        results.append(
            _convert_one(
                source,
                target,
                _convert_firms_tabular,
                compression_level=args.compression_level,
                overwrite=args.overwrite,
                dry_run=args.dry_run,
                delete_source=args.delete_source,
            )
        )

    return _print_results(results)


if __name__ == "__main__":
    raise SystemExit(main())
