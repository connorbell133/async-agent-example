# Asynchronous Gemini Chatbot

A proof-of-concept chatbot that demonstrates asynchronous tool execution with Google's Gemini AI, allowing the user to continue interacting with the chatbot while long-running tasks are processed in the background.

## Features

- FastAPI-based HTTP API for chat interactions
- Google Gemini AI integration for natural language understanding
- Tool calling capabilities for extending chatbot functionality
- Asynchronous task queuing and execution system
- In-memory conversation state management
- Periodic task monitoring
- Result re-integration into ongoing conversations

## Project Structure

```
.
├── app/                           # Main application package
│   ├── core/                      # Core functionality
│   │   └── config.py              # Application settings
│   ├── models/                    # Pydantic data models
│   │   └── chat.py                # Chat-related data models
│   ├── routers/                   # API route definitions
│   │   └── chat.py                # Chat-related endpoints
│   ├── services/                  # Business logic services
│   │   ├── gemini.py              # Gemini API service
│   │   └── task_manager.py        # Async task management
│   └── tools/                     # Tool implementations
│       └── weather.py             # Weather tool (with delay)
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Docker Compose configuration
├── requirements.txt               # Python dependencies
├── run.py                         # Script to run the application
├── test_chatbot.py                # Test script for the chatbot
└── .env.example                   # Example environment variables
```

## Requirements

- Python 3.8+
- Google Gemini API key

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd long-form-agent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file to add your Google API key
   ```

## Running the Application

### Local Development

Start the application with:

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload
```

### Using Docker

Build and start the container:

```bash
docker-compose up --build
```

## Testing

You can test the chatbot using the provided test script:

```bash
python test_chatbot.py
```

This script runs through a conversation flow that tests the asynchronous task execution and result re-integration.

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /api/chat`: Chat endpoint for sending messages to the chatbot

### Chat Endpoint

Request:
```json
{
  "user_id": "user-123",
  "message": "What's the weather like in London?"
}
```

Response:
```json
{
  "response": "I'm fetching the weather for London. This might take about 15 seconds. Feel free to ask me anything else in the meantime!"
}
```

## Flow Demonstration

1. User asks for weather in London
2. Chatbot acknowledges and starts the long-running task
3. User can continue asking other questions
4. When the weather task completes, the result is added to the conversation history
5. Chatbot incorporates the weather result in subsequent responses

## Design Considerations

- **In-memory State**: For simplicity, all state is stored in memory without persistence
- **Task Queuing**: Tasks are queued and executed asynchronously
- **Periodic Monitoring**: Background tasks periodically monitor task status
- **Result Re-integration**: When tasks complete, their results are added to the conversation history

## Limitations

- No persistent storage
- Limited error handling
- No authentication/authorization
- Single instance only (no distributed task queue)
- No real-time updates (client must poll for results)

## Future Enhancements

- Add persistent storage for conversations and tasks
- Implement more sophisticated error handling and retries
- Add WebSockets for real-time updates
- Implement distributed task queue for scalability
- Add more tools and tool types