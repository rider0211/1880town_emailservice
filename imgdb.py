import mysql.connector
from datetime import datetime, timedelta
from mysql.connector import Error

class IMGDB:
    def __init__(self, config):
        self.config = config

    def connect(self):
        return mysql.connector.connect(**self.config)

    def initialize_table(self):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            # Create table if it does not exist
            cursor.execute("""
                CREATE TABLE ScheduledMessages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255),
                    account_name VARCHAR(255),
                    username VARCHAR(255),
                    image_path VARCHAR(255),
                    scheduled_time DATETIME,
                    sent BOOLEAN DEFAULT FALSE
                );
            """)
            # Clear the table on restart
            cursor.execute("TRUNCATE TABLE ScheduledMessages;")
            conn.commit()
        except Error as e:
            print(f"Error initializing database: {e}")
            cursor.execute("TRUNCATE TABLE ScheduledMessages;")
            print(f"All data in 'ScheduledMessages' are successfully deleted.")
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def save_scheduled_message(self, email, account_name, username, image_path):
        db = self.connect()
        cursor = db.cursor()
        scheduled_time = datetime.now() + timedelta(days=1, hours=7 - datetime.now().hour, minutes=-datetime.now().minute)
        query = """
        INSERT INTO ScheduledMessages (email, account_name, username, image_path, scheduled_time, sent)
        VALUES (%s, %s, %s, %s, %s, FALSE)
        """
        cursor.execute(query, (email, account_name, username, image_path, scheduled_time))
        db.commit()
        cursor.close()
        db.close()

    def fetch_scheduled_messages(self):
        db = self.connect()
        cursor = db.cursor()
        now = datetime.now()
        cursor.execute("SELECT id, email, account_name, username, image_path FROM ScheduledMessages WHERE scheduled_time <= %s AND sent = FALSE", (now,))
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows

    def mark_message_as_sent(self, message_id):
        db = self.connect()
        cursor = db.cursor()
        cursor.execute("DELETE FROM ScheduledMessages WHERE id = %s", (message_id,))
        db.commit()
        cursor.close()
        db.close()
        print(f"Message with ID {message_id} sent and deleted from the database.")
