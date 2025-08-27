from crewai_tools import tool

from googleapiclient.discovery import build
from ..auth import get_google_credentials


@tool("Gmail Reader Tool")
def gmail_reader_tool(query: str) -> str:
    """Reads and searches for emails in a user's Gmail inbox."""
    creds = get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    # Search for messages matching the query
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = result.get("messages", [])

    if not messages:
        return "No messages found."

    # Fetch and combine the content of the messages
    email_content = []
    for msg in messages:
        txt = (
            service.users().messages().get(userId="me", id=msg["id"]).execute()
        )
        try:
            payload = txt["payload"]
            headers = payload["headers"]
            subject = next(
                h["value"] for h in headers if h["name"] == "Subject"
            )

            parts = payload.get("parts", [])
            body = ""
            if parts:
                # Find the plain text part
                part = next(
                    (p for p in parts if p["mimeType"] == "text/plain"),
                    None,
                )
                if part:
                    import base64

                    data = part["body"]["data"]
                    body = base64.urlsafe_b64decode(data).decode("utf-8")

            email_content.append(f"Subject: {subject}\nBody: {body}\n---")
        except (KeyError, StopIteration):
            # Handle cases where email format is unexpected
            email_content.append(
                f"Could not parse email with ID: {msg['id']}\n---"
            )

    return "\n".join(email_content)


@tool("Google Calendar Search Tool")
def google_calendar_search_tool(start_time: str, end_time: str) -> str:
    """Finds available time slots in a user's Google Calendar."""
    creds = get_google_credentials()
    service = build("calendar", "v3", credentials=creds)

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": "primary"}],
    }

    events_result = service.freebusy().query(body=body).execute()
    calendars = events_result.get("calendars", {})
    primary_calendar = calendars.get("primary", {})
    busy_times = primary_calendar.get("busy", [])

    if not busy_times:
        return (
            f"The calendar is completely free between {start_time} "
            f"and {end_time}."
        )

    # For simplicity, this tool will just return the busy times.
    # A more advanced implementation would calculate the free slots.
    busy_slots_str = "\n".join(
        [f"- From {slot['start']} to {slot['end']}" for slot in busy_times]
    )
    return f"The following time slots are busy:\n{busy_slots_str}"


@tool("Google Calendar Writer Tool")
def google_calendar_writer_tool(event_details: dict) -> str:
    """Creates a new event in the user's Google Calendar."""
    creds = get_google_credentials()
    service = build("calendar", "v3", credentials=creds)

    event = (
        service.events()
        .insert(calendarId="primary", body=event_details)
        .execute()
    )

    return f"Event created successfully. Event ID: {event.get('id')}"


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
            selection = int(
                input("Enter the number of your chosen time slot: ")
            )
            if 1 <= selection <= len(proposed_slots):
                return proposed_slots[selection - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
