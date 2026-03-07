@regression @prediction
Feature: Realtime Prediction Command Integrity
  Validate the prediction command directly without running the full collection pipeline.

  Scenario: realtime prediction command should not emit enhanced-map NoneType errors
    Given I prepare realtime silver input for countries "THA LAO" for today
    When I run "./scripts/predict_air_quality.sh --mode realtime --countries THA LAO --generate-map --validate-sensors --enhanced-maps --save-validation" with timeout 900
    Then the command should succeed
    And the command output should not contain "AIR QUALITY PREDICTION FAILED"
    And the command output should not contain "Failed to generate maps/charts"
    And the command output should not contain "'NoneType' object has no attribute 'empty'"
    And the directory "data/predictions/data/realtime" should contain at least 1 files matching "*.parquet" updated by the current command
