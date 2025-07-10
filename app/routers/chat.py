"""
Chat Router Module

This module defines the FastAPI router for chat endpoints,
handling user messages, tool calls, and asynchronous task management.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    Role,
    AsyncTask,
)
from app.services.gemini import GeminiService
from app.services.task_manager import queue_task, get_completed_tasks
from app.tools.weather import WEATHER_TOOL

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory storage for user sessions
# Structure: {user_id: {"messages": [ChatMessage]}}
user_sessions: Dict[str, Dict[str, Any]] = {}

# List of tool definitions
TOOL_DEFINITIONS = [WEATHER_TOOL]

# List of long-running tools
LONG_RUNNING_TOOLS = ["get_delayed_weather"]


async def get_gemini_service():
    """Dependency for getting the Gemini service."""
    return GeminiService()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest, gemini_service: GeminiService = Depends(get_gemini_service)
) -> ChatResponse:
    """Chat endpoint."""
    user_id = request.user_id
    message = request.message

    # Initialize user session if it doesn't exist
    if user_id not in user_sessions:
        # Add a system message to encourage helpful responses
        system_message = ChatMessage(
            role=Role.SYSTEM,
            content=(
                "You are a helpful AI assistant. You can use tools when needed, "
                "but you should also be able to answer general questions and have "
                "conversations. When tools are available, use them when appropriate, "
                "but don't limit yourself to only tool-related responses. "
                "Be conversational and helpful."
            ),
        )
        user_sessions[user_id] = {"messages": [system_message]}

    # Add user message to the session
    user_message = ChatMessage(role=Role.USER, content=message)
    user_sessions[user_id]["messages"].append(user_message)

    # Check if there are any completed tasks for this user
    completed_tasks = get_completed_tasks(user_id)

    # If there are completed tasks, add them to the conversation history
    # and prepare a natural response
    task_results_to_mention = []
    for task in completed_tasks:
        tool_result_message = ChatMessage(
            role=Role.ASSISTANT,
            content=f"[Tool Result] {task.tool_call.name}: {task.result}",
        )
        user_sessions[user_id]["messages"].append(tool_result_message)

        # Prepare a natural way to mention this completed task
        if task.tool_call.name == "get_delayed_weather":
            city = task.tool_call.parameters.get("city", "the city")
            task_results_to_mention.append(
                f"the weather in {city} you asked about earlier"
            )
        else:
            task_results_to_mention.append(
                f"the {task.tool_call.name} task you requested"
            )

        # Mark the task as processed
        task.processed = True

        logger.info("Added completed task result to conversation: %s", task.task_id)

    # If there are completed tasks, add a system message to encourage natural mention
    if task_results_to_mention:
        task_mention_content = (
            f"Note: You now have results for {', '.join(task_results_to_mention)}. "
            "Please answer the user's current question naturally, and if appropriate, "
            "also mention the completed task results at the end of your response in "
            "a natural way, like 'By the way, I found out about...' or "
            "'Also, regarding your earlier question about...'"
        )
        task_mention_prompt = ChatMessage(
            role=Role.SYSTEM,
            content=task_mention_content,
        )
        user_sessions[user_id]["messages"].append(task_mention_prompt)

    # Generate a response from Gemini
    text_response, tool_call = await gemini_service.generate_response(
        messages=user_sessions[user_id]["messages"], tools=TOOL_DEFINITIONS
    )

    # If Gemini returned a tool call
    if tool_call:
        logger.info("Gemini requested tool call: %s", tool_call.name)

        # Check if it's a long-running tool
        if tool_call.name in LONG_RUNNING_TOOLS:
            # Create a new async task
            task = AsyncTask(user_id=user_id, tool_call=tool_call)

            # Queue the task for execution
            await queue_task(task)

            # Return an acknowledgment to the user
            city_name = tool_call.parameters.get("city", "the city")
            response_text = (
                f"I'm fetching the weather for {city_name}. This might take "
                "about 15 seconds. Feel free to ask me anything else in the meantime!"
            )

            # Add assistant message to the session
            assistant_message = ChatMessage(role=Role.ASSISTANT, content=response_text)
            user_sessions[user_id]["messages"].append(assistant_message)

            return ChatResponse(response=response_text)

        # For non-long-running tools, execute synchronously (not implemented in this POC)
        response_text = (
            f"I would call {tool_call.name} with parameters {tool_call.parameters}, "
            "but synchronous tool execution is not implemented in this POC."
        )

        # Add assistant message to the session
        assistant_message = ChatMessage(role=Role.ASSISTANT, content=response_text)
        user_sessions[user_id]["messages"].append(assistant_message)

        return ChatResponse(response=response_text)

    # If it's a regular text response
    # Add assistant message to the session
    assistant_message = ChatMessage(role=Role.ASSISTANT, content=text_response)
    user_sessions[user_id]["messages"].append(assistant_message)

    return ChatResponse(response=text_response)
