from crewai.tools import BaseTool, tool
from googleapiclient.discovery import build

class GmailReaderTool(BaseTool):
    name: str = "Gmail Reader Tool"
    description: str = "Reads and searches for emails in a user's Gmail inbox."
    creds: object = None

    def __init__(self, creds):
        super().__init__()
        self.creds = creds

    def _run(self, query: str) -> str:
        import base64
        import json

        service = build('gmail', 'v1', credentials=self.creds)
        try:
            response = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
            messages = response.get('messages', [])

            emails = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                parts = payload.get('parts', [])

                body = ""
                if parts:
                    for part in parts:
                        if part['mimeType'] == 'text/plain':
                            encoded_body = part['body'].get('data', '')
                            body = base64.urlsafe_b64decode(encoded_body).decode('utf-8')
                            break

                emails.append({
                    'thread_id': msg['threadId'],
                    'body': body
                })

            return json.dumps(emails)
        except Exception as e:
            return f"An error occurred: {e}"

class GoogleCalendarSearchTool(BaseTool):
    name: str = "Google Calendar Search Tool"
    description: str = "Finds available time slots in a user's Google Calendar."
    creds: object = None

    def __init__(self, creds):
        super().__init__()
        self.creds = creds

    def _run(self, start_time: str, end_time: str) -> str:
        import json
        from datetime import datetime, timedelta

        service = build('calendar', 'v3', credentials=self.creds)
        try:
            now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

            freebusy_query = {
                "timeMin": start_time,
                "timeMax": end_time,
                "items": [{"id": "primary"}]
            }

            freebusy_result = service.freebusy().query(body=freebusy_query).execute()
            busy_slots = freebusy_result['calendars']['primary']['busy']

            # For simplicity, this example just returns the busy slots.
            # A real implementation would need to find the free slots between the busy ones.
            return json.dumps(busy_slots)
        except Exception as e:
            return f"An error occurred: {e}"

class GoogleCalendarWriterTool(BaseTool):
    name: str = "Google Calendar Writer Tool"
    description: str = "Creates a new event in the user's Google Calendar."
    creds: object = None

    def __init__(self, creds):
        super().__init__()
        self.creds = creds

    def _run(self, event_details: dict) -> str:
        import json

        service = build('calendar', 'v3', credentials=self.creds)
        try:
            event = service.events().insert(calendarId='primary', body=event_details).execute()
            return f"Event created successfully. Event ID: {event['id']}, Link: {event['htmlLink']}"
        except Exception as e:
            return f"An error occurred: {e}"

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
