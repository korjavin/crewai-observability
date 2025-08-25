
# Workflow: From Email to Calendar Event

This document describes the end-to-end workflow of the AI Scheduling Assistant, detailing the sequence of operations and the crucial human-in-the-loop approval step.

## 1. Triggering the Process

The entire workflow is initiated by running the main script:

```bash
python main.py
```

This script is responsible for:
1.  Loading environment variables from `.env`.
2.  Setting up the OpenTelemetry tracer.
3.  Instantiating the agents, tasks, and the two crews (`AnalysisCrew` and `BookingCrew`).
4.  Kicking off the `AnalysisCrew`.

## 2. Phase 1: Analysis and Proposal

This phase is handled by the **`AnalysisCrew`**. The flow is entirely autonomous.

-   **Step 1: Scan Emails**
    -   The `scan_emails_task` is executed by the `Email Reader Agent`.
    -   It calls the `read_emails` tool, searching for messages that might contain scheduling requests (e.g., containing words like "call," "meeting," "schedule").
    -   The content of these emails is passed as context to the next task.

-   **Step 2: Analyze Email Content**
    -   The `analyze_event_task` is executed by the `Event Analyst Agent`.
    -   It reads the email text and uses the LLM's reasoning ability to extract a structured summary, a list of attendees (and their emails), and a likely duration for the meeting.
    -   This structured data is passed to the next task.

-   **Step 3: Find Available Slots**
    -   The `find_slots_task` is executed by the `Scheduling Assistant Agent`.
    -   It takes the structured event data, specifically the attendees and duration.
    -   It calls the `find_available_slots` tool, which queries the Google Calendar API.
    -   The tool returns a list of potential slots, which the agent then formats into a human-readable list.

-   **Step 4: Present for Approval**
    -   The `AnalysisCrew` finishes its work. Its final output is the formatted list of proposed time slots.
    -   The `main.py` script prints this output to the console.

## 3. Phase 2: Human-in-the-Loop (Approval)

This is the most critical interactive step.

-   **Step 5: User Input**
    -   The script will display a prompt to the user, for example:

    ```
    I found a potential meeting request in an email from 'elon@x.com'.
    Topic: Discussing Mars Colonization Strategy
    Attendees: you, elon@x.com

    Here are some available slots:
    1. 2025-09-03T10:00:00-07:00
    2. 2025-09-03T14:30:00-07:00
    3. 2025-09-04T11:00:00-07:00

    Please select a slot number to book, or type 'n' to cancel: 
    ```

    -   The script then waits for the user to type a number and press Enter.

## 4. Phase 3: Booking

This phase is triggered only if the user approves a time slot.

-   **Step 6: Prepare for Booking**
    -   The `main.py` script takes the user's selected slot and the event details from the `AnalysisCrew`'s output.
    -   It dynamically creates the necessary context for the `BookingCrew`. This context includes the exact start/end times, the summary, attendees, and description.

-   **Step 7: Create the Event**
    -   The `main.py` script kicks off the **`BookingCrew`**.
    -   The `book_event_task` is executed by the `Event Booker Agent`.
    -   The agent calls the `create_calendar_event` tool, passing in all the details.
    -   The tool interacts with the Google Calendar API to create the event and invite the attendees.

-   **Step 8: Final Confirmation**
    -   The `BookingCrew` finishes, returning a confirmation message from the tool.
    -   The `main.py` script prints this final confirmation to the user:

    ```
    Success! Event has been created.
    View it here: https://calendar.google.com/event?action=VIEW&eid=...
    ```

If the user had typed 'n' to cancel, the script would simply terminate after the analysis phase.
