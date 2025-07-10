"""
Gemini Service Module

This module provides functionality for interacting with the Google Gen AI SDK,
including message conversion, tool handling, and response generation.
"""

import logging
from typing import List, Optional, Tuple

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.chat import ChatMessage, Role, ToolDefinition, ToolCall

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with the Google Gen AI SDK.

    This service provides methods to interact with Gemini models through the
    Google Gen AI SDK, supporting the Gemini Developer API, chat-based
    interactions, tool/function calling, and response generation.

    Attributes:
        client (genai.Client): The Google Gen AI client instance
        model_name (str): The name of the Gemini model to use
    """

    def __init__(self):
        """Initialize the Gemini service with Google Gen AI SDK configuration.

        Raises:
            RuntimeError: If the client initialization fails
            ValueError: If required environment variables are missing
        """
        self.model_name = settings.GEMINI_MODEL

        try:
            # For Gemini Developer API usage
            if not settings.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY environment variable is required for Gemini Developer API"
                )

            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            logger.info(
                "Initialized Google Gen AI client for Developer API with model: %s",
                self.model_name,
            )

        except Exception as e:
            logger.error("Failed to initialize Google Gen AI client: %s", str(e))
            raise RuntimeError(
                f"Failed to initialize Google Gen AI client: {str(e)}"
            ) from e

    def _convert_messages_to_genai_format(
        self, messages: List[ChatMessage]
    ) -> List[types.Content]:
        """Convert chat messages to Google Gen AI SDK Content format.

        Args:
            messages: List of ChatMessage objects to convert

        Returns:
            List of Google Gen AI SDK Content objects

        Note:
            - System messages are prefixed with [SYSTEM] and merged with the next user message
            - Tool responses are sent as model messages
            - The SDK only supports 'user' and 'model' roles
            - Ensures proper message alternation between user and model
        """
        genai_messages = []
        pending_system_messages = (
            []
        )  # Changed to list to handle multiple system messages
        last_role = None

        for message in messages:
            # Skip empty messages
            if not message.content or not message.content.strip():
                continue

            if message.role == Role.USER:
                # Combine any pending system messages with this user message
                content = message.content
                if pending_system_messages:
                    system_content = "\n".join(
                        [f"[SYSTEM] {msg}" for msg in pending_system_messages]
                    )
                    content = f"{system_content}\n\n{content}"
                    pending_system_messages.clear()

                # If the last message was also a user message, we need to handle it
                if last_role == "user":
                    # Combine with the last user message or add a model acknowledgment
                    if genai_messages and genai_messages[-1].role == "user":
                        # Combine with previous user message
                        prev_content = genai_messages[-1].parts[0].text
                        combined_content = f"{prev_content}\n\n{content}"
                        genai_messages[-1] = types.Content(
                            role="user", parts=[types.Part(text=combined_content)]
                        )
                        continue

                genai_messages.append(
                    types.Content(role="user", parts=[types.Part(text=content)])
                )
                last_role = "user"

            elif message.role == Role.ASSISTANT:
                # If the last message was also a model message, combine them
                if last_role == "model" and genai_messages:
                    prev_content = genai_messages[-1].parts[0].text
                    combined_content = f"{prev_content}\n\n{message.content}"
                    genai_messages[-1] = types.Content(
                        role="model", parts=[types.Part(text=combined_content)]
                    )
                else:
                    genai_messages.append(
                        types.Content(
                            role="model", parts=[types.Part(text=message.content)]
                        )
                    )
                last_role = "model"

            elif message.role == Role.SYSTEM:
                # Collect system messages to be prefixed to the next user message
                pending_system_messages.append(message.content)

            elif message.role == Role.TOOL:
                # Tool messages are treated as model responses
                tool_content = f"[TOOL RESULT] {message.content}"

                if last_role == "model" and genai_messages:
                    # Combine with previous model message
                    prev_content = genai_messages[-1].parts[0].text
                    combined_content = f"{prev_content}\n\n{tool_content}"
                    genai_messages[-1] = types.Content(
                        role="model", parts=[types.Part(text=combined_content)]
                    )
                else:
                    genai_messages.append(
                        types.Content(
                            role="model", parts=[types.Part(text=tool_content)]
                        )
                    )
                last_role = "model"

        # Handle any remaining system messages by creating a user message
        if pending_system_messages:
            system_content = "\n".join(
                [f"[SYSTEM] {msg}" for msg in pending_system_messages]
            )

            # If the last message was a user message, combine with it
            if last_role == "user" and genai_messages:
                prev_content = genai_messages[-1].parts[0].text
                combined_content = f"{prev_content}\n\n{system_content}"
                genai_messages[-1] = types.Content(
                    role="user", parts=[types.Part(text=combined_content)]
                )
            else:
                genai_messages.append(
                    types.Content(role="user", parts=[types.Part(text=system_content)])
                )

        # Ensure we have at least one message
        if not genai_messages:
            genai_messages.append(
                types.Content(role="user", parts=[types.Part(text="Hello")])
            )

        return genai_messages

    def _convert_tools_to_genai_format(
        self, tools: List[ToolDefinition]
    ) -> List[types.Tool]:
        """Convert tool definitions to Google Gen AI SDK Tool format.

        Args:
            tools: List of ToolDefinition objects to convert

        Returns:
            List of Google Gen AI SDK Tool objects with function declarations

        Note:
            Each tool is converted to a Tool with function_declarations as per the API docs.
        """
        function_declarations = []

        for tool in tools:
            # Build the parameters schema
            parameters_schema = {"type": "object", "properties": {}, "required": []}

            for param in tool.parameters:
                param_def = {"type": param.type}

                if param.description:
                    param_def["description"] = param.description

                parameters_schema["properties"][param.name] = param_def

                if param.required:
                    parameters_schema["required"].append(param.name)

            # Create the function declaration as a dictionary (not types.FunctionDeclaration)
            function_declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters_schema,
            }

            function_declarations.append(function_declaration)

        # Return a single Tool with all function declarations
        return [types.Tool(function_declarations=function_declarations)]

    async def generate_response(
        self, messages: List[ChatMessage], tools: Optional[List[ToolDefinition]] = None
    ) -> Tuple[str, Optional[ToolCall]]:
        """Generate a response using Google Gen AI SDK.

        Args:
            messages: List of chat messages for context
            tools: Optional list of tool definitions for function calling

        Returns:
            A tuple containing:
            - The generated text response (empty string if it's a tool call)
            - The tool call details (None if it's a text response)

        Raises:
            RuntimeError: For API errors or unexpected issues
        """
        try:
            genai_messages = self._convert_messages_to_genai_format(messages)
            logger.info("Generating response for %d messages", len(messages))

            # Prepare the generation config
            config_params = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            # Add tools if provided
            if tools:
                genai_tools = self._convert_tools_to_genai_format(tools)
                config_params["tools"] = genai_tools

            generation_config = types.GenerateContentConfig(**config_params)

            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=genai_messages,
                config=generation_config,
            )

            # Process response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]

                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        # Check for function calls using the correct API
                        if hasattr(part, "function_call") and part.function_call:
                            function_call = part.function_call

                            # Extract function call parameters correctly
                            parameters = {}
                            if hasattr(function_call, "args") and function_call.args:
                                # function_call.args is already a dict in the new API
                                parameters = dict(function_call.args)

                            tool_call = ToolCall(
                                name=function_call.name, parameters=parameters
                            )
                            logger.info(
                                "Function call detected: %s", function_call.name
                            )
                            return "", tool_call

                        # If it's text content
                        if hasattr(part, "text") and part.text:
                            return part.text, None

            # Fallback to response.text if available
            if hasattr(response, "text") and response.text:
                return response.text, None

            # Default empty response
            return "", None

        except Exception as e:
            error_msg = f"Error while generating response: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
