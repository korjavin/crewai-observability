from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.google_tools import (
    GmailReaderTool,
    GoogleCalendarSearchTool,
    GoogleCalendarWriterTool,
    human_approval_tool
)

@CrewBase
class SchedulingCrew:
    """SchedulingCrew for managing email-to-event workflow."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, creds):
        self.creds = creds
        self.gmail_tool = GmailReaderTool(creds=self.creds)
        self.calendar_search_tool = GoogleCalendarSearchTool(creds=self.creds)
        self.calendar_write_tool = GoogleCalendarWriterTool(creds=self.creds)

    @agent
    def email_triage_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['email_triage_agent'],
            tools=[self.gmail_tool],
            verbose=True
        )

    @agent
    def scheduling_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scheduling_agent'],
            tools=[self.calendar_search_tool],
            verbose=True
        )

    @agent
    def confirmation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['confirmation_agent'],
            tools=[human_approval_tool],
            verbose=True
        )

    @agent
    def booking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['booking_agent'],
            tools=[self.calendar_write_tool],
            verbose=True
        )

    @task
    def scan_inbox_task(self) -> Task:
        return Task(
            config=self.tasks_config['scan_inbox_task'],
            agent=self.email_triage_agent()
        )

    @task
    def find_slots_task(self) -> Task:
        return Task(
            config=self.tasks_config['find_slots_task'],
            agent=self.scheduling_agent()
        )

    @task
    def confirm_time_task(self) -> Task:
        return Task(
            config=self.tasks_config['confirm_time_task'],
            agent=self.confirmation_agent()
        )

    @task
    def create_event_task(self) -> Task:
        return Task(
            config=self.tasks_config['create_event_task'],
            agent=self.booking_agent()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the scheduling crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
