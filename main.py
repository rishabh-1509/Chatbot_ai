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
        # Dictionary containing the base URLs for different joke categories
        self.base_urls = {
            'programming': 'https://v2.jokeapi.dev/joke/Programming',
            'misc': 'https://v2.jokeapi.dev/joke/Miscellaneous',
            'dark': 'https://v2.jokeapi.dev/joke/Dark',
            'pun': 'https://v2.jokeapi.dev/joke/Pun',
            'christmas': 'https://v2.jokeapi.dev/joke/Christmas'
        }
        # List to store the history of jokes fetched
        self.joke_history = []
    
    def get_joke(self, category='misc'):
        """
        Fetches a joke from the specified category.
        
        Args:
            category (str): The joke category to fetch. Defaults to 'misc'.

        Returns:
            str: The fetched joke or an error message.
        """
        try:
            # Get the URL for the specified category, defaulting to 'misc'
            url = self.base_urls.get(category, self.base_urls['misc'])
            
            # Make an HTTP GET request to the joke API
            response = requests.get(f"{url}?type=single")
            
            if response.status_code == 200:
                # Parse the JSON response and extract the joke
                joke_data = response.json()
                joke = joke_data.get('joke', 'No joke found.')
                
                # Save the joke to the history list
                self.joke_history.append({'category': category, 'joke': joke})
                return joke
            else:
                return "Sorry, couldn't fetch a joke right now."
        
        except Exception as e:
            # Handle exceptions and return an error message
            return f"Error fetching joke: {str(e)}"
    
    def get_joke_categories(self):
        """
        Returns a list of all available joke categories.

        Returns:
            list: A list of joke category names.
        """
        return list(self.base_urls.keys())
    
    def get_random_joke(self):
        """
        Fetches a random joke from a randomly selected category.

        Returns:
            str: The fetched joke.
        """
        # Choose a random category and fetch a joke
        category = random.choice(list(self.base_urls.keys()))
        return self.get_joke(category)
    
    def get_joke_history(self, limit=5):
        """
        Returns the history of fetched jokes, limited to a specified number.

        Args:
            limit (int): The maximum number of jokes to return. Defaults to 5.

        Returns:
            list: A list of dictionaries containing joke details.
        """
        # Return the last 'limit' number of jokes from the history
        return self.joke_history[-limit:]
class WeatherIntegration:
    def __init__(self, api_key=None):
        """
        Initializes the WeatherIntegration class with an API key and base URL.

        Args:
            api_key (str): Optional. The OpenWeatherMap API key. If not provided,
                           it attempts to fetch from Streamlit secrets.
        """
        # Retrieve API key from arguments or Streamlit secrets
        self.api_key = api_key or st.secrets.get('OPENWEATHERMAP_API_KEY', 'bd5e378503939ddaee76f12ad7a97608')
        
        # Base URL for the OpenWeatherMap API
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city):
        """
        Fetches the current weather for a specified city.

        Args:
            city (str): Name of the city to fetch weather for.

        Returns:
            str: A formatted string summarizing the weather information or an error message.
        """
        # Check if the API key is available
        if not self.api_key:
            return "Weather API key not configured."
        
        # Parameters for the API request
        params = {
            'q': city,             # City name
            'appid': self.api_key, # API key
            'units': 'metric'      # Use metric units (Celsius)
        }
        
        try:
            # Make an HTTP GET request to fetch weather data
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data['cod'] == 200:  # Successful response
                # Extract key weather details from the API response
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                
                # Format the weather information into a summary
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
                # Handle errors from the API response (e.g., invalid city)
                return f"Could not find weather for {city}."
        
        except Exception as e:
            # Handle unexpected errors during the API call
            return f"Error fetching weather: {str(e)}"

class MemoryManager:
    def __init__(self, max_memory_size=50):
        """
        Initializes the MemoryManager with a specified maximum memory size.

        Attributes:
            long_term_memory (list): Stores long-term memories.
            short_term_memory (list): Stores short-term memories.
            max_memory_size (int): Maximum number of memories to store in either memory type.
        """
        self.long_term_memory = []  # List to store long-term memories.
        self.short_term_memory = []  # List to store short-term memories.
        self.max_memory_size = max_memory_size  # Define the memory size limit.

    def add_memory(self, memory, is_long_term=False):
        """
        Adds a memory to either short-term or long-term storage.

        Args:
            memory (str): The memory to store.
            is_long_term (bool): If True, the memory is added to long-term storage. Otherwise, it goes to short-term.
        """
        if is_long_term:
            self.long_term_memory.append(memory)  # Add memory to long-term list.
            # Ensure long-term memory doesn't exceed the max size by removing the oldest memory.
            if len(self.long_term_memory) > self.max_memory_size:
                self.long_term_memory.pop(0)
        else:
            self.short_term_memory.append(memory)  # Add memory to short-term list.
            # Ensure short-term memory doesn't exceed the max size by removing the oldest memory.
            if len(self.short_term_memory) > self.max_memory_size:
                self.short_term_memory.pop(0)

    def get_relevant_memories(self, query, memory_type='both'):
        """
        Retrieves memories relevant to a given query.

        Args:
            query (str): The search query to match against stored memories.
            memory_type (str): Specifies which type of memory to search. 
                               Options are 'long_term', 'short_term', or 'both' (default).

        Returns:
            list: A list of relevant memories matching the query.
        """

        def find_relevant_memories(memories, query):
            """
            Helper function to find relevant memories in a given list.

            Args:
                memories (list): List of stored memories to search.
                query (str): The search query.

            Returns:
                list: Memories containing any keyword from the query.
            """
            query_lower = query.lower()  # Convert query to lowercase for case-insensitive search.
            return [
                memory for memory in memories 
                if any(keyword in memory.lower() for keyword in query_lower.split())
            ]

        # Search only long-term memories.
        if memory_type == 'long_term':
            return find_relevant_memories(self.long_term_memory, query)
        # Search only short-term memories.
        elif memory_type == 'short_term':
            return find_relevant_memories(self.short_term_memory, query)
        # Search both long-term and short-term memories and combine results.
        else:
            return (
                find_relevant_memories(self.short_term_memory, query) + 
                find_relevant_memories(self.long_term_memory, query)
            )
