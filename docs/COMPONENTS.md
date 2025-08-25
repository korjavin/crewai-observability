## **II. Core Application Design: The `crewai` Event Scheduling Crew**

This section details the internal design of the `crewai` application itself, focusing on the definition of agents, tasks, and the custom tools that enable them to interact with external systems. The design prioritizes clarity, modularity, and adherence to `crewai` best practices.

### **2.1. Agent and Task Definitions**

Following `crewai`'s recommended best practices, agents are designed as specialists with narrowly defined roles and goals, which leads to higher-quality, more predictable outputs compared to generalist agents. The agent and task configurations are externalized into `agents.yaml` and `tasks.yaml` files for better maintainability and separation of concerns.

The table below provides a summary of the agents designed for this system, outlining their specific roles and responsibilities.

| Agent Name | Role | Goal | Backstory | Assigned Tools |
| :---- | :---- | :---- | :---- | :---- |
| `Email_Triage_Agent` | Inbox Analyst | To meticulously scan incoming emails and identify actionable meeting requests with high precision. | An expert in natural language understanding, trained to distinguish between casual mentions of meetings and concrete scheduling requests. | `GmailReaderTool` |
| `Scheduling_Agent` | Calendar Coordination Specialist | To analyze meeting requirements and find optimal, conflict-free time slots in the user's calendar. | A master of temporal logistics and scheduling algorithms, with deep knowledge of the Google Calendar API and common scheduling patterns. | `GoogleCalendarSearchTool` |
| `Confirmation_Agent` | User Interaction Liaison | To clearly present proposed meeting times to the user and accurately capture their final decision. | A communications expert focused on clarity and efficiency, ensuring the human-in-the-loop step is seamless and error-free. | `HumanApprovalTool` |
| `Booking_Agent` | Event Logistics Executor | To create precise and accurate calendar events based on confirmed details, ensuring all attendees are invited. | A detail-oriented administrative professional who never makes a mistake when booking an event, ensuring all required fields are perfect. | `GoogleCalendarWriterTool` |

The corresponding tasks are defined in `tasks.yaml` to provide concrete instructions for each agent.

**`config/agents.yaml`:**

email_triage_agent:

  role: 'Inbox Analyst'

  goal: 'To meticulously scan incoming emails and identify actionable meeting requests with high precision.'

  backstory: |

    You are an expert in natural language understanding, trained to distinguish

    between casual mentions of meetings and concrete scheduling requests. You are

    methodical and ignore marketing or non-relevant emails.

scheduling_agent:

  role: 'Calendar Coordination Specialist'

  goal: 'To analyze meeting requirements and find optimal, conflict-free time slots in the user''s calendar.'

  backstory: |

    You are a master of temporal logistics and scheduling algorithms, with deep

    knowledge of the Google Calendar API and common scheduling patterns. You prioritize

    finding slots that respect working hours and existing commitments.

confirmation_agent:

  role: 'User Interaction Liaison'

  goal: 'To clearly present proposed meeting times to the user and accurately capture their final decision.'

  backstory: |

    You are a communications expert focused on clarity and efficiency, ensuring

    the human-in-the-loop step is seamless and error-free. Your communication is

    always concise and direct.

booking_agent:

  role: 'Event Logistics Executor'

  goal: 'To create precise and accurate calendar events based on confirmed details, ensuring all attendees are invited.'

  backstory: |

    You are a detail-oriented administrative professional who never makes a mistake

    when booking an event, ensuring all required fields are perfect and all attendees

    receive an invitation.

**`config/tasks.yaml`:**

scan_inbox_task:

  agent: email_triage_agent

  description: |

    Scan the last 24 hours of emails in the Gmail inbox. Identify and extract the

    full content of any email that contains a clear intent to schedule a meeting.

    Focus on phrases like "let's meet," "can you find a time," or "schedule a call."

  expected_output: |

    A JSON object containing a list of potential meeting requests. Each item in the list

    should have the 'thread_id' and 'body' of the email. Return up to 5 potential emails.

    If no emails are found, return an empty list.

