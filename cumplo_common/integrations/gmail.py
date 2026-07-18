import base64
import re
from collections import UserDict
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from operator import itemgetter
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel

from cumplo_common.utils.constants import GMAIL_CREDENTIALS, GMAIL_FROM_EMAIL, GMAIL_LABEL, GMAIL_TOPIC, GMAIL_USER_ID

logger = getLogger(__name__)


class Attachment(BaseModel):
    """An attachment to an email."""

    path: str
    content_id: str


class Message(UserDict):
    """A Gmail message."""

    @property
    def sender(self) -> str | None:
        """The sender of the message."""
        headers = self.data.get("payload", {}).get("headers", [])
        sender = next((header["value"] for header in headers if header["name"] == "From"), None)

        if not sender:
            logger.error(f"No sender found in message: {self.data}")
            return None

        if not (result := re.search(r"<([^>]+)>", sender)):
            logger.error(f"No email found in {sender=}")
            return None

        return result.group(1)


class Gmail:
    """Integration with Gmail API."""

    @classmethod
    def _authenticate(cls) -> Any:
        """Authenticate with Gmail API."""
        credentials = service_account.Credentials.from_service_account_info(
            info=GMAIL_CREDENTIALS,
            subject=GMAIL_FROM_EMAIL,
            scopes=["https://mail.google.com/"],
        )
        return build(serviceName="gmail", version="v1", credentials=credentials)

    @classmethod
    def _get_message(cls, service: Any, message_id: str) -> Message:
        """Get a message from Gmail."""
        message = service.users().messages().get(userId=GMAIL_USER_ID, id=message_id).execute()
        return Message(message)

    @classmethod
    def subscribe(cls) -> dict:
        """Subscribe a PubSub topic to a Gmail label."""
        service = cls._authenticate()
        logger.info(f"Subscribing to Gmail label {GMAIL_LABEL} with topic {GMAIL_TOPIC}")

        request = {
            "labelFilterBehavior": "INCLUDE",
            "labelIds": [GMAIL_LABEL],
            "topicName": GMAIL_TOPIC,
        }
        response = service.users().watch(userId=GMAIL_USER_ID, body=request).execute()
        logger.info(f"Subscribed successfully. Expiration: {response.get('expiration')}")
        return response

    @classmethod
    def get_message(cls) -> Message | None:
        """
        Retrieve the message associated with a specific label.

        Returns:
            The message data as a dictionary, or None if not found

        """
        service = cls._authenticate()
        response = service.users().messages().list(userId=GMAIL_USER_ID, labelIds=[GMAIL_LABEL]).execute()

        if messages := response.get("messages"):
            return cls._get_message(service=service, message_id=messages[0]["id"])

        logger.warning(f"No messages found in Gmail for label {GMAIL_LABEL}")
        return None

    @classmethod
    def get_message_from_history(cls, history_id: str) -> Message | None:
        """
        Retrieve the last message associated with a specific label starting from a specific history ID.

        Args:
            history_id: The message history ID to look up

        Returns:
            The message data as a dictionary, or None if not found

        """
        service = cls._authenticate()
        history = service.users().history()
        response = history.list(userId=GMAIL_USER_ID, startHistoryId=history_id, labelId=GMAIL_LABEL).execute()

        # NOTE: The history is reversed to get the last message
        for history in reversed(response.get("history", [])):
            for message_added in history.get("messagesAdded", []):
                if message_id := message_added.get("message", {}).get("id"):
                    return cls._get_message(service=service, message_id=message_id)

        logger.warning(f"No messages found in Gmail for label {GMAIL_LABEL} starting from history ID {history_id}")
        return None

    @classmethod
    def send_email(cls, to: str, subject: str, content: str, *attachments: Attachment) -> dict:
        """
        Send an HTML email with attachments to a specific email address.

        Args:
            to: The email address to send the email to
            subject: The subject of the email
            content: The content of the email
            *attachments: The attachments to send with the email

        Returns:
            The response from the Gmail API

        """
        message = MIMEMultipart("related")
        message["Subject"] = subject
        message["From"] = GMAIL_FROM_EMAIL
        message["To"] = to

        message.attach(MIMEText(content, "html"))

        for attachment in attachments:
            with Path(attachment.path).open("rb") as file:
                attachment_image = MIMEImage(file.read())
                attachment_image.add_header("Content-ID", f"<{attachment.content_id}>")
                attachment_image.add_header("Content-Disposition", "inline", filename=attachment.path)
                message.attach(attachment_image)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service = cls._authenticate()

        return service.users().messages().send(userId=GMAIL_USER_ID, body={"raw": raw_message}).execute()

    @classmethod
    def get_last_message_from(cls, sender: str) -> Message | None:
        """
        Retrieve the last message from a specific sender.

        Returns:
            The message data as a dictionary, or None if not found

        """
        service = cls._authenticate()
        response = service.users().messages().list(userId=GMAIL_USER_ID, labelIds=[GMAIL_LABEL]).execute()

        if not (messages := response.get("messages")):
            logger.warning(f"No messages found in Gmail for label {GMAIL_LABEL}")
            return None

        for message_id in map(itemgetter("id"), messages):
            message = cls._get_message(service=service, message_id=message_id)
            if sender == message.sender:
                return message

        logger.warning(f"No messages found in Gmail for sender {sender}")
        return None
