import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")
TOKEN_PATH = os.getenv("TOKEN_PATH")

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Token invalide. Lancez l'authentification Gmail.")
    service = build('gmail', 'v1', credentials=creds)
    return service
