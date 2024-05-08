import mysql.connector
import json

class Database:
    def __init__(self, config):
        self.config = config

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def update_chat_history(self, email_address, account_name, messages, show_affirmation_card):
        conn = self.get_connection()
        cursor = conn.cursor()
        chat_json = json.dumps(messages)
        show_affirmation_card_int = 1 if show_affirmation_card else 0
        try:
            # Prepare the SQL statement to insert or update the data
            query = """
            INSERT INTO chat_sessions (email_address, account_name, chat_history, show_affirmation_card)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            chat_history = VALUES(chat_history), show_affirmation_card = VALUES(show_affirmation_card)
            """
            cursor.execute(query, (email_address, account_name, chat_json, show_affirmation_card_int))
            conn.commit()
        except mysql.connector.Error as err:
            print("Error: ", err)
        finally:
            cursor.close()
            conn.close()

    def fetch_card_status(self, email_address, account_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT show_affirmation_card FROM chat_sessions WHERE email_address = %s AND account_name = %s"
        cursor.execute(query, (email_address, account_name, ))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None

    def fetch_chat_history(self, email_address, account_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT chat_history FROM chat_sessions WHERE email_address = %s AND account_name = %s"
        cursor.execute(query, (email_address, account_name, ))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return json.loads(row[0]) if row else []
