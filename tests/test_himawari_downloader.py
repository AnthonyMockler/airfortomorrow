from argparse import Namespace
from datetime import datetime
from pathlib import Path

import pytest

from src.data_collectors.himawari_aod import (
    HIMAWARI_FTP_BASE_DIR,
    DownloadBatch,
    build_download_plan,
    download_historical_files,
    download_realtime_files,
    execute_download_plan,
    filter_month_directories_for_range,
)
from src.himawari_integrated_pipeline import build_himawari_download_command


class DummyLogger:
    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None

    def error(self, *_args, **_kwargs):
        return None


class FakeFTP:
    def __init__(self, listings=None):
        self.cwd_calls = []
        self.quit_called = False
        self.current_dir = HIMAWARI_FTP_BASE_DIR
        self.listings = listings or {}

    def cwd(self, path):
        self.cwd_calls.append(path)
        if path == "..":
            return None
        self.current_dir = path
        return None

    def nlst(self):
        return list(self.listings.get(self.current_dir, []))

    def retrbinary(self, command, callback):
        callback(f"downloaded:{command}".encode("utf-8"))

    def quit(self):
        self.quit_called = True


def _make_batch(month, day, *files):
    return DownloadBatch(month=month, day=day, hourly_files=tuple(files))


def test_build_download_plan_skips_interpolated_day(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda date_str, countries, mode: date_str == "20250101",
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda *args, **kwargs: False,
    )

    plan = build_download_plan(
        [_make_batch("202501", "01", "a.nc", "b.nc")],
        output_dir=str(tmp_path),
        logger=DummyLogger(),
        mode="historical",
        countries=["THA"],
    )

    assert plan.batches == []
    assert plan.skipped_interpolated_dates == ["20250101"]
    assert plan.skipped_interpolated_files == [
        ("202501", "01", "a.nc"),
        ("202501", "01", "b.nc"),
    ]


def test_build_download_plan_skips_h3_and_existing_raw_files(tmp_path, monkeypatch):
    output_dir = tmp_path / "raw"
    existing_dir = output_dir / "202501" / "01"
    existing_dir.mkdir(parents=True)
    (existing_dir / "keep.nc").write_bytes(b"existing")

    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda file_path, _h3_dir, _mode: Path(file_path).name == "skip-h3.nc",
    )

    plan = build_download_plan(
        [_make_batch("202501", "01", "skip-h3.nc", "keep.nc", "fetch.nc")],
        output_dir=str(output_dir),
        logger=DummyLogger(),
        mode="historical",
        countries=["THA"],
        check_h3_exists=True,
        h3_base_dir=str(tmp_path / "h3"),
    )

    assert [(batch.month, batch.day, batch.hourly_files) for batch in plan.batches] == [
        ("202501", "01", ("fetch.nc",))
    ]
    assert plan.skipped_h3_files == [("202501", "01", "skip-h3.nc")]
    assert plan.skipped_existing_files == [("202501", "01", "keep.nc")]


def test_build_download_plan_force_download_keeps_interpolated_skip(tmp_path, monkeypatch):
    output_dir = tmp_path / "raw"
    existing_dir = output_dir / "202501" / "01"
    existing_dir.mkdir(parents=True)
    (existing_dir / "keep.nc").write_bytes(b"existing")

    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda date_str, countries, mode: date_str == "20250101",
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda *args, **kwargs: False,
    )

    plan = build_download_plan(
        [_make_batch("202501", "01", "keep.nc")],
        output_dir=str(output_dir),
        logger=DummyLogger(),
        mode="historical",
        countries=["THA"],
        force_download=True,
    )

    assert plan.batches == []
    assert plan.skipped_interpolated_dates == ["20250101"]
    assert plan.skipped_existing_files == []


def test_filter_month_directories_for_range_limits_historical_listing():
    months = ["202412", "202501", "202502", "not-a-month"]

    selected = filter_month_directories_for_range(
        months,
        datetime(2025, 1, 1),
        datetime(2025, 1, 31),
    )

    assert selected == ["202501"]


