import os
import base64
from gmail_service import get_gmail_service

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def fetch_annonce_pdfs():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId='me',
        q="subject:annonce has:attachment"
    ).execute()

    messages = results.get('messages', [])
    pdf_files = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id']
        ).execute()

        parts = msg_data["payload"].get("parts", [])

        for part in parts:
            if part.get("mimeType") == "application/pdf":
                filename = part["filename"]
                att_id = part["body"]["attachmentId"]

                att = service.users().messages().attachments().get(
                    userId="me",
                    messageId=msg["id"],
                    id=att_id
                ).execute()

                data = base64.urlsafe_b64decode(att["data"])
                pdf_path = os.path.join(DOWNLOAD_DIR, filename)

                with open(pdf_path, "wb") as f:
                    f.write(data)

                pdf_files.append((msg["id"], pdf_path))

    return pdf_files
