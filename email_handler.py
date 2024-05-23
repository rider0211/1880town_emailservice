import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import message_from_bytes
import os
import random
from chat_agent import ChatAgent
from cardprocessor import change_image_text
from imgdb import IMGDB

class EmailHandler:
    def __init__(self, username, password, db_config, api_key, agent_name):
        self.username = username
        self.password = password
        self.agent = ChatAgent(api_key, db_config, agent_name)
        self.imgdb = IMGDB(db_config)
        self.imap_host = 'imap.gmail.com'
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
        self.connect()

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_host)
        self.mail.login(self.username, self.password)
        self.mail.select('inbox')

    def reconnect(self):
        self.close_connection()  # Close the existing connection if any
        self.connect()           # Re-establish a new connection

    def read_emails_bing(self):
        try:
            type, data = self.mail.search(None, 'UNSEEN')
        except imaplib.IMAP4.abort as e:
            print(f"IMAP connection aborted: {e}. Reconnecting...")
            self.connect()  # Ensure this method reinitializes self.mail correctly
            type, data = self.mail.search(None, 'UNSEEN')  # Retry the operation
        except Exception as e:
            print(f"An error occurred: {e}")

        for num in data[0].split():
            typ, data = self.mail.fetch(num, '(RFC822)')
            msg = message_from_bytes(data[0][1])
            email_from = msg['from']
            subject = msg['subject']
            if msg['In-Reply-To'] or msg.get('References'):
                response = "Hey there, superstars! Instead of hitting the Reply button, can you create a brand new message to chat with me? It's like starting a fresh adventure each time! I like this. Thanks a bunch, and keep being awesome!"
                self.reply_email(email_from, subject, response)
            else:
                body = self.decode_message(msg)
                response = self.agent.chat_bing(body, email_from)
                attachment_path = None
                if "7:00" in response:
                    imgnum = random.randint(1, 3)
                    attachment_path = f"{imgnum}_out.png"
                    change_image_text(imgnum, self.agent.agent_name, f"Hi {subject}", attachment_path)
                    self.imgdb.save_scheduled_message(email_from, 'bing', subject, attachment_path)
                self.reply_email(email_from, subject, response)
            self.mark_as_read(num)

    def read_emails_otis(self):
        try:
            type, data = self.mail.search(None, 'UNSEEN')
        except imaplib.IMAP4.abort as e:
            print(f"IMAP connection aborted: {e}. Reconnecting...")
            self.connect()
            type, data = self.mail.search(None, 'UNSEEN')
        except Exception as e:
            print(f"An error occurred: {e}")
        
        print("Unread emails count:", len(data[0].split()))

        for num in data[0].split():
            typ, data = self.mail.fetch(num, '(RFC822)')
            msg = message_from_bytes(data[0][1])
            email_from = msg['from']
            subject = msg['subject']
            
            if msg['In-Reply-To'] or msg.get('References'):
                response = "Hey there, superstars! Instead of hitting the Reply button, can you create a brand new message to chat with me? It's like starting a fresh adventure each time! I like this. Thanks a bunch, and keep being awesome!"
                self.reply_email(email_from, subject, response)
            else:
                body = self.decode_message(msg)
                print('subject:', subject)
                print('body:', body) 
                response = self.agent.chat_otis(subject, body, email_from)
                attachment_path = None

                # Check conditions for sending an attachment
                if "otis" in subject and self.agent.show_affirmation_card:
                    username = " ".join(subject.split()[1:])  # Assume username is part of the subject
                    imgnum = random.randint(1, 20)
                    attachment_path = f"img/useroutput/{username}_out.png"
                    change_image_text(imgnum, self.agent.agent_name, "Hi " + username, attachment_path)
                    self.imgdb.save_scheduled_message(email_from, 'otis', username, attachment_path)
                elif "7:00" in response:
                    username = self.agent.db.fetch_user_name(email_from, 'otis')
                    imgnum = random.randint(1, 20)
                    attachment_path = f"img/useroutput/{username}_out.png"
                    change_image_text(imgnum, self.agent.agent_name, "Hi " + username, attachment_path)
                    self.imgdb.save_scheduled_message(email_from, 'otis', username, attachment_path)
                # Send the response email
                self.reply_email(email_from, subject, response)
            self.mark_as_read(num)  # Mark the email as read

    def decode_message(self, msg, reply=False):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True).decode('utf-8')
                    if reply:
                        # Attempt to isolate updated text in the reply
                        return self.extract_new_text(payload)
                    return payload
        else:
            payload = msg.get_payload(decode=True).decode('utf-8')
            if reply:
                return self.extract_new_text(payload)
            return payload

    def extract_new_text(self, text):
        # Common patterns used to indicate quoted text in replies
        patterns = [
            r"^\s*>",  # Lines starting with ">"
            r"On\s.+\swrote:",  # "On [date] [email] wrote:" pattern
            r"From:\s.+",  # Starts with "From: "
            r"Sent from my\s.+"  # "Sent from my [device]" commonly added by mobile devices
        ]
        import re
        # Try to find the first occurrence of quoted text and split there
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return text[:match.start()].strip()
        return text  # If no quoted text is found, return the whole text

    def reply_email(self, recipient, subject, body, attachment_path=None):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = recipient
        msg['Subject'] = "Re: " + subject
        msg.attach(MIMEText(body, 'plain'))
        if attachment_path:
            with open(attachment_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<{}>'.format(os.path.basename(attachment_path)))
                msg.attach(img)
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.starttls()
        smtp.login(self.username, self.password)
        smtp.sendmail(self.username, recipient, msg.as_string())
        smtp.quit()

    def mark_as_read(self, num):
        self.mail.store(num, '+FLAGS', '\\Seen')

    def close_connection(self):
        self.mail.logout()

    def send_email_with_image(self, recipient, subject, body, image_path):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(image_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<image1>')
            msg.attach(img)

        self.smtp.send_message(msg)
        self.smtp.quit()