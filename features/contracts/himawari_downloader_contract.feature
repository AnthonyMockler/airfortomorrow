@himawari
Feature: Himawari downloader contract
  Protect the bounded raw-data downloader behavior without requiring full H3, aggregation, or interpolation runs.

  Scenario: Himawari collector Python entrypoint exposes downloader CLI options
    When I run "python src/data_collectors/himawari_aod.py --help"
    Then the command should succeed
    And the command output should include Himawari CLI options "--mode,--start-date,--end-date,--hours,--download-only,--skip-if-h3-exists,--download-workers,--help"

  @live
  Scenario: Historical downloader-only run creates fresh bounded raw files
    Given I clean the "data/raw/himawari" directory while preserving git-tracked files
    And I clean the "data/processed/himawari" directory while preserving git-tracked files
    When I run "python src/data_collectors/himawari_aod.py --mode historical --start-date 2025-01-01 --end-date 2025-01-01 --download-only --download-workers 2 --countries THA" with timeout 1800
    Then the command should succeed
    And the current run should create at least 1 new log files
    And the current run should produce at least 1 updated Himawari raw files for mode "historical"
    And the updated Himawari raw files for mode "historical" should include path tokens "202501,01"
    And the latest updated Himawari raw file for mode "historical" should be non-empty

  @live
  Scenario: Realtime downloader-only run creates fresh bounded raw files
    Given I clean the "data/raw/himawari" directory while preserving git-tracked files
    And I clean the "data/processed/himawari" directory while preserving git-tracked files
    When I run "python src/data_collectors/himawari_aod.py --mode realtime --hours 6 --download-only --download-workers 2 --countries THA" with timeout 1800
    Then the command should succeed
    And the current run should create at least 1 new log files
    And the current run should produce at least 1 updated Himawari raw files for mode "realtime"
    And the updated Himawari raw files for mode "realtime" should include month/day directories
    And the latest updated Himawari raw file for mode "realtime" should be non-empty
