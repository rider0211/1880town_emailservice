import openai
from MailListManager import MailListManager

# load_dotenv()

# openai.api_key = os.getenv('SECRET_KEY')

class ChatAgent:
    def __init__(self, name, animal, api_key, show_affirmation_card = False, model = "gpt-3.5-turbo", db_config = None):
        self.api_key = api_key
        self.name = name
        self.animal = animal
        self.model = model
        openai.api_key = api_key
        if db_config == None:
            self.db = MailListManager()
        else:
            self.db = MailListManager(db_config)
        self.show_affirmation_card = show_affirmation_card

    def analyze_user_response(self, user_input):
        response = openai.completions.create(
            model=self.model,
            prompt=f"Determine if the user's response indicates a desire to see the affirmation card. User response: '{user_input}'. Does the user want to see the card?",
            max_tokens=60
        )
        return "yes" in response.choices[0].text.lower()

    def chat(self, from_email, user_input):
        messages = []
        responsenumber = self.db.get_responsenumber_by_email(self.name, from_email)
        show_affirmation_card = self.db.get_show_affirmation_card_by_email(self.name, from_email)
        passnumber = self.db.get_passnumber_by_email(self.name, from_email)
        if responsenumber == 0:
            session_prompt = f"You are a {self.animal} named {self.name} in an 1880s town. You respond to messages and ask if users want to see an affirmation card."
            messages = [{"role": "system", "content": session_prompt}]
            self.show_affirmation_card = False
        else:
            messages = self.db.get_chathistory_by_email(self.name, from_email)
        responsenumber = responsenumber + 1
        messages.append({"role": "user", "content": user_input})

        if self.show_affirmation_card:
            if self.analyze_user_response(user_input):
                user_input += "\nHere is your affirmation card: [Imagine a beautiful card here!]"
            self.show_affirmation_card = False
        else:
            user_input += "\nWould you like to see an affirmation card?"
            self.show_affirmation_card = True

        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            session_token=session_token if session_token else None
        )
        
        bing_response = response['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": bing_response})

        if session_token is None:
            session_token = response['choices'][0]['session']['session_token']

        self.db.add_or_update_mail_entry(self.name, from_email, responsenumber, messages, show_affirmation_card, passnumber)
        return bing_response, session_token
