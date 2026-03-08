@contract
Feature: Compact Behave Shim Contract
  Repository-local compact Behave entrypoints and agent guidance should remain discoverable.

  Scenario: compact Behave shim help returns usage text without unknown option errors
    When I run "./scripts/run_behave_tests_compact.sh --help" with timeout 45
    Then the command exit code should be one of "0,1"
    And the command output should not contain "Unknown option"
    And the command output should contain "usage" case-insensitively

  Scenario: root agent guidance points to the compact Behave shim
    Given the file "AGENTS.md" should exist
    Then the file "AGENTS.md" should contain "./scripts/run_behave_tests_compact.sh"
    And the file "AGENTS.md" should contain "full raw output is explicitly needed"