class AdvancedChatbot:
    def __init__(self, model_name='microsoft/DialoGPT-medium'):
        """
        Initializes the chatbot with a language model, memory manager, and other components.

        Args:
            model_name (str): The name of the language model to use for chatbot responses.
        """
        try:
            # Load the language model and tokenizer from the specified model.
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
        except Exception as e:
            # Handle errors during model initialization.
            st.error(f"Error initializing model: {e}")
            self.tokenizer = None
            self.model = None
        
        # Initialize a memory manager for handling long-term and short-term memories.
        self.memory_manager = MemoryManager()
        self.chat_history = []  # Store the chat history between the user and the chatbot.
        self.user_name = None  # Store the user's name, if provided.
        self.weather_service = WeatherIntegration()  # Integration for fetching weather information.

        # Define intents and their associated keywords for intent recognition.
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'weather': ['weather', 'temperature', 'forecast'],
            'time': ['time', 'current time', 'what time'],
            'joke': ['joke', 'humor', 'funny'],
            'help': ['help', 'assist', 'support'],
            'memory': ['remember', 'recall', 'memory']
        }
        self.jokes_api = JokesAPI()  # Integration for fetching jokes.

    def recognize_intent(self, message):
        """
        Recognizes the intent of the user's message.

        Args:
            message (str): The user's message.

        Returns:
            str or tuple: The recognized intent, and additional details if necessary.
        """
        message_lower = message.lower()  # Convert the message to lowercase for case-insensitive matching.
        
        # Enhanced joke recognition: Check for specific joke categories.
        if 'joke' in message_lower:
            categories = self.jokes_api.get_joke_categories()  # Fetch available joke categories.
            for category in categories:
                if category in message_lower:
                    return 'joke', category  # Return the joke intent and category.
            return 'joke'

        # Special handling for weather: Extract city if mentioned.
        if 'weather' in message_lower or 'temperature' in message_lower:
            city_match = re.search(r'weather in (\w+)', message_lower)  # Look for "weather in [city]" pattern.
            if city_match:
                return 'weather', city_match.group(1)  # Return the weather intent and city name.
        
        # Check for other intents by matching keywords.
        for intent, keywords in self.intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent  # Return the matched intent.
        
        # Default intent for unrecognized messages.
        return 'general'

    def handle_predefined_intent(self, intent, city=None):
        """
        Handles predefined intents and generates appropriate responses.

        Args:
            intent (str): The recognized intent.
            city (str, optional): The city name for weather queries.

        Returns:
            str: The chatbot's response.
        """
        if intent == 'greeting':
            # Generate a greeting message, including the user's name if available.
            greeting = f"Hello{' ' + self.user_name if self.user_name else ''}! How can I help you today?"
            return greeting
        
        elif intent == 'weather':
            # Fetch and return weather information for the specified city.
            if city:
                return self.weather_service.get_weather(city)
            return "Please specify a city. Example: 'weather in New York'"
        
        elif intent == 'time':
            # Return the current time.
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        
        elif intent == 'joke':
            # Fetch and return a random joke.
            return self.jokes_api.get_random_joke()
        
        elif intent == 'help':
            # Provide information about the chatbot's capabilities.
            return "I can help with questions, tell jokes, or chat casually."
        
        return None  # Return None if the intent is unhandled.

    def process_message(self, message):
        """
        Processes a user message and generates an appropriate response.

        Args:
            message (str): The user's message.

        Returns:
            str: The chatbot's response.
        """
        # Check for memory-related commands (e.g., "remember", "recall").
        if message.lower().startswith('remember '):
            memory = message[9:]  # Extract the memory to store.
            self.memory_manager.add_memory(memory, is_long_term=True)  # Add to long-term memory.
            return f"I'll remember: {memory}"
        
        if message.lower().startswith('recall '):
            query = message[7:]  # Extract the query for retrieving memories.
            memories = self.memory_manager.get_relevant_memories(query)  # Search for relevant memories.
            if memories:
                return "Related memories:\n" + "\n".join(memories)  # Return matched memories.
            return "No relevant memories found."
        
        if message.lower().startswith('my name is '):
            self.user_name = message.split('my name is ')[1].strip()  # Extract the user's name.
            self.memory_manager.add_memory(f"User's name is {self.user_name}", is_long_term=True)  # Store the name.
            return f"Nice to meet you, {self.user_name}!"
        
        # Check for joke history requests.
        if 'joke history' in message.lower():
            joke_history = self.jokes_api.get_joke_history()  # Fetch joke history.
            if joke_history:
                return "Recent Joke History:\n" + "\n".join([
                    f"Category: {joke['category']}, Joke: {joke['joke']}" 
                    for joke in joke_history
                ])
            return "No joke history available."
        
        # Recognize the user's intent from the message.
        intent_result = self.recognize_intent(message)
        
        # Handle predefined intents with special arguments (e.g., city for weather).
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
        
        # Search for relevant memories to include in the context.
        memories = self.memory_manager.get_relevant_memories(message)
        if memories:
            context = "Relevant memories: " + "; ".join(memories) + "\n\n"
        else:
            context = ""
        
        # Perform a Wikipedia search for additional information.
        wiki_response = self.search_wikipedia(message)
        if wiki_response:
            return context + wiki_response
        
        # Generate a conversational response using the language model.
        response = self.generate_conversational_response(message)
        
        # Fallback response if no meaningful reply is generated.
        if not response or len(response.strip()) < 10:
            return "I'm sorry, I didn't understand that."
        
        # Add the user message and bot response to memory and chat history.
        self.memory_manager.add_memory(message)
        self.memory_manager.add_memory(response)
        
        self.chat_history.append({
            'user': message,
            'bot': response
        })
        
        return context + response

