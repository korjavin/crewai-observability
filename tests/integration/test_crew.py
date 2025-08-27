import pytest
from unittest.mock import patch
from crewai_observability.crew import SchedulingCrew
from crewai import Crew, Agent, Task

@pytest.fixture
def scheduling_crew():
    """Provides an instance of the SchedulingCrew."""
    return SchedulingCrew()

@pytest.fixture
def assembled_crew(scheduling_crew):
    """Provides an assembled crew object."""
    return scheduling_crew.crew()

def test_crew_creation(assembled_crew):
    """Tests that the main crew object is created correctly."""
    assert isinstance(assembled_crew, Crew), "The crew object should be an instance of Crew."
    assert assembled_crew.process == 'sequential', "The crew process should be sequential."

def test_agents_are_created_correctly(assembled_crew):
    """Tests that all agents are instantiated and have the correct tools."""
    agents = assembled_crew.agents
    assert len(agents) == 4, "There should be exactly four agents."

    # Check email_triage_agent
    email_agent = agents[0]
    assert email_agent.role == 'Inbox Analyst'
    assert len(email_agent.tools) > 0, "Email agent should have tools."
    assert email_agent.tools[0].name == 'Gmail Reader Tool'

    # Check scheduling_agent
    scheduling_agent = agents[1]
    assert scheduling_agent.role == 'Calendar Coordination Specialist'
    assert len(scheduling_agent.tools) > 0, "Scheduling agent should have tools."
    assert scheduling_agent.tools[0].name == 'Google Calendar Search Tool'

    # Check confirmation_agent
    confirmation_agent = agents[2]
    assert confirmation_agent.role == 'User Interaction Liaison'
    assert len(confirmation_agent.tools) > 0, "Confirmation agent should have tools."
    assert confirmation_agent.tools[0].name == 'Human Approval Tool'

    # Check booking_agent
    booking_agent = agents[3]
    assert booking_agent.role == 'Event Logistics Executor'
    assert len(booking_agent.tools) > 0, "Booking agent should have tools."
    assert booking_agent.tools[0].name == 'Google Calendar Writer Tool'

def test_tasks_are_created_and_assigned_correctly(assembled_crew):
    """Tests that all tasks are instantiated and assigned to the correct agents."""
    tasks = assembled_crew.tasks
    agents = assembled_crew.agents
    assert len(tasks) == 4, "There should be exactly four tasks."

    # Unpack agents for clarity
    email_agent, scheduling_agent, confirmation_agent, booking_agent = agents

    # Check scan_inbox_task
    scan_task = tasks[0]
    assert "Scan the last 24 hours" in scan_task.description
    assert scan_task.agent == email_agent, "Scan task should be assigned to the email agent."

    # Check find_slots_task
    find_slots_task = tasks[1]
    assert "extract the meeting topic" in find_slots_task.description
    assert find_slots_task.agent == scheduling_agent, "Find slots task should be assigned to the scheduling agent."

    # Check confirm_time_task
    confirm_time_task = tasks[2]
    assert "Present the proposed time slots clearly" in confirm_time_task.description
    assert confirm_time_task.agent == confirmation_agent, "Confirm time task should be assigned to the confirmation agent."

    # Check create_event_task
    create_event_task = tasks[3]
    assert "Using the confirmed time slot" in create_event_task.description
    assert create_event_task.agent == booking_agent, "Create event task should be assigned to the booking agent."
