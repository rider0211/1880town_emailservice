import schedule
import time
from email_handler import EmailHandler
from dotenv import load_dotenv
import os
from database import Database

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
OTIS_PASSWORD = os.getenv('OTIS_PASSWORD')
BING_PASSWORD = os.getenv('BING_PASSWORD')

db_config = {'user': 'root', 'password': '', 'host': 'localhost', 'database': 'chatbot', 'raise_on_warnings': True}

db = Database(db_config)
db.initialize_database()

bing_email_handler = EmailHandler('emmyandbing@gmail.com', BING_PASSWORD, db_config, SECRET_KEY, 'bing')
otis_email_handler = EmailHandler('otis1880town@gmail.com', OTIS_PASSWORD, db_config, SECRET_KEY, 'otis')

def job():
    print("Checking emails for Bing...")
    otis_email_handler.reconnect()
    bing_email_handler.read_emails_bing()
    print("Checking emails for Otis...")
    otis_email_handler.reconnect()
    otis_email_handler.read_emails_otis()

schedule.every(30).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
