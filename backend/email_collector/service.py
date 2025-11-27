import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service(token_path="token.json", creds_path="credentials.json"):
    """Authenticate and return a Gmail API service instance.

    Token and credentials paths are relative to this package directory.
    """
    script_dir = os.path.dirname(__file__)
    token_file = os.path.join(script_dir, token_path)
    creds_file = os.path.join(script_dir, creds_path)

    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
