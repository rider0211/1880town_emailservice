import schedule
import time
from email_handler import EmailHandler
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('SECRET_KEY')

# Configuration for database
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'chatbot',
    'raise_on_warnings': True
}

# Initialize email handlers for both Bing and Otis
bing_email_handler = EmailHandler('credentials_bing.json', 'token_bing.json', db_config, api_key, 'bing')
otis_email_handler = EmailHandler('credentials_otis.json', 'token_otis.json', db_config, api_key, 'otis')

# Start reading and responding to emails
def job():
    print("Checking emails for Bing...")
    bing_email_handler.read_emails_bing()
    print("Checking emails for Otis...")
    otis_email_handler.read_emails_otis()

# Schedule the job every 30 seconds
schedule.every(30).seconds.do(job)

# Run the scheduling in a loop
while True:
    schedule.run_pending()
    time.sleep(1)