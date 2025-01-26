# AI Chatbot

This project is an advanced conversational AI chatbot built using Streamlit, PyTorch, and the Hugging Face Transformers library. The chatbot can perform various tasks, including answering questions, telling jokes, providing weather updates, and engaging in casual conversations.

## Features

1. **Conversational AI**: The chatbot uses the `microsoft/DialoGPT-medium` model for natural and engaging conversations.
2. **Weather Integration**: Get current weather updates for any city using the OpenWeather API.
3. **Joke API**: Fetch jokes from multiple categories, such as Programming, Dark, Puns, and more.
4. **Memory Management**: Retain user-provided information (e.g., name, memories) for personalized interactions.
5. **Wikipedia Search**: Provide concise summaries for user queries based on Wikipedia.
6. **Interactive UI**: A user-friendly web-based interface built using Streamlit.

## Setup Instructions

### Prerequisites

- Python 3.8 or later installed on your system.
- A virtual environment (recommended).

### Installation

1. Clone the repository or download the source code:

```bash
$ git clone <repository-link>
$ cd <repository-directory>
```

2. Create a virtual environment and activate it:

```bash
$ python3 -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
$ pip install -r requirements.txt
```

4. Set up the OpenWeatherMap API key:
   - Obtain an API key from [OpenWeather](https://openweathermap.org/).
   - Add it to your `secrets.toml` file in the `.streamlit` directory as:
     ```toml
     [secrets]
     OPENWEATHERMAP_API_KEY = "your_api_key"
     ```

### Running the Application

Start the chatbot locally with:

```bash
$ streamlit run trail.py
```

Open the provided URL in your browser to interact with the chatbot.

## Examples of Queries

1. **General Conversation**:
   - User: "Hello"
   - Bot: "Hello! How can I help you today?"

2. **Weather Query**:
   - User: "What's the weather in New York?"
   - Bot: "Weather in New York: \n✿ Temperature: 10°C \n✿ Condition: Clear skies \n✿ Feels like: 8°C \n✿ Humidity: 60% \n✿ Wind Speed: 2.5 m/s"

3. **Joke Request**:
   - User: "Tell me a programming joke."
   - Bot: "Why do programmers prefer dark mode? Because light attracts bugs!"

4. **Time Query**:
   - User: "What's the current time?"
   - Bot: "The current time is 2:30 PM."

5. **Memory Commands**:
   - User: "Remember I love pizza."
   - Bot: "I'll remember: I love pizza."
   - User: "Recall pizza."
   - Bot: "Related memories: I love pizza."


