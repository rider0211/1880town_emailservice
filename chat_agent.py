import openai
from database import Database

class ChatAgent:
    def __init__(self, api_key, db_config, agent_name):
        self.api_key = api_key
        openai.api_key = api_key
        self.db = Database(db_config)
        self.agent_name = agent_name
        self.show_affirmation_card = True
    def analyze_user_response(self, user_input):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Determine if these sentences refer to want or agree to see the affirmation card. After that, please choose the answer about this 'yes', 'no' or 'not mentioned': {user_input}."}]
        )
        print(response.choices[0].message.content.lower())
        return "yes" in response.choices[0].message.content.lower()
    
    def chat_bing(self, user_input, email_address):
        print("chat bing", email_address)
        messages = []
        messages = self.db.fetch_chat_history(email_address, 'bing')
        print(messages)
        self.show_affirmation_card = self.db.fetch_card_status(email_address, 'bing')
        show_affirmation_card = self.db.fetch_card_status(email_address, 'bing')
        bing_response = ""
        if not messages:
            session_prompt = f"You are a horse named Bing in 1880s town. You respond to messages with funny phrases. Don't forget to end your message with 'Do you want to see my affirmation card? If so, please send I want your affirmation card message. message with your name subject.' for every response"
            messages = [{"role": "system", "content": session_prompt}]
            messages.append({"role": "user", "content": user_input})
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            bing_response = response.choices[0].message.content.strip()
            show_affirmation_card = True
        elif show_affirmation_card == True:
            status = self.analyze_user_response(user_input)
            print("status: ", status)
            if status:
                affirmation_card_agree_prompt = "You've sent your affirmation card just before. Don't end your message with 'Do you want to see my affirmation card? If so, please send I want your affirmation card message. message with your name subject.' anymore."
                messages.append({"role": "system", "content": affirmation_card_agree_prompt})
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                bing_response = response.choices[0].message.content.strip()
                bing_response = bing_response + "Here is my affirmation card."
                show_affirmation_card = False
                after_affirmation_card_shown_prompt = "It's enough for you to respond all messages. Don't need to ask about the affirmation card again."
                messages.append({"role": "system", "content": after_affirmation_card_shown_prompt})
            else:
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                bing_response = response.choices[0].message.content.strip()
        else:
            messages.append({"role": "user", "content": user_input})
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            bing_response = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": bing_response})
        print("show_affirmation_card: ", show_affirmation_card)
        self.db.update_chat_history(email_address, 'bing', messages, show_affirmation_card)
        return bing_response
    
    def chat_otis(self, subject, user_input, email_address):
        print("chat otis", email_address)
        messages = []
        messages = self.db.fetch_chat_history(email_address, 'otis')
        print(messages)
        self.show_affirmation_card = self.db.fetch_card_status(email_address, 'otis')
        show_affirmation_card = self.db.fetch_card_status(email_address, 'otis')
        otis_response = ""
        print(subject)
        if not messages:
            session_prompt = f"You are a camel named otis in 1880s town. Your password is 'otis1024'. You respond to messages with funny phrases. All of your response has to end up with asking password to get your affirmation card and talk to user that he has to input 'PW' in the subject to get the password."
            messages = [{"role": "system", "content": session_prompt}]
            messages.append({"role": "user", "content": user_input})
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            otis_response = response.choices[0].message.content.strip()
            show_affirmation_card = True
        elif show_affirmation_card:
            if "pw" in subject.lower():
                answer_pwd_prompt = f"At first you have to say that he has to input your password and his name in subject if he want to see your affirmation card. You response have to end up with 'The password is otis1024.'. You don't need to ask the password again."
                messages = [{"role": "system", "content": answer_pwd_prompt}]
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                otis_response = response.choices[0].message.content.strip()
                print(1)
            elif "otis" in subject.lower():
                affirmation_card_agree_prompt = "You've sent your affirmation card just before. Don't ask about the password and your affirmation card anymore."
                messages = [{"role": "system", "content": affirmation_card_agree_prompt}]
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                otis_response = response.choices[0].message.content.strip() + "Here is my affirmation card."
                show_affirmation_card = False
                print(2)
            else:
                retry_prompt = "You respond to messages with funny phrases. At the end of your response, you have to ask the password."
                messages.append({'role': "system", "content": retry_prompt})
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                otis_response = response.choices[0].message.content.strip()
                print(3)
        else:
            free_card_agree_prompt = "Don't ask about the password anymore. You don't need to ask about the affirmation card. You respond to messages with funny phrases and the informations about you."
            otis_info = "You are a camel named Otis. You live in the 1880 Town on the prairie in the middle of South Dakota. You are a senior member of the 1880 Town staff. The weather is partly cloudy, with approximately twelve MPH wind out of the Northwest. It is unseasonably warm for this time of year."
            messages.append({'role': "system", "content": free_card_agree_prompt})
            messages.append({"role": "system", "content": otis_info})
            messages.append({"role": "user", "content": user_input})
            if self.analyze_user_response(user_input):
                affirmation_card_agree_prompt = "You've sent your affirmation card just before."
                messages.append({"role": "system", "content": affirmation_card_agree_prompt})
                messages.append({"role": "user", "content": user_input})
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                otis_response = response.choices[0].message.content.strip() + "Here is my affirmation card."
                print(4)
            else:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                otis_response = response.choices[0].message.content.strip()
                print(5)
        messages.append({"role": "assistant", "content": otis_response})
        print("show_affirmation_card: ", show_affirmation_card)
        self.db.update_chat_history(email_address, 'otis', messages, show_affirmation_card)
        return otis_response