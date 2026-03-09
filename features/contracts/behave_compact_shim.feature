@contract
Feature: Compact Behave Shim Contract
  Repository-local compact Behave entrypoints and agent guidance should remain discoverable.

  Scenario: compact Behave shim help returns usage text without unknown option errors
    When I run "./scripts/run_behave_tests_compact.sh --help" with timeout 45
    Then the command exit code should be one of "0,1"
    And the command output should not contain "Unknown option"
    And the command output should contain "usage" case-insensitively
    And the command output should contain "--long-run"

  Scenario: root agent guidance points to the compact Behave shim
    Given the file "AGENTS.md" should exist
    Then the file "AGENTS.md" should contain "./scripts/run_behave_tests_compact.sh"
    And the file "AGENTS.md" should contain "full raw output is explicitly needed"

  Scenario: compact Behave shim long-run mode announces delayed check guidance
    When I run "./scripts/run_behave_tests_compact.sh --long-run -- --tags=@smoke" with timeout 180
    Then the command should succeed
    And the command output should contain "Long-run mode: enabled"
    And the command output should contain "Next check after:"
    And the command output should contain "Raw log:"
