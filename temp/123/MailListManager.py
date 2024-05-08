# from pymongo import MongoClient
import mysql.connector
import json
# from bson.objectid import ObjectId

class MailListManager:
    def __init__(self, host='localhost', database='maillist', user='root', password=''):
        self.conn = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS maillist")
        self.cursor.execute("USE maillist")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mailentries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_name VARCHAR(255) NOT NULL,
                emailaddress VARCHAR(255) NOT NULL,
                responsenumber INT NOT NULL,
                chathistory JSON,
                show_affirmation_card BOOLEAN DEFAULT FALSE,
                passnumber INT DEFAULT 0,
                UNIQUE (emailaddress, account_name)
                )
            """)
        self.conn.commit()

    def add_or_update_mail_entry(self, account_name, emailaddress, responsenumber, chathistory, show_affirmation_card=False, passnumber=0):
        chathistory = json.dumps(chathistory)
        if isinstance(chathistory, list):  # Ensure chathistory is a string
            chathistory = ' '.join(chathistory)
        query = "SELECT id FROM mailentries WHERE emailaddress = %s AND account_name = %s"
        self.cursor.execute(query, (emailaddress, account_name))
        existing_entry = self.cursor.fetchone()

        if existing_entry:
            update_query = """
                UPDATE mailentries SET responsenumber = %s, chathistory = %s, show_affirmation_card = %s, passnumber = %s
                WHERE emailaddress = %s AND account_name = %s
            """
            self.cursor.execute(update_query, (responsenumber, chathistory, int(show_affirmation_card), passnumber, emailaddress, account_name))
        else:
            insert_query = """
                INSERT INTO mailentries (account_name, emailaddress, responsenumber, chathistory, show_affirmation_card, passnumber)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (account_name, emailaddress, responsenumber, chathistory, int(show_affirmation_card), passnumber))
        self.conn.commit()

    def clear_all_data_in_database(self):
        try:
            self.cursor.execute("TRUNCATE TABLE mailentries")
            self.conn.commit()
            print("All data in the 'maillist' database has been cleared.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def get_responsenumber_by_email(self, account_name, emailaddress):
        query = "SELECT responsenumber FROM mailentries WHERE account_name = %s AND emailaddress = %s"
        self.cursor.execute(query, (account_name, emailaddress))
        result = self.cursor.fetchone()
        return result[0] if result else 0  # Return responsenumber if found, otherwise 0
        
    def get_show_affirmation_card_by_email(self, account_name, emailaddress):
        query = "SELECT show_affirmation_card FROM mailentries WHERE account_name = %s AND emailaddress = %s"
        self.cursor.execute(query, (account_name, emailaddress))
        result = self.cursor.fetchone()
        return result[0] if result else False
        
    def get_passnumber_by_email(self, account_name, emailaddress):
        query = "SELECT passnumber FROM mailentries WHERE account_name = %s AND emailaddress = %s"
        self.cursor.execute(query, (account_name, emailaddress))
        result = self.cursor.fetchone()
        return result[0] if result else 0
        
    def delete_mail_entry_by_email(self, account_name, emailaddress):
        query = "DELETE FROM mailentries WHERE account_name = %s AND emailaddress = %s"
        self.cursor.execute(query, (account_name, emailaddress))
        self.conn.commit()
        return self.cursor.rowcount
    
    def get_chathistory_by_email(self, account_name, emailaddress):
        query = "SELECT chathistory FROM mailentries WHERE account_name = %s AND emailaddress = %s"
        self.cursor.execute(query, (account_name, emailaddress))
        result = self.cursor.fetchone()
        return json.loads(result[0]) if result else None

    def update_mail_entry(self, account_name, emailaddress, responsenumber=None, chathistory=None, show_affirmation_card = None):
        update_fields = []
        params = []
        if responsenumber is not None:
            update_fields.append("responsenumber = %s")
            params.append(responsenumber)
        if chathistory is not None:
            update_fields.append("chathistory = %s")
            params.append(chathistory)
        if show_affirmation_card is not None:
            update_fields.append("show_affirmation_card = %s")
            params.append(show_affirmation_card)

        if update_fields:
            query = f"UPDATE mailentries SET {', '.join(update_fields)} WHERE account_name = %s AND emailaddress = %s"
            params.extend([account_name, emailaddress])
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.lastrowid  # Returns the ID of the updated row
        else:
            return None

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


# manager = MailListManager()  # Assuming MongoDB is running locally with default settings
# emailaddress = "titanrtx0714@gmail.com"
# account_name = "otis"

# # new_entry_id = manager.add_or_update_mail_entry(account_name, emailaddress, 1, "Initial chat history.")
# # print(f"Added new entry with ID: {new_entry_id}")

# # updated_entry_id = manager.add_or_update_mail_entry(emailaddress, 1, "Updated chat history with more information.")
# # print(f"Updated existing entry. ID of the updated entry (if any): {updated_entry_id}")

# responsenumber = manager.get_responsenumber_by_email(emailaddress, account_name)
# if responsenumber is not None:
#     print(f"Responsenumber for {emailaddress}: {responsenumber}")
# else:
#     print(f"No entry found for {emailaddress}")
# responseinfo = manager.get_chathistory_info(emailaddress)[0]
# print(responseinfo['chathistory'])
# deleted_count = manager.delete_mail_entry_by_email(emailaddress)

# manager.close_connection()
