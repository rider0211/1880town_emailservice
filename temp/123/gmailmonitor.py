import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os.path
import pickle
import re
from requests import HTTPError
from MailListManager import MailListManager
from chatresponse import Chatbot
from cardprocessor import change_image_text
import random

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

bing_original_prompt = """Imagine that you are a horse named bing in 1880 town. Please response the this email message. Don't forget that you must end your response to ask user to want to see your "affirmation card".:"""
bing_second_prompt = """Is the following email message agree to see affirmation card or not? Please answer only the result-'yes', 'no' or 'not mentioned'.: """
bing_third_yes_prompt = """Imagine that you attached the affirmation card just before. chat him as you like from now.:"""
bing_third_no_prompt = """Chat him as you like from now.:"""
original_prompt = """Imagine that you are a camel named Otis from 1880 town. Your password is "otis1024". please response this sentence. You have to ask about your password and Don't forget to end your response to "Do you want my affirmation card?" Only if there is a subject contain only 'PW', answer your password to him and tell him "If you want my affirmation card, please send me a new email with this password in subject and your name in message.".:
"""

passwordreply = """Hightlight about answering the password. If there is a question to ask about the password or he doesn't know about password, answer your password and tell him "If you want my affirmation card, please send me a new email with the password in subject and your name in message.". You can give him the password.:"""

passpassword_prompt = """Please imagine that he already answered the password and notify that you attached the affirmation card just before. chat him as you like from now. Don't metion about the password and affirmation card anymore before when he require your affirmation card and password. Then you have to ask him if he would like an animated video of 'Emmy’s tour of the 1880 town' and tell him "If you want my animated video, please send me a new email "I want video" in subject name":"""

free_prompt = """Don't ask about the password, affirmation card and anymore before when he require your affirmation card and there is no "PW" in subject again. chat him as you like from now.:"""

coloring_page_number = 0

def create_message_with_attachment(sender, to, subject, message_text, file_path=None):
    """Create a message for an email with an optional attachment."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Attach the message text
    message.attach(MIMEText(message_text, 'plain'))
    # Attach the specified file if provided
    if file_path:
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            message.attach(part)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def get_email_only(from_header):
    # Sample input from the 'From' header

    # Regular expression to match email addresses
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Extracting the email address using regex search
    from_email = re.search(email_regex, from_header)
    if from_email:
        from_email = from_email.group(0)
    else:
        from_email = None

    # print(from_email)
    return from_email

def get_service(account_name):
    creds = None
    token_path = f'token_{account_name}.pickle'
    credentials_path = f'credentials_{account_name}.json'
    print(credentials_path)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES, redirect_uri='http://localhost:5229/')
            creds = flow.run_local_server(port=5229)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {message['id']}")
        return message
    except HTTPError as error:
        print(f'An error occurred: {error}')
        return None

def reply_to_message(service, user_id, message_id, subject, reply_text, attachment_path):
    """Reply to a specific message."""
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
    from_email = get_email_only(next((header['value'] for header in message['payload']['headers'] if header['name'] == 'From'), None))
    if not from_email:
        print(f"Could not find sender's email for message ID: {message_id}")
        return

    # Preparing the reply
    reply_subject = f"Re: {subject}"
    reply_message = create_message_with_attachment(user_id, from_email, reply_subject, reply_text, attachment_path)

    # Sending the reply
    send_message(service, user_id, reply_message)

def mark_message_as_read(service, user_id, message_id):
    """Marks the message as read by removing the 'UNREAD' label."""
    try:
        service.users().messages().modify(
            userId=user_id,
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        print(f"Message {message_id} marked as read.")
    except Exception as error:
        print(f"An error occurred: {error}")

def check_unread_messages(service, db, account_name):
    print(service.users())
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])
    passnumber = 1024
    if not messages:
        print("No unread messages.")
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), None)
            content = msg['snippet']  # Using snippet as content for simplicity
            print(subject)
            print(content)
            from_email = get_email_only(next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'), None))
            isNew = db.get_responsenumber_by_email(account_name, from_email)
            print(isNew)
            agentgpt = Chatbot()
            if isNew == 0:
                if account_name == "bing":
                    attachment_path = None
                    reply_subject, reply_content = agentgpt.get_response(agentname="Bing", subject=subject, user_message=bing_original_prompt + "\n" + subject + content)
                    print(reply_content)
                    db.add_or_update_mail_entry(account_name, from_email, 1, agentgpt.conversation_history, True, passnumber)
                # attachment_path = None
                # passnumber = 1024
                # reply_subject, reply_content = ottisgpt.get_response(subject=subject, user_message=original_prompt + "\n" + subject + content)
                # db.add_or_update_mail_entry(account_name, from_email, 1, ottisgpt.conversation_history, False, passnumber)
            else:
                attachment_path = None
                responsenumber = isNew + 1
                agentgpt.conversation_history = db.get_chathistory_by_email(account_name, from_email)
                if responsenumber == 2:
                    reply_subject, reply_content = agentgpt.get_response(agentname="Bing", subject=subject, user_message=bing_second_prompt + "\n" + subject + content)
                    if reply_content == "yes":
                        imgnum = random.randint(1, 3)
                        attachment_path = f"{content}_out.png"
                        change_image_text(imgnum, f"Hi, {content}", attachment_path)
                        db.add_or_update_mail_entry(account_name. from_email, responsenumber, agentgpt.conversation_history, True, passnumber)
                        reply_subject, reply_content = agentgpt.get_response(subject=subject, user_message=bing_third_yes_prompt + "\n" + subject + content)
                    else:
                        db.add_or_update_mail_entry(account_name. from_email, responsenumber, agentgpt.conversation_history, True, passnumber)
                        reply_subject, reply_content = agentgpt.get_response(subject=subject, user_message=bing_third_no_prompt + "\n" + subject + content)
                else:
                    db.add_or_update_mail_entry(account_name. from_email, responsenumber, agentgpt.conversation_history, True, passnumber)
                    reply_subject, reply_content = agentgpt.get_response(subject=subject, user_message=bing_third_no_prompt + "\n" + subject + content)
            print(f"Replying to Message ID: {message['id']} - Subject: {subject}")

            mark_message_as_read(service, 'me', message['id'])
            reply_to_message(service, 'me', message['id'], "", reply_content, attachment_path)

def main():    
    account_names = ['otis', 'bing']
    services = {name: get_service(name) for name in account_names}
    # service = get_service()
    db = MailListManager()
    db.clear_all_data_in_database()
    while True:
        for account_name, service in services.items():
            print(f'Checking unread messages for {account_name}')
            check_unread_messages(service, db, account_name)
        time.sleep(30)  # Adjust the sleep time as necessary
    
if __name__ == '__main__':
    main()
