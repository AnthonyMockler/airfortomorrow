@openaq @contract
Feature: OpenAQ historical collector contract
  Protect the bounded historical OpenAQ collector path used for optimization work.

  @tier_a
  Scenario: collect_openaq_historical script exposes bounded historical CLI options
    When I run "./scripts/collect_openaq_historical.sh --help" with timeout 60
    Then the command should succeed
    And the command output should include CLI options "--years,--country-codes,--workers,--retries,--output-dir,--timeout,--location-limit,--start-date,--end-date,--test,--help"

  @tier_b @live
  Scenario: bounded historical OpenAQ collection with date window produces usable raw parquet data
    Given I clean the "data/raw/openaq/historical" directory while preserving git-tracked files
    When I run "./scripts/collect_openaq_historical.sh --years 2024 --country-codes 111 --workers 2 --location-limit 5 --start-date 2024-01-01 --end-date 2024-02-01" with timeout 2400
    Then the command should succeed
    And the command output should contain "Location limit: 5"
    And the current run should create at least 1 new log files
    And the current run should produce at least 1 updated historical parquet files for "openaq_raw"
    And the current run should produce no more than 5 updated historical parquet files for "openaq_raw"
    And the updated historical parquet files for "openaq_raw" should include date tokens "2024"
    And the latest updated historical parquet for "openaq_raw" should contain at least 1 rows
    And the latest updated historical parquet for "openaq_raw" should include columns "location_id,sensors_id,location,datetime,lat,lon,parameter,units,value"
    And the latest updated historical parquet for "openaq_raw" should have non-null values in columns "location_id,sensors_id,datetime,lat,lon,parameter,units,value"
    And the latest updated historical parquet for "openaq_raw" should have numeric values in column "value"
    And the latest updated historical parquet for "openaq_raw" should have all numeric values in column "value" between "0" and "1000"
    And the latest updated historical parquet for "openaq_raw" should have at least 1 unique values in column "sensors_id"
    And the latest updated historical parquet for "openaq_raw" should have date values in column "datetime" within "2024-01-01" and "2024-02-01"
