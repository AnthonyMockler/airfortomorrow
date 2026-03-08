@himawari
Feature: Himawari realtime collector and processor contract
  Protect Himawari realtime CLI and output-data contracts used by pipeline wrappers.

  Scenario: Himawari integrated wrapper exposes expected CLI options
    When I run "./scripts/run_himawari_integrated_pipeline.sh --help"
    Then the command exit code should be one of "0,1"
    And the command output should include Himawari CLI options "--mode,--hours,--countries,--start-date,--end-date,--skip-download,--skip-h3,--skip-aggregation,--skip-interpolation,--force-download,--download-workers,--timeout,--help"

  Scenario: Himawari integrated Python entrypoint exposes expected CLI options
    When I run "python src/himawari_integrated_pipeline.py --help"
    Then the command should succeed
    And the command output should include Himawari CLI options "--mode,--hours,--countries,--skip-download,--skip-h3,--force-download,--download-workers,--help"

  Scenario: Himawari realtime collector Python entrypoint exposes expected CLI options
    When I run "python src/data_collectors/himawari_aod.py --help"
    Then the command should succeed
    And the command output should include Himawari CLI options "--mode,--hours,--download-only,--transform-only,--skip-if-h3-exists,--download-workers,--help"

  Scenario: Himawari IDW entrypoint exposes boundary cache options
    When I run "python src/data_processors/himawari_idw_interpolator.py --help"
    Then the command should succeed
    And the command output should include Himawari CLI options "--mode,--input-dir,--output-dir,--countries,--rings,--weight-power,--buffer-degrees,--boundary-cache-dir,--refresh-boundary-cache,--help"

  @live @slow
  Scenario: Himawari realtime integrated run produces fresh, useful output artifacts
    Given I clean the "data/raw/himawari" directory while preserving git-tracked files
    And I clean the "data/processed/himawari" directory while preserving git-tracked files
    And I clean the "data/cache/himawari" directory while preserving git-tracked files
    And I reset the Himawari boundary cache directory
    When I run "./scripts/run_himawari_integrated_pipeline.sh --mode realtime --hours 24 --countries THA LAO" with timeout 2400
    Then the command should succeed
    And the command output should reference an existing log file
    And the command wall-clock duration should be at least 60 seconds
    And the current run should produce at least 1 updated Himawari realtime H3 parquet files
    And the latest updated Himawari realtime H3 parquet should contain at least 1 rows
    And the latest updated Himawari realtime H3 parquet should include columns "h3_08,aod_value,source_file,month,day"
    And the latest updated Himawari realtime H3 parquet should have non-null values in columns "h3_08,aod_value"
    And the latest updated Himawari realtime H3 parquet should have numeric values in column "aod_value"
    And the latest updated Himawari realtime H3 parquet should have at least 100 unique values in column "h3_08"
    And the current run should produce at least 1 updated Himawari realtime daily aggregated parquet files
    And the latest updated Himawari realtime daily aggregated parquet should contain at least 1 rows
    And the latest updated Himawari realtime daily aggregated parquet should include columns "h3_08,aod_1day"
    And the latest updated Himawari realtime daily aggregated parquet should have non-null values in columns "h3_08"
    And the latest updated Himawari realtime daily aggregated parquet should have numeric values in column "aod_1day"
    And the latest updated Himawari realtime daily aggregated parquet should have at least 100 unique values in column "h3_08"
    And the current run should produce at least 1 updated Himawari realtime interpolated parquet files
    And the latest updated Himawari realtime interpolated parquet should contain at least 1 rows
    And the latest updated Himawari realtime interpolated parquet should include columns "h3_08,date,aod_1day_interpolated"
    And the latest updated Himawari realtime interpolated parquet should have non-null values in columns "h3_08,date"
    And the latest updated Himawari realtime interpolated parquet should have numeric values in column "aod_1day_interpolated"
    And the directory "data/cache/geoboundaries" should contain at least 2 files matching "*.geojson" updated by the current command
