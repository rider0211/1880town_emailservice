from apscheduler.schedulers.background import BackgroundScheduler
import time
from email_handler import EmailHandler
from dotenv import load_dotenv
import os
from database import Database
from imgdb import IMGDB

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
OTIS_PASSWORD = "ifck bkvk pjjp sgdm"
BING_PASSWORD = "nwzy cztc xbbl ormj"

db_config = {'user': 'root', 'password': '', 'host': 'localhost', 'database': 'chatbot', 'raise_on_warnings': True}

db = Database(db_config)
imgdb = IMGDB(db_config)
imgdb.initialize_table()
db.initialize_database()

bing_email_handler = EmailHandler('emmyandbing@gmail.com', BING_PASSWORD, db_config, SECRET_KEY, 'bing')
otis_email_handler = EmailHandler('otis1880town@gmail.com', OTIS_PASSWORD, db_config, SECRET_KEY, 'otis')

def send_scheduled_emails():
    messages = imgdb.fetch_scheduled_messages()
    for message_id, email, account_name, username, image_path in messages:
        subject = "Your Scheduled Affirmation Card"
        body = f"Hi {username}, here is your scheduled affirmation card."
        if account_name == 'otis':
            otis_email_handler.send_email_with_image(email, subject, body, image_path)
        else:
            bing_email_handler.send_email_with_image(email, subject, body, image_path)
        imgdb.mark_message_as_sent(message_id)

def check_emails():
    print("Checking emails for Bing...")
    bing_email_handler.reconnect()
    bing_email_handler.read_emails_bing()
    print("Checking emails for Otis...")
    otis_email_handler.reconnect()
    otis_email_handler.read_emails_otis()

scheduler = BackgroundScheduler()
scheduler.add_job(check_emails, 'interval', seconds=30)
scheduler.add_job(send_scheduled_emails, 'cron', hour=7, minute=0)
scheduler.start()

try:
    # This will keep the main thread alive to keep the scheduler running,
    # alternatively you can use other long-running tasks or services depending on your application's requirement.
    while True:
        time.sleep(2)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
