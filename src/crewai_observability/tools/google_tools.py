from crewai_tools import BaseTool
from googleapiclient.discovery import build
from src.crewai_observability.auth import get_google_credentials

class GmailReaderTool(BaseTool):
    name: str = "Gmail Reader Tool"
    description: str = "Reads and searches for emails in a user's Gmail inbox."

    def _run(self, query: str) -> str:
        creds = get_google_credentials()
        service = build('gmail', 'v1', credentials=creds)

        # Search for messages matching the query
        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])

        if not messages:
            return "No messages found."

        # Fetch and combine the content of the messages
        email_content = []
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            try:
                payload = txt['payload']
                headers = payload['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')

                parts = payload.get('parts', [])
                body = ""
                if parts:
                    # Find the plain text part
                    part = next((p for p in parts if p['mimeType'] == 'text/plain'), None)
                    if part:
                        import base64
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')

                email_content.append(f"Subject: {subject}\nBody: {body}\n---")
            except (KeyError, StopIteration):
                # Handle cases where email format is unexpected
                email_content.append(f"Could not parse email with ID: {msg['id']}\n---")

        return "\n".join(email_content)

class GoogleCalendarSearchTool(BaseTool):
    name: str = "Google Calendar Search Tool"
    description: str = "Finds available time slots in a user's Google Calendar."

    def _run(self, start_time: str, end_time: str) -> str:
        creds = get_google_credentials()
        service = build('calendar', 'v3', credentials=creds)

        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": "primary"}]
        }

        events_result = service.freebusy().query(body=body).execute()
        calendars = events_result.get('calendars', {})
        primary_calendar = calendars.get('primary', {})
        busy_times = primary_calendar.get('busy', [])

        if not busy_times:
            return f"The calendar is completely free between {start_time} and {end_time}."

        # For simplicity, this tool will just return the busy times.
        # A more advanced implementation would calculate the free slots.
        busy_slots_str = "\n".join([f"- From {slot['start']} to {slot['end']}" for slot in busy_times])
        return f"The following time slots are busy:\n{busy_slots_str}"

class GoogleCalendarWriterTool(BaseTool):
    name: str = "Google Calendar Writer Tool"
    description: str = "Creates a new event in the user's Google Calendar."

    def _run(self, event_details: dict) -> str:
        creds = get_google_credentials()
        service = build('calendar', 'v3', credentials=creds)

        event = service.events().insert(calendarId='primary', body=event_details).execute()

        return f"Event created successfully. Event ID: {event.get('id')}"