def test_execute_download_plan_sequential_resets_to_base_dir(tmp_path, monkeypatch):
    ftp = FakeFTP()
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda *args, **kwargs: False,
    )
    plan = build_download_plan(
        [
            _make_batch("202501", "01", "a.nc"),
            _make_batch("202501", "02", "b.nc"),
        ],
        output_dir=str(tmp_path),
        logger=DummyLogger(),
        mode="historical",
        countries=["THA"],
    )

    downloaded = execute_download_plan(
        plan,
        output_dir=str(tmp_path),
        logger=DummyLogger(),
        ftp=ftp,
        download_workers=1,
    )

    assert downloaded == [
        ("202501", "01", "a.nc"),
        ("202501", "02", "b.nc"),
    ]
    assert ftp.cwd_calls == [
        "202501/01",
        HIMAWARI_FTP_BASE_DIR,
        "202501/02",
        HIMAWARI_FTP_BASE_DIR,
    ]


def test_execute_download_plan_threaded_uses_one_connection_per_batch(tmp_path, monkeypatch):
    created_connections = []

    def fake_connect(_user, _password):
        ftp = FakeFTP()
        created_connections.append(ftp)
        return ftp

    monkeypatch.setattr("src.data_collectors.himawari_aod.connect_to_ftp", fake_connect)
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda *args, **kwargs: False,
    )

    plan = build_download_plan(
        [
            _make_batch("202501", "01", "a.nc"),
            _make_batch("202501", "02", "b.nc"),
        ],
        output_dir=str(tmp_path),
        logger=DummyLogger(),
        mode="historical",
        countries=["THA"],
    )

    downloaded = execute_download_plan(
        plan,
        output_dir=str(tmp_path),
        logger=DummyLogger(),
        download_workers=2,
        ftp_user="user",
        ftp_password="pass",
    )

    assert sorted(downloaded) == [
        ("202501", "01", "a.nc"),
        ("202501", "02", "b.nc"),
    ]
    assert len(created_connections) == 2
    assert all(ftp.quit_called for ftp in created_connections)


def test_download_adapters_preserve_return_shapes(tmp_path, monkeypatch):
    historical_ftp = FakeFTP(
        listings={
            "202501/01": ["a.nc", "b.nc"],
        }
    )
    realtime_ftp = FakeFTP()

    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_interpolated_file_exists",
        lambda *args, **kwargs: False,
    )
    monkeypatch.setattr(
        "src.data_collectors.himawari_aod.check_h3_file_exists",
        lambda *args, **kwargs: False,
    )

    historical_result = download_historical_files(
        historical_ftp,
        ["202501/01"],
        str(tmp_path / "historical"),
        DummyLogger(),
        countries=["THA"],
        download_workers=1,
    )
    realtime_result = download_realtime_files(
        realtime_ftp,
        [("202501", "01", "c.nc")],
        str(tmp_path / "realtime"),
        DummyLogger(),
        countries=["THA"],
        download_workers=1,
    )

    assert historical_result == (2, 0)
    assert realtime_result == (
        [("202501", "01", "c.nc")],
        [],
    )


def test_build_himawari_download_command_includes_historical_download_workers():
    args = Namespace(
        mode="historical",
        start_date="2025-01-01",
        end_date="2025-01-02",
        hours=24,
        download_workers=3,
        raw_data_dir="./data/raw/himawari",
        tif_dir="./data/processed/himawari/tif",
        h3_dir="./data/processed/himawari/h3",
        log_dir="./logs",
        force_download=False,
        keep_originals=False,
        skip_download=False,
        skip_h3=False,
        countries=["THA"],
    )

    command = build_himawari_download_command(args)

    assert command[:4] == ["python", "src/data_collectors/himawari_aod.py", "--mode", "historical"]
    assert "--download-workers" in command
    assert command[command.index("--download-workers") + 1] == "3"
