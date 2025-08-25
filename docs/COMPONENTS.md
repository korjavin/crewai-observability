
# Components: Agents, Tasks, and Tools

This document provides a detailed description of the core components of the AI Scheduling Assistant: the Agents, the Tasks they perform, and the Tools they use.

## 1. The Role of the Model Context Protocol (MCP)

In this architecture, we assume that agents needing to interact with external services (like Google) do so through the **Model Context Protocol (MCP)**. The tools listed below are the practical implementations that would be exposed via this protocol.

An agent's interaction looks like this:
1.  The `crewai` agent determines a tool is needed (e.g., `read_emails`).
2.  It invokes the tool, which is understood to be an MCP-compliant endpoint.
3.  The tool function executes, handling its own authentication to the Google API and returning a standardized response to the agent.

This decouples the agent's logic from the tool's implementation. For this simulation, we will define these tools as standard Python functions, but the architecture presumes they operate under the MCP standard.

## 2. Tools

Tools are the functions that agents can execute to interact with the outside world.

### `src.tools.google_mail_tools.py`

-   **`read_emails(query: str, max_results: int = 5) -> list[dict]`**
    -   **Description**: Reads recent emails from Gmail that match a given query.
    -   **Inputs**: A search query (e.g., `'is:unread'`) and the maximum number of emails to fetch.
    -   **Output**: A list of dictionaries, where each dictionary contains the `subject`, `sender`, and `body` of an email.
    -   **Underlying API**: `gmail.users().messages().list()` and `gmail.users().messages().get()`.

### `src.tools.google_calendar_tools.py`

-   **`find_available_slots(attendees: list[str], duration_minutes: int = 60) -> list[str]`**
    -   **Description**: Finds available time slots in the next 7 days when all specified attendees are free.
    -   **Inputs**: A list of attendee email addresses and the desired meeting duration.
    -   **Output**: A list of suggested time slots in ISO 8601 format.
    -   **Underlying API**: `calendar.freebusy().query()`.

-   **`create_calendar_event(summary: str, start_time: str, end_time: str, attendees: list[str], description: str) -> str`**
    -   **Description**: Creates a new event in the user's Google Calendar.
    -   **Inputs**: The event title (`summary`), start/end times (ISO 8601), a list of attendee emails, and a description.
    -   **Output**: A confirmation string with the link to the created event.
    -   **Underlying API**: `calendar.events().insert()`.

## 3. Agents

Agents are the specialized AI workers in our crew.

### `src.agents.py`

-   **Email Reader Agent**
    -   **Role**: Email Scanning Specialist
    -   **Goal**: To efficiently scan a user's inbox for relevant new emails that might contain actionable requests or event proposals.
    -   **Backstory**: An expert at sifting through digital correspondence, this agent can quickly identify signal in the noise of a busy inbox.
    -   **Tools**: `[read_emails]`

-   **Event Analyst Agent**
    -   **Role**: Senior Event Analyst
    -   **Goal**: To carefully read and understand the content of an email, identify the core intent, and extract all necessary details for a potential calendar event (e.g., topic, participants, desired duration).
    -   **Backstory**: With a background in natural language understanding and semantic analysis, this agent excels at interpreting human communication and structuring it into actionable data.
    -   **Tools**: None (it operates on text provided by the previous agent).

-   **Scheduling Assistant Agent**
    -   **Role**: Calendar and Logistics Coordinator
    -   **Goal**: To take a proposed event and find the best possible time slots for it by cross-referencing the calendars of all required attendees.
    -   **Backstory**: A master of logistics and scheduling, this agent can navigate the complexities of multiple calendars to find the perfect meeting time.
    -   **Tools**: `[find_available_slots]`

-   **Event Booker Agent**
    -   **Role**: Executive Booking Agent
    -   **Goal**: To take a final, user-approved event (with a specific time slot) and officially create it on the Google Calendar, inviting all attendees.
    -   **Backstory**: This agent is the final step in the process, known for its reliability and precision. When it's given a task, it gets done correctly.
    -   **Tools**: `[create_calendar_event]`

## 4. Tasks

Tasks are the specific assignments given to the agents.

### `src.tasks.py`

-   **`scan_emails_task`**
    -   **Description**: Scan the inbox for unread emails that suggest a meeting or call needs to be scheduled.
    -   **Expected Output**: A list of email contents that are potential candidates for scheduling.
    -   **Agent**: Email Reader Agent

-   **`analyze_event_task`**
    -   **Description**: Analyze the provided email content. Extract the topic of the meeting, the names and emails of the people involved, and the suggested duration.
    -   **Expected Output**: A structured dictionary containing `summary`, `attendees`, and `duration_minutes` for a potential event.
    -   **Agent**: Event Analyst Agent

-   **`find_slots_task`**
    -   **Description**: Using the structured event details, search the calendar to find a list of 3-5 suitable time slots.
    -   **Expected Output**: A formatted string listing the available slots for the user to review.
    -   **Agent**: Scheduling Assistant Agent

-   **`book_event_task`**
    -   **Description**: Based on the user's selected time slot, create the event in Google Calendar. The context for this task will include the approved slot.
    -   **Expected Output**: A confirmation message stating that the event has been successfully created, including the event link.
    -   **Agent**: Event Booker Agent
