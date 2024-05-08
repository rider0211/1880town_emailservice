from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from chat_agent import ChatAgent
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from cardprocessor import change_image_text
import os
import random
import base64
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class EmailHandler:
    def __init__(self, credentials_file, token_file, db_config, api_key, agent_name):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = self.get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.agent = ChatAgent(api_key, db_config, agent_name)

    def get_credentials(self):
        creds = None
        credentials_file = self.credentials_file
        token_file = self.token_file
        # Check if the token file exists and has valid credentials
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            except Exception as e:
                os.remove(token_file)
                creds = None
        
        # If no valid credentials, start the authorization flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES, access_type='offline')
                creds = flow.run_console()  # This will give a URL to visit and ask for a token to enter in the console
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        return creds

    def read_emails_bing(self):
        results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        messages = results.get('messages', [])
        for msg in messages:
            msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            email_from = next(header['value'] for header in msg_detail['payload']['headers'] if header['name'] == 'From')
            text = self.decode_message(msg)
            subject = next((header['value'] for header in msg_detail['payload']['headers'] if header['name'] == 'Subject'), None)
            response = self.agent.chat_bing(text, email_from)
            attachment_path = None
            if "Here is my affirmation card." in response:
                imgnum = random.randint(1, 3)
                attachment_path = f"{imgnum}_out.png"
                change_image_text(imgnum, self.agent.agent_name, f"Hi, {subject}", attachment_path)
            self.reply_email(msg['id'], response, email_from, attachment_path)
            self.mark_as_read(msg['id'])
    
    def read_emails_otis(self):
        results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        messages = results.get('messages', [])
        for msg in messages:
            msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            email_from = next(header['value'] for header in msg_detail['payload']['headers'] if header['name'] == 'From')
            text = self.decode_message(msg)
            subject = next((header['value'] for header in msg_detail['payload']['headers'] if header['name'] == 'Subject'), None)
            response = self.agent.chat_otis(subject, text, email_from)
            attachment_path = None
            if "otis" in subject:
                imgnum = random.randint(1, 3)
                attachment_path = f"{imgnum}_out.png"
                change_image_text(imgnum, self.agent.agent_name, f"Hi, {subject}", attachment_path)
            self.reply_email(msg['id'], response, email_from, attachment_path)
            self.mark_as_read(msg['id'])

    def decode_message(self, msg):
        msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        parts = msg_detail['payload']['parts'][0]
        data = parts['body']['data']
        text = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
        return text

    def reply_email(self, message_id, message_text, email_from, file_path=None):
        message = MIMEMultipart()
        message['to'] = email_from
        message['subject'] = "Dear Friend"
        message.attach(MIMEText(message_text, 'plain'))

        if file_path:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
                message.attach(part)

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw_message}
        self.service.users().messages().send(userId='me', body=send_message).execute()



    def mark_as_read(self, message_id):
        self.service.users().messages().modify(userId='me', id=message_id,
            body={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}).execute()
