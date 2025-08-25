import pytest
from crewai_observability.crew import SchedulingCrew
from crewai import Agent

@pytest.fixture
def crew():
    """Fixture to initialize SchedulingCrew."""
    return SchedulingCrew()

def test_email_triage_agent_properties(crew):
    """Test the properties of the created email_triage_agent."""
    agent = crew.email_triage_agent()
    expected_config = crew.agents_config['email_triage_agent']

    assert isinstance(agent, Agent)
    assert agent.role == expected_config['role']
    assert agent.goal == expected_config['goal']
    assert agent.backstory == expected_config['backstory']
    assert len(agent.tools) == 1
    assert agent.verbose is True

def test_scheduling_agent_properties(crew):
    """Test the properties of the created scheduling_agent."""
    agent = crew.scheduling_agent()
    expected_config = crew.agents_config['scheduling_agent']

    assert isinstance(agent, Agent)
    assert agent.role == expected_config['role']
    assert agent.goal == expected_config['goal']
    assert agent.backstory == expected_config['backstory']
    assert len(agent.tools) == 1
    assert agent.verbose is True

def test_confirmation_agent_properties(crew):
    """Test the properties of the created confirmation_agent."""
    agent = crew.confirmation_agent()
    expected_config = crew.agents_config['confirmation_agent']

    assert isinstance(agent, Agent)
    assert agent.role == expected_config['role']
    assert agent.goal == expected_config['goal']
    assert agent.backstory == expected_config['backstory']
    assert len(agent.tools) == 1
    assert agent.verbose is True

def test_booking_agent_properties(crew):
    """Test the properties of the created booking_agent."""
    agent = crew.booking_agent()
    expected_config = crew.agents_config['booking_agent']

    assert isinstance(agent, Agent)
    assert agent.role == expected_config['role']
    assert agent.goal == expected_config['goal']
    assert agent.backstory == expected_config['backstory']
    assert len(agent.tools) == 1
    assert agent.verbose is True
