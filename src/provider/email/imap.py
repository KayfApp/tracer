from datetime import datetime, timezone
from provider.generic_provider import GenericProvider
import imaplib
import email
import email.utils
from email.header import decode_header

def _get_email_body(msg):
    """Extract the body from the email message."""
    # If the email message is multipart
    if msg.is_multipart():
        for part in msg.walk():
            # Look for text/plain or text/html content
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        # If the email is not multipart
        return msg.get_payload(decode=True).decode()


class ImapProvider(GenericProvider):
    _ID="IMAP@KAYF:1.0"
    _NAME="IMAP E-Mail"
    _DESCRIPTION="Provider implementation for IMAP."
    _AVATAR=""
    _SCHEMA={
        "connection" : "text",
        "user": "text",
        "password": "text"
    }

    def _setup(self) -> bool:
        data = self.data
        self._mail = imaplib.IMAP4_SSL(data['connection'])
        self._mail.login(data['user'], data['password'])
        return True

    def run(self) -> bool:
        if super().run() == False:
            return False

        last_fetched = self.last_fetched
        if last_fetched == None:
            return False

        self._mail.select("inbox")
        utc_min_datetime = datetime.min.replace(tzinfo=timezone.utc)
        search_criteria = "ALL" if last_fetched == utc_min_datetime else f"(SINCE {last_fetched.strftime("%d-%b-%Y")})"
        initiated_at = datetime.now(tz=timezone.utc)

        _, data = self._mail.search(None, search_criteria)
        email_ids = data[0].split()
        emails = []

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
                    
                    if(email_date == None):
                        continue

                    if email_date > last_fetched:
                        # Add email details to the list
                        emails.append({
                            "subject": subject,
                            "from": from_,
                            "date": email_date,
                            "body": _get_email_body(msg)
                        })

        self.update_last_fetched(initiated_at)
        print(emails)
        return True

    def _clean_up(self) -> None:
        self._mail.logout()
