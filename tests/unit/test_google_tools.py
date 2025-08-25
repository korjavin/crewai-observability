import base64
from unittest.mock import MagicMock, patch
from crewai_observability.tools.google_tools import (
    gmail_reader_tool,
    google_calendar_search_tool,
    google_calendar_writer_tool,
    human_approval_tool,
)


def b64_encode(s: str) -> str:
    """Helper to base64-encode a string for mock API responses."""
    return base64.urlsafe_b64encode(s.encode('utf-8')).decode('utf-8')


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_gmail_reader_with_messages_found(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    list_response = {'messages': [{'id': '123'}, {'id': '456'}]}
    get_response_1 = {
        'payload': {
            'headers': [{'name': 'Subject', 'value': 'Test Subject 1'}],
            'parts': [{'mimeType': 'text/plain', 'body': {'data': b64_encode('This is the body 1.')}}]
        }
    }
    get_response_2 = {
        'payload': {
            'headers': [{'name': 'Subject', 'value': 'Test Subject 2'}],
            'parts': [{'mimeType': 'text/plain', 'body': {'data': b64_encode('This is the body 2.')}}]
        }
    }

    # Configure the mock service chain
    mock_service.users().messages().list().execute.return_value = list_response

    # The .get() method is called multiple times, so we need to configure side_effect
    # The mock for the .get() call itself needs to have an .execute() method
    get_mock = MagicMock()
    get_mock.execute.side_effect = [get_response_1, get_response_2]
    mock_service.users().messages().get.return_value = get_mock

    # Act
    result = gmail_reader_tool.run(query="from:test@example.com")

    # Assert
    assert "Subject: Test Subject 1" in result
    assert "Body: This is the body 1." in result
    assert "Subject: Test Subject 2" in result
    assert "Body: This is the body 2." in result
    mock_get_credentials.assert_called_once()
    mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_get_credentials.return_value)


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_gmail_reader_no_messages_found(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.users().messages().list().execute.return_value = {}

    # Act
    result = gmail_reader_tool.run(query="some query")

    # Assert
    assert result == "No messages found."


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_gmail_reader_message_parsing_error(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.users().messages().list().execute.return_value = {'messages': [{'id': '789'}]}

    get_mock = MagicMock()
    get_mock.execute.return_value = {'id': '789'} # Simulate a malformed response
    mock_service.users().messages().get.return_value = get_mock

    # Act
    result = gmail_reader_tool.run(query="another query")

    # Assert
    assert "Could not parse email with ID: 789" in result


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_calendar_search_with_busy_slots(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    start_time = "2024-01-01T09:00:00Z"
    end_time = "2024-01-01T17:00:00Z"
    freebusy_response = {
        'calendars': {
            'primary': {
                'busy': [
                    {'start': '2024-01-01T10:00:00Z', 'end': '2024-01-01T11:00:00Z'},
                    {'start': '2024-01-01T14:00:00Z', 'end': '2024-01-01T15:00:00Z'}
                ]
            }
        }
    }
    mock_service.freebusy().query().execute.return_value = freebusy_response

    # Act
    result = google_calendar_search_tool.run(start_time=start_time, end_time=end_time)

    # Assert
    assert "The following time slots are busy:" in result
    assert "- From 2024-01-01T10:00:00Z to 2024-01-01T11:00:00Z" in result
    assert "- From 2024-01-01T14:00:00Z to 2024-01-01T15:00:00Z" in result


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_calendar_search_with_no_busy_slots(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    start_time = "2024-01-01T09:00:00Z"
    end_time = "2024-01-01T17:00:00Z"
    freebusy_response = {'calendars': {'primary': {'busy': []}}}
    mock_service.freebusy().query().execute.return_value = freebusy_response

    # Act
    result = google_calendar_search_tool.run(start_time=start_time, end_time=end_time)

    # Assert
    assert f"The calendar is completely free between {start_time} and {end_time}." in result


@patch('crewai_observability.tools.google_tools.build', autospec=True)
@patch('crewai_observability.tools.google_tools.get_google_credentials')
def test_calendar_writer_creates_event_successfully(mock_get_credentials, mock_build):
    # Arrange
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    event_details = {
        'summary': 'Test Meeting',
        'start': {'dateTime': '2024-01-01T10:00:00Z'},
        'end': {'dateTime': '2024-01-01T11:00:00Z'}
    }
    created_event_response = {'id': 'event_id_123', 'summary': 'Test Meeting'}
    mock_service.events().insert().execute.return_value = created_event_response

    # Act
    result = google_calendar_writer_tool.run(event_details=event_details)

    # Assert
    assert "Event created successfully. Event ID: event_id_123" in result


@patch('builtins.input', return_value='2')
@patch('builtins.print')
def test_human_approval_tool_valid_selection(mock_print, mock_input):
    proposed_slots = ["Slot A", "Slot B", "Slot C"]
    result = human_approval_tool.run(proposed_slots)
    assert result == "Slot B"
    mock_input.assert_called_once_with("Enter the number of your chosen time slot: ")


@patch('builtins.input', side_effect=['a', '5', '3'])
@patch('builtins.print')
def test_human_approval_tool_invalid_then_valid_selection(mock_print, mock_input):
    proposed_slots = ["Slot A", "Slot B", "Slot C"]
    result = human_approval_tool.run(proposed_slots)
    assert result == "Slot C"
    assert mock_input.call_count == 3
    mock_print.assert_any_call("Please enter a valid number.")
    mock_print.assert_any_call("Invalid selection. Please try again.")
