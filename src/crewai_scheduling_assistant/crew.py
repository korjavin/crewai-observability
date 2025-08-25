from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# from .tools.google_tools import (
#     GmailReaderTool,
#     GoogleCalendarSearchTool,
#     GoogleCalendarWriterTool,
#     human_approval_tool
# )

@CrewBase
class SchedulingCrew:
    """SchedulingCrew for managing email-to-event workflow."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # NOTE: In a real implementation, the 'creds' object from the OAuth flow
    # would need to be passed to these tool initializations.
    # gmail_tool = GmailReaderTool()
    # calendar_search_tool = GoogleCalendarSearchTool()
    # calendar_write_tool = GoogleCalendarWriterTool()

    @agent
    def email_triage_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['email_triage_agent'],
            # tools=[self.gmail_tool],
            verbose=True
        )

    @agent
    def scheduling_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scheduling_agent'],
            # tools=[self.calendar_search_tool],
            verbose=True
        )

    @agent
    def confirmation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['confirmation_agent'],
            # tools=[human_approval_tool],
            verbose=True
        )

    @agent
    def booking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_agent'],
            # tools=[self.calendar_write_tool],
            verbose=True
        )

    @task
    def scan_inbox_task(self) -> Task:
        return Task(config=self.tasks_config['scan_inbox_task'])

    @task
    def find_slots_task(self) -> Task:
        return Task(config=self.tasks_config['find_slots_task'])

    @task
    def confirm_time_task(self) -> Task:
        return Task(config=self.tasks_config['confirm_time_task'])

    @task
    def create_event_task(self) -> Task:
        return Task(config=self.tasks_config['create_event_task'])

    @crew
    def crew(self) -> Crew:
        """Creates the scheduling crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
