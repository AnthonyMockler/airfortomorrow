@openaq @contract
Feature: OpenAQ realtime collector contract
  Protect OpenAQ realtime CLI and data-output contracts used by pipeline wrappers.

  Scenario: collect_openaq_realtime script exposes expected CLI options
    When I run "./scripts/collect_openaq_realtime.sh --help" with timeout 60
    Then the command should succeed
    And the command output should include CLI options "--days,--timeout,--limit,--test-mode,--help"

  Scenario: OpenAQ realtime Python client exposes expected CLI options
    When I run "python -m src.data_processors.openaq_realtime_client --help" with timeout 60
    Then the command should succeed
    And the command output should include CLI options "--days,--locations,--limit,--output,--test-mode,--test-limit"

  @live
  Scenario: OpenAQ-only realtime pipeline run produces usable parquet data
    Given I clean the "data" directory while preserving git-tracked files
    When I run "./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO --pipelines openaq --skip-silver --skip-prediction --test-mode --test-openaq-limit 8" with timeout 1800
    Then the command should succeed
    And the command output should contain "Test mode: ENABLED (OpenAQ limit: 8)"
    And the command output should contain "OpenAQ Air Quality"
    And the command output should reference an existing log file
    And the current run should produce at least 1 updated OpenAQ realtime parquet files
    And the latest updated OpenAQ realtime parquet should contain at least 1 rows
    And the latest updated OpenAQ realtime parquet should include columns "location_id,sensor_id,datetime_from_local,datetime_from_utc,latitude,longitude,sensor_type,sensor_units,value,provider_name,owner_name,country,name"
    And the latest updated OpenAQ realtime parquet should have non-null values in columns "sensor_id,datetime_from_utc,value,latitude,longitude,sensor_type"
    And the latest updated OpenAQ realtime parquet should have numeric values in column "value"
    And the latest updated OpenAQ realtime parquet should have at least 1 unique values in column "sensor_id"

  @live @benchmark
  Scenario: OpenAQ realtime benchmark uses one tenth of live locations
    Given I compute an OpenAQ live sample limit at one tenth of baseline locations with minimum 20
    When I run OpenAQ realtime collection with the computed sample limit and timeout 2400
    Then the command should succeed
    And the command output should report the computed OpenAQ location limit
    And the command output should report OpenAQ collection duration of at least 20 seconds
    And the current run should produce at least 1 updated OpenAQ realtime parquet files
    And the latest updated OpenAQ realtime parquet should contain at least 1 rows
    And the latest updated OpenAQ realtime parquet should include columns "location_id,sensor_id,datetime_from_local,datetime_from_utc,latitude,longitude,sensor_type,sensor_units,value,provider_name,owner_name,country,name"
    And the latest updated OpenAQ realtime parquet should have non-null values in columns "sensor_id,datetime_from_utc,value,latitude,longitude,sensor_type"
    And the latest updated OpenAQ realtime parquet should have numeric values in column "value"
    And the latest updated OpenAQ realtime parquet should have at least 10 unique values in column "sensor_id"
    And the benchmark metadata should record one-tenth sample sizing
