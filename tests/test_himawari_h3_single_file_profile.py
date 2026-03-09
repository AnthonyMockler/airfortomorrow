import json
import os
from pathlib import Path

import numpy as np
import polars as pl
import pytest
from dotenv import dotenv_values

from src.data_processors.process_himawari_h3_streaming import profile_single_file_streaming


ARTIFACT_DIR = Path("tests/artifacts/himawari_single_file")
METADATA_PATH = ARTIFACT_DIR / "representative_file.json"
EXPECTED_PARQUET_PATH = ARTIFACT_DIR / "expected_h3_output.parquet"


def _load_metadata() -> dict:
    return json.loads(METADATA_PATH.read_text())


def _has_himawari_credentials() -> bool:
    if os.environ.get("HIMAWARI_FTP_USER") and os.environ.get("HIMAWARI_FTP_PASSWORD"):
        return True

    env_values = dotenv_values(".env")
    return bool(env_values.get("HIMAWARI_FTP_USER") and env_values.get("HIMAWARI_FTP_PASSWORD"))


def test_representative_himawari_artifact_is_present_and_plausible():
    assert METADATA_PATH.exists(), f"Missing metadata artifact: {METADATA_PATH}"
    assert EXPECTED_PARQUET_PATH.exists(), f"Missing expected parquet artifact: {EXPECTED_PARQUET_PATH}"

    metadata = _load_metadata()
    expected = pl.read_parquet(EXPECTED_PARQUET_PATH)

    assert metadata["source_file"]["filename"].endswith(".nc")
    assert metadata["countries"] == ["THA"]
    assert expected.height == metadata["expected_output"]["rows"]
    assert expected["h3_08"].n_unique() == metadata["expected_output"]["unique_h3"]
    assert expected["aod_value"].min() == pytest.approx(metadata["expected_output"]["aod_min"])
    assert expected["aod_value"].max() == pytest.approx(metadata["expected_output"]["aod_max"])
    assert expected["aod_value"].mean() == pytest.approx(metadata["expected_output"]["aod_mean"])
    assert expected["aod_value"].std() == pytest.approx(metadata["expected_output"]["aod_std"])


@pytest.mark.skipif(
    not _has_himawari_credentials(),
    reason="Himawari FTP credentials are required in env or .env for live single-file profiling",
)
def test_profile_single_representative_himawari_file_matches_expected_artifact(tmp_path):
    metadata = _load_metadata()

    output_dir = tmp_path / "output"
    result = profile_single_file_streaming(
        month=metadata["source_file"]["month"],
        day=metadata["source_file"]["day"],
        filename=metadata["source_file"]["filename"],
        countries=metadata["countries"],
        output_root=output_dir,
        keep_netcdf=True,
    )
    print(json.dumps(result["timings"], indent=2, sort_keys=True))
    assert result["result"].startswith("Success:")
    assert Path(result["parquet_path"]).parent.name == metadata["source_file"]["day"]
    assert Path(result["parquet_path"]).parent.parent.name == metadata["source_file"]["month"]

    expected_steps = {
        "download",
        "boundary_creation",
        "netcdf_to_tif",
        "mask",
        "raster_to_dataframe",
        "polars_conversion",
        "write_parquet",
        "cleanup",
        "processing_total",
        "full_total",
    }
    assert expected_steps.issubset(result["timings"])
    assert result["timings"]["full_total"] >= result["timings"]["processing_total"]

    actual = pl.read_parquet(result["parquet_path"]).sort("h3_08")
    expected = pl.read_parquet(EXPECTED_PARQUET_PATH).sort("h3_08")

    assert actual.schema == expected.schema
    assert actual.height == expected.height
    assert actual["h3_08"].to_list() == expected["h3_08"].to_list()
    assert actual["source_file"].to_list() == expected["source_file"].to_list()
    assert actual["month"].to_list() == expected["month"].to_list()
    assert actual["day"].to_list() == expected["day"].to_list()
    assert np.allclose(
        actual["aod_value"].to_numpy(),
        expected["aod_value"].to_numpy(),
        rtol=1e-6,
        atol=1e-8,
    )