def search_wikipedia(self, query):
    """
    Searches Wikipedia for a summary based on the provided query.

    Args:
        query (str): The search query, typically from the user's input.

    Returns:
        str or None: A brief summary from Wikipedia if the query is found, or None if an error occurs.
    """
    try:
        # Clean up the query by removing leading question words (e.g., "what", "who").
        clean_query = re.sub(r'^(what|who|where|when|why|how)\s+', '', query, flags=re.IGNORECASE)
        
        # Fetch a two-sentence summary from Wikipedia for the cleaned query.
        summary = wikipedia.summary(clean_query, sentences=2)
        return summary
    except Exception:
        # Return None if an error occurs (e.g., no results found).
        return None

def generate_conversational_response(self, message):
    """
    Generates a conversational response using the chatbot's language model.

    Args:
        message (str): The user's message to which the chatbot should respond.

    Returns:
        str: The generated response or an error message if the model is unavailable.
    """
    # Check if the tokenizer and model are properly initialized.
    if not self.tokenizer or not self.model:
        return "Sorry, my language model is not available right now."
    
    # Encode the user's input into token IDs, appending the end-of-sequence token.
    input_ids = self.tokenizer.encode(
        message + self.tokenizer.eos_token,  # Append EOS token to indicate the end of the input.
        return_tensors='pt'  # Return the encoded tokens as PyTorch tensors.
    )
    
    with torch.no_grad():  # Disable gradient computation for inference (faster and less memory-intensive).
        # Generate a response from the model using the input tokens.
        output = self.model.generate(
            input_ids,  # Input tokens.
            max_length=1000,  # Maximum length of the generated response.
            pad_token_id=self.tokenizer.eos_token_id  # Use the EOS token for padding.
        )
    
    # Decode the model's output tokens into a human-readable string.
    response = self.tokenizer.decode(
        output[:, input_ids.shape[-1]:][0],  # Slice out only the generated part of the output.
        skip_special_tokens=True  # Exclude special tokens from the decoded response.
    )
    
    return response

def main():
    """
    Main function to run the AI Chatbot application using Streamlit.
    """
    # Set up the Streamlit page configuration with a title and icon.
    st.set_page_config(page_title="AI Chatbot", page_icon="💬")
    
    # Display the title of the chatbot application.
    st.title("Advanced AI Chatbot")
    
    # Initialize the chatbot instance in the session state if it hasn't been already.
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = AdvancedChatbot()
    
    # Initialize messages in session state if they do not exist.
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # Stores the chat history as a list of dictionaries.
    
    # Display existing chat messages stored in session state.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):  # Use the role (user/assistant) to style the message.
            st.markdown(message["content"])  # Display the content of the message.
    
    # Handle user input in the chat input box.
    if prompt := st.chat_input("What would you like to chat about?"):
        # Add the user's message to the session state's chat history.
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user's message in the chat interface.
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get the chatbot's response to the user's input.
        with st.chat_message("assistant"):
            response = st.session_state.chatbot.process_message(prompt)  # Process the input to generate a response.
            st.markdown(response)  # Display the chatbot's response in the chat interface.
        
        # Add the chatbot's response to the session state's chat history.
        st.session_state.messages.append({"role": "assistant", "content": response})

# Entry point for the Streamlit application.
if __name__ == "__main__":
    main()
