import pytest
from unittest.mock import MagicMock, patch
from crewai_observability.crew import SchedulingCrew

@pytest.fixture
def mock_google_tools(mocker):
    """Fixture to mock Google-related tools and credentials."""
    mocker.patch(
        'crewai_observability.tools.google_tools.get_google_credentials',
        return_value=MagicMock()
    )
    mocker.patch(
        'crewai_observability.tools.google_tools.gmail_reader_tool.func',
        return_value="Subject: Meeting Request\n\nHi team, let's have a meeting next week to discuss the project."
    )
    mocker.patch(
        'crewai_observability.tools.google_tools.google_calendar_search_tool.func',
        return_value="['Monday 10 AM', 'Tuesday 2 PM']"
    )
    mocker.patch(
        'crewai_observability.tools.google_tools.human_approval_tool.func',
        return_value="Monday 10 AM"
    )
    mocker.patch(
        'crewai_observability.tools.google_tools.google_calendar_writer_tool.func',
        return_value="Event created successfully."
    )

from langchain_core.runnables import Runnable

def test_scheduling_crew(mock_google_tools):
    """Test the scheduling crew workflow with mocked tools."""
    with patch('crewai.agent.ChatOpenAI') as mock_chat_openai:
        mock_llm = MagicMock()
        mock_runnable = MagicMock(spec=Runnable)
        mock_llm.bind.return_value = mock_runnable
        mock_chat_openai.return_value = mock_llm
        # Initialize the crew
        crew = SchedulingCrew()

        # Kick off the crew with a sample input
        result = crew.crew().kickoff(inputs={"topic": "Project Discussion"})

        # Assert the final result
        assert result == "Event created successfully."
