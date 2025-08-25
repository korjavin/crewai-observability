import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]

def get_google_credentials():
    """Handles the OAuth 2.0 flow and returns valid credentials."""
    creds = None
    if os.path.exists('config/token.txt'):
        creds = Credentials.from_authorized_user_file('config/token.txt', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET_JSON')
            if not client_secret_json:
                raise ValueError("GOOGLE_CLIENT_SECRET_JSON environment variable not set.")

            client_config = json.loads(client_secret_json)
            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('config/token.txt', 'w') as token:
            token.write(creds.to_json())

    return creds
