@historical @contract
Feature: Historical collection contract
  Protect the documented historical collector workflows used for bounded real-data runs.

  Scenario: Documentation preserves the historical collection workflow
    Given the file "README.md" should exist
    Then the file "README.md" should contain "./scripts/run_complete_pipeline.sh --mode historical --start-date 2024-06-01 --end-date 2024-06-03 --countries THA LAO --generate-maps"
    And the file "DOCUMENTATION.md" should contain "./scripts/run_air_quality_integrated_pipeline.sh --mode historical"
    And the file "DOCUMENTATION.md" should contain "./scripts/run_era5_idw_pipeline.sh --mode historical"
    And the file "DOCUMENTATION.md" should contain "./scripts/run_firms_pipeline.sh --mode historical"
    And the file "DOCUMENTATION.md" should contain "./scripts/run_himawari_integrated_pipeline.sh --mode historical"

  @live @airquality
  Scenario: Air Quality historical integrated run produces fresh plausible output
    Given I prepare the historical collection workspace for "air_quality"
    When I run "./scripts/run_air_quality_integrated_pipeline.sh --mode historical --start-date 2026-01-01 --end-date 2026-01-03 --countries THA" with timeout 5400
    Then the command should succeed
    And the command output should contain "Air quality pipeline completed successfully."
    And the current run should create at least 1 new log files
    And the current run should produce at least 1 updated historical parquet files for "openaq_raw"
    And the current run should produce at least 1 updated historical parquet files for "airgradient_raw"
    And the current run should produce at least 1 updated historical parquet files for "air_quality"
    And the latest updated historical parquet for "air_quality" should contain at least 1 rows
    And the latest updated historical parquet for "air_quality" should include columns "location_id,date_utc,value,source,h3_08_text"
    And the latest updated historical parquet for "air_quality" should have non-null values in columns "location_id,date_utc,value,h3_08_text"
    And the latest updated historical parquet for "air_quality" should have numeric values in column "value"
    And the latest updated historical parquet for "air_quality" should have all numeric values in column "value" between "0" and "500"
    And the latest updated historical parquet for "air_quality" should have at least 3 unique values in column "date_utc"
    And the latest updated historical parquet for "air_quality" should have at least 3 unique values in column "location_id"
    And the latest updated historical parquet for "air_quality" should have date values in column "date_utc" within "2026-01-01" and "2026-01-03"

  @live @firms
  Scenario: FIRMS historical pipeline produces fresh plausible H3 output
    Given I prepare the historical collection workspace for "firms"
    When I run "./scripts/run_firms_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA" with timeout 5400
    Then the command should succeed
    And the command output should contain "Complete FIRMS pipeline executed successfully:"
    And the current run should create at least 1 new log files
    And the current run should produce at least 3 updated historical parquet files for "firms_h3"
    And the updated historical parquet files for "firms_h3" should include date tokens "20250101,20250102,20250103"
    And the latest updated historical parquet for "firms_h3" should contain at least 1 rows
    And the latest updated historical parquet for "firms_h3" should include columns "h3_08_text,value"
    And the latest updated historical parquet for "firms_h3" should have non-null values in columns "h3_08_text,value"
    And the latest updated historical parquet for "firms_h3" should have numeric values in column "value"
    And the latest updated historical parquet for "firms_h3" should have all numeric values in column "value" between "0" and "1000000"
    And the latest updated historical parquet for "firms_h3" should have at least 50 unique values in column "h3_08_text"
    And the latest updated historical parquet for "firms_h3" should have at least 2 unique values in column "value"

  @live @himawari @slow
  Scenario: Himawari historical integrated run produces fresh plausible outputs
    Given I prepare the historical collection workspace for "himawari"
    When I run "./scripts/run_himawari_integrated_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA" with timeout 7200
    Then the command should succeed
    And the command output should reference an existing log file
    And the current run should produce at least 10 updated historical parquet files for "himawari_h3"
    And the current run should produce at least 3 updated historical parquet files for "himawari_daily"
    And the updated historical parquet files for "himawari_daily" should include date tokens "20250101,20250102,20250103"
    And the current run should produce at least 3 updated historical parquet files for "himawari_interpolated"
    And the updated historical parquet files for "himawari_interpolated" should include date tokens "20250101,20250102,20250103"
    And the latest updated historical parquet for "himawari_h3" should contain at least 1 rows
    And the latest updated historical parquet for "himawari_h3" should include columns "h3_08,aod_value,source_file,month,day"
    And the latest updated historical parquet for "himawari_h3" should have non-null values in columns "h3_08,aod_value"
    And the latest updated historical parquet for "himawari_h3" should have numeric values in column "aod_value"
    And the latest updated historical parquet for "himawari_h3" should have all numeric values in column "aod_value" between "0" and "2.0"
    And the latest updated historical parquet for "himawari_h3" should have at least 100 unique values in column "h3_08"
    And the latest updated historical parquet for "himawari_daily" should contain at least 1 rows
    And the latest updated historical parquet for "himawari_daily" should include columns "h3_08,aod_1day"
    And the latest updated historical parquet for "himawari_daily" should have non-null values in columns "h3_08"
    And the latest updated historical parquet for "himawari_daily" should have numeric values in column "aod_1day"
    And the latest updated historical parquet for "himawari_daily" should have all numeric values in column "aod_1day" between "0" and "2.0"
    And the latest updated historical parquet for "himawari_daily" should have at least 100 unique values in column "h3_08"
    And the latest updated historical parquet for "himawari_interpolated" should contain at least 1 rows
    And the latest updated historical parquet for "himawari_interpolated" should include columns "h3_08,date,aod_1day_interpolated"
    And the latest updated historical parquet for "himawari_interpolated" should have non-null values in columns "h3_08,date"
    And the latest updated historical parquet for "himawari_interpolated" should have numeric values in column "aod_1day_interpolated"
    And the latest updated historical parquet for "himawari_interpolated" should have all numeric values in column "aod_1day_interpolated" between "0" and "2.0"
    And the latest updated historical parquet for "himawari_interpolated" should have at least 100 unique values in column "h3_08"
    And the latest updated historical parquet for "himawari_interpolated" should have date values in column "date" within "2025-01-01" and "2025-01-03"

  @live @era5 @slow
  Scenario: ERA5 historical IDW run produces fresh plausible output
    Given I prepare the historical collection workspace for "era5"
    When I run "./scripts/run_era5_idw_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA --params 2t --force" with timeout 7200
    Then the command should succeed
    And the command output should contain "ERA5 IDW Pipeline completed successfully!"
    And the command output should reference an existing log file
    And the current run should produce at least 3 updated historical parquet files for "era5"
    And the updated historical parquet files for "era5" should include date tokens "2025-01-01,2025-01-02,2025-01-03"
    And the latest updated historical parquet for "era5" should contain at least 1 rows
    And the latest updated historical parquet for "era5" should include columns "h3_08,date,2t"
    And the latest updated historical parquet for "era5" should have non-null values in columns "h3_08,date,2t"
    And the latest updated historical parquet for "era5" should have numeric values in column "2t"
    And the latest updated historical parquet for "era5" should have all numeric values in column "2t" between "250" and "330"
    And the latest updated historical parquet for "era5" should have at least 100 unique values in column "h3_08"
    And the latest updated historical parquet for "era5" should have date values in column "date" within "2025-01-01" and "2025-01-03"
