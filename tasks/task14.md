
# Task 14: Create Unit Tests for Agents

**Description:**

Create unit tests for the agents defined in `src/crewai_observability/crew.py`.

**Requirements:**

1.  Create a file named `tests/unit/test_agents.py`.
2.  Write unit tests for the `email_triage_agent`, `scheduling_agent`, `confirmation_agent`, and `booking_agent`.
3.  Use the `pytest-mock` library to mock the tools and the LLM calls.

**Acceptance Criteria:**

*   The unit tests are implemented in `tests/unit/test_agents.py`.
*   The tests cover the core functionality of the agents.
*   The tests run successfully without making any actual tool or LLM calls.
