import streamlit as st
import torch
import re
import random
import wikipedia
import datetime
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer

class JokesAPI:
    def __init__(self):
        self.base_urls = {
            'programming': 'https://v2.jokeapi.dev/joke/Programming',
            'misc': 'https://v2.jokeapi.dev/joke/Miscellaneous',
            'dark': 'https://v2.jokeapi.dev/joke/Dark',
            'pun': 'https://v2.jokeapi.dev/joke/Pun',
            'christmas': 'https://v2.jokeapi.dev/joke/Christmas'
        }
        self.joke_history = []
    
    def get_joke(self, category='misc'):
        try:
            url = self.base_urls.get(category, self.base_urls['misc'])
            response = requests.get(f"{url}?type=single")
            
            if response.status_code == 200:
                joke_data = response.json()
                joke = joke_data.get('joke', 'No joke found.')
                self.joke_history.append({'category': category, 'joke': joke})
                return joke
            else:
                return "Sorry, couldn't fetch a joke right now."
        
        except Exception as e:
            return f"Error fetching joke: {str(e)}"
    
    def get_joke_categories(self):
        return list(self.base_urls.keys())
    
    def get_random_joke(self):
        category = random.choice(list(self.base_urls.keys()))
        return self.get_joke(category)
    
    def get_joke_history(self, limit=5):
        return self.joke_history[-limit:]

class WeatherIntegration:
    def __init__(self, api_key=None):
        # Use Streamlit secrets for API key
        self.api_key = api_key or st.secrets.get('OPENWEATHERMAP_API_KEY', 'bd5e378503939ddaee76f12ad7a97608')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city):
        if not self.api_key:
            return "Weather API key not configured."
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Use Celsius
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data['cod'] == 200:
                # Extract key weather information
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                
                # Construct weather summary
                weather_summary = (
                    f"Weather in {city}:\n"
                    f"🌡️ Temperature: {temp}°C\n"
                    f"🌈 Condition: {description.capitalize()}\n"
                    f"🌬️ Feels like: {feels_like}°C\n"
                    f"💧 Humidity: {humidity}%\n"
                    f"🍃 Wind Speed: {wind_speed} m/s"
                )
                return weather_summary
            else:
                return f"Could not find weather for {city}."
        
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

class MemoryManager:
    def __init__(self, max_memory_size=50):
        self.long_term_memory = []
        self.short_term_memory = []
        self.max_memory_size = max_memory_size
    
    def add_memory(self, memory, is_long_term=False):
        if is_long_term:
            self.long_term_memory.append(memory)
            if len(self.long_term_memory) > self.max_memory_size:
                self.long_term_memory.pop(0)
        else:
            self.short_term_memory.append(memory)
            if len(self.short_term_memory) > self.max_memory_size:
                self.short_term_memory.pop(0)
    
    def get_relevant_memories(self, query, memory_type='both'):
        def find_relevant_memories(memories, query):
            query_lower = query.lower()
            return [
                memory for memory in memories 
                if any(keyword in memory.lower() for keyword in query_lower.split())
            ]
        
        if memory_type == 'long_term':
            return find_relevant_memories(self.long_term_memory, query)
        elif memory_type == 'short_term':
            return find_relevant_memories(self.short_term_memory, query)
        else:
            return (
                find_relevant_memories(self.short_term_memory, query) + 
                find_relevant_memories(self.long_term_memory, query)
            )

