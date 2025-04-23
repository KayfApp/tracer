from datetime import datetime, timezone

from globals import LOGGER
from provider.generic_provider import GenericProvider
import imaplib
import email
import email.utils
from email.header import decode_header
from typing import List, Dict, Optional
from provider.parser.cleanup import clean_up
from provider.parser.markup_parser import html_to_plain, markdown_to_plain
from provider.utils.pipeline import pipeline
from provider.utils.text_type_detector import TextType, detect_text_type

def _get_email_body(msg) -> Optional[str]:
    """Extracts the body from the email message."""
    # If the email message is multipart
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ["text/plain", "text/html"]:
                charset = part.get_content_charset() or 'utf-8'
                payload = part.get_payload(decode=True)
                try:
                    return payload.decode(charset)
                except (UnicodeDecodeError, TypeError) as e:
                    LOGGER.error(f"Decoding error for {charset}: {e}")
                    return None
    else:
        # If the email is not multipart
        charset = msg.get_content_charset() or 'utf-8'
        payload = msg.get_payload(decode=True)
        try:
            return payload.decode(charset)
        except (UnicodeDecodeError, TypeError) as e:
            LOGGER.error(f"Decoding error for {charset}: {e}")
            return None
    
    return None

class ImapProvider(GenericProvider):
    """Provider implementation for handling IMAP email fetching."""

    _ID = "IMAP@KAYF:1.0"
    _NAME = "IMAP E-Mail"
    _DESCRIPTION = "Provider implementation for IMAP."
    _AVATAR = ""
    _SCHEMA = {
        "connection": "text",
        "user": "text",
        "password": "text"
    }

    def _setup(self) -> bool:
        """Establishes a connection to the IMAP server.

        Returns:
            bool: True if the setup was successful, False otherwise.
        """
        data = self.data
        self._mail = imaplib.IMAP4_SSL(data['connection'])
        self._mail.login(data['user'], data['password'])
        return True

    def run(self) -> bool:
        """Fetches emails from the IMAP inbox.

        Returns:
            bool: True if the fetching was successful, False otherwise.
        """
        if not super().run():
            return False

        last_fetched = self.last_fetched
        if last_fetched is None:
            return False

        self._mail.select("inbox")
        utc_min_datetime = datetime.min.replace(tzinfo=timezone.utc)

        search_criteria = "ALL" if last_fetched == utc_min_datetime else f"(SINCE {last_fetched.strftime('%d-%b-%Y')})"
        initiated_at = datetime.now(tz=timezone.utc)

        try:
            _, data = self._mail.search(None, search_criteria)
            email_ids = data[0].split()
            emails: List[Dict] = []

            for email_id in email_ids:
                # Fetch the email by ID
                _, message_data = self._mail.fetch(email_id, "(RFC822)")

                for response_part in message_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Decode email subject
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")

                        # Get sender
                        from_ = msg.get("From")

                        # Parse the email date
                        date = msg.get("Date")
                        email_date = email.utils.parsedate_to_datetime(date)

                        if email_date is None:
                            continue

                        if email_date > last_fetched:
                            # Add email details to the list
                            emails.append({
                                "subject": subject,
                                "from": from_,
                                "date": email_date,
                                "body": _get_email_body(msg)
                            })

            for mail in emails:
                text = mail["body"]
                text = clean_up(text)               
                docs = pipeline(text, self.id, 'Email', "", mail["subject"], mail["from"], self._AVATAR, '', '', mail["date"])
                for doc in docs:
                    print(doc.id, doc.data)

            self.update_last_fetched(initiated_at)
            return True

        except imaplib.IMAP4.error as e:
            LOGGER.error(f"IMAP error occurred: {e}")
            return False
        except Exception as e:
            LOGGER.error(f"An unexpected error occurred: {e}")
            return False

    def _clean_up(self) -> None:
        """Logs out from the IMAP server."""
        if self._setup_completed is False:
            return

        if self._mail is not None:
            self._mail.logout()
