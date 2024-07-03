import base64
import os.path
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as GCredentials
from google_auth_oauthlib.flow import InstalledAppFlow as GInstalledAppFlow
from googleapiclient.discovery import Resource as DiscoveryResource
from googleapiclient.discovery import build

from .config import CONFIG
from .get_filled_template import get_filled_template
from .logger import on_email_sent
from .logos import Logos

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def create_message(name: str, target_email: str) -> dict[str, str]:
    """Returns the raw data to be used as the email"""

    msg = MIMEMultipart(_subtype="related")  # Multipart contains HTML content + images

    # Set HTML body and attach it
    email_template = get_filled_template(name)
    html_template, subject = email_template.html_template, email_template.subject
    body = MIMEText(html_template, _subtype="html")
    msg.attach(body)

    # Add logos as MIMEImages
    for i, logo in enumerate(
        (Logos.KGSMUN, Logos.INSTA, Logos.FACEBOOK)
    ):  # Logo order matters!
        content_name = i + 1
        img = MIMEImage(logo, "png")
        img.add_header("Content-Id", f"<{content_name}>")
        img.add_header("Content-Disposition", "inline", filename=f"{content_name}")
        msg.attach(img)

    msg["from"] = CONFIG["sender"]["email-address"]
    msg["subject"] = subject
    msg["to"] = target_email
    encoded_message = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode()  # Convert MIME Object to text representation (in bytes), then b64 encode those bytes, and convert back to a b64 encoded string
    return {"raw": encoded_message}


def get_gmail_service() -> DiscoveryResource:
    """Checks for creds, and returns a service"""
    creds = None

    if os.path.exists("token.json"):
        creds = GCredentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = GInstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service: DiscoveryResource = build("gmail", "v1", credentials=creds)
    return service


def send_email(name: str, target_email: str) -> None:
    service = get_gmail_service()
    service.users().messages().send(
        userId="me", body=create_message(name, target_email)
    )  # .execute()

    on_email_sent(name, target_email)
