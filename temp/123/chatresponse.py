import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('SECRET_KEY')

class Chatbot:
    def __init__(self, model="gpt-3.5-turbo", max_tokens = 60):
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []

    def add_message_to_conversation(self, agentname, message, is_user=True):
        speaker = "user:" if is_user else f"{agentname}:"
        self.conversation_history.append(f"{speaker} {message}")

    def get_response(self, agentname, subject, user_message):
        self.add_message_to_conversation(agentname, user_message, is_user=True)

        prompt = "\n".join(self.conversation_history)
        prompt += f"\n{agentname}:"

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                stop=["\n", " user:", f" {agentname}:"]
            )
            response_text = response.choices[0].message.content.strip()
            if response_text == "yes" or response_text == "no" or response_text =="not mentioned":
                return subject, response_text
            else:
                self.add_message_to_conversation(agentname, response_text, is_user=False)
                subject_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": f"Write a concise subject line for a reply to an email titled '{subject}':"}],
                    max_tokens=60,
                    temperature=0.7
                )
                reply_subject = subject_response.choices[0].message.content.strip()
                print(reply_subject)
                return reply_subject, response_text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None