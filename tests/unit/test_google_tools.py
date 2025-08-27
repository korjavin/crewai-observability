from unittest.mock import patch

from tests.helpers import (
    mock_google_auth,
    mock_google_service_build,
    get_mock_email_list,
    get_mock_email_content,
    get_mock_freebusy_query_response,
    get_mock_event_insert_response,
)
from crewai_observability.tools.google_tools import (
    gmail_reader_tool,
    google_calendar_search_tool,
    google_calendar_writer_tool,
    human_approval_tool,
)


def test_gmail_reader_tool_with_messages(monkeypatch):
    """
    Tests that the gmail_reader_tool correctly processes and returns
    email content when messages are found.
    """
    # Arrange
    mock_google_auth(monkeypatch)
    mock_gmail_data = {
        "list": get_mock_email_list(count=1),
        "get": get_mock_email_content(
            subject="Test Subject", body="This is a test body."
        ),
    }
    mock_google_service_build(monkeypatch, "gmail", mock_gmail_data)

    # Act
    result = gmail_reader_tool.run(query="from:test@example.com")

    # Assert
    assert "Subject: Test Subject" in result
    assert "Body: This is a test body." in result


def test_gmail_reader_tool_no_messages(monkeypatch):
    """
    Tests that the gmail_reader_tool returns the correct message
    when no emails are found.
    """
    # Arrange
    mock_google_auth(monkeypatch)
    mock_gmail_data = {"list": get_mock_email_list(count=0)}
    mock_google_service_build(monkeypatch, "gmail", mock_gmail_data)

    # Act
    result = gmail_reader_tool.run(query="is:unread")

    # Assert
    assert result == "No messages."


def test_google_calendar_search_tool_with_busy_slots(monkeypatch):
    """
    Tests the calendar search tool when there are busy slots.
    """
    # Arrange
    mock_google_auth(monkeypatch)
    busy_slots = [
        {"start": "2024-09-01T10:00:00Z", "end": "2024-09-01T11:00:00Z"}
    ]
    mock_calendar_data = {
        "query": get_mock_freebusy_query_response(busy_slots=busy_slots)
    }
    mock_google_service_build(monkeypatch, "calendar", mock_calendar_data)

    # Act
    result = google_calendar_search_tool.run(
        start_time="2024-09-01T09:00:00Z",
        end_time="2024-09-01T17:00:00Z",
    )

    # Assert
    assert "The following time slots are busy:" in result
    assert (
        "- From 2024-09-01T10:00:00Z to 2024-09-01T11:00:00Z" in result
    )


def test_google_calendar_search_tool_with_no_busy_slots(monkeypatch):
    """
    Tests the calendar search tool when the calendar is free.
    """
    # Arrange
    mock_google_auth(monkeypatch)
    mock_calendar_data = {
        "query": get_mock_freebusy_query_response(busy_slots=[])
    }
    mock_google_service_build(monkeypatch, "calendar", mock_calendar_data)
    start_time = "2024-09-01T09:00:00Z"
    end_time = "2024-09-01T17:00:00Z"

    # Act
    result = google_calendar_search_tool.run(
        start_time=start_time, end_time=end_time
    )

    # Assert
    assert (
        f"The calendar is completely free between {start_time} "
        f"and {end_time}." in result
    )


def test_google_calendar_writer_tool_success(monkeypatch):
    """
    Tests that the calendar writer tool successfully creates an event.
    """
    # Arrange
    mock_google_auth(monkeypatch)
    mock_calendar_data = {
        "insert": get_mock_event_insert_response(event_id="evt123")
    }
    mock_google_service_build(monkeypatch, "calendar", mock_calendar_data)
    event_details = {
        "summary": "Final Review",
        "start": {"dateTime": "2024-09-01T10:00:00Z"},
        "end": {"dateTime": "2024-09-01T11:00:00Z"},
        "attendees": [{"email": "test@example.com"}],
    }

    # Act
    result = google_calendar_writer_tool.run(event_details=event_details)

    # Assert
    assert "Event created successfully. Event ID: evt123" in result


@patch("builtins.input", return_value="2")
def test_human_approval_tool_valid_selection(mock_input):
    """
    Tests the human approval tool with a valid user selection.
    """
    proposed_slots = ["Slot A", "Slot B", "Slot C"]
    result = human_approval_tool.run(proposed_slots=proposed_slots)
    assert result == "Slot B"


@patch("builtins.input", side_effect=["x", "4", "1"])
@patch("builtins.print")
def test_human_approval_tool_invalid_then_valid(mock_print, mock_input):
    """
    Tests the human approval tool with invalid inputs before a valid one.
    """
    proposed_slots = ["Slot A", "Slot B", "Slot C"]
    result = human_approval_tool.run(proposed_slots=proposed_slots)
    assert result == "Slot A"
    assert mock_input.call_count == 3
    mock_print.assert_any_call("Please enter a valid number.")
    mock_print.assert_any_call("Invalid selection. Please try again.")