class AdvancedChatbot:
    def __init__(self, model_name='microsoft/DialoGPT-medium'):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
        except Exception as e:
            st.error(f"Error initializing model: {e}")
            self.tokenizer = None
            self.model = None
        
        self.memory_manager = MemoryManager()
        self.chat_history = []
        self.user_name = None
        self.weather_service = WeatherIntegration()
        
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'weather': ['weather', 'temperature', 'forecast'],
            'time': ['time', 'current time', 'what time'],
            'joke': ['joke', 'humor', 'funny'],
            'help': ['help', 'assist', 'support'],
            'memory': ['remember', 'recall', 'memory']
        }
        self.jokes_api = JokesAPI()
    
    def recognize_intent(self, message):
        message_lower = message.lower()
        
        # Enhanced joke recognition
        if 'joke' in message_lower:
            # Check for specific joke category
            categories = self.jokes_api.get_joke_categories()
            for category in categories:
                if category in message_lower:
                    return 'joke', category
            return 'joke'

        # Special handling for weather
        if 'weather' in message_lower or 'temperature' in message_lower:
            # Extract city if possible
            city_match = re.search(r'weather in (\w+)', message_lower)
            if city_match:
                return 'weather', city_match.group(1)
        
        for intent, keywords in self.intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def handle_predefined_intent(self, intent, city=None):
        if intent == 'greeting':
            greeting = f"Hello{' ' + self.user_name if self.user_name else ''}! How can I help you today?"
            return greeting
        
        elif intent == 'weather':
            if city:
                return self.weather_service.get_weather(city)
            return "Please specify a city. Example: 'weather in New York'"
        
        elif intent == 'time':
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        
        elif intent == 'joke':
            return self.jokes_api.get_random_joke()
        
        elif intent == 'help':
            return "I can help with questions, tell jokes, or chat casually."
        
        return None
    
    def process_message(self, message):
        # Check for memory-related commands
        if message.lower().startswith('remember '):
            memory = message[9:]
            self.memory_manager.add_memory(memory, is_long_term=True)
            return f"I'll remember: {memory}"
        
        if message.lower().startswith('recall '):
            query = message[7:]
            memories = self.memory_manager.get_relevant_memories(query)
            if memories:
                return "Related memories:\n" + "\n".join(memories)
            return "No relevant memories found."
        
        if message.lower().startswith('my name is '):
            self.user_name = message.split('my name is ')[1].strip()
            self.memory_manager.add_memory(f"User's name is {self.user_name}", is_long_term=True)
            return f"Nice to meet you, {self.user_name}!"
        
        # Check for joke history or joke-related requests
        if 'joke history' in message.lower():
            joke_history = self.jokes_api.get_joke_history()
            if joke_history:
                return "Recent Joke History:\n" + "\n".join([
                    f"Category: {joke['category']}, Joke: {joke['joke']}" 
                    for joke in joke_history
                ])
            return "No joke history available."
        
        # Existing intent recognition
        intent_result = self.recognize_intent(message)
        
        # Handle weather intent separately
        if isinstance(intent_result, tuple):
            intent, city = intent_result
            intent_response = self.handle_predefined_intent(intent, city)
            if intent_response:
                return intent_response
        else:
            intent = intent_result
            intent_response = self.handle_predefined_intent(intent)
            if intent_response:
                return intent_response
        
        # Try to find relevant memories first
        memories = self.memory_manager.get_relevant_memories(message)
        if memories:
            context = "Relevant memories: " + "; ".join(memories) + "\n\n"
        else:
            context = ""
        
        # Wikipedia search
        wiki_response = self.search_wikipedia(message)
        if wiki_response:
            return context + wiki_response
        
        # Generate conversational response
        response = self.generate_conversational_response(message)
        
        if not response or len(response.strip()) < 10:
            return "I'm sorry, I didn't understand that."
        
        # Add to chat and memory history
        self.memory_manager.add_memory(message)
        self.memory_manager.add_memory(response)
        
        self.chat_history.append({
            'user': message,
            'bot': response
        })
        
        return context + response
    
    def search_wikipedia(self, query):
        try:
            clean_query = re.sub(r'^(what|who|where|when|why|how)\s+', '', query, flags=re.IGNORECASE)
            summary = wikipedia.summary(clean_query, sentences=2)
            return summary
        except Exception:
            return None
    
    def generate_conversational_response(self, message):
        if not self.tokenizer or not self.model:
            return "Sorry, my language model is not available right now."
        
        input_ids = self.tokenizer.encode(
            message + self.tokenizer.eos_token, 
            return_tensors='pt'
        )
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids, 
                max_length=1000, 
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(
            output[:, input_ids.shape[-1]:][0], 
            skip_special_tokens=True
        )
        
        return response

def main():
    st.set_page_config(page_title="AI Chatbot", page_icon="💬")
    
    st.title("Advanced AI Chatbot")
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = AdvancedChatbot()
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if prompt := st.chat_input("What would you like to chat about?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            response = st.session_state.chatbot.process_message(prompt)
            st.markdown(response)
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
