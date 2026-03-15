from pathlib import Path

import geopandas as gpd

from src.utils import boundary_utils


def test_boundary_loader_prefers_static_asset_over_download(monkeypatch, tmp_path):
    assets_dir = tmp_path / "assets"
    static_dir = assets_dir / "boundaries"
    static_dir.mkdir(parents=True)
    static_file = static_dir / "geoBoundaries-THA-ADM0.geojson"
    static_file.write_text('{"type":"FeatureCollection","features":[]}')

    cache_dir = tmp_path / "cache"

    monkeypatch.setattr(boundary_utils, "STATIC_BOUNDARY_DIR", static_dir)
    monkeypatch.setattr(boundary_utils, "BOUNDARY_CACHE_DIR", cache_dir)

    captured_paths = []

    def fake_read_file(source):
        captured_paths.append(source)
        return "static-boundary"

    monkeypatch.setattr(gpd, "read_file", fake_read_file)

    class UnexpectedSession:
        def get(self, *args, **kwargs):
            raise AssertionError("network should not be called when static asset exists")

    result = boundary_utils._load_or_download_country_boundary("THA", UnexpectedSession(), logger=type("L", (), {
        "info": lambda *args, **kwargs: None,
        "debug": lambda *args, **kwargs: None,
        "warning": lambda *args, **kwargs: None,
        "error": lambda *args, **kwargs: None,
    })())

    assert result == "static-boundary"
    assert captured_paths == [static_file]
