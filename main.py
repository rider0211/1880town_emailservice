import schedule
import time
from email_handler import EmailHandler
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('SECRET_KEY')
otis_pwd = os.getenv('OTIS_PASSWORD')
bing_pwd = os.getenv('BING_PASSWORD')
db_config = {'user': 'root', 'password': '', 'host': 'localhost', 'database': 'chatbot', 'raise_on_warnings': True}

# bing_email_handler = EmailHandler('emmyandbing@gmail.com', 'Korgi123', db_config, api_key, 'bing')
otis_email_handler = EmailHandler('otis1880town@gmail.com', 'ifck bkvk pjjp sgdm', db_config, api_key, 'otis')

def job():
    # print("Checking emails for Bing...")
    # bing_email_handler.read_emails_bing()
    print("Checking emails for Otis...")
    otis_email_handler.reconnect()
    otis_email_handler.read_emails_otis()

schedule.every(30).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
