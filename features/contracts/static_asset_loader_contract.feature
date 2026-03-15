@contract @static_assets
Feature: Static asset loader contract
  Protect the CSV bootstrap assets used by the AQ pipeline with a fast loader-compatibility check.

  Scenario: Fast static asset validation succeeds against bootstrap CSVs
    When I run "./scripts/validate_static_assets.sh --sample-rows 500" with timeout 300
    Then the command should succeed
    And the command output should contain "Validated static asset loaders:"
    And the command output should contain "elevation: success"
    And the command output should contain "landcover: success"
    And the command output should contain "worldpop: success"
    And the command output should contain "airgradient_seed_sensors: success"
    And the command output should contain "firms_historical_samples: success"
    And the command output should contain "Static asset contract validation passed."