find_slots_task:

  agent: scheduling_agent

  description: |

    From the provided email text, extract the meeting topic, attendees' email addresses,

    and the requested duration. If duration is not specified, assume 30 minutes.

    Query the Google Calendar to find three available slots in the next 5 business days

    that work for the user.

  expected_output: |

    A structured list of three proposed time slots in ISO 8601 format, along with the

    extracted meeting topic and attendee list. For example:

    {

      "topic": "Project Phoenix Sync",

      "attendees": ["user@example.com", "colleague@example.com"],

      "slots": ["..."]

    }

confirm_time_task:

  agent: confirmation_agent

  description: |

    Present the proposed time slots clearly to the user for approval. The user will

    select one of the options. Wait for their selection and capture it accurately.

  expected_output: |

    The single, user-confirmed time slot in ISO 8601 format, returned as a string.

create_event_task:

  agent: booking_agent

  description: |

    Using the confirmed time slot, meeting topic, and attendee list, create a new event

    in the Google Calendar. Ensure the event title is the meeting topic and all attendees

    are invited.

  expected_output: |

    A confirmation string containing the Google Calendar event ID and a link to the event.

    For example: "Event created successfully. Event ID: abc123xyz789".

### **2.2. Custom Tool Implementation**

Agents require tools to interact with external systems. The following custom tools will be implemented in Python, using the `@tool` decorator for simplicity and clarity. These tools will encapsulate all interactions with the Google Workspace APIs and the user.

**`src/project_name/tools/google_tools.py`:**

from crewai_tools import BaseTool, tool

from googleapiclient.discovery import build

# Assume 'creds' object is obtained from the OAuth flow in Section IV

# and is available in the context where these tools are initialized.

class GmailReaderTool(BaseTool):

    name: str = "Gmail Reader Tool"

    description: str = "Reads and searches for emails in a user's Gmail inbox."

    def _run(self, query: str) -> str:

        service = build('gmail', 'v1', credentials=creds)

        # Implementation to search and fetch emails based on the query

        #...

        return "Email content here..."

class GoogleCalendarSearchTool(BaseTool):

    name: str = "Google Calendar Search Tool"

    description: str = "Finds available time slots in a user's Google Calendar."

    def _run(self, start_time: str, end_time: str) -> str:

        service = build('calendar', 'v3', credentials=creds)

        # Implementation to query free/busy information

        #...

        return "List of available slots..."

class GoogleCalendarWriterTool(BaseTool):

    name: str = "Google Calendar Writer Tool"

    description: str = "Creates a new event in the user's Google Calendar."

    def _run(self, event_details: dict) -> str:

        service = build('calendar', 'v3', credentials=creds)

        # Implementation to create a calendar event

        #...

        return "Event created with ID:..."

@tool("Human Approval Tool")

def human_approval_tool(proposed_slots: list) -> str:

    """

    Presents a list of proposed time slots to the user and waits for their

    selection. This is the human-in-the-loop interface.

    """

    print("Please review the following proposed meeting times:")

    for i, slot in enumerate(proposed_slots):

        print(f"{i+1}. {slot}")

    while True:

        try:

            selection = int(input("Enter the number of your chosen time slot: "))

            if 1 <= selection <= len(proposed_slots):

                return proposed_slots[selection - 1]

            else:

                print("Invalid selection. Please try again.")

        except ValueError:

            print("Please enter a valid number.")

### **2.3. Workflow Orchestration (`crew.py`)**

The `crew.py` file is the central point where the agents, tasks, and tools are assembled into a cohesive, executable `Crew`. For the cognitive sub-tasks delegated by the main `Flow`, a `Process.sequential` workflow is appropriate, ensuring that email analysis precedes calendar searching, for example.

**`src/project_name/crew.py`:**

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

    # NOTE: In a real implementation, the 'creds' object from the OAuth flow

    # would need to be passed to these tool initializations.

    gmail_tool = GmailReaderTool()

    calendar_search_tool = GoogleCalendarSearchTool()

    calendar_write_tool = GoogleCalendarWriterTool()

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