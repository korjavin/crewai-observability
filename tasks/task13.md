
# Task 13: Create Unit Tests for Tools

**Description:**

Create unit tests for the custom tools in `src/crewai_observability/tools/google_tools.py`.

**Requirements:**

1.  Create a file named `tests/unit/test_google_tools.py`.
2.  Write unit tests for the `GmailReaderTool`, `GoogleCalendarSearchTool`, and `GoogleCalendarWriterTool` classes.
3.  Use the `pytest-mock` library to mock the Google API calls.
4.  Write a unit test for the `human_approval_tool` and mock the `input` function.

**Acceptance Criteria:**

*   The unit tests are implemented in `tests/unit/test_google_tools.py`.
*   The tests cover the core functionality of the tools.
*   The tests run successfully without making any actual API calls or requiring user interaction.
