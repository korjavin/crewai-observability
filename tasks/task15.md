
# Task 15: Create Integration Tests for the Crew

**Description:**

Create integration tests for the `SchedulingCrew` workflow.

**Note:** If you are facing dependency issues with `crewai-tools`, please refer to `task15_remediation.md` for guidance.

**Requirements:**

1.  Create a file named `tests/integration/test_crew.py`.
2.  Write an integration test that runs the `SchedulingCrew` with mocked data.
3.  The test should verify that the crew runs successfully and produces the expected output.
4.  Use the `pytest-mock` library to mock the Google API calls and user input.

**Acceptance Criteria:**

*   The integration test is implemented in `tests/integration/test_crew.py`.
*   The test covers the end-to-end workflow of the `SchedulingCrew`.
*   The test runs successfully without making any actual API calls or requiring user interaction.
